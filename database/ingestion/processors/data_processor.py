"""
JobPocket 데이터 전처리 통합 관리 모듈입니다.
각종 파서(Parser), 클리너(Cleaner), 포맷터(Formatter), 인리처(Enricher)를
순차적으로 호출하여 원천 데이터를 DB 규격에 맞는 구조화된 형태로 변환합니다.
"""

import pandas as pd
from .parsers.jobpost_parser import JobPostParser
from .parsers.resume_parser import ResumeParser
from .parsers.selfintro_parser import SelfIntroParser
from .formatters.db_formatter import DBFormatter
from .data_enricher import DataEnricher
from .mappings import JOB_TITLE_MAP, CAREER_TYPE_MAP


class DataProcessor:
    """전처리 공정의 관리자. 각 Parser, Cleaner, Formatter, Enricher를 순서대로 실행함."""

    def __init__(self, company_cleaner):
        self.company_cleaner = company_cleaner
        self.jobpost_parser = JobPostParser()
        self.resume_parser = ResumeParser()
        self.selfintro_parser = SelfIntroParser()
        self.db_formatter = DBFormatter()
        self.data_enricher = DataEnricher()
        self._is_cleaner_fitted = False

    def _normalize_by_map(
        self, text: str, mapping: dict, default: str = "others"
    ) -> str:
        if not text:
            return None
        text = str(text).lower()
        for target, keywords in mapping.items():
            if any(k in text for k in keywords):
                return target
        return default

    def run_preprocess_pipeline(self, raw_dataset) -> pd.DataFrame:
        # 1. 채용공고 파싱
        jobpost_data = [self.jobpost_parser.parse(jp) for jp in raw_dataset["jobpost"]]
        df = pd.DataFrame(jobpost_data)

        # 2. 회사명 정제 (Fitted 확인)
        if not self._is_cleaner_fitted:
            self.company_cleaner.fit(df["company"])
            self._is_cleaner_fitted = True
        df["company"] = df["company"].apply(self.company_cleaner.clean)

        # 3. 직무 및 경력 표준화 (Mappings 사용)
        df["position_type"] = df["position_type"].apply(
            lambda x: self._normalize_by_map(x, JOB_TITLE_MAP)
        )
        df["career_type"] = df["career_type"].apply(
            lambda x: self._normalize_by_map(x, CAREER_TYPE_MAP, default=None)
        )

        # 4. 이력서 및 자기소개서 파싱
        df["resume_cleaned"] = [
            self.resume_parser.parse(r) for r in raw_dataset["resume"]
        ]
        df["selfintro"] = raw_dataset["selfintro"]
        df["selfintro_evaluation"] = [
            self.selfintro_parser.parse_evaluation(e) for e in raw_dataset["evaluation"]
        ]
        df["selfintro_score"] = [
            self.selfintro_parser.parse_score(s) for s in raw_dataset["selfintro_score"]
        ]
        df["selfintro_grade"] = raw_dataset["selfintro_grade"]

        # 5. 최종 포맷팅 (DB 규격, 추가 필터링 로직)
        df = self.db_formatter.format(df)

        # 6. ID 및 해시 부여 (Enrichment)
        df = self.data_enricher.enrich_ids(df)

        return df
