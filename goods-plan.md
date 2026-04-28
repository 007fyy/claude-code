# goods-plan.md — 珑饰商品模块开发计划

**模块范围**：商品 SPU/SKU 展示、关键词搜索、多维筛选、AR 素材管理、种子数据导入  
**技术栈**：FastAPI + SQLAlchemy 2.x + Pydantic v2  
**工作目录**：`L:\claude-code\backend\`  
**架构规范**：严格遵循 `L:\claude-code\CLAUDE.md`

---

## 当前状态说明

| 文件 | 状态 | 说明 |
|---|---|---|
| `models/goods.py` | ✅ 已存在 | GoodsSpu、GoodsSku，旧 Column 风格 |
| `routers/goods.py` | ⚠️ 需重构 | 路由存在但用 `import schemas`（旧）、HTTPException |
| `schemas.py` | ⚠️ 旧版 | SpuListItem 等在扁平 schemas.py 中，需迁移到 schemas/ |
| `goods_images` 表 | ❌ 缺失 | 模型未创建 |
| `schemas/goods.py` | ❌ 缺失 | 需新建 |
| `services/goods_service.py` | ❌ 缺失 | 逻辑内联在路由里 |
| 种子数据导入脚本 | ❌ 缺失 | jewelry.json 未导入 DB |

---

## 任务总览

| # | 任务 | 预计时间 | 依赖 |
|---|---|---|---|
| 1 | 补充商品图片模型 goods_images | 20 min | 无 |
| 2 | 创建 schemas/goods.py（Pydantic） | 30 min | 1 |
| 3 | 创建 GoodsService（list + detail） | 40 min | 1、2 |
| 4 | 重构商品列表接口（搜索+筛选+分页） | 30 min | 3 |
| 5 | 重构商品详情接口（含 SKU + 脸型匹配） | 20 min | 3 |
| 6 | 种子数据导入脚本（jewelry.json → DB） | 30 min | 1 |
| 7 | 管理端：商品 CRUD 接口 | 40 min | user-plan Task 4、3 |
| 8 | 管理端：SKU 管理 & AR 参数配置接口 | 30 min | 7 |
| 9 | AR 素材文件上传接口 | 30 min | 8 |
| 10 | 全流程冒烟测试 | 20 min | 全部 |

---

## Task 1：补充商品图片模型 goods_images

**预计时间**：20 分钟  
**依赖**：无  
**完成标志**：`python -c "import models; print('goods_images' in __import__('database').Base.metadata.tables)"` 输出 True

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。项目位于 L:\claude-code\backend\。

【当前状态】
- backend/models/goods.py 已存在（GoodsSpu、GoodsSku，旧 Column 风格）
- GoodsSpu 的 detail_images 字段是 JSON 存图片 URL 数组

【任务】在 backend/models/goods.py 末尾追加 GoodsImage 模型（与 GoodsSpu 关联）：

class GoodsImage(Base):
    __tablename__ = "goods_images"

    id = Column(_BIG(), primary_key=True, autoincrement=True)
    spu_id = Column(BigInteger, ForeignKey("goods_spu.id"), nullable=False, index=True)
    url = Column(String(512), nullable=False)
    sort = Column(Integer, default=0)    # 排序，数字越小越靠前

    spu = relationship("GoodsSpu", back_populates="images")

同时在 GoodsSpu 类里追加关联（在 skus relationship 下方）：
    images = relationship("GoodsImage", back_populates="spu",
                         order_by="GoodsImage.sort", lazy="select")

最后更新 backend/models/__init__.py，在现有 from models.goods import 行追加 GoodsImage：
    from models.goods import GoodsSpu, GoodsSku, GoodsImage    # noqa: F401
并在 __all__ 中追加 "GoodsImage"。

【验证】运行：
    python -c "
    import models
    from database import engine, Base
    Base.metadata.create_all(bind=engine)
    print('goods_images in tables:', 'goods_images' in Base.metadata.tables)
    "
预期输出 True。
```

---

## Task 2：创建 schemas/goods.py（Pydantic）

**预计时间**：30 分钟  
**依赖**：Task 1  
**完成标志**：`python -c "from schemas.goods import SpuListItem, SpuDetail, SkuOut"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建商品模块的 Pydantic v2 Schema。

【前提】backend/schemas/ 包已存在（schemas/common.py 有 ApiResponse[T]）

【任务】创建 backend/schemas/goods.py，包含以下模型：

SkuOut:             # SKU 响应（含 AR 参数）
    sku_id: int
    sku_name: str
    color: str | None
    material: str | None
    size: str | None
    price: float
    original_price: float | None
    stock: int
    ar_asset_url: str | None
    ar_scale_base: float = 1.0
    ar_offset_x: float = 0.0
    ar_offset_y: float = 0.0
    ar_rotation_offset: float = 0.0
    model_config = ConfigDict(from_attributes=True)

SpuListItem:        # 商品列表卡片
    spu_id: int
    name: str
    category: str
    material: str | None
    cover_url: str | None
    style_tags: list[str]
    occasion_tags: list[str]
    price_min: float            # 最低 SKU 价格
    price_max: float            # 最高 SKU 价格
    ar_available: bool          # 是否有可试戴 SKU
    sort_weight: int
    model_config = ConfigDict(from_attributes=True)

SpuDetail:          # 商品详情（含全部 SKU）
    spu_id: int
    name: str
    category: str
    sub_category: str | None
    description: str | None
    material: str | None
    cover_url: str | None
    detail_images: list[str]
    style_tags: list[str]
    occasion_tags: list[str]
    target_face_shapes: list[str]
    mount_type: str | None
    skus: list[SkuOut]
    face_match_tip: str | None = None   # 脸型匹配提示文案，由后端动态生成
    model_config = ConfigDict(from_attributes=True)

GoodsListQuery:     # 列表查询参数（用于 Query 解析）
    category: str | None = None
    keyword: str | None = None
    style: str | None = None
    material: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    sort: str = "default"    # default | price_asc | price_desc | newest
    page: int = 1
    page_size: int = 20

GoodsListOut:       # 列表分页响应
    total: int
    page: int
    page_size: int
    items: list[SpuListItem]

# 管理端使用
SpuCreateReq:       # 创建商品请求
    name: str
    category: str
    sub_category: str | None = None
    description: str | None = None
    material: str | None = None
    cover_url: str | None = None
    mount_type: str | None = None
    style_tags: list[str] = []
    occasion_tags: list[str] = []
    target_face_shapes: list[str] = []
    sort_weight: int = 100

SpuUpdateReq:       # 更新商品请求（全部可选）
    name: str | None = None
    description: str | None = None
    material: str | None = None
    cover_url: str | None = None
    style_tags: list[str] | None = None
    occasion_tags: list[str] | None = None
    target_face_shapes: list[str] | None = None
    sort_weight: int | None = None

SkuCreateReq:       # 新增 SKU
    sku_name: str
    color: str | None = None
    material: str | None = None
    size: str | None = None
    price: float
    original_price: float | None = None
    stock: int = 0
    ar_asset_url: str | None = None
    ar_scale_base: float = 1.0
    ar_offset_x: float = 0.0
    ar_offset_y: float = 0.0
    ar_rotation_offset: float = 0.0

SkuUpdateReq:       # 编辑 SKU（全部可选）
    sku_name: str | None = None
    price: float | None = None
    original_price: float | None = None
    stock: int | None = None
    ar_asset_url: str | None = None
    ar_scale_base: float | None = None
    ar_offset_x: float | None = None
    ar_offset_y: float | None = None
    ar_rotation_offset: float | None = None
    status: str | None = None    # "on" | "off"

【验证】运行：
    python -c "
    from schemas.goods import SpuListItem, SpuDetail, SkuOut, GoodsListQuery
    print('SpuDetail fields:', list(SpuDetail.model_fields.keys()))
    print('SkuOut fields:', list(SkuOut.model_fields.keys()))
    "
```

---

## Task 3：创建 GoodsService（list + detail）

**预计时间**：40 分钟  
**依赖**：Task 1、2  
**完成标志**：Python 脚本直接调用 service 返回商品数据

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在将商品路由中的内联逻辑提取为 Service 类。

【当前状态】商品查询逻辑散落在 backend/routers/goods.py 中，没有独立 service 层。

【任务】创建 backend/services/goods_service.py：

class GoodsService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, q: GoodsListQuery, face_shape: str | None = None) -> GoodsListOut:
        """
        商品列表查询，支持多维筛选：
        1. 基础过滤：status == "on"（或整数 1，兼容现有模型）
        2. category 过滤：精确匹配
        3. keyword 过滤：name LIKE %keyword%（用 SQLAlchemy .contains()）
        4. style 过滤：style_tags JSON 包含指定值（用 .cast(String).contains(style)）
        5. material 过滤：material LIKE %material%
        6. price_min/price_max：关联最小 SKU 价格过滤（子查询或关联 goods_sku）
        7. 排序：
           default → sort_weight DESC, id DESC
           price_asc → 最小 SKU 价格 ASC
           price_desc → 最小 SKU 价格 DESC
           newest → id DESC
        8. 分页：offset + limit
        将查询结果转换为 list[SpuListItem] 并返回 GoodsListOut
        """

    def detail(self, spu_id: int, face_shape: str | None = None) -> SpuDetail:
        """
        商品详情，包含：
        - SPU 基础信息
        - 所有 status==on 的 SKU（转为 SkuOut 列表）
        - detail_images（从 goods_images 表 + spu.detail_images JSON 合并）
        - face_match_tip：若 face_shape in spu.target_face_shapes，
          返回 "你是{face_shape_cn}，该款式与你的脸型高度匹配"；否则 None
        若 spu 不存在或 status==off，抛出 BizError(1001, "商品不存在")
        """

    def get_or_404(self, spu_id: int) -> GoodsSpu:
        spu = self.db.get(GoodsSpu, spu_id)
        if not spu or spu.status not in (1, "on"):
            raise BizError(1001, "商品不存在")
        return spu

    def _spu_to_list_item(self, spu: GoodsSpu) -> SpuListItem:
        """将 ORM 对象转为 SpuListItem，计算 price_min/price_max/ar_available"""

脸型中文映射（在模块顶部定义）：
    FACE_SHAPE_CN = {"oval": "椭圆脸", "round": "圆脸", "square": "方脸", "oblong": "长脸"}

【验证】运行（需先完成 Task 6 种子数据导入）：
    python -c "
    from database import SessionLocal
    from services.goods_service import GoodsService
    from schemas.goods import GoodsListQuery
    db = SessionLocal()
    svc = GoodsService(db)
    result = svc.list(GoodsListQuery(page=1, page_size=5))
    print('total:', result.total, 'items:', len(result.items))
    if result.items:
        d = svc.detail(result.items[0].spu_id)
        print('detail skus:', len(d.skus))
    db.close()
    "
```

---

## Task 4：重构商品列表接口（搜索+筛选+分页）

**预计时间**：30 分钟  
**依赖**：Task 3  
**完成标志**：`curl "http://localhost:8000/api/v1/goods/list?category=earring&page=1"` 返回 `code:0` 和商品数组

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在用 GoodsService 重构商品列表路由，替换掉旧的内联查询逻辑。

【当前状态】backend/routers/goods.py 中 list_goods() 是内联逻辑，用旧 schemas。

【任务】完全重写 backend/routers/goods.py 的 list_goods 路由：

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.common import ApiResponse
from schemas.goods import GoodsListOut, GoodsListQuery
from services.goods_service import GoodsService
from core.deps import get_current_user   # 可选登录
from models.user import User

router = APIRouter()

@router.get("/list", response_model=ApiResponse[GoodsListOut])
def list_goods(
    category: str | None = Query(None),
    keyword: str | None = Query(None),
    style: str | None = Query(None),
    material: str | None = Query(None),
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    sort: str = Query("default"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    # 可选登录——游客也能浏览，登录后可返回脸型匹配信息
    current_user: User | None = Depends(lambda: None),   # 暂时设为 None，Task 5 再细化
):
    q = GoodsListQuery(
        category=category, keyword=keyword, style=style, material=material,
        price_min=price_min, price_max=price_max, sort=sort,
        page=page, page_size=page_size
    )
    data = GoodsService(db).list(q)
    return ApiResponse(data=data)

注意：保留原有路由前缀（main.py 中注册为 /api/v1/goods），不要修改 main.py。

【验证】启动服务后：
    # 基本列表
    curl -s "http://localhost:8000/api/v1/goods/list" | python -m json.tool

    # 分类筛选
    curl -s "http://localhost:8000/api/v1/goods/list?category=earring" | python -m json.tool

    # 关键词搜索
    curl -s "http://localhost:8000/api/v1/goods/list?keyword=珍珠" | python -m json.tool

    # 价格区间
    curl -s "http://localhost:8000/api/v1/goods/list?price_min=50&price_max=200&sort=price_asc" | python -m json.tool
```

---

## Task 5：重构商品详情接口（含 SKU + 脸型匹配）

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：`curl "http://localhost:8000/api/v1/goods/1"` 返回含 skus 数组和 ar 参数的详情

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在重构商品详情路由。

【任务】重写 backend/routers/goods.py 的 get_spu 路由：

@router.get("/{spu_id}", response_model=ApiResponse[SpuDetail])
def get_spu(
    spu_id: int,
    db: Session = Depends(get_db),
):
    data = GoodsService(db).detail(spu_id)
    return ApiResponse(data=data)

（未来可传入 face_shape 参数，现在先传 None）

【验证】
    # 存在的商品
    curl -s "http://localhost:8000/api/v1/goods/1" | python -m json.tool
    预期：返回含 name、description、skus（数组含 ar_asset_url）的详情

    # 不存在的商品
    curl -s "http://localhost:8000/api/v1/goods/9999" | python -m json.tool
    预期：{"code": 1001, "message": "商品不存在", "data": null}

    # 验证 SKU 的 AR 参数完整性
    curl -s "http://localhost:8000/api/v1/goods/1" | python -c "
    import sys, json
    d = json.load(sys.stdin)
    sku = d['data']['skus'][0]
    print('AR params:', sku.get('ar_asset_url'), sku.get('ar_scale_base'))
    "
```

---

## Task 6：种子数据导入脚本（jewelry.json → DB）

**预计时间**：30 分钟  
**依赖**：Task 1  
**完成标志**：运行脚本后 `goods_spu` 表有数据，再次运行不重复插入

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在编写种子数据导入脚本。

【数据源】L:\claude-code\docs\jewelry.json
【数据结构】{"goods": [{id, name, category, skus:[{sku_name, color, price, ...}], ...}]}

【任务】创建 backend/scripts/seed_goods.py：

功能要求：
1. 读取 docs/jewelry.json（路径相对于项目根目录，脚本内用 os.path 计算绝对路径）
2. 对每个 goods 条目：
   a. 检查 goods_spu 表是否已有同名商品（按 name 判断），有则跳过（幂等）
   b. 插入 GoodsSpu 记录（映射 category/description/material/cover_url/mount_type/
      style_tags/occasion_tags/target_face_shapes/sort_weight）
   c. 对每个 sku 条目插入 GoodsSku 记录（映射 sku_name/color/price/original_price/
      stock/ar_asset_url/ar_scale_base/ar_offset_x/ar_offset_y/ar_rotation_offset）
   d. 若 detail_images 非空，同时插入 GoodsImage 记录（按 sort 顺序）
3. 全部成功后打印导入统计

脚本顶部加：
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # 确保能导入 backend 包

字段映射说明（jewelry.json 字段 → 数据库字段）：
    "id" → 忽略（数据库自增）
    "sort_weight" → sort_weight
    "skus[].ar_scale_base" → ar_scale_base（float）
    jewelry.json 中 status 字段不存在 → 默认 1（已上架）

【运行】
    cd L:\claude-code
    python backend/scripts/seed_goods.py
预期输出：
    导入完成：新增 SPU 8 条，SKU 16 条，图片 16 条
    （再次运行：已跳过 8 条（已存在）)
```

---

## Task 7：管理端商品 CRUD 接口

**预计时间**：40 分钟  
**依赖**：user-plan Task 4（require_admin）、Task 3  
**完成标志**：管理员 token 可创建商品，普通用户 token 被拒绝（code:2003）

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现管理端商品管理接口。

【前提】
- core/deps.py 中 require_admin 已实现（检查 user.role == "admin"）
- schemas/goods.py 中 SpuCreateReq、SpuUpdateReq 已定义

【任务】创建 backend/routers/admin_goods.py：

router = APIRouter(prefix="/admin/goods", tags=["管理-商品"])

# 所有接口都加 Depends(require_admin)

@router.get("", response_model=ApiResponse[GoodsListOut])
def admin_list_goods(
    status: str | None = Query(None),   # 可查 off 状态商品
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db = Depends(get_db),
    admin = Depends(require_admin),
):
    """管理端列表可查所有状态商品"""

@router.post("", response_model=ApiResponse[SpuDetail])
def create_goods(req: SpuCreateReq, db = Depends(get_db), admin = Depends(require_admin)):
    """创建新商品（不含 SKU，SKU 通过 Task 8 单独添加）"""

@router.put("/{spu_id}", response_model=ApiResponse[SpuDetail])
def update_goods(spu_id: int, req: SpuUpdateReq, db = Depends(get_db), admin = Depends(require_admin)):
    """更新商品基础信息，只更新非 None 字段"""

@router.patch("/{spu_id}/status", response_model=ApiResponse[None])
def toggle_status(spu_id: int, status: str = Body(..., embed=True), db = Depends(get_db), admin = Depends(require_admin)):
    """上下架商品，status 只允许 "on"(1) 或 "off"(0)"""

在 backend/main.py 注册：
    from routers import admin_goods
    app.include_router(admin_goods.router, prefix="/api/v1")

【验证】先获取 admin token（需要有 role=admin 的用户，临时可直接在 DB 修改），然后：
    # 创建商品
    curl -s -X POST http://localhost:8000/api/v1/admin/goods \
      -H "Authorization: Bearer ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"name":"测试耳环","category":"earring","mount_type":"ear_lobe","sort_weight":50}' \
      | python -m json.tool

    # 普通用户 token 应被拒绝
    curl -s -X POST http://localhost:8000/api/v1/admin/goods \
      -H "Authorization: Bearer USER_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"name":"xxx","category":"earring","mount_type":"ear_lobe"}' \
      | python -m json.tool
    # 预期：{"code": 2003, "message": "无管理员权限", "data": null}
```

---

## Task 8：管理端 SKU 管理 & AR 参数配置

**预计时间**：30 分钟  
**依赖**：Task 7  
**完成标志**：管理员可新增 SKU 并设置 AR 偏移参数，前端 AR 试戴能读取新参数

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在在 admin_goods.py 追加 SKU 管理接口。

【任务】在 backend/routers/admin_goods.py 追加以下接口：

@router.post("/{spu_id}/sku", response_model=ApiResponse[SkuOut])
def add_sku(spu_id: int, req: SkuCreateReq, db=Depends(get_db), admin=Depends(require_admin)):
    """
    为指定 SPU 新增 SKU。
    先验证 SPU 存在（不管 status），不存在则 BizError(1001, "商品不存在")。
    创建 GoodsSku 记录并返回 SkuOut。
    """

@router.put("/{spu_id}/sku/{sku_id}", response_model=ApiResponse[SkuOut])
def update_sku(spu_id: int, sku_id: int, req: SkuUpdateReq, db=Depends(get_db), admin=Depends(require_admin)):
    """
    更新 SKU（含 AR 参数）。验证 sku.spu_id == spu_id，否则 BizError(1001)。
    只更新非 None 字段（model_dump(exclude_none=True)）。
    status 字段：若传 "on" 则写 1，"off" 则写 0（兼容现有模型的 Integer status）。
    """

@router.delete("/{spu_id}/sku/{sku_id}", response_model=ApiResponse[None])
def delete_sku(spu_id: int, sku_id: int, db=Depends(get_db), admin=Depends(require_admin)):
    """软删除：将 sku.status 置为 0（下架），不物理删除"""

【验证】
    SPU_ID=1  # 已有商品的 id
    # 新增 SKU
    curl -s -X POST "http://localhost:8000/api/v1/admin/goods/$SPU_ID/sku" \
      -H "Authorization: Bearer ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"sku_name":"测试款·银色","color":"银色","price":99.0,"stock":10,
           "ar_asset_url":"/assets/ar/test.png","ar_scale_base":1.1,
           "ar_offset_x":-3.0,"ar_offset_y":5.0}' | python -m json.tool

    # 验证商品详情中出现新 SKU
    curl -s "http://localhost:8000/api/v1/goods/$SPU_ID" | python -c "
    import sys,json; d=json.load(sys.stdin); print('SKU count:', len(d['data']['skus']))
    "
```

---

## Task 9：AR 素材文件上传接口

**预计时间**：30 分钟  
**依赖**：Task 8  
**完成标志**：上传 PNG 文件后返回可访问的静态 URL，AR 试戴页可直接使用该 URL

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现 AR PNG 素材的文件上传接口。

【背景】AR 试戴需要每个 SKU 对应一张透明背景的 PNG 文件，存在 backend/assets/ar/ 目录，
数据库 goods_sku.ar_asset_url 存相对路径（如 /assets/ar/crescent-silver.png），
FastAPI 通过 StaticFiles 提供静态文件访问。

【任务】在 backend/routers/admin_goods.py 追加文件上传接口：

from fastapi import UploadFile, File
import shutil, uuid, os

ASSETS_AR_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "ar")

@router.post("/upload/ar-asset", response_model=ApiResponse[dict])
async def upload_ar_asset(
    file: UploadFile = File(...),
    admin=Depends(require_admin),
):
    """
    上传 AR 试戴素材（仅允许 PNG 格式，大小 < 5MB）。
    返回 {"url": "/assets/ar/xxx.png"} 供前端或 SKU 编辑接口使用。

    验证：
    1. file.content_type == "image/png"，否则 BizError(1010, "仅支持 PNG 格式")
    2. 读取内容，len(content) < 5*1024*1024，否则 BizError(1011, "文件不能超过 5MB")

    存储：
    1. 确保 ASSETS_AR_DIR 目录存在（os.makedirs）
    2. 文件名用 uuid4 + ".png"，避免冲突
    3. 写入文件（open(dest, 'wb')）
    4. 返回相对 URL: /assets/ar/{filename}
    """

注意：backend/main.py 中已有 app.mount("/assets", StaticFiles(directory="assets"))，
上传后的文件可直接通过 http://localhost:8000/assets/ar/xxx.png 访问。
若 StaticFiles 挂载不存在，提醒在 main.py 中添加（先检查 assets 目录是否存在）。

【验证】准备一个 test.png 文件，然后：
    curl -s -X POST http://localhost:8000/api/v1/admin/goods/upload/ar-asset \
      -H "Authorization: Bearer ADMIN_TOKEN" \
      -F "file=@test.png" | python -m json.tool
    预期：{"code": 0, "message": "ok", "data": {"url": "/assets/ar/xxxx.png"}}

    # 验证可访问
    URL=$(上一步返回的 url)
    curl -I "http://localhost:8000$URL"
    预期：HTTP 200
```

---

## Task 10：全流程冒烟测试

**预计时间**：20 分钟  
**依赖**：全部前序任务  
**完成标志**：脚本全部输出 code:0，没有 500 错误

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对商品模块做完整验收。

【任务】创建 backend/scripts/smoke_test_goods.sh：

#!/usr/bin/env bash
set -e
BASE="http://localhost:8000/api/v1"

echo "=== [1] 商品列表（全部）==="
curl -s "$BASE/goods/list" | python -c "
import sys,json; d=json.load(sys.stdin)
print('code:', d['code'], '| total:', d['data']['total'])
assert d['code'] == 0 and d['data']['total'] > 0, 'FAIL: 商品列表为空'
print('PASS')
"

echo "=== [2] 按分类筛选（耳饰）==="
curl -s "$BASE/goods/list?category=earring" | python -c "
import sys,json; d=json.load(sys.stdin)
items = d['data']['items']
print('耳饰数量:', len(items))
assert all(i['category']=='earring' for i in items), 'FAIL: 含非耳饰商品'
print('PASS')
"

echo "=== [3] 关键词搜索 ==="
curl -s "$BASE/goods/list?keyword=耳" | python -c "
import sys,json; d=json.load(sys.stdin)
print('搜索结果数:', d['data']['total']); print('PASS')
"

echo "=== [4] 价格排序 ==="
curl -s "$BASE/goods/list?sort=price_asc&page_size=5" | python -c "
import sys,json; d=json.load(sys.stdin)
prices = [i['price_min'] for i in d['data']['items']]
assert prices == sorted(prices), f'FAIL: 价格未升序 {prices}'
print('PASS 价格升序:', prices)
"

echo "=== [5] 商品详情（含 SKU）==="
SPU_ID=1
curl -s "$BASE/goods/$SPU_ID" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code'] == 0, 'FAIL'
print('商品名:', d['data']['name'], '| SKU数:', len(d['data']['skus']))
print('PASS')
"

echo "=== [6] 商品不存在（code:1001）==="
curl -s "$BASE/goods/99999" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code'] == 1001, f'FAIL: expected 1001, got {d[\"code\"]}'
print('PASS code:1001')
"

echo ""
echo "✓ 商品模块冒烟测试全部通过！"

【执行】
    # 先导入种子数据
    cd L:\claude-code && python backend/scripts/seed_goods.py
    # 启动服务
    uvicorn main:app --reload --port 8000
    # 执行测试
    bash backend/scripts/smoke_test_goods.sh
```

---

## 附录：文件变更清单

```
backend/
├── models/
│   ├── goods.py          ← 修改（Task 1：追加 GoodsImage）
│   └── __init__.py       ← 修改（Task 1：导出 GoodsImage）
│
├── schemas/
│   └── goods.py          ← 新建（Task 2）
│
├── services/
│   └── goods_service.py  ← 新建（Task 3）
│
├── routers/
│   ├── goods.py          ← 重构（Task 4、5）
│   └── admin_goods.py    ← 新建（Task 7、8、9）
│
├── scripts/
│   ├── seed_goods.py         ← 新建（Task 6）
│   └── smoke_test_goods.sh   ← 新建（Task 10）
│
└── main.py               ← 修改（Task 7：注册 admin_goods router）
```
