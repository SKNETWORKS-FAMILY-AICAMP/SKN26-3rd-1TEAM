"""
JobPocket 대량 적재(Bulk Load) 구현체 모듈입니다.
SQLAlchemy Engine의 커넥션 풀을 활용하여 MySQL 데이터베이스에
대용량 데이터를 효율적으로 배치 삽입(Batch Insert)하는 기능을 수행합니다.
"""

import json
import pandas as pd
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .sql_queries import (
    INSERT_COMPANY_SQL,
    INSERT_JOBPOST_SQL,
    INSERT_APPLICANT_SQL,
    INSERT_VECTOR_SQL,
)

from processors.mappings import (
    REQUIRED_COMPANY_COLS,
    REQUIRED_JOBPOST_COLS,
    REQUIRED_APPLICANT_COLS,
)


class JobPocketBulkLoader:
    """SQLAlchemy Engine을 활용하여 MySQL DB에 대량의 데이터를 효율적으로 적재하는 클래스"""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def _bulk_insert(
        self, sql: str, data: List[Dict[str, Any]], table_name: str
    ) -> None:
        """SQLAlchemy 엔진을 통해 대량 삽입을 수행합니다."""
        if not data:
            return

        # engine.begin()은 커넥션을 가져오고 자동으로 트랜잭션을 시작/커밋/롤백합니다.
        with self.engine.begin() as conn:
            try:
                # SQLAlchemy text()와 dict list를 사용하여 배치 삽입 수행
                exec_result = conn.execute(text(sql), data)
                print(f"✅ {table_name}: {exec_result.rowcount}개 행 적재 완료")
            except Exception as e:
                print(f"❌ {table_name} 적재 실패: {e}")
                raise e

    def upload_companies(self, df: pd.DataFrame) -> None:
        """회사 정보 적재"""
        # 필요한 컬럼만 추출하고 중복 제거 후 dict list로 변환
        companies = df[REQUIRED_COMPANY_COLS].drop_duplicates()
        data = companies.to_dict("records")
        self._bulk_insert(INSERT_COMPANY_SQL, data, "Companies")

    def upload_jobposts(self, df: pd.DataFrame) -> None:
        """채용공고 정보 적재"""
        jobposts = df[REQUIRED_JOBPOST_COLS].drop_duplicates()
        data = jobposts.to_dict("records")
        self._bulk_insert(INSERT_JOBPOST_SQL, data, "JobPosts")

    def upload_applicants_and_vectors(self, df: pd.DataFrame) -> None:
        """지원자 기록 및 벡터 정보 적재"""
        # 1. 지원 기록 준비
        applicants = df[REQUIRED_APPLICANT_COLS]
        app_data = applicants.to_dict("records")
        self._bulk_insert(INSERT_APPLICANT_SQL, app_data, "Applicants Records")

        # 2. 벡터 데이터 준비
        if "resume_embedding" in df.columns:
            vector_data = [
                {
                    "record_id": row.applicant_id,
                    "embedding": json.dumps(row.resume_embedding),
                }
                for row in df.itertuples()
            ]
            self._bulk_insert(INSERT_VECTOR_SQL, vector_data, "Resume Vectors")
