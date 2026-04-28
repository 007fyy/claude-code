from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship
from database import Base

_BIG = lambda: BigInteger().with_variant(Integer, "sqlite")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    user_id = Column(Integer, default=1)
    sku_id = Column(BigInteger, ForeignKey("goods_sku.id"), nullable=False)
    quantity = Column(Integer, default=1)
    selected = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    sku = relationship("GoodsSku")
