# 统一导出所有 ORM 模型
# 保持 `import models; models.GoodsSpu` 等旧式调用不变
# 新代码推荐用 `from models.user import User` 按需导入

from models.goods import GoodsSpu, GoodsSku          # noqa: F401
from models.cart import CartItem                      # noqa: F401
from models.order import Order, OrderItem, RefundOrder  # noqa: F401
from models.user import User                          # noqa: F401
from models.verify_code import VerifyCode             # noqa: F401
from models.address import Address                    # noqa: F401
from models.favorite import UserFavorite              # noqa: F401
from models.tracking_event import TrackingEvent       # noqa: F401
from models.browse_history import BrowseHistory        # noqa: F401

__all__ = [
    "GoodsSpu", "GoodsSku",
    "CartItem",
    "Order", "OrderItem", "RefundOrder",
    "User", "VerifyCode", "Address",
    "UserFavorite", "TrackingEvent", "BrowseHistory",
]
