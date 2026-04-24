"""
auth router

인증(Auth) 관련 API 엔드포인트를 정의합니다.

역할:
- 클라이언트 요청(Request)을 받아 service 계층으로 전달
- service 계층의 결과를 그대로 반환

구성:
- POST /login: 사용자 로그인
- POST /signup: 사용자 회원가입

주의:
- 비즈니스 로직은 service 계층에서 처리합니다.
- DB 접근 및 비밀번호 해싱 로직은 포함하지 않습니다.
"""

from fastapi import APIRouter

from schemas import LoginRequest, SignupRequest
from services import login_user, signup_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
def login(req: LoginRequest):
    """
    사용자 로그인 API

    Request Body:
        email (str): 사용자 이메일
        password (str): 사용자 비밀번호 (평문)

    Returns:
        dict:
            status (str): 처리 결과 ("success")
            user_info (dict): 사용자 정보
                - username (str)
                - email (str)
                - resume_data (str)

    Raises:
        HTTPException:
            401: 이메일 또는 비밀번호가 일치하지 않을 경우
    """
    return login_user(
        email=req.email,
        password=req.password,
    )


@router.post("/signup")
def signup(req: SignupRequest):
    """
    사용자 회원가입 API

    Request Body:
        name (str): 사용자 이름
        email (str): 사용자 이메일
        password (str): 사용자 비밀번호 (평문)

    Returns:
        dict:
            status (str): 처리 결과 ("success")
            detail (str): 처리 메시지

    Raises:
        HTTPException:
            400: 중복 이메일 또는 DB 처리 실패 시
    """
    return signup_user(
        name=req.name,
        email=req.email,
        password=req.password,
    )
