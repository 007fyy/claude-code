from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.address import Address


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50), default=None)
    avatar_url: Mapped[str | None] = mapped_column(String(255), default=None)
    # role: "user" 普通用户 | "admin" 管理员
    role: Mapped[str] = mapped_column(String(10), default="user", nullable=False)
    # 用户画像（冷启动问卷 + AI 导购采集）
    style_prefs: Mapped[list | None] = mapped_column(JSON, default=None)
    occasion_prefs: Mapped[list | None] = mapped_column(JSON, default=None)
    budget_pref: Mapped[str | None] = mapped_column(String(20), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    addresses: Mapped[list["Address"]] = relationship(
        "Address", back_populates="user", lazy="select"
    )
