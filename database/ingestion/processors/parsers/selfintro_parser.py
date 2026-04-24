"""
자기소개서 평가 데이터 전용 파서 모듈입니다.
비정형 평가 문자열에서 특정 태그를 식별하여
평가 내용과 수치화된 점수를 정규표현식으로 정밀하게 추출합니다.
"""

import re


class SelfIntroParser:
    """자기소개서 평가 결과 및 점수 등을 추출하는 파서"""

    def parse_evaluation(self, evaluation: str) -> str:
        if not evaluation or not isinstance(evaluation, str):
            return ""

        # <eval_selfintro> 태그 사이의 내용 추출
        pattern = r"<eval_selfintro>(.*?)</eval_selfintro>"
        match = re.search(pattern, evaluation, re.DOTALL)

        if match:
            return match.group(1).strip()
        return ""

    def parse_score(self, score) -> float:
        try:
            return float(score) if score is not None else 0.0
        except (ValueError, TypeError):
            return 0.0
