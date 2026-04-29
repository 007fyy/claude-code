from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, func
from database import Base

_BIG = lambda: BigInteger().with_variant(Integer, "sqlite")


class BrowseHistory(Base):
    __tablename__ = "browse_history"
    __table_args__ = (
        Index("ix_browse_user_time", "user_id", "created_at"),
    )

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    spu_id = Column(_BIG(), ForeignKey("goods_spu.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
