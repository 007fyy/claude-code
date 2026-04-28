# 重导出旧版 schemas，保持 `import schemas; schemas.GoodsListResp` 等旧式调用兼容
from schemas.legacy import (  # noqa: F401
    Resp, SkuItem, SpuListItem, GoodsListResp, SpuDetail, SpuDetailResp,
    AddCartReq, UpdateCartReq, CartItemOut, CartListResp,
    CreateOrderReq, PayOrderReq, OrderItemOut, OrderOut, OrderListResp,
    ApplyRefundReq,
)
