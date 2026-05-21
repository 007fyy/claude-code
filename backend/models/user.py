from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
# 避免循环导入，只有在类型检查时才导入Address类
# TYPE_CHECKING是一个特殊的常量，在类型检查时为True，在运行时为False。这样可以避免在运行时导入Address类，从而避免循环导入的问题。
if TYPE_CHECKING:
    from models.address import Address

# 解释代码，定义了一个User类，继承自Base，表示数据库中的用户表。该类包含以下字段：
# - id: 用户ID，主键，自增
# - email: 用户邮箱，唯一且不能为空
# - password_hash: 用户密码的哈希值，不能为空
# - nickname: 用户昵称，可以为空
# - avatar_url: 用户头像URL，可以为空
# - role: 用户角色，默认为"user"，不能为空
# - style_prefs: 用户的风格偏好，存储为JSON格式，可以为空
# - occasion_prefs: 用户的场合偏好，存储为JSON格式，可以为空
# - budget_pref: 用户的预算偏好，可以为空
# - created_at: 用户创建时间，默认为当前时间，不能为空
# - updated_at: 用户更新时间，默认为当前时间，更新时自动修改，不能为空  
# 此外，User类还定义了一个与Address类的关系，表示一个用户可以有多个地址。
# 该关系通过relationship函数实现，back_populates参数指定了Address类中对应的属性名，lazy参数指定了加载方式为"select"。
# 总的来说，这段代码定义了一个用户模型，用于在数据库中存储用户信息，并与地址模型建立了关联。 
# User数据存储在mysql中码？
# 如何查看User数据库中的数据？ --- 可以使用MySQL客户端工具（如MySQL Workbench）连接到数据库，执行SQL查询语句来查看User表中的数据，例如：SELECT * FROM users;
class User(Base):
    __tablename__ = "users"
 
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50), default=None)
    avatar_url: Mapped[str | None] = mapped_column(String(255), default=None)
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    gender: Mapped[str | None] = mapped_column(String(10), default=None)
    birthday: Mapped[str | None] = mapped_column(String(20), default=None)
    signature: Mapped[str | None] = mapped_column(String(100), default=None)
    bio: Mapped[str | None] = mapped_column(Text, default=None)
    # role: "user" 普通用户 | "admin" 管理员
    role: Mapped[str] = mapped_column(String(10), default="user", nullable=False)
    # 用户画像（冷启动问卷 + AI 导购采集）
    style_prefs: Mapped[list | None] = mapped_column(JSON, default=None)
    occasion_prefs: Mapped[list | None] = mapped_column(JSON, default=None)
    budget_pref: Mapped[str | None] = mapped_column(String(20), default=None)
    face_type: Mapped[str | None] = mapped_column(String(20), default=None)
    skin_tone: Mapped[str | None] = mapped_column(String(20), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    addresses: Mapped[list["Address"]] = relationship(
        "Address", back_populates="user", lazy="select"
    )
