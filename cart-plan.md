# cart-plan.md — 珑饰购物车模块开发计划

**模块范围**：加入购物车、列表查询、修改数量/规格、删除、勾选结算  
**技术栈**：FastAPI + SQLAlchemy + JWT 认证  
**工作目录**：`L:\claude-code\backend\`  
**架构规范**：严格遵循 `L:\claude-code\CLAUDE.md`

---

## 当前状态说明

| 文件 | 状态 | 说明 |
|---|---|---|
| `models/cart.py` | ⚠️ 需调整 | CartItem 存在，字段用 quantity（CLAUDE.md 用 qty） |
| `routers/cart.py` | ⚠️ 需重构 | 路由存在但 DEMO_USER=1、HTTPException、旧 schemas |
| `schemas/cart.py` | ❌ 缺失 | 需新建 |
| `services/cart_service.py` | ❌ 缺失 | 逻辑内联在路由里 |

---

## 任务总览

| # | 任务 | 预计时间 | 依赖 |
|---|---|---|---|
| 1 | 对齐 CartItem 模型字段 | 20 min | 无 |
| 2 | 创建 schemas/cart.py | 20 min | 1 |
| 3 | 创建 CartService（核心业务逻辑） | 40 min | 1、2 |
| 4 | 重构加入购物车接口（接入 JWT） | 20 min | 3、user-plan |
| 5 | 重构购物车列表接口 | 20 min | 3、user-plan |
| 6 | 重构修改数量/规格接口 | 20 min | 3 |
| 7 | 重构删除购物车项接口 | 15 min | 3 |
| 8 | 全流程冒烟测试 | 20 min | 全部 |

---

## Task 1：对齐 CartItem 模型字段

**预计时间**：20 分钟  
**依赖**：无  
**完成标志**：`python -c "from models.cart import CartItem; print([c.key for c in CartItem.__table__.columns])"` 含 qty、user_id、selected

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对齐购物车模型字段。

【当前状态】backend/models/cart.py 中 CartItem 的数量字段是 quantity，
CLAUDE.md 规范和前端 api/cart.js 均使用 qty。
同时 user_id 当前是 Column(Integer, default=1)，需要改为外键关联 users 表。

【任务】修改 backend/models/cart.py：

① 将 quantity 字段改名为 qty（兼容旧数据：同时保留 quantity 作为同义词的需求不存在，
   直接改名即可，现有 SQLite DB 是开发数据库，可删重建）

② 将 user_id 改为外键（但保持 Integer 类型，兼容 SQLite）：
   user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

③ 追加 updated_at 字段：
   updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

④ 追加 UNIQUE 约束（同一用户同一 SKU 只能有一行，累加数量而非重复插入）：
   __table_args__ = (
       UniqueConstraint("user_id", "sku_id", name="uk_user_sku"),
   )

⑤ 在 models/__init__.py 确认 CartItem 仍被导出（已有则不变）。

【验证】运行：
    python -c "
    import models
    from database import engine, Base
    # 开发环境：删旧表重建（注意：会清空数据）
    from models.cart import CartItem
    CartItem.__table__.drop(engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    cols = [c.key for c in CartItem.__table__.columns]
    print('CartItem columns:', cols)
    assert 'qty' in cols, 'qty 字段缺失'
    assert 'qty' in cols, 'PASS'
    print('PASS')
    "
```

---

## Task 2：创建 schemas/cart.py

**预计时间**：20 分钟  
**依赖**：Task 1  
**完成标志**：`python -c "from schemas.cart import AddCartReq, CartItemOut, CartListOut"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建购物车模块的 Pydantic Schema。

【前提】backend/schemas/ 包已存在（schemas/common.py 有 ApiResponse[T]）

【任务】创建 backend/schemas/cart.py：

AddCartReq:             # 加入购物车请求
    sku_id: int
    qty: int = 1        # 数量，ge=1

UpdateCartReq:          # 修改购物车项请求（至少传一个字段）
    cart_item_id: int
    qty: int | None = None       # 修改数量（传 0 等同于删除）
    selected: bool | None = None # 修改勾选状态

CartItemOut:            # 购物车条目响应（含商品快照）
    cart_item_id: int
    sku_id: int
    spu_id: int
    sku_name: str
    spu_name: str
    cover_url: str | None
    color: str | None
    price: float
    original_price: float | None
    qty: int
    selected: bool
    subtotal: float             # price * qty，后端计算
    ar_available: bool          # 是否可试戴
    ar_asset_url: str | None
    mount_type: str | None

CartListOut:            # 购物车列表响应
    items: list[CartItemOut]
    total_price: float          # 所有 selected=True 的 subtotal 之和
    selected_count: int         # selected=True 的商品件数（非条目数，是数量之和）
    total_count: int            # 购物车总条目数

【验证】
    python -c "
    from schemas.cart import AddCartReq, CartItemOut, CartListOut
    req = AddCartReq(sku_id=1, qty=2)
    print('AddCartReq:', req.model_dump())
    print('CartListOut fields:', list(CartListOut.model_fields.keys()))
    "
```

---

## Task 3：创建 CartService（核心业务逻辑）

**预计时间**：40 分钟  
**依赖**：Task 1、2  
**完成标志**：Python 脚本直接调用 service 完成增删改查

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建购物车业务逻辑层。

【任务】创建 backend/services/cart_service.py：

class CartService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def add(self, sku_id: int, qty: int) -> CartItemOut:
        """
        加入购物车，业务规则：
        1. 查询 GoodsSku，不存在或 status!=1 → BizError(1101, "商品规格不存在")
        2. 查询该 user_id + sku_id 是否已有购物车记录
           - 已有：accumulated qty += qty（不超过 99，超出 BizError(1102, "数量不能超过99")）
           - 没有：插入新 CartItem 记录（qty, selected=True）
        3. db.commit()
        4. 返回 _to_out(cart_item)
        """

    def list(self) -> CartListOut:
        """
        获取购物车列表：
        1. 查询所有 user_id 对应的 CartItem（join GoodsSku、GoodsSpu）
        2. 构建 CartItemOut 列表
        3. 计算 total_price（selected=True 的 subtotal 之和）
        4. 计算 selected_count（selected=True 的 qty 之和）
        5. 返回 CartListOut
        """

    def update(self, cart_item_id: int, qty: int | None, selected: bool | None) -> CartItemOut:
        """
        更新购物车项：
        1. 查 CartItem，不存在或 user_id 不匹配 → BizError(1103, "购物车项不存在")
        2. qty 不为 None 时：
           - qty <= 0 → 删除该项（等同于 remove）
           - qty > 0 → 更新数量（上限 99）
        3. selected 不为 None 时：更新勾选状态
        4. db.commit()
        5. 若已删除则返回 None；否则返回 _to_out(item)
        """

    def remove(self, cart_item_id: int) -> None:
        """删除购物车项，验证归属"""

    def _to_out(self, item: CartItem) -> CartItemOut:
        """将 ORM 对象转为 CartItemOut（需关联查 sku 和 spu）"""

    def _get_or_403(self, cart_item_id: int) -> CartItem:
        item = self.db.get(CartItem, cart_item_id)
        if not item or item.user_id != self.user_id:
            raise BizError(1103, "购物车项不存在")
        return item

【验证】运行（需先完成 user-plan Task 7 登录，user_id=1 存在）：
    python -c "
    from database import SessionLocal, engine, Base
    import models
    Base.metadata.create_all(bind=engine)
    from services.cart_service import CartService
    db = SessionLocal()
    svc = CartService(db, user_id=1)
    # 添加（sku_id=1 需存在）
    try:
        result = svc.add(sku_id=1, qty=2)
        print('加入购物车:', result.sku_name, 'qty:', result.qty)
        cart = svc.list()
        print('购物车条目数:', cart.total_count, '总价:', cart.total_price)
    except Exception as e:
        print('注意：需先导入商品种子数据，error:', e)
    db.close()
    "
```

---

## Task 4：重构加入购物车接口（接入 JWT）

**预计时间**：20 分钟  
**依赖**：Task 3、user-plan  
**完成标志**：无 token 返回 code:2001，有 token 成功加入购物车

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在重构购物车路由，接入 JWT 认证。

【当前状态】backend/routers/cart.py 存在，但用 DEMO_USER=1、HTTPException、旧 schemas。

【任务】完全重写 backend/routers/cart.py（保留路由路径不变，和 main.py 中注册一致）：

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.common import ApiResponse
from schemas.cart import AddCartReq, CartItemOut, CartListOut, UpdateCartReq
from services.cart_service import CartService
from core.deps import get_current_user
from models.user import User

router = APIRouter()

@router.post("/add", response_model=ApiResponse[CartItemOut])
def add_to_cart(
    req: AddCartReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = CartService(db, current_user.id).add(req.sku_id, req.qty)
    return ApiResponse(data=item)

（其余接口见 Task 5-7）

注意：main.py 中已有 app.include_router(cart.router, prefix="/api/v1/cart")，无需修改。

【验证】先获取 TOKEN（user-plan Task 7），然后：
    # 无 token（应返回 code:2001）
    curl -s -X POST http://localhost:8000/api/v1/cart/add \
      -H "Content-Type: application/json" \
      -d '{"sku_id":1,"qty":1}' | python -m json.tool

    # 有 token（应成功）
    curl -s -X POST http://localhost:8000/api/v1/cart/add \
      -H "Authorization: Bearer TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"sku_id":1,"qty":1}' | python -m json.tool
    # 预期：{"code":0,"data":{"cart_item_id":...,"sku_name":...,"qty":1,...}}

    # 重复添加（应累加数量）
    curl -s -X POST http://localhost:8000/api/v1/cart/add \
      -H "Authorization: Bearer TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"sku_id":1,"qty":2}' | python -m json.tool
    # 预期：qty=3
```

---

## Task 5：重构购物车列表接口

**预计时间**：20 分钟  
**依赖**：Task 3、4  
**完成标志**：`GET /cart/list` 返回含商品快照信息的列表，selected_count 和 total_price 正确

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在重构后的 backend/routers/cart.py 中追加购物车列表接口。

【任务】在 cart.py 追加：

@router.get("/list", response_model=ApiResponse[CartListOut])
def cart_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = CartService(db, current_user.id).list()
    return ApiResponse(data=data)

【验证】
    curl -s http://localhost:8000/api/v1/cart/list \
      -H "Authorization: Bearer TOKEN" | python -m json.tool
    预期：
    {
      "code": 0,
      "data": {
        "items": [{"cart_item_id":1,"sku_name":"...","qty":3,"selected":true,"subtotal":504,...}],
        "total_price": 504.0,
        "selected_count": 3,
        "total_count": 1
      }
    }

    # 验证 total_price 计算正确
    curl -s http://localhost:8000/api/v1/cart/list \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    items = d['items']
    expected = sum(i['subtotal'] for i in items if i['selected'])
    print('total_price:', d['total_price'], '| 手动计算:', expected)
    assert abs(d['total_price'] - expected) < 0.01, 'FAIL: 总价计算错误'
    print('PASS')
    "
```

---

## Task 6：重构修改数量/规格接口

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：修改数量后列表中对应商品数量变化，qty=0 时自动删除

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 cart.py 追加修改购物车项接口。

【任务】追加：

@router.put("/update", response_model=ApiResponse[CartItemOut | None])
def update_cart(
    req: UpdateCartReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新数量或勾选状态。
    若 qty=0（删除操作）则返回 ApiResponse(data=None)；
    否则返回更新后的 CartItemOut。
    """
    result = CartService(db, current_user.id).update(req.cart_item_id, req.qty, req.selected)
    return ApiResponse(data=result)

【验证】先获取一个 cart_item_id（从 GET /cart/list 结果中），然后：
    CART_ITEM_ID=1

    # 修改数量
    curl -s -X PUT http://localhost:8000/api/v1/cart/update \
      -H "Authorization: Bearer TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"cart_item_id\":$CART_ITEM_ID,\"qty\":5}" | python -m json.tool
    # 预期：qty=5

    # 取消勾选
    curl -s -X PUT http://localhost:8000/api/v1/cart/update \
      -H "Authorization: Bearer TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"cart_item_id\":$CART_ITEM_ID,\"selected\":false}" | python -m json.tool

    # 验证列表中 total_price 变化
    curl -s http://localhost:8000/api/v1/cart/list \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    print('total_price after deselect:', d['total_price'])
    "
```

---

## Task 7：重构删除购物车项接口

**预计时间**：15 分钟  
**依赖**：Task 3  
**完成标志**：删除后列表中该商品消失，删他人商品返回 code:1103

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 cart.py 追加删除接口。

【任务】追加：

@router.delete("/remove/{cart_item_id}", response_model=ApiResponse[None])
def remove_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    CartService(db, current_user.id).remove(cart_item_id)
    return ApiResponse()

【验证】
    CART_ITEM_ID=1

    # 删除
    curl -s -X DELETE "http://localhost:8000/api/v1/cart/remove/$CART_ITEM_ID" \
      -H "Authorization: Bearer TOKEN" | python -m json.tool
    # 预期：{"code":0,"message":"ok","data":null}

    # 重复删除（应返回 code:1103）
    curl -s -X DELETE "http://localhost:8000/api/v1/cart/remove/$CART_ITEM_ID" \
      -H "Authorization: Bearer TOKEN" | python -m json.tool
    # 预期：{"code":1103,"message":"购物车项不存在","data":null}

    # 删除后列表
    curl -s http://localhost:8000/api/v1/cart/list \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    print('删除后条目数:', d['total_count'])
    "
```

---

## Task 8：全流程冒烟测试

**预计时间**：20 分钟  
**依赖**：全部前序任务  
**完成标志**：脚本全程无 code 非零，购物车状态变化符合预期

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对购物车模块做完整验收。

【前提】
- 已有有效 JWT TOKEN（来自 user-plan 登录流程）
- 已导入商品种子数据（sku_id=1 存在）

【任务】创建 backend/scripts/smoke_test_cart.sh：

#!/usr/bin/env bash
set -e
BASE="http://localhost:8000/api/v1"

echo "请粘贴登录获得的 TOKEN："
read -r TOKEN

echo "=== [1] 加入购物车（sku_id=1, qty=2）==="
ITEM=$(curl -s -X POST "$BASE/cart/add" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sku_id":1,"qty":2}')
echo "$ITEM" | python -m json.tool
python -c "import sys,json; d=json.loads('$ITEM'); assert d['code']==0; print('PASS')" 2>/dev/null || \
  python -c "
import json; d=$ITEM
assert d['code']==0, f'FAIL: {d}'
print('PASS qty:', d['data']['qty'])
"

echo "=== [2] 重复加入（累加 qty，预期 qty=3）==="
curl -s -X POST "$BASE/cart/add" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sku_id":1,"qty":1}' | python -m json.tool

echo "=== [3] 查看购物车列表 ==="
LIST=$(curl -s "$BASE/cart/list" -H "Authorization: Bearer $TOKEN")
echo "$LIST" | python -m json.tool
CART_ITEM_ID=$(echo "$LIST" | python -c "import sys,json; print(json.load(sys.stdin)['data']['items'][0]['cart_item_id'])")

echo "=== [4] 修改数量为 5 ==="
curl -s -X PUT "$BASE/cart/update" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"cart_item_id\":$CART_ITEM_ID,\"qty\":5}" | python -m json.tool

echo "=== [5] 取消勾选 ==="
curl -s -X PUT "$BASE/cart/update" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"cart_item_id\":$CART_ITEM_ID,\"selected\":false}" | python -m json.tool

echo "=== [6] 验证 total_price=0（未勾选）==="
curl -s "$BASE/cart/list" -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)['data']
assert d['total_price'] == 0.0, f'FAIL: {d[\"total_price\"]}'
print('PASS total_price=0')
"

echo "=== [7] 删除购物车项 ==="
curl -s -X DELETE "$BASE/cart/remove/$CART_ITEM_ID" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "=== [8] 验证购物车为空 ==="
curl -s "$BASE/cart/list" -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)['data']
assert d['total_count'] == 0, 'FAIL: 购物车不为空'
print('PASS 购物车已清空')
"

echo "=== [9] 无 Token 访问（code:2001）==="
curl -s "$BASE/cart/list" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code'] == 2001, f'FAIL: {d[\"code\"]}'
print('PASS 鉴权拦截正常')
"

echo ""
echo "✓ 购物车模块全部测试通过！"
```

---

## 附录：文件变更清单

```
backend/
├── models/
│   └── cart.py               ← 修改（Task 1：字段对齐）
│
├── schemas/
│   └── cart.py               ← 新建（Task 2）
│
├── services/
│   └── cart_service.py       ← 新建（Task 3）
│
├── routers/
│   └── cart.py               ← 重构（Task 4-7）
│
└── scripts/
    └── smoke_test_cart.sh    ← 新建（Task 8）
```
