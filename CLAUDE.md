# CLAUDE.md — 珑饰（LongShi）后端开发规范


## 项目概览

珑饰是一款面向女性消费者的智能饰品电商平台，核心差异化能力：AI 引导导购、AR 虚拟试戴、脸型×意图融合推荐。

**整体架构**：

```
前端 (Vue 3 + Vite, :5173)
       ↓  /api/* 反向代理
后端 (FastAPI, :8000)
       ↓  SQLAlchemy ORM
数据库 (MySQL 8.0)
```

- 前端：Vue 3 + Element Plus + Axios，Vite 开发服务器 `:5173`
- 后端：Python FastAPI，运行在 `:8000`
- 数据库：MySQL 8.0，ORM 使用 SQLAlchemy 2.x，迁移使用 Alembic
- **图片/AR素材**：文件存 `backend/assets/`，数据库只存 URL 路径字符串
- 前后端数据交互通过 JSON（HTTP 响应体），字段命名一律 `snake_case`
- `docs/jewelry.json` 作为商品种子数据，启动时通过脚本导入数据库

---

## 技术栈

| 层次 | 库 | 版本要求 |
|---|---|---|
| Web 框架 | FastAPI | ≥ 0.111 |
| ASGI 服务器 | Uvicorn | ≥ 0.29 |
| 数据验证 | Pydantic v2 | ≥ 2.7 |
| ORM | SQLAlchemy | ≥ 2.0 |
| 数据库迁移 | Alembic | ≥ 1.13 |
| MySQL 驱动 | PyMySQL | ≥ 1.1 |
| JWT 认证 | python-jose[cryptography] | ≥ 3.3 |
| 图片处理 | Pillow | ≥ 10.3 |
| 密码哈希 | passlib[bcrypt] | ≥ 1.7 |
| Python | — | 3.11+ |
| MySQL | — | 8.0+ |

---

## 目录结构

```
backend/
├── main.py                 # FastAPI 应用入口
├── config.py               # 全局配置（数据库连接、JWT secret 等）
├── database.py             # SQLAlchemy engine / Session 工厂
├── requirements.txt
├── .env                    # 本地环境变量（不提交 git）
├── .env.example            # 环境变量模板（提交 git）
│
├── models/                 # SQLAlchemy ORM 模型（数据库表定义）
│   ├── base.py             # declarative_base()
│   ├── user.py
│   ├── goods.py
│   ├── order.py
│   ├── aftersale.py
│   └── face.py
│
├── schemas/                # Pydantic 模型（请求体 + 响应体）
│   ├── common.py           # ApiResponse[T]
│   ├── user.py
│   ├── goods.py
│   ├── order.py
│   └── aftersale.py
│
├── routers/                # 路由层，一个业务域一个文件
│   ├── auth.py
│   ├── goods.py
│   ├── cart.py
│   ├── order.py
│   ├── aftersale.py
│   ├── face.py
│   ├── recommend.py
│   └── admin.py
│
├── services/               # 业务逻辑层（操作数据库）
│   ├── goods_service.py
│   ├── cart_service.py
│   ├── order_service.py
│   ├── aftersale_service.py
│   ├── face_service.py
│   └── recommend_service.py
│
├── alembic/                # 数据库迁移文件（alembic init 生成）
│   └── versions/
│
├── scripts/
│   └── seed_goods.py       # 从 docs/jewelry.json 导入商品种子数据
│
└── assets/                 # 静态资源（图片文件，不进数据库）
    ├── goods/              # 商品图片
    └── ar/                 # AR 试戴 PNG 素材
```

> `models/` 是数据库表结构，`schemas/` 是 API 请求/响应的数据格式，两者职责严格分离。

---

## 数据库表设计

### users — 用户

```sql
CREATE TABLE users (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  phone        VARCHAR(20)  NOT NULL UNIQUE,
  nickname     VARCHAR(50)  DEFAULT NULL,
  avatar_url   VARCHAR(255) DEFAULT NULL,
  role         ENUM('user','admin') NOT NULL DEFAULT 'user',
  -- 用户画像（冷启动问卷 + AI 导购采集）
  style_prefs    JSON    DEFAULT NULL,   -- ["优雅复古","简约精致"]
  occasion_prefs JSON    DEFAULT NULL,   -- ["约会出行","日常通勤"]
  budget_pref    VARCHAR(20) DEFAULT NULL, -- "50-200"
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### verify_codes — 短信验证码

```sql
CREATE TABLE verify_codes (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  phone      VARCHAR(20) NOT NULL,
  code       VARCHAR(10) NOT NULL,
  expired_at DATETIME    NOT NULL,        -- 5 分钟有效
  used       TINYINT(1)  NOT NULL DEFAULT 0,
  created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_phone (phone)
);
```

### addresses — 收货地址

```sql
CREATE TABLE addresses (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id    INT UNSIGNED NOT NULL,
  name       VARCHAR(50)  NOT NULL,
  phone      VARCHAR(20)  NOT NULL,
  province   VARCHAR(30)  NOT NULL,
  city       VARCHAR(30)  NOT NULL,
  district   VARCHAR(30)  NOT NULL,
  detail     VARCHAR(200) NOT NULL,       -- 详细地址
  is_default TINYINT(1)   NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### face_profiles — 脸型档案

```sql
CREATE TABLE face_profiles (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id      INT UNSIGNED NOT NULL UNIQUE,
  face_shape   ENUM('oval','round','square','oblong') NOT NULL,
  skin_tone    ENUM('warm','cool','neutral') NOT NULL,
  suggestions  JSON DEFAULT NULL,   -- ["弧形耳环更显温柔", ...]
  not_recommended JSON DEFAULT NULL,
  analyzed_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### goods_spu — 商品（SPU）

```sql
CREATE TABLE goods_spu (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  category     ENUM('earring','necklace','bracelet','ring','set') NOT NULL,
  sub_category VARCHAR(50)  DEFAULT NULL,
  description  TEXT         DEFAULT NULL,
  material     VARCHAR(100) DEFAULT NULL,
  cover_url    VARCHAR(255) DEFAULT NULL,  -- 主封面图路径
  mount_type   VARCHAR(30)  DEFAULT NULL,  -- AR 挂载点类型: ear_lobe / neck 等
  style_tags     JSON DEFAULT NULL,        -- ["优雅复古","法式轻奢"]
  occasion_tags  JSON DEFAULT NULL,        -- ["约会出行","日常通勤"]
  target_face_shapes JSON DEFAULT NULL,    -- ["oval","oblong"]
  face_weight_penalty JSON DEFAULT NULL,   -- {"oval": -5} 算法反馈写入此处
  sort_weight  INT UNSIGNED NOT NULL DEFAULT 100,
  status       ENUM('on','off') NOT NULL DEFAULT 'on',
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_category (category),
  INDEX idx_status   (status)
);
```

### goods_images — 商品图片

```sql
CREATE TABLE goods_images (
  id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  spu_id   INT UNSIGNED NOT NULL,
  url      VARCHAR(255) NOT NULL,
  sort     INT UNSIGNED NOT NULL DEFAULT 0,  -- 排序，0 最前
  FOREIGN KEY (spu_id) REFERENCES goods_spu(id)
);
```

### goods_sku — 商品规格（SKU）

```sql
CREATE TABLE goods_sku (
  id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  spu_id         INT UNSIGNED    NOT NULL,
  sku_name       VARCHAR(150)    NOT NULL,   -- "月牙弧形耳环 · 银色925银"
  color          VARCHAR(30)     DEFAULT NULL,
  material       VARCHAR(50)     DEFAULT NULL,
  size           VARCHAR(30)     DEFAULT NULL,
  price          DECIMAL(10, 2)  NOT NULL,
  original_price DECIMAL(10, 2)  DEFAULT NULL,
  stock          INT UNSIGNED    NOT NULL DEFAULT 0,
  -- AR 试戴参数
  ar_asset_url      VARCHAR(255) DEFAULT NULL,   -- AR PNG 文件路径
  ar_scale_base     FLOAT        DEFAULT 1.0,
  ar_offset_x       FLOAT        DEFAULT 0.0,
  ar_offset_y       FLOAT        DEFAULT 0.0,
  ar_rotation_offset FLOAT       DEFAULT 0.0,
  status         ENUM('on','off') NOT NULL DEFAULT 'on',
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (spu_id) REFERENCES goods_spu(id),
  INDEX idx_spu_id (spu_id)
);
```

### cart_items — 购物车

```sql
CREATE TABLE cart_items (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id    INT UNSIGNED NOT NULL,
  sku_id     INT UNSIGNED NOT NULL,
  qty        INT UNSIGNED NOT NULL DEFAULT 1,
  selected   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_sku (user_id, sku_id),    -- 同一 SKU 不重复添加，累加数量
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (sku_id)  REFERENCES goods_sku(id)
);
```

### orders — 订单

```sql
CREATE TABLE orders (
  id           VARCHAR(30)    PRIMARY KEY,   -- "LS202604280001"
  user_id      INT UNSIGNED   NOT NULL,
  status       ENUM(
    'pending_pay',   -- 待支付
    'pending_ship',  -- 待发货（已支付）
    'in_transit',    -- 运输中
    'completed',     -- 已完成
    'cancelled'      -- 已取消
  ) NOT NULL DEFAULT 'pending_pay',
  -- 收货地址快照（下单时拷贝，地址变更不影响历史订单）
  addr_name    VARCHAR(50)    NOT NULL,
  addr_phone   VARCHAR(20)    NOT NULL,
  addr_detail  VARCHAR(300)   NOT NULL,
  amount       DECIMAL(10, 2) NOT NULL,
  shipping_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  pay_method   ENUM('wechat','alipay') DEFAULT NULL,
  note         VARCHAR(300)   DEFAULT NULL,
  tracking_no        VARCHAR(50)  DEFAULT NULL,
  logistics_company  VARCHAR(50)  DEFAULT NULL,
  paid_at      DATETIME DEFAULT NULL,
  shipped_at   DATETIME DEFAULT NULL,
  completed_at DATETIME DEFAULT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_user_status (user_id, status)
);
```

### order_items — 订单商品明细

```sql
CREATE TABLE order_items (
  id         INT UNSIGNED   AUTO_INCREMENT PRIMARY KEY,
  order_id   VARCHAR(30)    NOT NULL,
  sku_id     INT UNSIGNED   NOT NULL,
  spu_id     INT UNSIGNED   NOT NULL,
  -- 商品信息快照（下单时拷贝，商品改价不影响历史订单）
  name       VARCHAR(150)   NOT NULL,
  cover_url  VARCHAR(255)   DEFAULT NULL,
  price      DECIMAL(10, 2) NOT NULL,
  qty        INT UNSIGNED   NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  INDEX idx_order_id (order_id)
);
```

### aftersale — 售后申请

```sql
CREATE TABLE aftersale (
  id         VARCHAR(30)  PRIMARY KEY,   -- "AS202604280001"
  order_id   VARCHAR(30)  NOT NULL,
  user_id    INT UNSIGNED NOT NULL,
  type       ENUM('refund','exchange') NOT NULL,
  status     ENUM(
    'pending_review',     -- 待审核
    'rejected',           -- 已拒绝（终态）
    'pending_return',     -- 审核通过，待用户寄回
    'in_transit_return',  -- 退货运输中
    'refund_processing',  -- 退款处理中
    'refunded'            -- 已退款（终态）
  ) NOT NULL DEFAULT 'pending_review',
  reason     ENUM(
    'quality_issue',       -- 商品质量问题
    'description_mismatch',-- 与描述不符
    'effect_mismatch',     -- 佩戴效果不符合预期（触发算法反馈）
    'size_mismatch',       -- 尺寸/规格不合适
    'dislike',             -- 不喜欢
    'other'
  ) NOT NULL,
  note             VARCHAR(500) DEFAULT NULL,
  return_tracking  VARCHAR(50)  DEFAULT NULL,   -- 用户填写的退货快递单号
  admin_note       VARCHAR(300) DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (user_id)  REFERENCES users(id),
  INDEX idx_status (status)
);
```

### aftersale_items — 售后商品明细

```sql
CREATE TABLE aftersale_items (
  id           INT UNSIGNED   AUTO_INCREMENT PRIMARY KEY,
  aftersale_id VARCHAR(30)    NOT NULL,
  sku_id       INT UNSIGNED   NOT NULL,
  name         VARCHAR(150)   NOT NULL,
  price        DECIMAL(10, 2) NOT NULL,
  qty          INT UNSIGNED   NOT NULL,
  FOREIGN KEY (aftersale_id) REFERENCES aftersale(id)
);
```

---

## SQLAlchemy ORM 模型规范

### base.py

```python
# models/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### 示例：goods.py

```python
# models/goods.py
from datetime import datetime
from sqlalchemy import String, Text, JSON, Enum, DECIMAL, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class GoodsSpu(Base):
    __tablename__ = "goods_spu"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    cover_url: Mapped[str | None] = mapped_column(String(255))
    style_tags: Mapped[list | None] = mapped_column(JSON)
    occasion_tags: Mapped[list | None] = mapped_column(JSON)
    target_face_shapes: Mapped[list | None] = mapped_column(JSON)
    face_weight_penalty: Mapped[dict | None] = mapped_column(JSON)
    sort_weight: Mapped[int] = mapped_column(default=100)
    status: Mapped[str] = mapped_column(String(10), default="on")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    skus: Mapped[list["GoodsSku"]] = relationship(back_populates="spu", lazy="select")
    images: Mapped[list["GoodsImage"]] = relationship(back_populates="spu", lazy="select")
```

---

## database.py

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

路由中通过 `Depends(get_db)` 注入 Session：

```python
@router.get("/list")
def get_list(db: Session = Depends(get_db), user = Depends(get_current_user)):
    ...
```

---

## config.py

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/longshi?charset=utf8mb4"
    JWT_SECRET: str = "change-me-in-production"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7   # 7 天
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()

class BizError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
```

`.env` 文件（本地开发，不提交 git）：

```
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/longshi?charset=utf8mb4
JWT_SECRET=your-secret-key
DEBUG=True
```

---

## API 规范

### 统一响应格式

所有接口返回 HTTP 200，业务结果通过 `code` 字段区分：

```json
{ "code": 0, "message": "ok", "data": { ... } }
```

错误响应：

```json
{ "code": 1001, "message": "商品不存在", "data": null }
```

**重要**：不用 HTTP 4xx/5xx 表达业务错误，统一 HTTP 200 + 非零 `code`，与前端 `http.js` 拦截器逻辑一致。

### 错误码

| 范围 | 域 |
|---|---|
| 0 | 成功 |
| 1001–1099 | 商品 |
| 1101–1199 | 购物车 |
| 1201–1299 | 订单 |
| 1301–1399 | 售后 |
| 2001–2099 | 认证 |
| 5000+ | 服务端内部错误 |

### 公共响应模型

```python
# schemas/common.py
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T | None = None
```

### 认证

- 登录后服务端签发 JWT，payload 含 `user_id` 和 `exp`
- 前端请求头 `Authorization: Bearer <token>`
- 需要登录的接口：`Depends(get_current_user)`
- 管理端接口：`Depends(require_admin)`（额外校验 `role == "admin"`）

### 接口清单

**认证**
- `POST /api/v1/auth/send-code` — 发送验证码（mock：不调真实短信，验证码写入 `verify_codes` 表，控制台打印）
- `POST /api/v1/auth/login` — 手机号+验证码登录，返回 `{token, user_info}`

**商品**
- `GET /api/v1/goods/list` — 商品列表，支持 `category / keyword / style / material / price_min / price_max / sort / page / page_size`
- `GET /api/v1/goods/{spu_id}` — 商品详情（含 SKU 列表、脸型匹配说明）

**购物车**
- `GET /api/v1/cart/list` — 购物车列表
- `POST /api/v1/cart/add` — 加入购物车 `{sku_id, qty}`
- `PUT /api/v1/cart/update` — 修改数量/规格 `{cart_item_id, qty?, sku_id?}`
- `DELETE /api/v1/cart/remove/{cart_item_id}` — 删除

**订单**
- `POST /api/v1/order/create` — 创建订单 `{cart_item_ids, address_id, pay_method, note?}`
- `POST /api/v1/order/pay` — 模拟支付 `{order_id}` → 状态变为 `pending_ship`，扣减 SKU 库存
- `POST /api/v1/order/cancel` — 取消订单（仅 `pending_pay` 可取消），`?order_id=`
- `GET /api/v1/order/list` — 订单列表，`?status=`
- `GET /api/v1/order/{order_id}` — 订单详情

**售后**
- `POST /api/v1/order/refund/apply` — 申请售后 `{order_id, items, type, reason, note?}`
- `GET /api/v1/order/refund/{aftersale_id}` — 售后进度
- `POST /api/v1/order/refund/{aftersale_id}/fill-tracking` — 填写退货快递单号 `{tracking_no}`

**脸型**
- `POST /api/v1/face/analyze` — 上传图片分析脸型（multipart/form-data）
- `GET /api/v1/face/profile` — 获取当前用户脸型档案

**推荐**
- `GET /api/v1/recommend/list` — 个性化推荐商品

**管理端**（需 admin JWT）
- `GET /api/v1/admin/dashboard` — 数据看板（统计查询）
- `GET /api/v1/admin/goods` — 商品列表管理
- `PUT /api/v1/admin/goods/{spu_id}` — 编辑商品
- `PATCH /api/v1/admin/goods/{spu_id}/status` — 上下架 `{status}`
- `POST /api/v1/admin/goods/{spu_id}/sku` — 添加 SKU
- `PUT /api/v1/admin/goods/{spu_id}/sku/{sku_id}` — 编辑 SKU（含 AR 参数）
- `GET /api/v1/admin/orders` — 所有订单，支持状态/关键词/日期过滤
- `POST /api/v1/admin/orders/{order_id}/ship` — 发货 `{tracking_no, logistics_company}`
- `GET /api/v1/admin/aftersale` — 售后审核列表
- `POST /api/v1/admin/aftersale/{id}/approve` — 审核通过
- `POST /api/v1/admin/aftersale/{id}/reject` — 拒绝 `{admin_note}`

---

## 业务规则

### 订单状态机

```
pending_pay
  │ POST /order/pay（模拟支付，扣库存）
  ▼
pending_ship
  │ admin POST /admin/orders/{id}/ship（录入快递单号）
  ▼
in_transit
  │ 用户确认收货（或 15 天后 mock 自动完成）
  ▼
completed
  │ 用户申请售后
  └── aftersale 表独立追踪

cancelled ← pending_pay 状态下用户取消（库存无需回滚，支付前未扣减）
```

**库存操作时机**：
- 支付成功时扣减 `goods_sku.stock`
- 售后状态到达 `refunded` 时回流库存

### 售后状态机

```
pending_review
  ├── admin 拒绝 → rejected（终态）
  └── admin 通过 → pending_return
                      │ 用户填写退货快递单号
                      ▼
                  in_transit_return
                      │（admin 确认收到退货）
                      ▼
                  refund_processing
                      │（mock 立即完成）
                      ▼
                  refunded（终态）
                  ← 触发：库存回流 + 算法反馈
```

### 算法反馈触发（`refunded` 状态写入时）

满足以下全部条件时，更新 `goods_spu.face_weight_penalty`：
1. `aftersale.type == 'refund'`
2. `aftersale.reason == 'effect_mismatch'`
3. 状态变更为 `refunded`
4. 该用户在 `face_profiles` 中存在有效记录

操作：读取 `face_weight_penalty` JSON 字段，对应 `face_shape` 的值 `-= 5`（累积降权）。

### 推荐评分规则（规则引擎，非 ML）

```
score = spu.sort_weight
      + (20 if user.face_shape in spu.target_face_shapes else 0)
      + spu.face_weight_penalty.get(user.face_shape, 0)   # 可为负
      + sum(10 for tag in spu.occasion_tags if tag in user.occasion_prefs)
      + sum(10 for tag in spu.style_tags    if tag in user.style_prefs)
      # 预算不匹配则整体排除
```

---

## 编码规范

### 路由层模板

```python
# routers/goods.py
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.common import ApiResponse
from schemas.goods import GoodsListItem, GoodsDetail
from services.goods_service import GoodsService

router = APIRouter(prefix="/goods", tags=["商品"])

@router.get("/list", response_model=ApiResponse[list[GoodsListItem]])
def get_goods_list(
    category: str | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    data = GoodsService(db).list(category=category, keyword=keyword, page=page, page_size=page_size)
    return ApiResponse(data=data)
```

### 服务层模板

```python
# services/goods_service.py
from sqlalchemy.orm import Session
from models.goods import GoodsSpu
from config import BizError

class GoodsService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_404(self, spu_id: int) -> GoodsSpu:
        spu = self.db.get(GoodsSpu, spu_id)
        if not spu or spu.status == "off":
            raise BizError(1001, "商品不存在")
        return spu
```

### 业务错误处理

```python
# main.py
@app.exception_handler(BizError)
async def biz_error_handler(request, exc: BizError):
    from fastapi.responses import JSONResponse
    return JSONResponse({"code": exc.code, "message": exc.message, "data": None})
```

### 命名约定

| 对象 | 风格 |
|---|---|
| Python 文件/函数/变量 | `snake_case` |
| Python 类 | `PascalCase` |
| 数据库表名/列名 | `snake_case` |
| API 响应 JSON 字段 | `snake_case` |
| URL 路径段 | `kebab-case`（如 `/send-code`） |

---

## main.py 结构

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings, BizError
from routers import auth, goods, cart, order, aftersale, face, recommend, admin

app = FastAPI(title="珑饰 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(BizError)
async def biz_error_handler(request, exc: BizError):
    from fastapi.responses import JSONResponse
    return JSONResponse({"code": exc.code, "message": exc.message, "data": None})

for r in [auth.router, goods.router, cart.router, order.router,
          aftersale.router, face.router, recommend.router, admin.router]:
    app.include_router(r, prefix="/api/v1")

app.mount("/assets", StaticFiles(directory="assets"), name="assets")
```

---

## 开发启动

```bash
# 1. 创建数据库
mysql -u root -p -e "CREATE DATABASE longshi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. 安装依赖
cd backend
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填写 MySQL 密码

# 4. 执行数据库迁移
alembic upgrade head

# 5. 导入种子数据
python scripts/seed_goods.py

# 6. 启动后端
uvicorn main:app --reload --port 8000

# 前端（另开终端）
cd frontend
npm install
npm run dev   # :5173，/api 自动代理到 :8000
```

API 文档：`http://localhost:8000/docs`

---

## 脸型分析（mock 实现说明）

`face_service.py` 原型阶段不接入真实 CV 模型：
1. 用 Pillow 读取图片，验证格式（jpg/png）和大小（< 10MB）
2. 按图片宽高比简单推断脸型（宽高比 > 0.9 → round，< 0.75 → oblong，其余 → oval）
3. 肤色固定返回 `warm`（可后续接入真实分析）
4. 结果写入 `face_profiles` 表，更新 `users` 表的 `face_shape` / `skin_tone` 字段

生产环境替换真实模型时只需修改 `face_service.py` 内部实现，接口不变。
