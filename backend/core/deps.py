from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from config import BizError
from core.security import verify_token
from database import get_db
from models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise BizError(2001, "请先登录")
    user_id = verify_token(credentials.credentials)
    user = db.get(User, user_id)
    if not user:
        raise BizError(2001, "用户不存在")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise BizError(2003, "无管理员权限")
    return current_user
