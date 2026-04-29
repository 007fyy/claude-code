import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import BizError, settings
from models.user import User
from models.verify_code import VerifyCode

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _send_email(to_email: str, code: str) -> None:
    msg = MIMEText(
        f"您的珑饰验证码是：{code}\n\n验证码5分钟内有效，请勿泄露给他人。",
        "plain",
        "utf-8",
    )
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = "【珑饰】邮箱验证码"

    with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
        smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        smtp.sendmail(settings.EMAIL_USER, to_email, msg.as_string())


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def _use_real_email(self) -> bool:
        return bool(settings.EMAIL_USER and settings.EMAIL_PASSWORD)

    def send_code(self, email: str) -> bool:
        """Send verification code. Returns True if user already registered."""
        now = datetime.utcnow()

        is_registered = self.db.query(User).filter(User.email == email).first() is not None

        code = str(random.randint(100000, 999999))
        self.db.add(VerifyCode(
            email=email,
            code=code,
            expired_at=now + timedelta(minutes=5),
            used=False,
        ))
        self.db.commit()

        if self._use_real_email():
            _send_email(email, code)
        else:
            raise BizError(2006, "邮件服务未配置，无法发送验证码")

        print(f"[VERIFY CODE] {email} -> {code}（5分钟有效）")

        return is_registered

    def _consume_code(self, email: str, code: str) -> None:
        now = datetime.utcnow()
        record = (
            self.db.query(VerifyCode)
            .filter(
                VerifyCode.email == email,
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

    def login_with_password(self, email: str, password: str):
        from core.security import create_access_token

        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise BizError(2011, "该邮箱尚未注册")
        if not pwd_ctx.verify(password, user.password_hash):
            raise BizError(2012, "密码错误")

        token = create_access_token(user.id)
        return token, user

    def verify(self, email: str, code: str, password: str | None = None, nickname: str | None = None):
        """Register new user with verification code. Existing users must use /auth/login."""
        from core.security import create_access_token

        self._consume_code(email, code)
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            raise BizError(2013, "该邮箱已注册，请使用密码登录")

        if not password:
            raise BizError(2010, "新用户请设置密码")

        user = User(
            email=email,
            password_hash=pwd_ctx.hash(password),
            nickname=nickname or email.split("@")[0],
            role="user",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        token = create_access_token(user.id)
        return token, user, True
