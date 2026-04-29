from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from config import BizError
from core.security import verify_token
from database import get_db
from models.user import User
# 注释：这个文件定义了核心依赖项，包括安全认证和用户权限验证。
# 它使用FastAPI的Depends机制来注入依赖项，并使用HTTPBearer进行安全认证。
# get_current_user函数用于获取当前登录的用户信息，如果用户未登录或不存在，则抛出相应的错误。
# require_admin函数用于验证当前用户是否具有管理员权限，如果没有，则抛出相应的错误。
security = HTTPBearer(auto_error=False)

# 解释每一行代码：

# 9. 如果credentials为None，表示用户未登录，抛出BizError错误，错误码2001，错误信息"请先登录"
# 10. 调用verify_token函数验证JWT令牌，获取用户ID
# 11. 使用数据库会话获取用户信息，如果用户不存在，抛出BizError错误，错误码2001，错误信息"用户不存在"
# 12. 返回当前登录的用户信息        

# 8. 定义get_current_user函数，接受HTTPAuthorizationCredentials和数据库会话
#    作为参数，返回当前登录的用户信息
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
