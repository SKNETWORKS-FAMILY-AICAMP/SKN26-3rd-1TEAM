"""
repository/base.py 테스트

TABLE_PREFIX를 기반으로 테이블 이름이 정상적으로 생성되는지 검증합니다.
"""

import pytest
import repository.base as repository_base


pytestmark = [pytest.mark.repository, pytest.mark.unit]


def test_table_name_without_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    prefix가 없을 때 테이블 이름이 그대로 반환되는지 확인합니다.
    """
    monkeypatch.setattr(repository_base, "TABLE_PREFIX", "")

    result: str = repository_base.table_name("users")

    assert result == "users"


def test_table_name_with_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    prefix가 적용되었을 때 테이블 이름이 정상적으로 생성되는지 확인합니다.
    """
    monkeypatch.setattr(repository_base, "TABLE_PREFIX", "test_")

    result: str = repository_base.table_name("users")

    assert result == "test_users"
