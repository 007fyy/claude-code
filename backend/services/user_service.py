from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import BizError
from models.user import User
from schemas.user import ChangePasswordReq, UpdatePrefsReq, UpdateUserReq

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_me(self, user: User, req: UpdateUserReq) -> User:
        update_data = req.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_prefs(self, user: User, req: UpdatePrefsReq) -> User:
        update_data = req.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user: User, req: ChangePasswordReq) -> None:
        if not pwd_ctx.verify(req.old_password, user.password_hash):
            raise BizError(2009, "原密码错误")
        user.password_hash = pwd_ctx.hash(req.new_password)
        self.db.commit()
