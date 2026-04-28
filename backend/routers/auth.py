from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.common import ApiResponse
from schemas.user import LoginOut, LoginReq, SendCodeReq, UserOut
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/send-code", response_model=ApiResponse[None])
def send_code(req: SendCodeReq, db: Session = Depends(get_db)):
    AuthService(db).send_code(req.phone)
    return ApiResponse()


@router.post("/login", response_model=ApiResponse[LoginOut])
def login(req: LoginReq, db: Session = Depends(get_db)):
    token, user = AuthService(db).login(req.phone, req.code)
    return ApiResponse(data=LoginOut(token=token, user=UserOut.model_validate(user)))
