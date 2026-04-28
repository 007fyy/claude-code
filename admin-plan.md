# admin-plan.md — 珑饰管理端模块开发计划

**模块范围**：管理员权限校验、数据看板、商品 CRUD、SKU/AR 管理、订单发货、售后审核  
**技术栈**：FastAPI + SQLAlchemy + JWT 认证（role=admin）  
**工作目录**：`L:\claude-code\backend\`  
**架构规范**：严格遵循 `L:\claude-code\CLAUDE.md`

---

## 当前状态说明

| 文件 | 状态 | 说明 |
|---|---|---|
| `core/deps.py` | ⚠️ 待确认 | get_current_user 存在，require_admin 可能缺失 |
| `routers/admin.py` | ❌ 缺失 | 需新建，包含全部管理端接口 |
| admin 账号 | ❌ 缺失 | 需提供创建脚本 |

---

## 任务总览

| # | 任务 | 预计时间 | 依赖 |
|---|---|---|---|
| 1 | 创建 require_admin 依赖 + 管理员账号脚本 | 20 min | user-plan |
| 2 | 创建数据看板接口（统计查询） | 30 min | order-plan、goods-plan |
| 3 | 创建商品管理接口（上下架、编辑） | 30 min | goods-plan |
| 4 | 创建 SKU 管理接口（添加/编辑/AR 参数） | 20 min | 3 |
| 5 | 创建订单管理接口（列表、发货） | 20 min | order-plan |
| 6 | 创建售后审核接口（审核/拒绝/确认收货） | 30 min | aftersale-plan |
| 7 | 注册路由到 main.py | 10 min | 2~6 |
| 8 | 全流程冒烟测试 | 30 min | 全部 |

---

## Task 1：创建 require_admin 依赖 + 管理员账号脚本

**预计时间**：20 分钟  
**依赖**：user-plan（User 模型、get_current_user 存在）  
**完成标志**：非 admin 用户访问管理接口返回 code:2003，admin 用户正常通过

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在为管理端添加权限校验依赖。

【任务一】在 backend/core/deps.py 追加：

from config import BizError

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    管理员权限校验：
    1. 检查 current_user.role == "admin"
    2. 不满足 → BizError(2003, "需要管理员权限")
    3. 满足 → 返回 current_user
    """
    if current_user.role != "admin":
        raise BizError(2003, "需要管理员权限")
    return current_user

【任务二】创建 backend/scripts/create_admin.py：

#!/usr/bin/env python
"""
创建管理员账号脚本（开发环境使用）
用法：python scripts/create_admin.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
import models  # noqa: F401 - 触发所有模型注册

def create_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from models.user import User
        from sqlalchemy import select
        phone = "13800000000"  # 管理员手机号
        existing = db.execute(select(User).where(User.phone == phone)).scalar_one_or_none()
        if existing:
            existing.role = "admin"
            db.commit()
            print(f"已将 {phone} 更新为管理员")
        else:
            admin = User(
                phone=phone,
                nickname="超级管理员",
                role="admin",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"管理员账号创建成功：phone={phone}，id={admin.id}")
        print("登录方式：POST /api/v1/auth/send-code + POST /api/v1/auth/login")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

【验证】
    # 创建管理员账号
    cd backend && python scripts/create_admin.py

    # 登录管理员获取 TOKEN（先 send-code，再 login）
    curl -s -X POST http://localhost:8000/api/v1/auth/send-code \
      -H "Content-Type: application/json" \
      -d '{"phone":"13800000000"}' | python -m json.tool

    # 从数据库/日志中获取验证码，然后登录
    curl -s -X POST http://localhost:8000/api/v1/auth/login \
      -H "Content-Type: application/json" \
      -d '{"phone":"13800000000","code":"XXXX"}' | python -c "
    import sys,json; d=json.load(sys.stdin)
    print('role:', d['data']['user_info']['role'])
    assert d['data']['user_info']['role'] == 'admin', 'FAIL'
    print('PASS ADMIN_TOKEN:', d['data']['token'][:20], '...')
    "

    # 普通用户访问管理接口（code:2003）
    curl -s http://localhost:8000/api/v1/admin/dashboard \
      -H "Authorization: Bearer USER_TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)
    assert d['code'] == 2003, f'FAIL: {d}'
    print('PASS 普通用户被拒绝')
    "
```

---

## Task 2：数据看板接口

**预计时间**：30 分钟  
**依赖**：Task 1、orders 表、goods_spu 表、aftersale 表  
**完成标志**：`GET /admin/dashboard` 返回 KPI 统计数据

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建管理员数据看板接口。

【任务】新建 backend/routers/admin.py，实现第一个接口：

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from database import get_db
from schemas.common import ApiResponse
from core.deps import require_admin
from models.user import User
from models.order import Order
from models.goods import GoodsSpu, GoodsSku
from models.aftersale import Aftersale

router = APIRouter(tags=["管理端"])

@router.get("/dashboard", response_model=ApiResponse[dict])
def dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    数据看板统计：
    返回以下字段：
    {
      "total_orders": int,           # 总订单数
      "pending_pay_count": int,      # 待支付订单数
      "pending_ship_count": int,     # 待发货订单数
      "total_revenue": float,        # 已支付订单（非 pending_pay/cancelled）的 amount 总和
      "total_users": int,            # 用户总数
      "total_goods_on": int,         # 上架商品 SPU 数
      "total_aftersale": int,        # 总售后申请数
      "pending_review_count": int,   # 待审核售后数
    }
    """
    ...

【验证】
    curl -s http://localhost:8000/api/v1/admin/dashboard \
      -H "Authorization: Bearer ADMIN_TOKEN" | python -m json.tool
    # 预期：所有字段均为数字，不报错
```

---

## Task 3：商品管理接口（上下架、编辑）

**预计时间**：30 分钟  
**依赖**：Task 1、goods-plan  
**完成标志**：可上下架商品，编辑商品基本信息

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 admin.py 追加商品管理接口。

【任务】追加以下接口：

@router.get("/goods", response_model=ApiResponse[dict])
def admin_goods_list(
    status: str | None = Query(None),   # "on" | "off" | None（全部）
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    管理员商品列表（含下架商品）：
    - 支持 status 筛选（None 返回全部，包括 off）
    - 支持 keyword 搜索（name LIKE %keyword%）
    - 返回 {total, page, page_size, items: [{spu_id, name, category, status, sort_weight, sku_count, cover_url}]}
    """
    ...

@router.patch("/goods/{spu_id}/status", response_model=ApiResponse[None])
def admin_toggle_status(
    spu_id: int,
    status: str = Body(..., embed=True),   # "on" | "off"
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """上下架商品：status 只允许 "on" 或 "off"，否则 BizError(1001, '无效状态值')"""
    ...

@router.put("/goods/{spu_id}", response_model=ApiResponse[None])
def admin_update_goods(
    spu_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    编辑商品基本信息（允许字段：name, description, sort_weight, style_tags, occasion_tags,
    target_face_shapes, material, mount_type）
    其余字段忽略（防止意外覆盖 face_weight_penalty 等）
    """
    ALLOWED = {"name", "description", "sort_weight", "style_tags",
               "occasion_tags", "target_face_shapes", "material", "mount_type"}
    ...

【验证】
    # 查看商品列表（含下架）
    curl -s "http://localhost:8000/api/v1/admin/goods?page_size=5" \
      -H "Authorization: Bearer ADMIN_TOKEN" | python -m json.tool

    # 下架第 1 个商品
    curl -s -X PATCH "http://localhost:8000/api/v1/admin/goods/1/status" \
      -H "Authorization: Bearer ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"status":"off"}' | python -m json.tool
    # 预期：code:0

    # 普通商品接口 /goods/list 已看不到该商品
    curl -s "http://localhost:8000/api/v1/goods/1" | python -c "
    import sys,json; d=json.load(sys.stdin)
    assert d['code'] == 1001, f'FAIL: {d}'
    print('PASS 下架后不可见')
    "

    # 恢复上架
    curl -s -X PATCH "http://localhost:8000/api/v1/admin/goods/1/status" \
      -H "Authorization: Bearer ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"status":"on"}' | python -m json.tool
```

---

## Task 4：SKU 管理接口（添加/编辑/AR 参数）

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：可新增 SKU 并填入 AR 参数

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 admin.py 追加 SKU 管理接口。

【任务】追加：

@router.post("/goods/{spu_id}/sku", response_model=ApiResponse[dict])
def admin_add_sku(
    spu_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    新增 SKU：
    必填字段：sku_name (str), price (float, gt=0), stock (int, ge=0)
    可选字段：color, material, size, original_price, ar_asset_url,
              ar_scale_base, ar_offset_x, ar_offset_y, ar_rotation_offset
    返回新建 SKU 的 {sku_id, sku_name, price, stock, ar_asset_url}
    """
    ...

@router.put("/goods/{spu_id}/sku/{sku_id}", response_model=ApiResponse[None])
def admin_update_sku(
    spu_id: int,
    sku_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    编辑 SKU（含 AR 参数）：
    允许字段：sku_name, price, original_price, stock, color, material, size,
              ar_asset_url, ar_scale_base, ar_offset_x, ar_offset_y, ar_rotation_offset, status
    验证 sku.spu_id == spu_id，否则 BizError(1001, 'SKU 不存在')
    """
    ...

【验证】
    # 新增 SKU
    curl -s -X POST "http://localhost:8000/api/v1/admin/goods/1/sku" \
      -H "Authorization: Bearer ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "sku_name":"测试款·玫瑰金",
        "price":299.00,
        "stock":50,
        "color":"玫瑰金",
        "ar_scale_base":1.2,
        "ar_offset_x":0.1
      }' | python -m json.tool
    # 预期：code:0，data 含新 sku_id

    # 编辑 AR 参数
    curl -s -X PUT "http://localhost:8000/api/v1/admin/goods/1/sku/NEW_SKU_ID" \
      -H "Authorization: Bearer ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"ar_scale_base":1.5,"ar_offset_y":-0.05}' | python -m json.tool
    # 预期：code:0
```

---

## Task 5：订单管理接口（列表、发货）

**预计时间**：20 分钟  
**依赖**：Task 1、order-plan  
**完成标志**：管理员可查看所有订单，可发货（状态变 in_transit）

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 admin.py 追加订单管理接口。

【任务】追加：

@router.get("/orders", response_model=ApiResponse[dict])
def admin_order_list(
    status: str | None = Query(None),
    keyword: str | None = Query(None),   # 搜索订单号
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    管理员订单列表（全部用户）：
    - 支持 status 筛选
    - 支持 keyword 模糊搜索（order.id LIKE %keyword%）
    - 返回 {total, page, page_size, items: [OrderOut...]}
    - 按 created_at DESC 排序
    """
    ...

@router.post("/orders/{order_id}/ship", response_model=ApiResponse[None])
def admin_ship_order(
    order_id: str,
    tracking_no: str = Body(..., embed=True),
    logistics_company: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    发货（状态流转：pending_ship → in_transit）：
    1. 查 Order，status != "pending_ship" → BizError(1207, "订单状态不支持发货")
    2. 更新 status="in_transit"，tracking_no, logistics_company, shipped_at=now()
    3. db.commit()
    """
    ...

【验证】
    # 查询所有待发货订单
    curl -s "http://localhost:8000/api/v1/admin/orders?status=pending_ship" \
      -H "Authorization: Bearer ADMIN_TOKEN" | python -m json.tool

    # 发货（替换 ORDER_ID）
    curl -s -X POST "http://localhost:8000/api/v1/admin/orders/ORDER_ID/ship" \
      -H "Authorization: Bearer ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"tracking_no":"SF9876543210","logistics_company":"顺丰快递"}' | python -m json.tool
    # 预期：code:0

    # 用户查看订单详情（应有 tracking_no 和 status=in_transit）
    curl -s "http://localhost:8000/api/v1/order/ORDER_ID" \
      -H "Authorization: Bearer USER_TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    assert d['status']=='in_transit', f'FAIL: {d[\"status\"]}'
    print('PASS 已发货，tracking_no:', d['tracking_no'])
    "
```

---

## Task 6：售后审核接口

**预计时间**：30 分钟  
**依赖**：Task 1、aftersale-plan Task 3  
**完成标志**：管理员审核通过/拒绝正常，confirm-received 触发库存回流和算法反馈

> 注意：此任务与 aftersale-plan Task 5 重叠，如已实现则跳过，验证接口即可。

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 admin.py 追加售后审核接口。

【任务】追加（若 aftersale-plan Task 5 已实现则验证即可）：

@router.get("/aftersale", response_model=ApiResponse[dict])
def admin_aftersale_list(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """所有用户的售后单（管理视角），支持 status 筛选"""
    ...

@router.post("/aftersale/{aftersale_id}/approve", response_model=ApiResponse[None])
def admin_approve_aftersale(aftersale_id: str, ...):
    """审核通过：pending_review → pending_return"""
    ...

@router.post("/aftersale/{aftersale_id}/reject", response_model=ApiResponse[None])
def admin_reject_aftersale(aftersale_id: str, admin_note: str = Body(..., embed=True), ...):
    """拒绝：pending_review → rejected"""
    ...

@router.post("/aftersale/{aftersale_id}/confirm-received", response_model=ApiResponse[None])
def admin_confirm_received(aftersale_id: str, ...):
    """确认收货：in_transit_return → refunded（触发库存回流 + 算法反馈）"""
    ...

【验证】
    # 列出待审核售后
    curl -s "http://localhost:8000/api/v1/admin/aftersale?status=pending_review" \
      -H "Authorization: Bearer ADMIN_TOKEN" | python -m json.tool
```

---

## Task 7：注册路由到 main.py

**预计时间**：10 分钟  
**依赖**：Task 2~6  
**完成标志**：所有 `/api/v1/admin/*` 接口出现在 OpenAPI 文档

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。将管理端路由注册到 main.py。

【任务】在 backend/main.py 中追加：
    from routers import admin
    app.include_router(admin.router, prefix="/api/v1/admin")

【验证】
    curl -s http://localhost:8000/openapi.json | python -c "
    import sys,json
    paths = list(json.load(sys.stdin)['paths'].keys())
    admin_paths = [p for p in paths if '/admin/' in p]
    print('管理端接口数量:', len(admin_paths))
    print('接口列表:')
    for p in admin_paths:
        print(' ', p)
    assert len(admin_paths) >= 7, 'FAIL 接口数量不足'
    print('PASS')
    "
```

---

## Task 8：全流程冒烟测试

**预计时间**：30 分钟  
**依赖**：全部前序任务  
**完成标志**：管理端完整工作流（看板→商品管理→发货→售后审核）正常

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对管理端做完整验收。

【任务】创建 backend/scripts/smoke_test_admin.sh：

#!/usr/bin/env bash
set -e
BASE="http://localhost:8000/api/v1"

echo "请粘贴管理员 TOKEN："
read -r ADMIN_TOKEN
echo "请粘贴普通用户 TOKEN："
read -r USER_TOKEN

echo "=== [1] 权限校验 ==="
curl -s "$BASE/admin/dashboard" -H "Authorization: Bearer $USER_TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==2003, f'FAIL: {d}'
print('PASS 普通用户被拒绝 (code:2003)')
"

echo "=== [2] 数据看板 ==="
curl -s "$BASE/admin/dashboard" -H "Authorization: Bearer $ADMIN_TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0, f'FAIL: {d}'
data=d['data']
print('总订单:', data['total_orders'], '| 总收入:', data['total_revenue'])
print('上架商品:', data['total_goods_on'], '| 待审核售后:', data['pending_review_count'])
"

echo "=== [3] 商品列表（管理视角，含下架）==="
curl -s "$BASE/admin/goods?page_size=3" -H "Authorization: Bearer $ADMIN_TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)['data']
print('商品总数:', d['total'])
for g in d['items'][:3]:
    print(' ', g['name'], '| status:', g['status'])
"

echo "=== [4] 商品上下架测试 ==="
# 下架
curl -s -X PATCH "$BASE/admin/goods/1/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"off"}' | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0; print('PASS 下架成功')
"
# 用户视角不可见
curl -s "$BASE/goods/1" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==1001, f'FAIL: {d}'
print('PASS 用户看不到下架商品')
"
# 恢复
curl -s -X PATCH "$BASE/admin/goods/1/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"on"}' > /dev/null
echo "已恢复上架"

echo "=== [5] 订单发货 ==="
ORDER_ID=$(curl -s "$BASE/admin/orders?status=pending_ship&page_size=1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | \
  python -c "import sys,json; items=json.load(sys.stdin)['data']['items']; print(items[0]['order_id'] if items else 'NONE')")
if [ "$ORDER_ID" = "NONE" ]; then
  echo "暂无待发货订单（跳过发货测试）"
else
  curl -s -X POST "$BASE/admin/orders/$ORDER_ID/ship" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"tracking_no":"SF0000000001","logistics_company":"顺丰速运"}' | python -c "
  import sys,json; d=json.load(sys.stdin)
  assert d['code']==0, f'FAIL: {d}'
  print('PASS 发货成功，订单ID:', '$ORDER_ID')
  "
fi

echo "=== [6] 售后审核列表 ==="
curl -s "$BASE/admin/aftersale" -H "Authorization: Bearer $ADMIN_TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0, f'FAIL: {d}'
print('售后单总数:', d['data'].get('total', len(d['data'].get('items', []))))
"

echo ""
echo "✓ 管理端模块全部测试通过！"
```

---

## 附录：文件变更清单

```
backend/
├── core/
│   └── deps.py              ← 追加 require_admin（Task 1）
│
├── routers/
│   └── admin.py             ← 新建（Task 2-6）
│
├── main.py                  ← 注册 admin 路由（Task 7）
│
└── scripts/
    ├── create_admin.py      ← 新建（Task 1）
    └── smoke_test_admin.sh  ← 新建（Task 8）
```

## 附录：管理端接口清单

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /admin/dashboard | 数据看板 KPI |
| GET | /admin/goods | 商品列表（含下架）|
| PATCH | /admin/goods/{spu_id}/status | 上下架 |
| PUT | /admin/goods/{spu_id} | 编辑商品信息 |
| POST | /admin/goods/{spu_id}/sku | 新增 SKU |
| PUT | /admin/goods/{spu_id}/sku/{sku_id} | 编辑 SKU/AR 参数 |
| GET | /admin/orders | 所有订单列表 |
| POST | /admin/orders/{order_id}/ship | 发货 |
| GET | /admin/aftersale | 售后列表 |
| POST | /admin/aftersale/{id}/approve | 审核通过 |
| POST | /admin/aftersale/{id}/reject | 拒绝 |
| POST | /admin/aftersale/{id}/confirm-received | 确认收货 |
