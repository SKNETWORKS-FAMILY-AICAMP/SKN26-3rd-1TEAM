"""
데이터 강화 및 관계 식별자 생성 모듈입니다.
전처리된 데이터에 회사 ID, 채용공고 해시 기반 ID, 지원자 순번 ID 등을 부여하여
데이터베이스의 관계형 구조를 형성하고 데이터 정합성을 확보합니다.
"""

import hashlib
import pandas as pd
from typing import Any


class DataEnricher:
    """관계형 ID 생성 및 해시 추출 등 데이터 강화(Enrichment)를 담당하는 클래스"""

    def enrich_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Company ID, JobPost ID, Applicant ID 등을 생성합니다."""
        df = df.copy()

        # 1. Company ID 생성
        if "company" in df.columns:
            df["company_id"], _ = pd.factorize(df["company"])
            df["company_id"] += 1

        # 2. JobPost ID 생성 (내용 기반 해시 활용)
        # 동일 기업, 동일 직무, 동일 경력에 대해서도 여러 개의 공고가 올라오는 경우가 있으며
        # 기업 소개가 같은 경우에 자격요건, 우대 사항이 유일하여 상대적으로 내용이 짧은 기업 소개를 해시하여 유니크 조합 생성
        if "description" in df.columns:
            df["desc_hash"] = df["description"].apply(self._get_hash)

            jobpost_cols = ["company", "position_type", "career_type", "desc_hash"]
            # 존재하는 컬럼들만 기준으로 그룹화
            valid_cols = [c for c in jobpost_cols if c in df.columns]
            df["jobpost_id"] = df.groupby(valid_cols, sort=False).ngroup() + 1

        # 3. Applicant ID 생성
        df["applicant_id"] = range(1, len(df) + 1)

        return df

    def _get_hash(self, text: Any) -> str:
        """텍스트의 MD5 해시를 반환합니다."""
        if not text:
            return "empty"
        return hashlib.md5(str(text).strip().encode()).hexdigest()
