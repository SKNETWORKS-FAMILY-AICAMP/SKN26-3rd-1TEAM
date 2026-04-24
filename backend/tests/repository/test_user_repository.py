"""
repository/user_repository.py 테스트

users 테이블에 대한 DB 접근 로직을 검증합니다.
"""

import pytest
import repository.base as repository_base

from repository.user_repository import (
    add_user_via_web,
    get_user,
    update_resume_data,
)
from utils.security import hash_pw


pytestmark = [pytest.mark.repository, pytest.mark.integration]


def test_add_user_via_web_success(
    clean_db,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    정상적인 회원가입이 성공하는지 검증합니다.
    """
    monkeypatch.setattr(repository_base, "TABLE_PREFIX", "test_")

    password_hash: str = hash_pw("pass123")

    success: bool
    message: str

    success, message = add_user_via_web(
        name="테스트유저",
        password_hash=password_hash,
        email="repo@example.com",
    )

    assert success is True
    assert "회원가입 성공" in message

    user = get_user("repo@example.com")

    assert user is not None
    assert user["username"] == "테스트유저"
    assert user["email"] == "repo@example.com"


def test_add_user_via_web_duplicate_email(
    clean_db,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    동일 이메일로 회원가입 시 실패하는지 검증합니다.
    """
    monkeypatch.setattr(repository_base, "TABLE_PREFIX", "test_")

    password_hash: str = hash_pw("pass123")

    add_user_via_web(
        name="테스트유저",
        password_hash=password_hash,
        email="duplicate@example.com",
    )

    success, message = add_user_via_web(
        name="중복유저",
        password_hash=password_hash,
        email="duplicate@example.com",
    )

    assert success is False
    assert "이미" in message


def test_get_user_returns_none_when_not_found(
    clean_db,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    존재하지 않는 이메일 조회 시 None 반환을 검증합니다.
    """
    monkeypatch.setattr(repository_base, "TABLE_PREFIX", "test_")

    user = get_user("missing@example.com")

    assert user is None


def test_update_resume_data_success(
    clean_db,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    이력서 데이터 업데이트가 정상 동작하는지 검증합니다.
    """
    monkeypatch.setattr(repository_base, "TABLE_PREFIX", "test_")

    password_hash: str = hash_pw("pass123")

    add_user_via_web(
        name="이력서유저",
        password_hash=password_hash,
        email="resume@example.com",
    )

    resume_data: dict = {
        "personal": {"gender": "남성"},
        "education": {"school": "테스트대학교"},
    }

    success: bool = update_resume_data(
        email="resume@example.com",
        resume_data=resume_data,
    )

    assert success is True

    user = get_user("resume@example.com")

    assert user is not None
    assert "테스트대학교" in user["resume_data"]


def test_update_resume_data_fail_when_user_not_found(
    clean_db,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    존재하지 않는 사용자에 대해 업데이트 시 False 반환을 검증합니다.
    """
    monkeypatch.setattr(repository_base, "TABLE_PREFIX", "test_")

    success: bool = update_resume_data(
        email="missing@example.com",
        resume_data={},
    )

    assert success is False
