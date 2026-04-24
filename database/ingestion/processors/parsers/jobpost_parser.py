"""
채용공고 비정형 데이터 파서 모듈입니다.
텍스트 형식의 채용공고에서 정규표현식을 활용하여 기업명, 포지션,
주요 업무, 자격 요건, 우대 사항 등의 필드 데이터를 계층적으로 추출합니다.
"""

import re


class JobPostParser:
    """채용공고 텍스트에서 각 항목(기업명, 직무, 자격요건 등)을 추출하는 파서"""

    def __init__(self):
        self.section_map = {
            "주요업무": "responsibilities",
            "자격요건": "qualifications",
            "우대사항": "preferred",
        }

    def parse(self, jobpost: str) -> dict:
        if not jobpost:
            return {}

        company = re.search(r"\*\*기업명\*\*:\s*\[(.*?)\]", jobpost)
        career_type = re.search(r"\*\*신입/경력\*\*:\s*\[(.*?)\]", jobpost)
        description = re.search(r"\*\*소개\*\*:\s*(.*?)(?=\n\n|$)", jobpost, re.DOTALL)
        position = re.search(r"\*\*포지션명\*\*:\s*\[(.*?)\]", jobpost)

        res = {
            "company": company.group(1).strip() if company else None,
            "description": description.group(1).strip() if description else None,
            "position_type": position.group(1).strip() if position else None,
            "career_type": career_type.group(1).strip() if career_type else None,
            "responsibilities": "",
            "qualifications": "",
            "preferred": "",
        }

        lines = jobpost.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            found_header = False
            for kor_name, eng_name in self.section_map.items():
                if kor_name in line:
                    current_section = eng_name
                    found_header = True
                    break

            if found_header:
                continue

            if current_section and line.startswith("-"):
                clean_item = line.lstrip("- ").strip()
                res[current_section] += f"{clean_item}\n"

        return res
