"""
데이터 적재 공정의 상태 관리 및 실행을 담당하는 마스터 파이프라인 모듈입니다.
체크포인트 매니저를 통해 작업 진행 상황을 유지하며, 데이터 간의 관계를 고려하여
순차적으로 DB 적재를 오케스트레이션합니다.
"""

import pandas as pd
from tqdm import tqdm
from typing import Any
from .bulk_loader import JobPocketBulkLoader
from .checkpoint_manager import CheckpointManager


class JobPocketPipeline:
    """전체 적재 공정을 관리하며 진행 상태를 유지하는 마스터 파이프라인"""

    def __init__(
        self,
        loader: JobPocketBulkLoader,
        embeddings: Any,
        checkpoint_file: str = "upload_checkpoint.json",
    ) -> None:
        self.loader = loader
        self.embeddings = embeddings
        self.checkpoint_mgr = CheckpointManager(checkpoint_file)
        self.state = self._init_state()

    def _init_state(self) -> dict:
        """체크포인트에서 상태를 로드하거나 새로 생성"""
        stored_idx = self.checkpoint_mgr.load_checkpoint()
        # 기존 호환성을 위해 딕셔너리 구조 유지
        return {
            "companies": stored_idx > 0,
            "jobposts": stored_idx > 0,
            "applicants_last_index": stored_idx,
        }

    def _save_state(self, index: int) -> None:
        """진행 상태 저장"""
        self.checkpoint_mgr.save_checkpoint(index)

    def execute(self, df: pd.DataFrame, chunk_size: int = 50) -> None:
        """데이터프레임을 기반으로 순차적 적재 실행 (ID는 data_enricher를 통해 부여됨)"""

        # 🏢 [Phase 1] 기초 정보 적재
        if not self.state["companies"]:
            print("🏢 [Phase 1] 회사 정보 적재 중...")
            self.loader.upload_companies(df)
            self.state["companies"] = True

        if not self.state["jobposts"]:
            print("🚀 [Phase 2] 채용공고 정보 적재 중...")
            self.loader.upload_jobposts(df)
            self.state["jobposts"] = True

        # 🚀 [Phase 3] 메인 데이터 및 벡터 적재
        total_rows = len(df)
        start_idx = self.state["applicants_last_index"]

        if start_idx < total_rows:
            with tqdm(
                total=total_rows, initial=start_idx, desc="Ingesting", unit="row"
            ) as pbar:
                for i in range(start_idx, total_rows, chunk_size):
                    end_idx = min(i + chunk_size, total_rows)
                    chunk_df = df.iloc[i:end_idx].copy()

                    # 🧬 실시간 청크 단위 임베딩 생성 (메모리 효율화)
                    if (
                        self.embeddings is not None
                        and "resume_cleaned" in chunk_df.columns
                    ):
                        texts = chunk_df["resume_cleaned"].tolist()
                        vectors = self.embeddings.embed_documents(texts)
                        chunk_df["resume_embedding"] = vectors

                    # Loader 호출
                    self.loader.upload_applicants_and_vectors(chunk_df)

                    # 상태 갱신 및 저장
                    self.state["applicants_last_index"] = end_idx
                    self._save_state(end_idx)
                    pbar.update(len(chunk_df))

        print("\n🎉 모든 데이터 적재가 완료되었습니다!")
