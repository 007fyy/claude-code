import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from config import BizError
from models.verify_code import VerifyCode


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def send_code(self, phone: str) -> None:
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        recent = (
            self.db.query(VerifyCode)
            .filter(
                VerifyCode.phone == phone,
                VerifyCode.used == False,  # noqa: E712
                VerifyCode.expired_at > now,
                VerifyCode.created_at > one_minute_ago,
            )
            .first()
        )
        if recent:
            raise BizError(2005, "发送太频繁，请 1 分钟后再试")

        code = str(random.randint(100000, 999999))
        record = VerifyCode(
            phone=phone,
            code=code,
            expired_at=now + timedelta(minutes=5),
            used=False,
        )
        self.db.add(record)
        self.db.commit()
        print(f"[MOCK SMS] 手机号 {phone} 的验证码为：{code}，5分钟内有效")

    def verify_code(self, phone: str, code: str) -> None:
        now = datetime.utcnow()
        record = (
            self.db.query(VerifyCode)
            .filter(
                VerifyCode.phone == phone,
                VerifyCode.code == code,
                VerifyCode.used == False,  # noqa: E712
                VerifyCode.expired_at > now,
            )
            .order_by(VerifyCode.created_at.desc())
            .first()
        )
        if not record:
            raise BizError(2002, "验证码错误或已过期")
        record.used = True
        self.db.commit()

    def login(self, phone: str, code: str):
        from core.security import create_access_token
        from models.user import User

        self.verify_code(phone, code)

        user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            user = User(phone=phone, role="user")
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        token = create_access_token(user.id)
        return token, user
