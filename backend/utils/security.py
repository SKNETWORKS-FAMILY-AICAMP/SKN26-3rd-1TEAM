"""
security utilities

인증/보안 관련 순수 유틸리티 함수를 제공합니다.

역할:
- 비밀번호 해시 생성

주의:
- DB 접근 로직은 포함하지 않습니다.
- 인증 비즈니스 로직은 services 계층에서 처리합니다.
"""

import hashlib


def hash_pw(password: str) -> str:
    """
    비밀번호를 SHA-256 해시 문자열로 변환합니다.

    Args:
        password: 원본 비밀번호.

    Returns:
        SHA-256으로 해싱된 64자리 hex 문자열.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
