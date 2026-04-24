"""
JobPocket 인제션을 위한 데이터 로딩 유틸리티 모듈입니다.
HuggingFace Hub로부터 원격 데이터셋(이력서 매칭 데이터)을 안전하게 불러오는
기능을 담당하며, 파이프라인의 데이터 공급원 역할을 수행합니다.
"""

from datasets import Dataset, load_dataset


def fetch_dataset(data_split: str = "train") -> Dataset:
    """
    HuggingFace Hub에서 특정 스플릿의 데이터셋을 로드합니다.

    Args:
        data_split (str): 로드할 데이터 스플릿 (기본값 "train")

    Returns:
        Dataset: 로드된 HuggingFace 데이터셋 객체
    """
    print(f"📡 HuggingFace에서 '{data_split}' 데이터셋 로드 중...")
    dataset = load_dataset("Youseff1987/resume-matching-dataset-v2", split=data_split)
    return dataset
