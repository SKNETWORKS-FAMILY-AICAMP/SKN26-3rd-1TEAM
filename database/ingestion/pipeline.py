"""
JobPocket 데이터 전체 ETL 파이프라인 오케스트레이션 스크립트입니다.
CLI 인자를 통해 실행 옵션(청크 사이즈, 데이터 제한 등)을 조절할 수 있습니다.
"""

import sys
import argparse
import pandas as pd
from pathlib import Path

# 프로젝트 루트를 경로에 추가 (backend.common 접근용)
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

try:
    from loaders.data_loader import fetch_dataset
    from processors.cleaners.company_cleaner import CompanyNameCleaner
    from processors.data_processor import DataProcessor
    from processors.mappings import (
        COMPANY_EN_TO_KO_MAP,
        COMPANY_TYPO_FIX_MAP,
        COMPANY_CONFLICT_GROUPS,
        COMPANY_PROTECTED_KEYWORDS,
    )
    from writers.bulk_loader import JobPocketBulkLoader
    from writers.ingestion_pipeline import JobPocketPipeline
    from backend.common.db import vector_engine
    from backend.common.config import EMBEDDING_CONFIG
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError as e:
    print(f"❌ 임포트 에러: {e}")
    sys.exit(1)


def run_main_pipeline(
    chunk_size: int, limit: int = None, checkpoint_file: str = "checkpoint.json"
) -> None:
    """
    전체 데이터 인제션 파이프라인을 실행합니다.
    """

    # 1. 데이터 소스 로드 (전체 로드)
    print("📥 [1/4] 원천 데이터셋을 불러오는 중...")
    raw_dataset = fetch_dataset("train")

    # 2. 엔진 및 모델 초기화
    print("🧹 [2/4] 전처리 엔진 및 임베딩 모델 초기화 중...")
    hf_embeddings = HuggingFaceEmbeddings(**EMBEDDING_CONFIG)

    company_cleaner = CompanyNameCleaner(
        en_to_ko_map=COMPANY_EN_TO_KO_MAP,
        typo_fix_map=COMPANY_TYPO_FIX_MAP,
        conflict_groups=COMPANY_CONFLICT_GROUPS,
        protected_keywords=COMPANY_PROTECTED_KEYWORDS,
    )
    processor = DataProcessor(company_cleaner)

    # 3. 전처리 파이프라인 실행 (모든 데이터에 대해 수행)
    print("⚙️ [3/4] 전체 데이터 전처리 및 구조화 시작...")
    full_processed_df: pd.DataFrame = processor.run_preprocess_pipeline(raw_dataset)

    # 전처리 완료 후 샘플링 적용
    if limit:
        print(
            f"🎲 전처리 완료된 {len(full_processed_df)}건 중 {limit}건을 랜덤 샘플링합니다."
        )
        train_df = full_processed_df.sample(
            n=min(limit, len(full_processed_df))
        ).reset_index(drop=True)
    else:
        train_df = full_processed_df

    print(f"✅ 전처리 완료! (최종 적재 대상: {len(train_df)}건)")

    # 4. DB 적재 파이프라인 가동 (실시간 임베딩 포함)
    print(f"🚀 [4/4] DB 적재 시작 (Chunk Size: {chunk_size})...")
    db_loader = JobPocketBulkLoader(engine=vector_engine)

    load_pipeline = JobPocketPipeline(
        loader=db_loader, embeddings=hf_embeddings, checkpoint_file=checkpoint_file
    )

    try:
        load_pipeline.execute(train_df, chunk_size=chunk_size)
        print("\n🏁 [FINISH] 모든 데이터 적재가 성공적으로 완료되었습니다.")
    except Exception as e:
        print(f"\n❗ 적재 중 오류 발생: {e}")
        print(
            f"💡 중단된 지점은 {checkpoint_file}에 저장되었습니다. 다시 실행하면 재개합니다."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="JobPocket Data Ingestion Pipeline CLI"
    )

    parser.add_argument(
        "--chunk_size",
        type=int,
        default=3000,
        help="한 번에 처리할 데이터의 개수 (기본값: 3000)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="최종적으로 DB에 적재할 데이터의 최대 개수 (지정하지 않으면 전처리된 전체 데이터)",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="checkpoint.json",
        help="체크포인트 파일 이름 (기본값: checkpoint.json)",
    )

    args = parser.parse_args()

    run_main_pipeline(
        chunk_size=args.chunk_size, limit=args.limit, checkpoint_file=args.checkpoint
    )
