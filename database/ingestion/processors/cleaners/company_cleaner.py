"""
회사명 정규화 및 표준화 전문 컴포넌트입니다.
비정형 텍스트로 유입되는 회사명에서 불필요한 기호를 제거하고, 영문-한글 변환
및 유사도(Edit Distance) 분석을 통해 유사한 기업명들을 하나로 통합합니다.
"""

import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Optional, Any
import pandas as pd


class CompanyNameCleaner:
    """회사명 정제 및 표준화를 담당하는 클래스"""

    def __init__(
        self,
        en_to_ko_map: Dict[str, str],
        typo_fix_map: Dict[str, str],
        conflict_groups: List[Set[str]],
        protected_keywords: Set[str],
    ) -> None:
        self.en_to_ko_map = en_to_ko_map
        self.typo_fix_map = typo_fix_map
        self.conflict_groups = conflict_groups
        self.protected_keywords = protected_keywords

        self.counts: Optional[Counter] = None  # 회사명 빈도 수 계산
        self.name_to_conflict_words: Optional[Dict[str, Set[str]]] = None
        self.correction_map: Optional[Dict[str, str]] = None

    def _precompute_conflicts(self) -> Dict[str, Set[str]]:
        """각 이름이 어떤 충돌 그룹의 단어를 가지고 있는지 미리 계산"""
        mapping: Dict[str, Set[str]] = defaultdict(set)
        if self.counts is None:
            return dict(mapping)

        all_unique_names = self.counts.keys()
        all_conflict_words = set().union(*self.conflict_groups)

        for name in all_unique_names:
            name_low = name.lower()
            for word in all_conflict_words:
                if word in name_low:
                    mapping[name].add(word)
        return dict(mapping)

    def fit(self, company_series: pd.Series) -> None:
        """데이터셋의 회사명 분포를 분석하여 교정 맵을 생성합니다."""
        raw_series = company_series.apply(self.basic_normalize)
        self.counts = Counter(raw_series)
        self.name_to_conflict_words = self._precompute_conflicts()
        self.correction_map = self.build_correction_map()

    def basic_normalize(self, name: Any) -> str:
        """기초적인 정규화를 수행합니다. (괄호 제거, 영문 변환 등)"""
        if not isinstance(name, str) or name.strip() == "":
            return ""

        # 1. 다양한 괄호 및 내부 내용 제거
        name = re.sub(r"\(.*?\)|\[.*?\]|\{.*?\}|<.*?>", "", name)

        # 2. 오타 교정
        for typo, correct in self.typo_fix_map.items():
            name = name.replace(typo, correct)

        # 3. 영문 키워드 한글화
        for en_pattern, ko_word in self.en_to_ko_map.items():
            name = re.sub(en_pattern, ko_word, name, flags=re.IGNORECASE)

        # 4. 접미사 표준화
        name = re.sub(r"솔루션[스즈]?$|솔루션[스즈]?(?=\s)", "솔루션즈", name)
        name = re.sub(r"네트웍[스즈]?$|네트워크$", "네트웍스", name)
        name = re.sub(r"시스템[스즈]?$", "시스템즈", name)
        name = re.sub(r"게임[스즈]?$", "게임즈", name)

        # 5. 공백 정규화
        name = re.sub(r"\s+", " ", name)
        return name.strip()

    def is_edit_distance_one(self, s1: str, s2: str) -> bool:
        """두 단어의 Edit Distance가 1인지 판별합니다."""
        l1, l2 = len(s1), len(s2)
        if abs(l1 - l2) > 1:
            return False
        if l1 < l2:
            s1, s2 = s2, s1
            l1, l2 = l2, l1

        for i in range(len(s2)):
            if s1[i] != s2[i]:
                return s1[i + 1 :] == s2[i + 1 :] if l1 == l2 else s1[i + 1 :] == s2[i:]
        return l1 != l2

    def build_correction_map(self) -> Dict[str, str]:
        """유사한 회사명들을 빈도수가 높은 쪽으로 통합하는 맵을 생성합니다."""
        if self.counts is None or self.name_to_conflict_words is None:
            return {}

        unique_names = sorted(list(self.counts.keys()), key=len)
        mapping: Dict[str, str] = {}

        for i in range(len(unique_names)):
            n1 = unique_names[i]
            for j in range(i + 1, len(unique_names)):
                n2 = unique_names[j]

                if len(n2) - len(n1) > 1:
                    break

                if n1 in self.protected_keywords or n2 in self.protected_keywords:
                    continue

                n1_words = self.name_to_conflict_words.get(n1, set())
                n2_words = self.name_to_conflict_words.get(n2, set())

                if n1_words and n2_words:
                    is_conflict = False
                    for group in self.conflict_groups:
                        c1 = n1_words.intersection(group)
                        c2 = n2_words.intersection(group)
                        if c1 and c2 and c1 != c2:
                            is_conflict = True
                            break
                    if is_conflict:
                        continue

                if self.is_edit_distance_one(n1, n2):
                    major = n1 if self.counts[n1] >= self.counts[n2] else n2
                    minor = n2 if major == n1 else n1
                    mapping[minor] = major
        return mapping

    def clean(self, name: Any) -> str:
        """전체 정제 프로세스를 실행합니다."""
        s1 = self.basic_normalize(name)
        if self.correction_map is None:
            return s1
        s2 = self.correction_map.get(s1, s1)
        return self.basic_normalize(s2)
