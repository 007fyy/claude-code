# user-plan.md — 珑饰用户模块开发计划

**模块范围**：登录/注册（手机号+验证码）、JWT 认证、用户信息管理、冷启动问卷、收货地址 CRUD  
**技术栈**：FastAPI + SQLAlchemy 2.x + Pydantic v2 + python-jose JWT  
**工作目录**：`L:\claude-code\backend\`  
**架构规范**：严格遵循 `L:\claude-code\CLAUDE.md`

---

## 任务总览

| # | 任务 | 预计时间 | 依赖 |
|---|---|---|---|
| 1 | 安装依赖 & 初始化 config.py | 20 min | 无 |
| 2 | 数据库模型（users / verify_codes / addresses） | 30 min | 1 |
| 3 | 公共 Schema + 用户/地址 Pydantic 模型 | 30 min | 2 |
| 4 | JWT 工具函数 & 认证依赖注入 | 30 min | 1 |
| 5 | 验证码服务（生成 + mock 发送） | 30 min | 2、3 |
| 6 | 发送验证码接口 POST /auth/send-code | 20 min | 5 |
| 7 | 登录服务 & 登录接口 POST /auth/login | 40 min | 4、5、6 |
| 8 | 用户信息接口 GET/PUT /user/me | 30 min | 7 |
| 9 | 冷启动问卷接口 PATCH /user/prefs | 20 min | 8 |
| 10 | 收货地址服务（CRUD + 默认地址逻辑） | 40 min | 7 |
| 11 | 收货地址接口 /user/address | 30 min | 10 |
| 12 | 注册路由 & 全流程冒烟测试 | 30 min | 全部 |

---

## Task 1：安装依赖 & 初始化 config.py

**预计时间**：20 分钟  
**依赖**：无  
**完成标志**：`python -c "from config import settings, BizError"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。项目位于 L:\claude-code\backend\，使用 FastAPI + SQLAlchemy + Pydantic v2。

【任务】完成以下两件事：

① 更新 backend/requirements.txt，在现有内容基础上追加以下依赖（若已存在则跳过）：
   python-jose[cryptography]==3.3.0
   passlib[bcrypt]==1.7.4
   pydantic-settings==2.3.4
   PyMySQL==1.1.1
   python-multipart==0.0.9
   Pillow==10.4.0

② 创建 backend/config.py，内容如下：

   - Settings 类（继承 pydantic_settings.BaseSettings）：
     DATABASE_URL: str = "sqlite:///./jewelry.db"   ← 开发阶段保持 SQLite，与现有 database.py 一致
     JWT_SECRET: str = "longshi-dev-secret-change-in-prod"
     JWT_EXPIRE_MINUTES: int = 60 * 24 * 7   # 7 天
     DEBUG: bool = True
     Config.env_file = ".env"

   - settings = Settings() 单例

   - BizError(Exception) 类：
     __init__(self, code: int, message: str)
     保存 self.code 和 self.message

   - 同时创建 backend/.env.example（不创建 .env，避免提交密钥）：
     DATABASE_URL=sqlite:///./jewelry.db
     JWT_SECRET=your-secret-key-here
     DEBUG=True

③ 更新 backend/main.py，在 FastAPI app 上注册全局 BizError 异常处理器：
   @app.exception_handler(BizError)
   async def biz_error_handler(request, exc: BizError):
       from fastapi.responses import JSONResponse
       return JSONResponse({"code": exc.code, "message": exc.message, "data": None})

   注意：只追加异常处理器，不修改已有的路由和中间件。

【验证】运行：
   python -c "from config import settings, BizError; print(settings.JWT_SECRET)"
应输出 JWT secret 字符串，无报错。
```

---

## Task 2：数据库模型（users / verify_codes / addresses）

**预计时间**：30 分钟  
**依赖**：Task 1  
**完成标志**：`python -c "import models; print([t for t in __import__('database').Base.metadata.tables])"` 包含 users、verify_codes、addresses

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。项目位于 L:\claude-code\backend\，使用 SQLAlchemy 2.x Mapped 语法。

【当前状态】
- backend/database.py 已存在，包含 Base = declarative_base() 和 get_db()
- backend/models/ 目录已存在，包含 goods.py、cart.py、order.py（旧 Column 风格）和 __init__.py
- __init__.py 当前导出：GoodsSpu, GoodsSku, CartItem, Order, OrderItem, RefundOrder

【任务】在 backend/models/ 目录下创建 3 个新文件，使用 SQLAlchemy 2.x Mapped + mapped_column 语法，
从 database 导入 Base（from database import Base）：

① backend/models/user.py — User 模型
字段（完全按照以下规格）：
   id: Mapped[int]          主键，autoincrement
   phone: Mapped[str]       String(20)，unique=True，nullable=False，用户唯一标识
   nickname: Mapped[str|None]   String(50)，default=None
   avatar_url: Mapped[str|None] String(255)，default=None
   role: Mapped[str]        String(10)，default="user"，可选值 "user" / "admin"
   style_prefs: Mapped[list|None]    JSON，default=None，存 ["优雅复古","简约精致"]
   occasion_prefs: Mapped[list|None] JSON，default=None，存 ["约会出行"]
   budget_pref: Mapped[str|None]     String(20)，default=None，存 "50-200"
   created_at: Mapped[datetime]  DateTime，server_default=func.now()
   updated_at: Mapped[datetime]  DateTime，server_default=func.now()，onupdate=func.now()

   关联：addresses: Mapped[list["Address"]] = relationship("Address", back_populates="user", lazy="select")
   用 TYPE_CHECKING + if TYPE_CHECKING: from models.address import Address 避免循环导入

② backend/models/verify_code.py — VerifyCode 模型
字段：
   id: Mapped[int]          主键
   phone: Mapped[str]       String(20)，nullable=False，index=True
   code: Mapped[str]        String(10)，nullable=False
   expired_at: Mapped[datetime]  DateTime，nullable=False（发送时写入 now()+5分钟）
   used: Mapped[bool]       Boolean，default=False（验证成功后置 True 防重放）
   created_at: Mapped[datetime]  DateTime，server_default=func.now()

③ backend/models/address.py — Address 模型
字段：
   id: Mapped[int]          主键
   user_id: Mapped[int]     ForeignKey("users.id", ondelete="CASCADE")，index=True
   name: Mapped[str]        String(50)，nullable=False（收件人姓名）
   phone: Mapped[str]       String(20)，nullable=False
   province: Mapped[str]    String(30)，nullable=False
   city: Mapped[str]        String(30)，nullable=False
   district: Mapped[str]    String(30)，nullable=False
   detail: Mapped[str]      String(200)，nullable=False（详细地址）
   is_default: Mapped[bool] Boolean，default=False
   created_at: Mapped[datetime]  DateTime，server_default=func.now()

   关联：user: Mapped["User"] = relationship("User", back_populates="addresses")
   同样用 TYPE_CHECKING 避免循环导入

④ 更新 backend/models/__init__.py，在现有导出末尾追加：
   from models.user import User          # noqa: F401
   from models.verify_code import VerifyCode  # noqa: F401
   from models.address import Address    # noqa: F401
   并在 __all__ 中追加 "User", "VerifyCode", "Address"

【验证】运行：
   python -c "
   import models
   from database import engine, Base
   Base.metadata.create_all(bind=engine)
   print('Tables:', sorted(Base.metadata.tables.keys()))
   "
输出应包含：addresses, users, verify_codes（以及原有的 cart_items, goods_sku 等）
```

---

## Task 3：公共 Schema + 用户/地址 Pydantic 模型

**预计时间**：30 分钟  
**依赖**：Task 2  
**完成标志**：`python -c "from schemas.user import LoginReq, UserOut; from schemas.address import AddressOut"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在需要创建 Pydantic v2 响应/请求模型。

【当前状态】
- backend/schemas.py 已存在（旧版，包含商品/购物车/订单的 schema，暂不修改）
- backend/schemas/ 目录不存在，需要新建

【任务】创建 backend/schemas/ 包（4 个文件）：

① backend/schemas/__init__.py — 空文件即可

② backend/schemas/common.py — 统一响应体
   from typing import Generic, TypeVar
   from pydantic import BaseModel

   T = TypeVar("T")

   class ApiResponse(BaseModel, Generic[T]):
       code: int = 0
       message: str = "ok"
       data: T | None = None

③ backend/schemas/user.py — 用户相关 Pydantic 模型（严格按以下规格）：

   SendCodeReq:
     phone: str    # 手机号，格式验证：11位数字，使用 @field_validator 校验

   LoginReq:
     phone: str
     code: str

   UserOut:    # 返回给前端的用户信息
     id: int
     phone: str
     nickname: str | None
     avatar_url: str | None
     role: str
     style_prefs: list | None
     occasion_prefs: list | None
     budget_pref: str | None
     model_config = ConfigDict(from_attributes=True)

   UpdateUserReq:   # 修改昵称/头像
     nickname: str | None = None
     avatar_url: str | None = None

   UpdatePrefsReq:  # 冷启动问卷 / AI 导购更新画像
     style_prefs: list[str] | None = None       # ["优雅复古","简约精致"]
     occasion_prefs: list[str] | None = None    # ["约会出行","日常通勤"]
     budget_pref: str | None = None             # "50-200"

   LoginOut:    # 登录成功返回
     token: str
     user: UserOut

④ backend/schemas/address.py — 收货地址 Pydantic 模型：

   AddressCreate:
     name: str
     phone: str
     province: str
     city: str
     district: str
     detail: str
     is_default: bool = False

   AddressUpdate:   # 所有字段可选，只更新传入的字段
     name: str | None = None
     phone: str | None = None
     province: str | None = None
     city: str | None = None
     district: str | None = None
     detail: str | None = None
     is_default: bool | None = None

   AddressOut:
     id: int
     user_id: int
     name: str
     phone: str
     province: str
     city: str
     district: str
     detail: str
     is_default: bool
     model_config = ConfigDict(from_attributes=True)

【手机号验证器示例】（在 SendCodeReq 中）：
   @field_validator("phone")
   @classmethod
   def phone_must_be_valid(cls, v: str) -> str:
       if not re.match(r"^1[3-9]\d{9}$", v):
           raise ValueError("手机号格式不正确")
       return v

【验证】运行：
   python -c "
   from schemas.common import ApiResponse
   from schemas.user import LoginReq, UserOut, SendCodeReq
   from schemas.address import AddressOut, AddressCreate
   print('SendCodeReq fields:', list(SendCodeReq.model_fields.keys()))
   print('UserOut fields:', list(UserOut.model_fields.keys()))
   print('AddressCreate fields:', list(AddressCreate.model_fields.keys()))
   "
```

---

## Task 4：JWT 工具函数 & 认证依赖注入

**预计时间**：30 分钟  
**依赖**：Task 1  
**完成标志**：`python -c "from core.security import create_access_token, verify_token; from core.deps import get_current_user"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现 JWT 工具和 FastAPI 依赖注入。

【依赖库】python-jose[cryptography]（已在 requirements.txt 中）

【任务】创建 backend/core/ 包（3 个文件）：

① backend/core/__init__.py — 空文件

② backend/core/security.py — JWT 工具函数：

   从 config 导入 settings（用 settings.JWT_SECRET 和 settings.JWT_EXPIRE_MINUTES）

   create_access_token(user_id: int) -> str:
     payload = {
       "sub": str(user_id),
       "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
     }
     使用 python-jose: jose.jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
     返回 token 字符串

   verify_token(token: str) -> int:
     使用 jose.jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
     返回 int(payload["sub"])
     若 token 无效/过期，捕获 JWTError 并抛出 BizError(2001, "Token 无效或已过期")

③ backend/core/deps.py — FastAPI 依赖函数：

   从 fastapi.security 导入 HTTPBearer, HTTPAuthorizationCredentials
   security = HTTPBearer(auto_error=False)

   get_current_user(
     credentials: HTTPAuthorizationCredentials | None = Depends(security),
     db: Session = Depends(get_db)
   ) -> User（models.user.User）:
     - 若 credentials 为 None，抛出 BizError(2001, "请先登录")
     - 调用 verify_token(credentials.credentials) 得到 user_id
     - db.get(User, user_id)，若无此用户，抛出 BizError(2001, "用户不存在")
     - 返回 User ORM 对象

   require_admin(
     current_user: User = Depends(get_current_user)
   ) -> User:
     - 若 current_user.role != "admin"，抛出 BizError(2003, "无管理员权限")
     - 返回 current_user

【验证】运行：
   python -c "
   from core.security import create_access_token, verify_token
   token = create_access_token(user_id=1)
   print('Token:', token[:30], '...')
   user_id = verify_token(token)
   print('Decoded user_id:', user_id)
   assert user_id == 1
   print('JWT 工具验证通过')
   "
```

---

## Task 5：验证码服务（生成 + mock 发送）

**预计时间**：30 分钟  
**依赖**：Task 2、Task 3  
**完成标志**：`python -c "from services.auth_service import AuthService"` 无报错；数据库中能查到写入的验证码

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现验证码服务（mock，不调真实短信接口）。

【当前状态】
- backend/models/verify_code.py 已存在（VerifyCode 模型）
- backend/database.py 已存在（get_db, engine）
- backend/config.py 已存在（BizError）

【任务】创建 backend/services/auth_service.py（包含验证码发送逻辑）：

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def send_code(self, phone: str) -> None:
        """
        生成 6 位随机数字验证码，写入 verify_codes 表，控制台打印（mock 发送）。
        同一手机号 1 分钟内不允许重复发送（防刷）。
        """
        步骤：
        1. 查询 verify_codes 表，找出该 phone 最近 1 分钟内 used=False 且 expired_at > now() 的记录。
           如果存在，抛出 BizError(2005, "发送太频繁，请 1 分钟后再试")
        
        2. 生成 6 位随机验证码：random.randint(100000, 999999) 转字符串
        
        3. 插入新 VerifyCode 记录：
           phone=phone, code=code,
           expired_at=datetime.utcnow() + timedelta(minutes=5),
           used=False
           db.add(record); db.commit()
        
        4. 控制台打印（模拟短信）：
           print(f"[MOCK SMS] 手机号 {phone} 的验证码为：{code}，5分钟内有效")

        注意：不要在此处验证手机号格式，格式验证已在 Pydantic Schema 层完成。

    def verify_code(self, phone: str, code: str) -> None:
        """
        校验验证码。成功则将 used 置为 True。失败抛 BizError。
        """
        步骤：
        1. 查询最近一条符合条件的记录：
           phone=phone, code=code, used=False, expired_at > datetime.utcnow()
           按 created_at DESC 排序，取第一条
        
        2. 若无记录：抛出 BizError(2002, "验证码错误或已过期")
        
        3. 将该记录的 used 置为 True，db.commit()

还需同时创建 backend/services/__init__.py（空文件）。

【验证】创建临时测试脚本 /tmp/test_send_code.py 并运行：
   from database import SessionLocal, engine, Base
   import models
   Base.metadata.create_all(bind=engine)
   from services.auth_service import AuthService
   db = SessionLocal()
   svc = AuthService(db)
   svc.send_code("13800138000")
   print("send_code 执行成功，查看控制台输出的验证码")
   db.close()
运行：python /tmp/test_send_code.py
预期：控制台打印 [MOCK SMS] ... 验证码 ...
```

---

## Task 6：发送验证码接口 POST /auth/send-code

**预计时间**：20 分钟  
**依赖**：Task 3、Task 5  
**完成标志**：`curl -X POST http://localhost:8000/api/v1/auth/send-code -H "Content-Type: application/json" -d '{"phone":"13800138000"}'` 返回 `{"code":0,"message":"ok","data":null}`

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现发送验证码的 HTTP 接口。

【当前状态】
- backend/services/auth_service.py 已存在（AuthService.send_code）
- backend/schemas/user.py 已存在（SendCodeReq）
- backend/schemas/common.py 已存在（ApiResponse）
- backend/config.py 已存在（BizError，已注册到 main.py 的 exception_handler）

【任务】创建 backend/routers/auth.py：

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/send-code", response_model=ApiResponse[None])
def send_code(req: SendCodeReq, db: Session = Depends(get_db)):
    AuthService(db).send_code(req.phone)
    return ApiResponse()    # code=0, message="ok", data=None

注意：
- 导入来源：from schemas.user import SendCodeReq; from schemas.common import ApiResponse
- from services.auth_service import AuthService
- from database import get_db
- 不要捕获 BizError，让全局 exception_handler 处理

【同时】更新 backend/main.py，在已有路由之后追加注册 auth.router：
   from routers import auth as auth_router
   app.include_router(auth_router.router, prefix="/api/v1")

【验证】
1. 启动服务：uvicorn main:app --reload --port 8000
2. 运行：
   curl -s -X POST http://localhost:8000/api/v1/auth/send-code \
     -H "Content-Type: application/json" \
     -d '{"phone":"13800138000"}' | python -m json.tool
   预期返回：{"code": 0, "message": "ok", "data": null}
   同时服务控制台打印验证码

3. 测试手机号格式校验（应返回 422 或 BizError）：
   curl -s -X POST http://localhost:8000/api/v1/auth/send-code \
     -H "Content-Type: application/json" \
     -d '{"phone":"12345"}' | python -m json.tool
```

---

## Task 7：登录服务 & 登录接口 POST /auth/login

**预计时间**：40 分钟  
**依赖**：Task 4、Task 5、Task 6  
**完成标志**：调用登录接口返回包含 `token` 的 JSON，token 可被 `verify_token` 解码

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现登录逻辑（手机号+验证码，首次登录自动注册）。

【当前状态】
- AuthService.send_code / verify_code 已实现
- core/security.py 的 create_access_token 已实现
- schemas/user.py 的 LoginReq, UserOut, LoginOut 已定义
- models/user.py 的 User 模型已存在

【任务一】在 backend/services/auth_service.py 的 AuthService 类中追加 login 方法：

    def login(self, phone: str, code: str) -> tuple[str, User]:
        """
        1. 调用 self.verify_code(phone, code)（内部已抛出 BizError）
        2. 查询 User 表，按 phone 查找
        3. 若用户不存在，自动创建（首次登录即注册）：
           new_user = User(phone=phone, role="user")
           self.db.add(new_user); self.db.commit(); self.db.refresh(new_user)
        4. 调用 create_access_token(user.id) 生成 token
        5. 返回 (token, user)
        """
        from core.security import create_access_token  # 避免循环导入，在函数内导入

【任务二】在 backend/routers/auth.py 追加登录接口：

@router.post("/login", response_model=ApiResponse[LoginOut])
def login(req: LoginReq, db: Session = Depends(get_db)):
    token, user = AuthService(db).login(req.phone, req.code)
    return ApiResponse(data=LoginOut(token=token, user=UserOut.model_validate(user)))

【验证】完整流程测试（在服务启动的情况下）：

步骤1 — 发送验证码，记录控制台打印的 6 位 code：
   curl -s -X POST http://localhost:8000/api/v1/auth/send-code \
     -H "Content-Type: application/json" \
     -d '{"phone":"13900139000"}' | python -m json.tool

步骤2 — 用获得的 code 登录（替换 CODE 为实际值）：
   curl -s -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"phone":"13900139000","code":"CODE"}' | python -m json.tool

预期返回：
{
  "code": 0,
  "message": "ok",
  "data": {
    "token": "eyJ...",
    "user": {"id": 1, "phone": "13900139000", "role": "user", ...}
  }
}

步骤3 — 测试错误码（验证码错误）：
   curl -s -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"phone":"13900139000","code":"000000"}' | python -m json.tool
预期：{"code": 2002, "message": "验证码错误或已过期", "data": null}
```

---

## Task 8：用户信息接口 GET/PUT /user/me

**预计时间**：30 分钟  
**依赖**：Task 7  
**完成标志**：携带有效 JWT 调用 `/user/me` 返回用户信息，PUT 更新昵称后再 GET 能看到新值

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现用户信息的读取和修改接口。

【当前状态】
- core/deps.py 的 get_current_user 已实现（返回 User ORM 对象）
- schemas/user.py 的 UserOut, UpdateUserReq 已定义

【任务一】创建 backend/services/user_service.py：

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_me(self, user: User) -> User:
        return user    # 直接返回，路由层转为 UserOut

    def update_me(self, user: User, req: UpdateUserReq) -> User:
        """
        只更新 req 中非 None 的字段（nickname, avatar_url）。
        model_dump(exclude_none=True) 可用于获取非 None 字段。
        db.commit(); db.refresh(user)
        返回更新后的 user
        """
        update_data = req.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

【任务二】创建 backend/routers/user.py：

router = APIRouter(prefix="/user", tags=["用户"])

@router.get("/me", response_model=ApiResponse[UserOut])
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ApiResponse(data=UserOut.model_validate(current_user))

@router.put("/me", response_model=ApiResponse[UserOut])
def update_me(
    req: UpdateUserReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService(db).update_me(current_user, req)
    return ApiResponse(data=UserOut.model_validate(user))

【同时】在 backend/main.py 注册 user.router：
   from routers import user as user_router
   app.include_router(user_router.router, prefix="/api/v1")

【验证】先完成 Task 7 得到 TOKEN，然后：

获取用户信息：
   curl -s http://localhost:8000/api/v1/user/me \
     -H "Authorization: Bearer TOKEN" | python -m json.tool

更新昵称：
   curl -s -X PUT http://localhost:8000/api/v1/user/me \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"nickname":"小雯"}' | python -m json.tool
预期：返回的 user.nickname 为 "小雯"

无 Token 访问（验证鉴权）：
   curl -s http://localhost:8000/api/v1/user/me | python -m json.tool
预期：{"code": 2001, "message": "请先登录", "data": null}
```

---

## Task 9：冷启动问卷接口 PATCH /user/prefs

**预计时间**：20 分钟  
**依赖**：Task 8  
**完成标志**：更新偏好后 `GET /user/me` 返回的 `style_prefs` 已变更

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现冷启动问卷（风格/场合/预算偏好）的更新接口。

【当前状态】
- backend/services/user_service.py 已存在（UserService 类）
- backend/routers/user.py 已存在（已有 GET/PUT /user/me）
- schemas/user.py 的 UpdatePrefsReq 已定义

【任务一】在 UserService 追加 update_prefs 方法：

    def update_prefs(self, user: User, req: UpdatePrefsReq) -> User:
        """
        更新用户画像偏好字段（style_prefs / occasion_prefs / budget_pref）。
        只更新 req 中非 None 的字段（允许部分更新）。
        db.commit(); db.refresh(user); 返回 user
        """

【任务二】在 backend/routers/user.py 追加：

@router.patch("/prefs", response_model=ApiResponse[UserOut])
def update_prefs(
    req: UpdatePrefsReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService(db).update_prefs(current_user, req)
    return ApiResponse(data=UserOut.model_validate(user))

【验证】
更新偏好：
   curl -s -X PATCH http://localhost:8000/api/v1/user/prefs \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"style_prefs":["优雅复古","简约精致"],"occasion_prefs":["约会出行"],"budget_pref":"50-200"}' \
     | python -m json.tool
预期：返回 user 中 style_prefs=["优雅复古","简约精致"]

只更新部分字段（其余不变）：
   curl -s -X PATCH http://localhost:8000/api/v1/user/prefs \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"budget_pref":"200-500"}' | python -m json.tool
预期：budget_pref 变为 "200-500"，style_prefs 仍为上一步设置的值
```

---

## Task 10：收货地址服务（CRUD + 默认地址逻辑）

**预计时间**：40 分钟  
**依赖**：Task 7  
**完成标志**：单元测试验证增删改查和默认地址切换逻辑

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现收货地址的业务逻辑层。

【当前状态】
- backend/models/address.py 已存在（Address 模型）
- backend/schemas/address.py 已存在（AddressCreate, AddressUpdate, AddressOut）
- backend/config.py 的 BizError 已存在

【任务】在 backend/services/ 创建 address_service.py：

class AddressService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def list(self) -> list[Address]:
        """返回当前用户所有地址，is_default=True 的排在最前"""
        return (
            self.db.query(Address)
            .filter(Address.user_id == self.user_id)
            .order_by(Address.is_default.desc(), Address.created_at.asc())
            .all()
        )

    def create(self, req: AddressCreate) -> Address:
        """
        新增地址。
        业务规则：每个用户最多 5 条地址，超出抛出 BizError(1102, "最多保存5个收货地址")。
        若 req.is_default=True 或这是该用户的第一条地址，调用 _set_all_non_default() 后再设置新地址 is_default=True。
        """

    def update(self, address_id: int, req: AddressUpdate) -> Address:
        """
        更新地址。先验证地址属于当前用户（否则 BizError(1103, "地址不存在")）。
        若 req.is_default=True，先清除其他默认地址。
        只更新非 None 字段。
        """

    def delete(self, address_id: int) -> None:
        """
        删除地址。验证归属。
        若删除的是默认地址，自动将 created_at 最新的其他地址设为默认（若还有其他地址）。
        """

    def set_default(self, address_id: int) -> Address:
        """将指定地址设为默认，清除同用户其他地址的 is_default。"""
        addr = self._get_or_403(address_id)
        self._set_all_non_default()
        addr.is_default = True
        self.db.commit()
        self.db.refresh(addr)
        return addr

    def _get_or_403(self, address_id: int) -> Address:
        addr = self.db.get(Address, address_id)
        if not addr or addr.user_id != self.user_id:
            raise BizError(1103, "地址不存在")
        return addr

    def _set_all_non_default(self) -> None:
        """将该用户所有地址的 is_default 置为 False（批量更新）"""
        self.db.query(Address).filter(Address.user_id == self.user_id).update(
            {"is_default": False}
        )

【验证】创建 /tmp/test_address.py 并运行：
   from database import SessionLocal, engine, Base
   import models
   Base.metadata.create_all(bind=engine)
   from services.auth_service import AuthService
   from services.address_service import AddressService
   from schemas.address import AddressCreate, AddressUpdate

   db = SessionLocal()
   # 先确保用户存在（user_id=1 来自之前的登录测试）
   svc = AddressService(db, user_id=1)
   addr = svc.create(AddressCreate(
       name="张晓雯", phone="13800138000",
       province="浙江省", city="杭州市", district="西湖区",
       detail="文一西路 xxx 号", is_default=True
   ))
   print("新增地址 id:", addr.id, "is_default:", addr.is_default)
   addrs = svc.list()
   print("地址列表数量:", len(addrs))
   db.close()
运行：python /tmp/test_address.py
```

---

## Task 11：收货地址 HTTP 接口

**预计时间**：30 分钟  
**依赖**：Task 9（user.router 已建）、Task 10  
**完成标志**：5 个地址接口均可通过 curl 调用并返回正确结果

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在在已有的 backend/routers/user.py 中追加收货地址的 5 个接口。

【当前状态】
- backend/routers/user.py 已存在（已有 GET/PUT /user/me 和 PATCH /user/prefs）
- backend/services/address_service.py 已存在（AddressService 类）
- backend/schemas/address.py 已存在（AddressCreate, AddressUpdate, AddressOut）

【任务】在 backend/routers/user.py 末尾追加以下 5 个接口（前缀已是 /user）：

GET    /user/address          — 获取地址列表
POST   /user/address          — 新增地址
PUT    /user/address/{id}     — 修改地址
DELETE /user/address/{id}     — 删除地址
PATCH  /user/address/{id}/default  — 设为默认

路由实现模板：
@router.get("/address", response_model=ApiResponse[list[AddressOut]])
def list_address(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    addrs = AddressService(db, current_user.id).list()
    return ApiResponse(data=[AddressOut.model_validate(a) for a in addrs])

@router.post("/address", response_model=ApiResponse[AddressOut])
def create_address(req: AddressCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    addr = AddressService(db, current_user.id).create(req)
    return ApiResponse(data=AddressOut.model_validate(addr))

# PUT, DELETE, PATCH /default 按同样模式实现，调用对应 Service 方法

【验证】（TOKEN 来自 Task 7）

新增地址：
   curl -s -X POST http://localhost:8000/api/v1/user/address \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"张晓雯","phone":"13800138000","province":"浙江省","city":"杭州市","district":"西湖区","detail":"文一西路 1 号","is_default":true}' \
     | python -m json.tool

获取地址列表：
   curl -s http://localhost:8000/api/v1/user/address \
     -H "Authorization: Bearer TOKEN" | python -m json.tool

修改地址（替换 ADDR_ID 为实际 id）：
   curl -s -X PUT http://localhost:8000/api/v1/user/address/ADDR_ID \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"detail":"文三路 2 号"}' | python -m json.tool

删除地址：
   curl -s -X DELETE http://localhost:8000/api/v1/user/address/ADDR_ID \
     -H "Authorization: Bearer TOKEN" | python -m json.tool

删除后获取列表验证数量变化：
   curl -s http://localhost:8000/api/v1/user/address \
     -H "Authorization: Bearer TOKEN" | python -m json.tool
```

---

## Task 12：注册路由 & 全流程冒烟测试

**预计时间**：30 分钟  
**依赖**：全部前序任务  
**完成标志**：从发验证码到修改地址的完整链路全部返回 `code:0`，服务日志无 error

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在完成用户模块的收尾工作：统一注册路由并执行全流程验收。

【任务一】检查并更新 backend/main.py，确保以下路由全部注册（已注册的跳过，不重复）：
   from routers import auth as auth_router
   from routers import user as user_router
   app.include_router(auth_router.router, prefix="/api/v1")
   app.include_router(user_router.router, prefix="/api/v1")

   同时确认 BizError 全局异常处理器已注册（参见 Task 1）。

【任务二】更新 backend/requirements.txt，确保包含以下条目（版本号已在 Task 1 确认）：
   python-jose[cryptography]
   passlib[bcrypt]
   pydantic-settings
   PyMySQL
   python-multipart
   Pillow

【任务三】创建 backend/scripts/smoke_test_user.sh，内容为完整的 bash 测试脚本：

#!/usr/bin/env bash
# 用户模块冒烟测试 — 需先启动服务 uvicorn main:app --reload --port 8000
set -e
BASE="http://localhost:8000/api/v1"
PHONE="13700000001"

echo "=== [1] 发送验证码 ==="
curl -s -X POST "$BASE/auth/send-code" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$PHONE\"}" | python -m json.tool

echo ""
echo "请从上方控制台复制验证码，输入后按回车："
read -r CODE

echo "=== [2] 登录（首次自动注册）==="
LOGIN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$PHONE\",\"code\":\"$CODE\"}")
echo "$LOGIN" | python -m json.tool
TOKEN=$(echo "$LOGIN" | python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

echo "=== [3] 获取用户信息 ==="
curl -s "$BASE/user/me" -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "=== [4] 更新昵称 ==="
curl -s -X PUT "$BASE/user/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname":"测试用户"}' | python -m json.tool

echo "=== [5] 更新偏好 ==="
curl -s -X PATCH "$BASE/user/prefs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"style_prefs":["优雅复古"],"occasion_prefs":["约会出行"],"budget_pref":"50-200"}' \
  | python -m json.tool

echo "=== [6] 新增收货地址 ==="
ADDR=$(curl -s -X POST "$BASE/user/address" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","phone":"13800138000","province":"广东省","city":"深圳市","district":"南山区","detail":"科技园 1 号","is_default":true}')
echo "$ADDR" | python -m json.tool
ADDR_ID=$(echo "$ADDR" | python -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")

echo "=== [7] 获取地址列表 ==="
curl -s "$BASE/user/address" -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "=== [8] 修改地址 ==="
curl -s -X PUT "$BASE/user/address/$ADDR_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"detail":"科技园 2 号"}' | python -m json.tool

echo "=== [9] 无 Token 访问（验证鉴权拦截）==="
curl -s "$BASE/user/me" | python -m json.tool

echo ""
echo "✓ 全部冒烟测试通过！用户模块开发完成。"

【执行验收】
1. 启动服务：uvicorn main:app --reload --port 8000
2. 另开终端运行：bash backend/scripts/smoke_test_user.sh
3. 检查每步返回的 code 均为 0，最后一步（无 Token）返回 code=2001
4. 在 http://localhost:8000/docs 确认 /auth 和 /user 分组的接口均已显示
```

---

## 附录：文件变更清单

完成全部 12 个 Task 后，用户模块新增/修改的文件：

```
backend/
├── config.py                    ← 新建（Task 1）
├── .env.example                 ← 新建（Task 1）
├── requirements.txt             ← 修改（Task 1、12）
├── main.py                      ← 修改（Task 1、6、8、12）
│
├── models/
│   ├── user.py                  ← 新建（Task 2）
│   ├── verify_code.py           ← 新建（Task 2）
│   ├── address.py               ← 新建（Task 2）
│   └── __init__.py              ← 修改（Task 2）
│
├── schemas/
│   ├── __init__.py              ← 新建（Task 3）
│   ├── common.py                ← 新建（Task 3）
│   ├── user.py                  ← 新建（Task 3）
│   └── address.py               ← 新建（Task 3）
│
├── core/
│   ├── __init__.py              ← 新建（Task 4）
│   ├── security.py              ← 新建（Task 4）
│   └── deps.py                  ← 新建（Task 4）
│
├── services/
│   ├── __init__.py              ← 新建（Task 5）
│   ├── auth_service.py          ← 新建（Task 5、7）
│   ├── user_service.py          ← 新建（Task 8、9）
│   └── address_service.py       ← 新建（Task 10）
│
├── routers/
│   ├── auth.py                  ← 新建（Task 6、7）
│   └── user.py                  ← 新建（Task 8、9、11）
│
└── scripts/
    └── smoke_test_user.sh       ← 新建（Task 12）
```
