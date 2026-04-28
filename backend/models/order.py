from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey,
    Integer, Numeric, String, func,
)
from sqlalchemy.orm import relationship
from database import Base

_BIG = lambda: BigInteger().with_variant(Integer, "sqlite")


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
