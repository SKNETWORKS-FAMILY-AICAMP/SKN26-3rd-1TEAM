"""
이력서 텍스트 데이터 구조화 파서 모듈입니다.
일정 형식을 가진 이력서 텍스트에서 학력, 경력, 주요 성과 섹션을 구분하고
DB 저장 및 검색에 용이하도록 핵심 정보를 요약 및 재구성합니다.
"""

import re


class ResumeParser:
    """이력서 텍스트에서 학력 및 경력을 추출하고 구조화하는 파서"""

    def parse(self, resume: str) -> str:
        if not resume:
            return ""

        edu_match = re.search(r"\*\*학력:\*\*", resume)
        exp_match = re.search(r"\*\*경력 및 경험:\*\*", resume)

        if not edu_match or not exp_match:
            return resume

        # 학력 섹션 추출 (최종학력 위주)
        edu_section = resume[edu_match.end() : exp_match.start()].strip()
        edu_lines = [
            line.strip("- ").strip() for line in edu_section.split("\n") if line.strip()
        ]
        final_edu = edu_lines[-1] if edu_lines else ""

        # 경력 및 경험 섹션 이후 추출
        experience_and_beyond = resume[exp_match.start() :].strip()

        # 구조화된 요약 생성
        summary = f"[최종학력] {final_edu}\n{experience_and_beyond}"
        refined_summary = re.sub(r"\*\*(.*?):\*\*", r"[\1]", summary)
        refined_summary = re.sub(r"\n{2,}", "\n", refined_summary)

        return refined_summary.strip()
