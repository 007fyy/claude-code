from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey,
    Integer, JSON, Numeric, String, Text, func,
)
from sqlalchemy.orm import relationship
from database import Base

# SQLite only auto-increments INTEGER PRIMARY KEY (rowid alias), not BIGINT.
# with_variant keeps BigInteger semantics on real databases while staying compatible with SQLite.
_BIG = lambda: BigInteger().with_variant(Integer, "sqlite")


class GoodsSpu(Base):
    __tablename__ = "goods_spu"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(32), nullable=False)
    sub_category = Column(String(64))
    brand = Column(String(100))
    description = Column(Text)
    description_vector = Column(JSON)
    style_tags = Column(JSON)
    occasion_tags = Column(JSON)
    material = Column(String(64))
    target_face_shapes = Column(JSON)
    mount_type = Column(String(32), nullable=False)
    cover_url = Column(String(512))
    detail_images = Column(JSON)
    status = Column(Integer, default=1)
    sort_weight = Column(Integer, default=0)
    match_penalty_matrix = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

    skus = relationship("GoodsSku", back_populates="spu", lazy="select")


class GoodsSku(Base):
    __tablename__ = "goods_sku"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    spu_id = Column(BigInteger, ForeignKey("goods_spu.id"), nullable=False)
    sku_name = Column(String(200), nullable=False)
    color = Column(String(32))
    size = Column(String(32))
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2))
    stock = Column(Integer, default=0)
    frozen_stock = Column(Integer, default=0)
    ar_asset_url = Column(String(512))
    ar_offset_x = Column(Numeric(6, 2), default=0)
    ar_offset_y = Column(Numeric(6, 2), default=0)
    ar_scale_base = Column(Numeric(5, 3), default=1.000)
    ar_rotation_offset = Column(Numeric(5, 2), default=0)
    weight_g = Column(Numeric(6, 2))
    status = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    spu = relationship("GoodsSpu", back_populates="skus")
