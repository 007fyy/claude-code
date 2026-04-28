from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class VerifyCode(Base):
    __tablename__ = "verify_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 手机号（加索引，登录时按手机号查最新验证码）
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    # 过期时间（发送时写入 now() + 5 分钟）
    expired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # 是否已使用（验证成功后置 True，防止重放）
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
