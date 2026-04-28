

# order-plan.md — 珑饰订单模块开发计划

**模块范围**：创建订单、模拟支付、取消订单、订单列表/详情、物流状态流转  
**技术栈**：FastAPI + SQLAlchemy + JWT 认证  
**工作目录**：`L:\claude-code\backend\`  
**架构规范**：严格遵循 `L:\claude-code\CLAUDE.md`

---

## 当前状态说明

| 文件 | 状态 | 说明 |
|---|---|---|
| `models/order.py` | ⚠️ 需对齐 | Order 用整数 PK，CLAUDE.md 用字符串 ID（LS...），状态值不一致 |
| `routers/order.py` | ⚠️ 需重构 | 路由存在但 DEMO_USER=1、HTTPException、状态值 "paid" 非 "pending_ship" |
| `schemas/order.py` | ❌ 缺失 | 需新建 |
| `services/order_service.py` | ❌ 缺失 | 逻辑内联在路由里 |

---

## 任务总览

| # | 任务 | 预计时间 | 依赖 |
|---|---|---|---|
| 1 | 对齐订单模型（字符串 PK + 状态枚举） | 30 min | 无 |
| 2 | 创建 schemas/order.py | 30 min | 1 |
| 3 | 创建 OrderService（创建订单 + 库存锁定） | 40 min | 1、2 |
| 4 | 重构创建订单接口（接入 JWT + 地址快照） | 30 min | 3、user-plan、cart-plan |
| 5 | 重构模拟支付接口（状态流转到 pending_ship） | 20 min | 3 |
| 6 | 重构取消订单接口（库存回滚） | 20 min | 3 |
| 7 | 重构订单列表接口（支持状态筛选） | 20 min | 3 |
| 8 | 重构订单详情接口（含物流进度） | 20 min | 3 |
| 9 | 全流程冒烟测试 | 30 min | 全部 |

---

## Task 1：对齐订单模型

**预计时间**：30 分钟  
**依赖**：无  
**完成标志**：`python -c "from models.order import Order; print(Order.__table__.c.keys())"` 含 id(str)、addr_name 等字段

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对齐订单相关模型，使其符合 CLAUDE.md 设计。

【CLAUDE.md 订单表设计要点】
- orders.id 是 VARCHAR(30) 主键（如 "LS202604280001"），非自增整数
- 收货信息用快照字段：addr_name/addr_phone/addr_detail（下单时拷贝，不引用地址表）
- 状态值：pending_pay / pending_ship / in_transit / completed / cancelled
- 包含：paid_at / shipped_at / completed_at 时间字段

【任务】完全重写 backend/models/order.py（不保留旧模型，但保持文件名不变）：

① Order 模型（__tablename__ = "orders"）：
   id: 字符串主键 Column(String(30), primary_key=True)（如 "LS202604280001"）
   user_id: Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
   status: Column(String(20), default="pending_pay", nullable=False)
     允许值：pending_pay / pending_ship / in_transit / completed / cancelled
   addr_name: Column(String(50), nullable=False)   ← 收货人姓名快照
   addr_phone: Column(String(20), nullable=False)
   addr_detail: Column(String(300), nullable=False)  ← 省市区+详情合并字段
   amount: Column(Numeric(10,2), nullable=False)
   shipping_fee: Column(Numeric(10,2), default=0.00)
   pay_method: Column(String(20))                  ← "wechat" | "alipay"
   note: Column(String(300))
   tracking_no: Column(String(50))
   logistics_company: Column(String(50))
   paid_at / shipped_at / completed_at: Column(DateTime, nullable=True)
   created_at / updated_at: Column(DateTime, server_default + onupdate)
   items: relationship("OrderItem", back_populates="order", lazy="select")

② OrderItem 模型（__tablename__ = "order_items"）：
   id: 自增整数主键
   order_id: Column(String(30), ForeignKey("orders.id"), nullable=False, index=True)
   sku_id / spu_id: Column(Integer, nullable=False)
   name: Column(String(150), nullable=False)   ← 商品名快照
   cover_url: Column(String(255))
   price: Column(Numeric(10,2), nullable=False)
   qty: Column(Integer, nullable=False)
   order: relationship("Order", back_populates="items")

③ 删除旧的 RefundOrder 类（售后模块独立实现，见 aftersale-plan.md）

④ 更新 models/__init__.py：替换 RefundOrder 为新的 Order、OrderItem 导出

【验证】
    python -c "
    import models
    from database import engine, Base
    from models.order import Order, OrderItem
    Order.__table__.drop(engine, checkfirst=True)
    OrderItem.__table__.drop(engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    print('Order columns:', list(Order.__table__.c.keys()))
    print('OrderItem columns:', list(OrderItem.__table__.c.keys()))
    # 验证 id 是字符串类型
    from sqlalchemy import String
    assert isinstance(Order.__table__.c.id.type, String), 'id 应为 String 类型'
    print('PASS')
    "
```

---

## Task 2：创建 schemas/order.py

**预计时间**：30 分钟  
**依赖**：Task 1  
**完成标志**：`python -c "from schemas.order import CreateOrderReq, OrderOut"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建订单模块的 Pydantic Schema。

【任务】创建 backend/schemas/order.py：

CreateOrderReq:         # 创建订单请求
    cart_item_ids: list[int]     # 要结算的购物车项 ID 列表
    address_id: int              # 收货地址 ID（从 addresses 表查快照）
    pay_method: str              # "wechat" | "alipay"
    note: str | None = None

    @field_validator("pay_method")
    # 验证只允许 "wechat" 或 "alipay"

PayOrderReq:            # 支付请求（模拟）
    order_id: str               # 订单 ID（字符串）

OrderItemOut:           # 订单商品行
    sku_id: int
    spu_id: int
    name: str
    cover_url: str | None
    price: float
    qty: int
    subtotal: float     # price * qty，后端计算

OrderOut:               # 订单摘要（列表用）
    order_id: str
    status: str
    status_label: str   # 状态中文标签，后端转换
    addr_name: str
    addr_phone: str
    addr_detail: str
    amount: float
    shipping_fee: float
    pay_method: str | None
    tracking_no: str | None
    logistics_company: str | None
    note: str | None
    items: list[OrderItemOut]
    paid_at: str | None     # ISO 8601 字符串
    shipped_at: str | None
    completed_at: str | None
    created_at: str | None

OrderListOut:
    total: int
    page: int
    page_size: int
    items: list[OrderOut]

STATUS_LABELS = {        # 模块级常量，供 service 层使用
    "pending_pay": "待付款",
    "pending_ship": "待发货",
    "in_transit": "运输中",
    "completed": "已完成",
    "cancelled": "已取消",
}

【验证】
    python -c "
    from schemas.order import CreateOrderReq, OrderOut, STATUS_LABELS
    print('STATUS_LABELS:', STATUS_LABELS)
    req = CreateOrderReq(cart_item_ids=[1,2], address_id=1, pay_method='wechat')
    print('req:', req.model_dump())
    "
```

---

## Task 3：创建 OrderService

**预计时间**：40 分钟  
**依赖**：Task 1、2  
**完成标志**：Python 脚本直接调用 service 完成订单创建

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建订单业务逻辑层。

【任务】创建 backend/services/order_service.py：

import random, time
from datetime import datetime

ORDER_ID_PREFIX = "LS"

def _gen_order_id() -> str:
    """生成订单号：LS + yyyyMMddHHmmss + 4位随机数"""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    rand = random.randint(1000, 9999)
    return f"{ORDER_ID_PREFIX}{ts}{rand}"

class OrderService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def create(self, req: CreateOrderReq) -> OrderOut:
        """
        创建订单：
        1. 查询 cart_item_ids 对应的购物车项（必须属于当前用户且 selected=True）
           若列表为空 → BizError(1201, "没有可下单的购物车项")
        2. 查询 address_id 对应的地址（必须属于当前用户）
           → BizError(1202, "收货地址不存在")
        3. 逐项检查库存（sku.stock >= qty），不足 → BizError(1203, f"{sku_name} 库存不足")
        4. 生成订单 ID（_gen_order_id()）
        5. 扣减 goods_sku.stock（with_for_update() 行级锁）
        6. 插入 Order 记录（地址快照：addr_name/addr_phone/addr_detail 从 address 对象拼接）
        7. 逐项插入 OrderItem 记录（价格/名称快照）
        8. 删除已下单的购物车项
        9. db.commit()
        10. 返回 _to_out(order)
        """

    def pay(self, order_id: str) -> OrderOut:
        """
        模拟支付：
        1. 查 Order，不存在/不属于当前用户 → BizError(1204, "订单不存在")
        2. status != "pending_pay" → BizError(1205, "订单状态不支持支付")
        3. 更新 status="pending_ship"，paid_at=datetime.now()
        4. db.commit()
        5. 返回 _to_out(order)
        """

    def cancel(self, order_id: str) -> None:
        """
        取消订单：
        1. 查 Order，验证归属
        2. status != "pending_pay" → BizError(1206, "只有待支付订单可取消")
        3. 回滚库存：逐项 sku.stock += qty
        4. 更新 status="cancelled"
        5. db.commit()
        """

    def list_orders(self, status: str | None, page: int, page_size: int) -> OrderListOut:
        """按用户查询，支持状态筛选，分页"""

    def get_detail(self, order_id: str) -> OrderOut:
        """查订单详情，验证归属"""

    def _to_out(self, order: Order) -> OrderOut:
        """ORM → OrderOut，计算 status_label、格式化时间"""

    def _get_or_404(self, order_id: str) -> Order:
        order = self.db.get(Order, order_id)
        if not order or order.user_id != self.user_id:
            raise BizError(1204, "订单不存在")
        return order
```

---

## Task 4：重构创建订单接口

**预计时间**：30 分钟  
**依赖**：Task 3、user-plan、cart-plan  
**完成标志**：下单后返回字符串格式的 order_id，库存相应减少

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在完全重写 backend/routers/order.py。

【任务】重写 order.py，替换旧版，保持路由路径和 main.py 注册方式不变：

router = APIRouter()

@router.post("/create", response_model=ApiResponse[OrderOut])
def create_order(
    req: CreateOrderReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = OrderService(db, current_user.id).create(req)
    return ApiResponse(data=order)

（Task 5-8 继续在此文件追加其余接口）

【验证】先确保购物车中有商品且用户有地址（来自 cart-plan 和 user-plan）：
    # 获取购物车中的 cart_item_id
    curl -s http://localhost:8000/api/v1/cart/list \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    print('cart_item_ids:', [i['cart_item_id'] for i in d['items']])
    "

    # 获取地址 id
    curl -s http://localhost:8000/api/v1/user/address \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    print('address_id:', d[0]['id'] if d else 'NO ADDRESS')
    "

    # 创建订单（替换 CART_ID 和 ADDR_ID）
    curl -s -X POST http://localhost:8000/api/v1/order/create \
      -H "Authorization: Bearer TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"cart_item_ids":[CART_ID],"address_id":ADDR_ID,"pay_method":"wechat"}' \
      | python -m json.tool
    # 预期：order_id 为 "LS202604XXXXXXXX" 格式字符串
```

---

## Task 5：重构模拟支付接口

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：支付后订单状态变为 pending_ship，paid_at 有值

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在重构后的 order.py 追加支付接口。

【任务】追加：

@router.post("/pay", response_model=ApiResponse[OrderOut])
def pay_order(req: PayOrderReq, db=Depends(get_db), current_user=Depends(get_current_user)):
    order = OrderService(db, current_user.id).pay(req.order_id)
    return ApiResponse(data=order)

【验证】先创建订单得到 ORDER_ID，然后：
    curl -s -X POST http://localhost:8000/api/v1/order/pay \
      -H "Authorization: Bearer TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"order_id":"ORDER_ID"}' | python -m json.tool
    # 预期：status="pending_ship"，status_label="待发货"，paid_at 有值

    # 重复支付（应报错 code:1205）
    curl -s -X POST http://localhost:8000/api/v1/order/pay \
      -H "Authorization: Bearer TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"order_id":"ORDER_ID"}' | python -m json.tool
    # 预期：{"code":1205,"message":"订单状态不支持支付","data":null}
```

---

## Task 6：重构取消订单接口

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：取消后库存回滚，重复取消返回 code:1206

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 order.py 追加取消接口。

【任务】追加：

@router.post("/cancel", response_model=ApiResponse[None])
def cancel_order(
    order_id: str = Query(...),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    OrderService(db, current_user.id).cancel(order_id)
    return ApiResponse()

【验证】新建一个待支付订单，然后：
    # 取消
    curl -s -X POST "http://localhost:8000/api/v1/order/cancel?order_id=ORDER_ID" \
      -H "Authorization: Bearer TOKEN" | python -m json.tool
    # 预期：code:0

    # 验证订单状态
    curl -s "http://localhost:8000/api/v1/order/ORDER_ID" \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    assert d['status'] == 'cancelled', 'FAIL'
    print('PASS status:', d['status'])
    "

    # 已支付订单不能取消（先支付一个新订单再尝试取消）
    curl -s -X POST "http://localhost:8000/api/v1/order/cancel?order_id=PAID_ORDER_ID" \
      -H "Authorization: Bearer TOKEN" | python -m json.tool
    # 预期：code:1206
```

---

## Task 7：重构订单列表接口

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：列表返回正确，status 过滤有效，分页正常

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 order.py 追加订单列表接口。

【任务】追加：

@router.get("/list", response_model=ApiResponse[OrderListOut])
def order_list(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    data = OrderService(db, current_user.id).list_orders(status, page, page_size)
    return ApiResponse(data=data)

【验证】
    # 全部订单
    curl -s "http://localhost:8000/api/v1/order/list" \
      -H "Authorization: Bearer TOKEN" | python -m json.tool

    # 过滤待发货
    curl -s "http://localhost:8000/api/v1/order/list?status=pending_ship" \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    assert all(i['status']=='pending_ship' for i in d['items']), 'FAIL'
    print('PASS pending_ship count:', len(d['items']))
    "
```

---

## Task 8：重构订单详情接口

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：返回完整订单信息含 items 数组和物流字段

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 order.py 追加订单详情接口。

【注意】FastAPI 路由有优先级，GET /list 必须在 GET /{order_id} 之前注册，
否则 "list" 会被当作 order_id 参数。请确保在同一 router 中 /list 在 /{order_id} 上方。

【任务】追加（注意放在 /list 之后）：

@router.get("/{order_id}", response_model=ApiResponse[OrderOut])
def order_detail(order_id: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    data = OrderService(db, current_user.id).get_detail(order_id)
    return ApiResponse(data=data)

【验证】
    ORDER_ID=LS...  # 替换为真实订单 ID
    curl -s "http://localhost:8000/api/v1/order/$ORDER_ID" \
      -H "Authorization: Bearer TOKEN" | python -m json.tool
    # 预期：含 items 数组（有 name、price、qty、subtotal），addr_name 等地址快照字段

    # 访问不存在的订单
    curl -s "http://localhost:8000/api/v1/order/LS000000000000" \
      -H "Authorization: Bearer TOKEN" | python -m json.tool
    # 预期：{"code":1204,"message":"订单不存在","data":null}
```

---

## Task 9：全流程冒烟测试

**预计时间**：30 分钟  
**依赖**：全部前序任务  
**完成标志**：从加入购物车到支付/取消的完整链路全部正常

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对订单模块做完整验收。

【任务】创建 backend/scripts/smoke_test_order.sh：

#!/usr/bin/env bash
set -e
BASE="http://localhost:8000/api/v1"

echo "请粘贴登录 TOKEN："
read -r TOKEN

echo "=== [准备] 加入购物车 ==="
curl -s -X POST "$BASE/cart/add" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sku_id":1,"qty":1}' > /dev/null

CART_ITEM_ID=$(curl -s "$BASE/cart/list" -H "Authorization: Bearer $TOKEN" | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['items'][0]['cart_item_id'])")

ADDR_ID=$(curl -s "$BASE/user/address" -H "Authorization: Bearer $TOKEN" | \
  python -c "import sys,json; items=json.load(sys.stdin)['data']; print(items[0]['id'] if items else 'NONE')")

if [ "$ADDR_ID" = "NONE" ]; then
  echo "请先添加收货地址（运行 user-plan smoke test）"
  exit 1
fi

echo "购物车ID: $CART_ITEM_ID  地址ID: $ADDR_ID"

echo "=== [1] 创建订单 ==="
ORDER=$(curl -s -X POST "$BASE/order/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"cart_item_ids\":[$CART_ITEM_ID],\"address_id\":$ADDR_ID,\"pay_method\":\"wechat\"}")
echo "$ORDER" | python -m json.tool
ORDER_ID=$(echo "$ORDER" | python -c "import sys,json; print(json.load(sys.stdin)['data']['order_id'])")
echo "订单ID: $ORDER_ID"

echo "=== [2] 查看订单列表（应有 pending_pay 订单）==="
curl -s "$BASE/order/list?status=pending_pay" -H "Authorization: Bearer $TOKEN" | \
  python -c "import sys,json; d=json.load(sys.stdin); print('待付款订单数:', d['data']['total'])"

echo "=== [3] 支付订单 ==="
curl -s -X POST "$BASE/order/pay" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"order_id\":\"$ORDER_ID\"}" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0 and d['data']['status']=='pending_ship', f'FAIL: {d}'
print('PASS 状态已变为 pending_ship')
"

echo "=== [4] 重复支付（应报错 1205）==="
curl -s -X POST "$BASE/order/pay" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"order_id\":\"$ORDER_ID\"}" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==1205, f'FAIL: {d[\"code\"]}'
print('PASS 重复支付被拒')
"

echo "=== [5] 创建另一个订单并取消 ==="
curl -s -X POST "$BASE/cart/add" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"sku_id":1,"qty":1}' > /dev/null
CART2=$(curl -s "$BASE/cart/list" -H "Authorization: Bearer $TOKEN" | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['items'][0]['cart_item_id'])")
ORDER2=$(curl -s -X POST "$BASE/order/create" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"cart_item_ids\":[$CART2],\"address_id\":$ADDR_ID,\"pay_method\":\"alipay\"}" | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['order_id'])")
curl -s -X POST "$BASE/order/cancel?order_id=$ORDER2" -H "Authorization: Bearer $TOKEN" | \
  python -c "import sys,json; d=json.load(sys.stdin); assert d['code']==0; print('PASS 取消成功')"

echo "=== [6] 订单详情 ==="
curl -s "$BASE/order/$ORDER_ID" -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)['data']
print('订单号:', d['order_id'], '| 状态:', d['status_label'])
print('商品数:', len(d['items']), '| 金额:', d['amount'])
"

echo ""
echo "✓ 订单模块全部测试通过！"
```

---

## 附录：文件变更清单

```
backend/
├── models/
│   └── order.py              ← 重写（Task 1）
│
├── schemas/
│   └── order.py              ← 新建（Task 2）
│
├── services/
│   └── order_service.py      ← 新建（Task 3）
│
├── routers/
│   └── order.py              ← 重构（Task 4-8）
│
└── scripts/
    └── smoke_test_order.sh   ← 新建（Task 9）
```
