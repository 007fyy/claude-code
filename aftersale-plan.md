# aftersale-plan.md — 珑饰售后模块开发计划

**模块范围**：申请售后、填写退货单号、售后进度查询、管理员审核、库存回流、算法反馈  
**技术栈**：FastAPI + SQLAlchemy + JWT 认证  
**工作目录**：`L:\claude-code\backend\`  
**架构规范**：严格遵循 `L:\claude-code\CLAUDE.md`

---

## 当前状态说明

| 文件 | 状态 | 说明 |
|---|---|---|
| `models/order.py` | ⚠️ 含旧 RefundOrder | order-plan Task 1 会删除 RefundOrder，本模块用独立 Aftersale 模型 |
| `models/aftersale.py` | ❌ 缺失 | 需新建 |
| `schemas/aftersale.py` | ❌ 缺失 | 需新建 |
| `services/aftersale_service.py` | ❌ 缺失 | 需新建 |
| `routers/aftersale.py` | ❌ 缺失 | 需新建（老 router 中有 /refund/apply，需迁移） |

---

## 任务总览

| # | 任务 | 预计时间 | 依赖 |
|---|---|---|---|
| 1 | 创建售后模型 Aftersale + AftersaleItem | 30 min | order-plan Task 1 |
| 2 | 创建 schemas/aftersale.py | 20 min | 1 |
| 3 | 创建 AftersaleService（申请/查询/填单号） | 40 min | 1、2 |
| 4 | 创建 routers/aftersale.py（用户接口） | 20 min | 3 |
| 5 | 在 admin.py 追加售后审核接口 | 30 min | 3、admin-plan |
| 6 | 实现库存回流逻辑（refunded 终态） | 20 min | 3 |
| 7 | 实现算法反馈逻辑（effect_mismatch → penalty） | 20 min | 6 |
| 8 | 注册路由到 main.py | 10 min | 4 |
| 9 | 全流程冒烟测试 | 30 min | 全部 |

---

## Task 1：创建售后模型

**预计时间**：30 分钟  
**依赖**：order-plan Task 1（orders 表存在）  
**完成标志**：`python -c "from models.aftersale import Aftersale, AftersaleItem; print('OK')"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建售后模块的数据库模型。

【CLAUDE.md 售后表设计要点】
- aftersale.id 是 VARCHAR(30) 主键（如 "AS202604280001"）
- status：pending_review / rejected / pending_return / in_transit_return / refund_processing / refunded
- reason：quality_issue / description_mismatch / effect_mismatch / size_mismatch / dislike / other
- type：refund / exchange
- AftersaleItem 独立表，存每件退货商品的快照

【任务】新建 backend/models/aftersale.py：

① Aftersale 模型（__tablename__ = "aftersale"）：
   id: Column(String(30), primary_key=True)          # "AS202604280001"
   order_id: Column(String(30), ForeignKey("orders.id"), nullable=False, index=True)
   user_id: Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
   type: Column(String(20), nullable=False)           # "refund" | "exchange"
   status: Column(String(30), nullable=False, default="pending_review")
     允许值：pending_review / rejected / pending_return /
             in_transit_return / refund_processing / refunded
   reason: Column(String(30), nullable=False)
     允许值：quality_issue / description_mismatch / effect_mismatch /
             size_mismatch / dislike / other
   note: Column(String(500), nullable=True)
   return_tracking: Column(String(50), nullable=True)   # 用户退货快递单号
   admin_note: Column(String(300), nullable=True)
   created_at: Column(DateTime, server_default=func.now())
   updated_at: Column(DateTime, server_default=func.now(), onupdate=func.now())
   items: relationship("AftersaleItem", back_populates="aftersale", lazy="select")

② AftersaleItem 模型（__tablename__ = "aftersale_items"）：
   id: 自增整数主键
   aftersale_id: Column(String(30), ForeignKey("aftersale.id"), nullable=False, index=True)
   sku_id: Column(Integer, nullable=False)
   name: Column(String(150), nullable=False)    # 商品名快照
   price: Column(Numeric(10,2), nullable=False)
   qty: Column(Integer, nullable=False)
   aftersale: relationship("Aftersale", back_populates="items")

③ 更新 models/__init__.py：追加 Aftersale、AftersaleItem 导出

【验证】
    python -c "
    import models
    from database import engine, Base
    from models.aftersale import Aftersale, AftersaleItem
    Aftersale.__table__.drop(engine, checkfirst=True)
    AftersaleItem.__table__.drop(engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    print('Aftersale columns:', list(Aftersale.__table__.c.keys()))
    print('AftersaleItem columns:', list(AftersaleItem.__table__.c.keys()))
    print('PASS')
    "
```

---

## Task 2：创建 schemas/aftersale.py

**预计时间**：20 分钟  
**依赖**：Task 1  
**完成标志**：`python -c "from schemas.aftersale import ApplyAftersaleReq, AftersaleOut"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建售后模块的 Pydantic Schema。

【任务】创建 backend/schemas/aftersale.py：

ApplyAftersaleReq:       # 申请售后请求
    order_id: str
    type: str            # "refund" | "exchange"
    reason: str          # 参照 CLAUDE.md reason 枚举
    note: str | None = None
    items: list[AftersaleItemReq]   # 售后商品列表

    @field_validator("type")
    # 只允许 "refund" 或 "exchange"

    @field_validator("reason")
    # 只允许 CLAUDE.md 中的 reason 枚举值

AftersaleItemReq:
    sku_id: int
    qty: int             # ge=1

FillTrackingReq:         # 填写退货快递单号
    tracking_no: str     # 退货快递单号（非空）

AftersaleItemOut:
    sku_id: int
    name: str
    price: float
    qty: int
    subtotal: float      # price * qty

AftersaleOut:            # 售后单详情
    aftersale_id: str
    order_id: str
    type: str
    status: str
    status_label: str    # 状态中文标签
    reason: str
    reason_label: str    # 原因中文标签
    note: str | None
    return_tracking: str | None
    admin_note: str | None
    items: list[AftersaleItemOut]
    created_at: str | None

AFTERSALE_STATUS_LABELS = {
    "pending_review": "待审核",
    "rejected": "已拒绝",
    "pending_return": "待退货",
    "in_transit_return": "退货运输中",
    "refund_processing": "退款处理中",
    "refunded": "已退款",
}

AFTERSALE_REASON_LABELS = {
    "quality_issue": "商品质量问题",
    "description_mismatch": "与描述不符",
    "effect_mismatch": "佩戴效果不符合预期",
    "size_mismatch": "尺寸/规格不合适",
    "dislike": "不喜欢",
    "other": "其他",
}

【验证】
    python -c "
    from schemas.aftersale import ApplyAftersaleReq, AftersaleOut, AFTERSALE_STATUS_LABELS
    print('STATUS_LABELS:', AFTERSALE_STATUS_LABELS)
    req = ApplyAftersaleReq(
        order_id='LS202604280001',
        type='refund',
        reason='effect_mismatch',
        items=[{'sku_id':1,'qty':1}]
    )
    print('req:', req.model_dump())
    "
```

---

## Task 3：创建 AftersaleService

**预计时间**：40 分钟  
**依赖**：Task 1、2  
**完成标志**：Python 脚本直接调用 service 申请售后无异常

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建售后业务逻辑层。

【任务】创建 backend/services/aftersale_service.py：

import random
from datetime import datetime

AFTERSALE_ID_PREFIX = "AS"

def _gen_aftersale_id() -> str:
    """生成售后单号：AS + yyyyMMddHHmmss + 4位随机数"""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{AFTERSALE_ID_PREFIX}{ts}{random.randint(1000,9999)}"

class AftersaleService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def apply(self, req: ApplyAftersaleReq) -> AftersaleOut:
        """
        申请售后：
        1. 查订单（order_id 存在 + 属于当前用户 + status == "completed"）
           不满足 → BizError(1301, "订单不支持售后")
        2. 检查是否已存在非 rejected 的售后单
           → BizError(1302, "该订单已申请售后")
        3. 验证 req.items 中每个 sku_id 在该订单的 order_items 中存在且 qty 不超过已购数量
           → BizError(1303, "售后商品不在订单中")
        4. 生成 aftersale_id（_gen_aftersale_id()）
        5. 插入 Aftersale 记录（status="pending_review"）
        6. 逐项插入 AftersaleItem 记录（价格从 order_items 快照中取）
        7. db.commit()
        8. 返回 _to_out(aftersale)
        """

    def get_detail(self, aftersale_id: str) -> AftersaleOut:
        """
        查询售后详情：
        1. 查 Aftersale，验证归属（user_id）
           不存在/不属于 → BizError(1304, "售后单不存在")
        2. 返回 _to_out(aftersale)
        """

    def fill_tracking(self, aftersale_id: str, tracking_no: str) -> AftersaleOut:
        """
        填写退货快递单号：
        1. 查 Aftersale，验证归属
        2. status != "pending_return" → BizError(1305, "当前状态不支持填写快递单号")
        3. 更新 return_tracking=tracking_no，status="in_transit_return"
        4. db.commit()
        5. 返回 _to_out(aftersale)
        """

    def _to_out(self, aftersale: Aftersale) -> AftersaleOut:
        """ORM → AftersaleOut，计算 status_label、reason_label、subtotal"""

    def _get_or_404(self, aftersale_id: str) -> Aftersale:
        rec = self.db.get(Aftersale, aftersale_id)
        if not rec or rec.user_id != self.user_id:
            raise BizError(1304, "售后单不存在")
        return rec
```

---

## Task 4：创建 routers/aftersale.py（用户接口）

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：三个接口均可正常调用

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建售后用户接口路由。

【任务】新建 backend/routers/aftersale.py：

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.common import ApiResponse
from schemas.aftersale import ApplyAftersaleReq, AftersaleOut, FillTrackingReq
from services.aftersale_service import AftersaleService
from core.deps import get_current_user
from models.user import User

router = APIRouter(tags=["售后"])

@router.post("/apply", response_model=ApiResponse[AftersaleOut])
def apply_aftersale(
    req: ApplyAftersaleReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = AftersaleService(db, current_user.id).apply(req)
    return ApiResponse(data=data)

@router.get("/{aftersale_id}", response_model=ApiResponse[AftersaleOut])
def aftersale_detail(
    aftersale_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = AftersaleService(db, current_user.id).get_detail(aftersale_id)
    return ApiResponse(data=data)

@router.post("/{aftersale_id}/fill-tracking", response_model=ApiResponse[AftersaleOut])
def fill_tracking(
    aftersale_id: str,
    req: FillTrackingReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = AftersaleService(db, current_user.id).fill_tracking(aftersale_id, req.tracking_no)
    return ApiResponse(data=data)

【注意】main.py 中注册：
    app.include_router(aftersale.router, prefix="/api/v1/order/refund")

【验证】
    # 申请售后（需已有 completed 订单）
    curl -s -X POST http://localhost:8000/api/v1/order/refund/apply \
      -H "Authorization: Bearer TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "order_id":"ORDER_ID",
        "type":"refund",
        "reason":"effect_mismatch",
        "items":[{"sku_id":1,"qty":1}]
      }' | python -m json.tool
    # 预期：aftersale_id 为 "AS202604XXXXXXXX"，status="pending_review"
```

---

## Task 5：在 admin.py 追加售后审核接口

**预计时间**：30 分钟  
**依赖**：Task 3、admin-plan  
**完成标志**：管理员可审核通过/拒绝，状态正确流转

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 backend/routers/admin.py 追加售后审核接口。

【任务】在 admin.py 中追加以下接口（需 require_admin 依赖）：

@router.get("/aftersale", response_model=ApiResponse[list[AftersaleOut]])
def admin_aftersale_list(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """查询所有用户的售后单列表（管理员视角），支持状态筛选"""
    ...

@router.post("/aftersale/{aftersale_id}/approve", response_model=ApiResponse[AftersaleOut])
def admin_approve(
    aftersale_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    审核通过：
    1. 查 Aftersale，status != "pending_review" → BizError(1306, "当前状态不可操作")
    2. 更新 status="pending_return"
    3. db.commit()
    4. 返回 AftersaleOut
    """
    ...

@router.post("/aftersale/{aftersale_id}/reject", response_model=ApiResponse[AftersaleOut])
def admin_reject(
    aftersale_id: str,
    admin_note: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    拒绝申请：
    1. 查 Aftersale，status != "pending_review" → BizError(1306, "当前状态不可操作")
    2. 更新 status="rejected"，admin_note=admin_note
    3. db.commit()
    """
    ...

@router.post("/aftersale/{aftersale_id}/confirm-received", response_model=ApiResponse[AftersaleOut])
def admin_confirm_received(
    aftersale_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    确认收到退货（触发退款 + 库存回流 + 算法反馈）：
    1. status != "in_transit_return" → BizError(1306, "当前状态不可操作")
    2. 更新 status="refund_processing"（模拟退款处理中）
    3. 立即更新 status="refunded"（mock 立即完成）
    4. 库存回流：逐项 sku.stock += qty
    5. 算法反馈（见 Task 7）
    6. db.commit()
    """
    ...

【验证】先登录管理员账号获取 ADMIN_TOKEN，然后：
    # 审核通过
    curl -s -X POST "http://localhost:8000/api/v1/admin/aftersale/AS_ID/approve" \
      -H "Authorization: Bearer ADMIN_TOKEN" | python -m json.tool
    # 预期：status="pending_return"，status_label="待退货"
```

---

## Task 6：实现库存回流逻辑

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：confirm-received 后对应 SKU 库存增加

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 aftersale_service.py 中实现库存回流。

【任务】在 AftersaleService（或 admin 服务层）中，当售后状态变为 refunded 时：

def _restore_stock(self, aftersale: Aftersale) -> None:
    """
    库存回流：
    1. 遍历 aftersale.items
    2. 对每个 item，查询 GoodsSku（with_for_update() 加锁）
    3. sku.stock += item.qty
    （db.commit() 由调用方统一提交）
    """

此方法在 admin confirm-received 接口中调用，写入 refunded 前执行。

【验证】
    # 确认收到退货前查 SKU 库存
    python -c "
    from database import SessionLocal
    from models.goods import GoodsSku
    db = SessionLocal()
    sku = db.get(GoodsSku, 1)
    print('回流前 stock:', sku.stock)
    db.close()
    "

    # 执行 confirm-received
    curl -s -X POST "http://localhost:8000/api/v1/admin/aftersale/AS_ID/confirm-received" \
      -H "Authorization: Bearer ADMIN_TOKEN" | python -m json.tool

    # 确认库存增加
    python -c "
    from database import SessionLocal
    from models.goods import GoodsSku
    db = SessionLocal()
    sku = db.get(GoodsSku, 1)
    print('回流后 stock:', sku.stock)
    db.close()
    "
```

---

## Task 7：实现算法反馈逻辑

**预计时间**：20 分钟  
**依赖**：Task 6  
**完成标志**：effect_mismatch 退款完成后，goods_spu.face_weight_penalty 对应脸型 -=5

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在售后 refunded 终态时实现算法反馈。

【CLAUDE.md 算法反馈触发条件】
同时满足以下条件时触发：
1. aftersale.type == "refund"
2. aftersale.reason == "effect_mismatch"
3. 状态变更为 "refunded"
4. 该用户在 face_profiles 中存在有效记录

【操作】
读取 face_profiles.face_shape（如 "oval"），
然后对每个售后商品对应的 goods_spu，
将 face_weight_penalty[face_shape] -= 5（累积降权）

【任务】在 aftersale_service.py（或 admin 服务层）中实现：

def _apply_algorithm_feedback(self, aftersale: Aftersale) -> None:
    """
    算法反馈：
    1. 检查 aftersale.type == "refund" and aftersale.reason == "effect_mismatch"
       不满足则直接返回（不报错）
    2. 查 face_profiles，获取 user.face_shape
       找不到则直接返回
    3. 遍历 aftersale.items，获取每个 sku_id 对应的 spu_id
       查 GoodsSpu（用 sku.spu_id）
    4. 更新 spu.face_weight_penalty：
       penalty = spu.face_weight_penalty or {}
       penalty[face_shape] = penalty.get(face_shape, 0) - 5
       spu.face_weight_penalty = penalty
    （db.commit() 由调用方统一提交）
    """

此方法在 _restore_stock 之后、db.commit() 之前调用。

【验证】
    # 完成一次 effect_mismatch 退款，然后检查 penalty
    python -c "
    from database import SessionLocal
    from models.goods import GoodsSpu
    db = SessionLocal()
    spu = db.get(GoodsSpu, 1)
    print('face_weight_penalty:', spu.face_weight_penalty)
    # 预期：{'oval': -5} 或更小（多次触发则累积）
    db.close()
    "
```

---

## Task 8：注册路由到 main.py

**预计时间**：10 分钟  
**依赖**：Task 4  
**完成标志**：`GET /api/v1/order/refund/AS_ID` 接口可访问

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。将售后路由注册到 main.py。

【当前状态】backend/main.py 已注册了 goods、cart、order 路由。
旧 order.py 中可能有 /refund/apply 接口，需删除（由新的 aftersale 路由接管）。

【任务】
1. 在 backend/main.py 中追加：
   from routers import aftersale
   app.include_router(aftersale.router, prefix="/api/v1/order/refund")

2. 在 backend/routers/order.py 中删除旧的 /refund/apply 路由（如果存在）

【验证】
    # 启动服务后查看路由文档
    curl -s http://localhost:8000/openapi.json | python -c "
    import sys,json
    paths = list(json.load(sys.stdin)['paths'].keys())
    aftersale = [p for p in paths if 'refund' in p]
    print('售后接口:', aftersale)
    "
```

---

## Task 9：全流程冒烟测试

**预计时间**：30 分钟  
**依赖**：全部前序任务  
**完成标志**：从 completed 订单到退款完成、库存回流的完整链路正常

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对售后模块做完整验收。

【任务】创建 backend/scripts/smoke_test_aftersale.sh：

#!/usr/bin/env bash
set -e
BASE="http://localhost:8000/api/v1"

echo "请粘贴用户 TOKEN："
read -r TOKEN
echo "请粘贴管理员 TOKEN："
read -r ADMIN_TOKEN

echo "=== [准备] 查询一个 completed 状态的订单 ==="
ORDER_ID=$(curl -s "$BASE/order/list?status=completed" -H "Authorization: Bearer $TOKEN" | \
  python -c "import sys,json; items=json.load(sys.stdin)['data']['items']; print(items[0]['order_id'] if items else 'NONE')")
if [ "$ORDER_ID" = "NONE" ]; then
  echo "请先完成一笔订单（pending_pay→pay→admin ship→completed）"
  exit 1
fi
SKU_ID=$(curl -s "$BASE/order/$ORDER_ID" -H "Authorization: Bearer $TOKEN" | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['items'][0]['sku_id'])")
echo "使用订单 $ORDER_ID，SKU $SKU_ID"

echo "=== [0] 记录回流前库存 ==="
STOCK_BEFORE=$(python -c "
from database import SessionLocal
from models.goods import GoodsSku
db = SessionLocal()
sku = db.get(GoodsSku, $SKU_ID)
print(sku.stock if sku else 0)
db.close()
")
echo "回流前库存: $STOCK_BEFORE"

echo "=== [1] 申请售后（退款，佩戴效果不符）==="
AS_RESP=$(curl -s -X POST "$BASE/order/refund/apply" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"order_id\":\"$ORDER_ID\",\"type\":\"refund\",\"reason\":\"effect_mismatch\",\"items\":[{\"sku_id\":$SKU_ID,\"qty\":1}]}")
echo "$AS_RESP" | python -m json.tool
AS_ID=$(echo "$AS_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['data']['aftersale_id'])")
echo "售后单ID: $AS_ID"

echo "=== [2] 重复申请（应报错 1302）==="
curl -s -X POST "$BASE/order/refund/apply" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"order_id\":\"$ORDER_ID\",\"type\":\"refund\",\"reason\":\"dislike\",\"items\":[{\"sku_id\":$SKU_ID,\"qty\":1}]}" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==1302, f'FAIL: {d}'
print('PASS 重复申请被拒')
"

echo "=== [3] 管理员审核通过 ==="
curl -s -X POST "$BASE/admin/aftersale/$AS_ID/approve" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0 and d['data']['status']=='pending_return', f'FAIL: {d}'
print('PASS 已通过审核，status=pending_return')
"

echo "=== [4] 用户填写退货快递单号 ==="
curl -s -X POST "$BASE/order/refund/$AS_ID/fill-tracking" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tracking_no":"SF1234567890"}' | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0 and d['data']['status']=='in_transit_return', f'FAIL: {d}'
print('PASS 快递单号已填写，status=in_transit_return')
"

echo "=== [5] 管理员确认收货（触发退款+库存回流+算法反馈）==="
curl -s -X POST "$BASE/admin/aftersale/$AS_ID/confirm-received" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0 and d['data']['status']=='refunded', f'FAIL: {d}'
print('PASS 已退款，status=refunded')
"

echo "=== [6] 验证库存回流 ==="
STOCK_AFTER=$(python -c "
from database import SessionLocal
from models.goods import GoodsSku
db = SessionLocal()
sku = db.get(GoodsSku, $SKU_ID)
print(sku.stock if sku else 0)
db.close()
")
python -c "
before, after = $STOCK_BEFORE, $STOCK_AFTER
assert after > before, f'FAIL 库存未回流: before={before} after={after}'
print(f'PASS 库存回流: {before} → {after}')
"

echo "=== [7] 验证算法反馈（face_weight_penalty） ==="
python -c "
from database import SessionLocal
from models.goods import GoodsSpu, GoodsSku
db = SessionLocal()
sku = db.get(GoodsSku, $SKU_ID)
if sku:
    spu = db.get(GoodsSpu, sku.spu_id)
    if spu:
        print('face_weight_penalty:', spu.face_weight_penalty)
        print('（若用户有脸型档案，应有负值；否则为 None 或空字典）')
db.close()
"

echo ""
echo "✓ 售后模块全部测试通过！"
```

---

## 附录：文件变更清单

```
backend/
├── models/
│   └── aftersale.py              ← 新建（Task 1）
│
├── schemas/
│   └── aftersale.py              ← 新建（Task 2）
│
├── services/
│   └── aftersale_service.py      ← 新建（Task 3）
│
├── routers/
│   ├── aftersale.py              ← 新建（Task 4）
│   └── admin.py                  ← 追加售后审核接口（Task 5）
│
├── main.py                       ← 注册 aftersale 路由（Task 8）
│
└── scripts/
    └── smoke_test_aftersale.sh   ← 新建（Task 9）
```
