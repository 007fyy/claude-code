from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey,
    Integer, JSON, Numeric, String, Text, func,
)
from sqlalchemy.orm import relationship
from database import Base

# SQLite only auto-increments INTEGER PRIMARY KEY (rowid alias), not BIGINT PRIMARY KEY.
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


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1)
    sku_id = Column(BigInteger, ForeignKey("goods_sku.id"), nullable=False)
    quantity = Column(Integer, default=1)
    selected = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    sku = relationship("GoodsSku")


class Order(Base):
    __tablename__ = "orders"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False)
    user_id = Column(Integer, default=1)
    total_amount = Column(Numeric(10, 2), nullable=False)
    pay_amount = Column(Numeric(10, 2))
    status = Column(String(32), default="pending_pay")
    receiver_name = Column(String(64))
    receiver_phone = Column(String(20))
    receiver_address = Column(String(512))
    remark = Column(String(256))
    pay_time = Column(DateTime)
    ship_time = Column(DateTime)
    receive_time = Column(DateTime)
    cancel_time = Column(DateTime)
    cancel_reason = Column(String(256))
    created_at = Column(DateTime, server_default=func.now())

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    spu_id = Column(BigInteger, nullable=False)
    sku_id = Column(BigInteger, nullable=False)
    sku_name = Column(String(200))
    cover_url = Column(String(512))
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, default=1)
    subtotal = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")


class RefundOrder(Base):
    __tablename__ = "refund_orders"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    refund_no = Column(String(32), unique=True, nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    order_item_id = Column(BigInteger, ForeignKey("order_items.id"), nullable=False)
    user_id = Column(Integer, default=1)
    sku_id = Column(BigInteger, nullable=False)
    quantity = Column(Integer, default=1)
    refund_amount = Column(Numeric(10, 2), nullable=False)
    reason_type = Column(String(32), nullable=False)
    reason_detail = Column(String(512))
    status = Column(String(32), default="pending_review")
    face_shape_at_purchase = Column(String(32))
    feedback_processed = Column(Integer, default=0)
    review_note = Column(String(512))
    reviewed_at = Column(DateTime)
    return_tracking_no = Column(String(64))
    restocked_at = Column(DateTime)
    refunded_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
