"""旧版 schemas，保持与 routers/goods.py、cart.py、order.py 的向后兼容。"""
from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional, Any


class Resp(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class SkuItem(BaseModel):
    sku_id: int
    sku_name: str
    color: Optional[str] = ""
    size: Optional[str] = ""
    price: float
    original_price: Optional[float] = None
    stock: int
    ar_available: bool
    ar_asset_url: Optional[str] = None
    ar_offset_x: float = 0
    ar_offset_y: float = 0
    ar_scale_base: float = 1.0
    ar_rotation_offset: float = 0


class SpuListItem(BaseModel):
    spu_id: int
    name: str
    category: str
    material: Optional[str] = ""
    style_tags: List[str] = []
    cover_url: Optional[str] = ""
    price_range: str
    mount_type: str
    default_sku_id: Optional[int] = None
    ar_available: bool
    ar_asset_url: Optional[str] = None


class GoodsListResp(BaseModel):
    code: int = 0
    message: str = "success"
    total: int
    page: int
    page_size: int
    items: List[SpuListItem]


class SpuDetail(BaseModel):
    spu_id: int
    name: str
    category: str
    description: Optional[str] = ""
    style_tags: List[str] = []
    occasion_tags: List[str] = []
    material: Optional[str] = ""
    cover_url: Optional[str] = ""
    detail_images: List[str] = []
    target_face_shapes: List[str] = []
    mount_type: str
    skus: List[SkuItem] = []


class SpuDetailResp(Resp):
    data: Optional[SpuDetail] = None


class AddCartReq(BaseModel):
    sku_id: int
    quantity: int = 1


class UpdateCartReq(BaseModel):
    cart_item_id: int
    quantity: Optional[int] = None
    selected: Optional[int] = None


class CartItemOut(BaseModel):
    cart_item_id: int
    sku_id: int
    spu_id: int
    sku_name: str
    spu_name: str
    cover_url: Optional[str] = ""
    price: float
    quantity: int
    selected: int
    subtotal: float
    ar_asset_url: Optional[str] = None
    mount_type: str


class CartListResp(BaseModel):
    code: int = 0
    message: str = "success"
    items: List[CartItemOut]
    total_selected: float
    selected_count: int


class CreateOrderReq(BaseModel):
    cart_item_ids: Optional[List[int]] = None
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    remark: Optional[str] = ""


class PayOrderReq(BaseModel):
    order_id: int
    pay_method: str = "mock_wechat"


class OrderItemOut(BaseModel):
    sku_name: Optional[str]
    cover_url: Optional[str]
    price: float
    quantity: int
    subtotal: float


class OrderOut(BaseModel):
    order_id: int
    order_no: str
    total_amount: float
    pay_amount: Optional[float]
    status: str
    receiver_name: Optional[str]
    receiver_address: Optional[str]
    items: List[OrderItemOut] = []
    created_at: Optional[str]


class OrderListResp(BaseModel):
    code: int = 0
    message: str = "success"
    total: int
    items: List[OrderOut]


class ApplyRefundReq(BaseModel):
    order_item_id: int
    reason_type: str
    reason_detail: Optional[str] = ""
