from sqlalchemy import BigInteger, Column, DateTime, Integer, JSON, String, func
from database import Base

_BIG = lambda: BigInteger().with_variant(Integer, "sqlite")


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    event_type = Column(String(32), nullable=False, index=True)
    target_type = Column(String(32), nullable=False)
    target_id = Column(String(64), nullable=True)
    page_path = Column(String(256), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
