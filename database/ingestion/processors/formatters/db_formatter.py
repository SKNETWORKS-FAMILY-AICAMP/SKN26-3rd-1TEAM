"""
데이터베이스 규격 맞춤형 최종 포맷터 모듈입니다.
전처리된 데이터프레임의 컬럼명을 DB 스키마에 맞게 변경하고, 결측치 처리 및
등급 데이터의 매핑(한글 -> 영문)을 수행하여 적재 직전의 최종 데이터를 생성합니다.
"""

import pandas as pd
from ..mappings import GRADE_MAP


class DBFormatter:
    """전처리된 데이터를 DB 스키마에 맞게 최종 변환하는 포맷터"""

    def format(self, df: pd.DataFrame) -> pd.DataFrame:
        # 1. 등급 맵핑 (상/중/하 -> high/mid/low)
        if "selfintro_grade" in df.columns:
            df["selfintro_grade"] = df["selfintro_grade"].map(GRADE_MAP)

        # 2. 결측치 처리
        df = df.dropna(how="any")

        # 3. 비즈니스 로직에 맞게 추가 필터링
        # '상' 등급 자소서에 해당하는 데이터만 올릴 예정
        if "selfintro_grade" in df.columns:
            df = df[df["selfintro_grade"] == "high"]

        return df
