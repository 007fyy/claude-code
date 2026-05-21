from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.common import ApiResponse
from schemas.user import LoginOut, LoginReq, ResetPasswordReq, SendCodeOut, SendCodeReq, UserOut, VerifyReq
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/send-code", response_model=ApiResponse[SendCodeOut])
def send_code(req: SendCodeReq, db: Session = Depends(get_db)):
    is_registered = AuthService(db).send_code(req.email)
    return ApiResponse(
        data=SendCodeOut(is_registered=is_registered),
        message="该邮箱已注册，请使用密码登录" if is_registered else "验证码已发送到您的邮箱",
    )


@router.post("/send-reset-code", response_model=ApiResponse[None])
def send_reset_code(req: SendCodeReq, db: Session = Depends(get_db)):
    AuthService(db).send_reset_code(req.email)
    return ApiResponse(data=None, message="验证码已发送到您的邮箱")


@router.post("/reset-password", response_model=ApiResponse[None])
def reset_password(req: ResetPasswordReq, db: Session = Depends(get_db)):
    AuthService(db).reset_password(req.email, req.code, req.new_password)
    return ApiResponse(data=None, message="密码重置成功，请使用新密码登录")


@router.post("/login", response_model=ApiResponse[LoginOut])
def login(req: LoginReq, db: Session = Depends(get_db)):
    token, user = AuthService(db).login_with_password(req.email, req.password)
    return ApiResponse(data=LoginOut(
        token=token,
        user=UserOut.model_validate(user),
        is_new_user=False,
    ))


@router.post("/verify", response_model=ApiResponse[LoginOut])
def verify(req: VerifyReq, db: Session = Depends(get_db)):
    token, user, is_new = AuthService(db).verify(
        req.email, req.code, req.password, req.nickname
    )
    return ApiResponse(data=LoginOut(
        token=token,
        user=UserOut.model_validate(user),
        is_new_user=is_new,
    ))
