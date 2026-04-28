from sqlalchemy.orm import Session

from models.user import User
from schemas.user import UpdatePrefsReq, UpdateUserReq


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
