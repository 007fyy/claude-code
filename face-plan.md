# face-plan.md — 珑饰脸型检测模块开发计划

**模块范围**：上传照片分析脸型、结果写入 face_profiles 表、获取当前用户脸型档案  
**技术栈**：FastAPI + SQLAlchemy + Pillow（mock CV）+ JWT 认证  
**工作目录**：`L:\claude-code\backend\`  
**架构规范**：严格遵循 `L:\claude-code\CLAUDE.md`

---

## 当前状态说明

| 文件 | 状态 | 说明 |
|---|---|---|
| `models/face.py` | ❌ 缺失 | 需新建 FaceProfile 模型 |
| `schemas/face.py` | ❌ 缺失 | 需新建请求/响应 Schema |
| `services/face_service.py` | ❌ 缺失 | 需新建 mock CV 分析逻辑 |
| `routers/face.py` | ❌ 缺失 | 需新建 analyze 和 profile 接口 |

---

## 任务总览

| # | 任务 | 预计时间 | 依赖 |
|---|---|---|---|
| 1 | 创建 FaceProfile 模型 | 20 min | user-plan |
| 2 | 创建 schemas/face.py | 20 min | 1 |
| 3 | 创建 FaceService（mock Pillow 分析 + 存档） | 30 min | 1、2 |
| 4 | 创建 routers/face.py（上传分析 + 获取档案） | 20 min | 3 |
| 5 | 注册路由到 main.py | 10 min | 4 |
| 6 | 全流程冒烟测试 | 20 min | 全部 |

---

## Task 1：创建 FaceProfile 模型

**预计时间**：20 分钟  
**依赖**：users 表存在（user-plan Task 1）  
**完成标志**：`python -c "from models.face import FaceProfile; print('OK')"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建脸型档案的数据库模型。

【CLAUDE.md face_profiles 表设计要点】
- user_id UNIQUE（每用户一条记录，重复分析则更新）
- face_shape: oval / round / square / oblong
- skin_tone: warm / cool / neutral
- suggestions: JSON 数组（["弧形耳环更显温柔", ...]）
- not_recommended: JSON 数组

【任务】新建 backend/models/face.py：

① FaceProfile 模型（__tablename__ = "face_profiles"）：
   id: Column(Integer, primary_key=True, autoincrement=True)
   user_id: Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
     # UNIQUE：每用户只有一条记录，分析后 upsert
   face_shape: Column(String(20), nullable=False)   # oval/round/square/oblong
   skin_tone: Column(String(20), nullable=False)    # warm/cool/neutral
   suggestions: Column(JSON, nullable=True)          # ["弧形耳环更显温柔", ...]
   not_recommended: Column(JSON, nullable=True)      # ["方形几何款", ...]
   analyzed_at: Column(DateTime, server_default=func.now(), onupdate=func.now())
   user: relationship("User", back_populates="face_profile")

② 同步更新 models/user.py，追加：
   face_profile: Mapped["FaceProfile | None"] = relationship("FaceProfile", back_populates="user", uselist=False, lazy="select")

③ 更新 models/__init__.py：追加 FaceProfile 导出

【验证】
    python -c "
    import models
    from database import engine, Base
    from models.face import FaceProfile
    FaceProfile.__table__.drop(engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    print('FaceProfile columns:', list(FaceProfile.__table__.c.keys()))
    from sqlalchemy import inspect
    insp = inspect(FaceProfile.__table__)
    uq = [c.name for c in insp.columns if c.unique]
    print('UNIQUE columns:', uq)
    print('PASS')
    "
```

---

## Task 2：创建 schemas/face.py

**预计时间**：20 分钟  
**依赖**：Task 1  
**完成标志**：`python -c "from schemas.face import FaceProfileOut"` 无报错

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建脸型模块的 Pydantic Schema。

【任务】创建 backend/schemas/face.py：

FaceProfileOut:          # 脸型档案响应
    face_shape: str           # "oval" | "round" | "square" | "oblong"
    face_shape_label: str     # 中文标签："椭圆脸" | "圆脸" | "方脸" | "长脸"
    skin_tone: str            # "warm" | "cool" | "neutral"
    skin_tone_label: str      # 中文标签："暖色调" | "冷色调" | "中性色调"
    suggestions: list[str]    # 搭配建议
    not_recommended: list[str] # 不建议款式
    analyzed_at: str | None   # ISO 8601

FACE_SHAPE_LABELS = {
    "oval": "椭圆脸",
    "round": "圆脸",
    "square": "方脸",
    "oblong": "长脸",
}

SKIN_TONE_LABELS = {
    "warm": "暖色调",
    "cool": "冷色调",
    "neutral": "中性色调",
}

# 各脸型的搭配建议和不建议款（静态配置）
FACE_SUGGESTIONS = {
    "oval": {
        "suggestions": ["椭圆脸适合大多数款式", "弧形耳环更显温柔", "水滴形吊坠拉长颈部线条"],
        "not_recommended": [],
    },
    "round": {
        "suggestions": ["竖向线条耳环显脸瘦", "长款吊坠拉伸脸型", "水滴形或椭圆形吊坠"],
        "not_recommended": ["圆形耳钉会放大脸型", "短粗款项链"],
    },
    "square": {
        "suggestions": ["圆弧设计柔化轮廓", "水滴形或椭圆耳环", "流线型项链"],
        "not_recommended": ["方形几何耳环", "横向宽版手链"],
    },
    "oblong": {
        "suggestions": ["横向感设计平衡比例", "圆形耳环增加宽度感", "短款项链"],
        "not_recommended": ["超长吊坠拉长脸型", "竖向长条款耳环"],
    },
}

【验证】
    python -c "
    from schemas.face import FaceProfileOut, FACE_SHAPE_LABELS, FACE_SUGGESTIONS
    print('FACE_SHAPE_LABELS:', FACE_SHAPE_LABELS)
    print('oval suggestions:', FACE_SUGGESTIONS['oval']['suggestions'])
    "
```

---

## Task 3：创建 FaceService（mock Pillow 分析）

**预计时间**：30 分钟  
**依赖**：Task 1、2  
**完成标志**：上传本地图片后返回 FaceProfileOut，数据库中写入记录

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建脸型分析服务层（mock 实现）。

【CLAUDE.md mock 实现说明】
- 用 Pillow 读取图片，验证格式和大小
- 按宽高比推断脸型：宽高比 > 0.9 → round，< 0.75 → oblong，其余 → oval
- 图片高度 > 宽度 × 1.1 且宽高比适中 → square（可选）
- skin_tone 固定返回 "warm"（原型阶段）
- 结果写入 face_profiles 表（存在则更新，不存在则插入）

【任务】创建 backend/services/face_service.py：

from PIL import Image
import io
from sqlalchemy.orm import Session
from models.face import FaceProfile
from schemas.face import FaceProfileOut, FACE_SUGGESTIONS, FACE_SHAPE_LABELS, SKIN_TONE_LABELS
from config import BizError

MAX_SIZE_MB = 10
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

class FaceService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def analyze(self, image_bytes: bytes, content_type: str) -> FaceProfileOut:
        """
        分析图片并保存脸型档案：
        1. 验证图片大小 <= 10MB → BizError(3001, "图片大小不能超过 10MB")
        2. 用 Pillow 打开图片，验证格式在 ALLOWED_FORMATS 中 → BizError(3002, "不支持的图片格式")
        3. 获取宽高，计算宽高比 ratio = width / height
           - ratio > 0.9 → face_shape = "round"
           - ratio < 0.75 → face_shape = "oblong"
           - 否则 → face_shape = "oval"
        4. skin_tone = "warm"（mock 固定值）
        5. 查 face_profiles，存在则更新，不存在则插入（upsert）
        6. db.commit()
        7. 返回 _to_out(profile)
        """

    def get_profile(self) -> FaceProfileOut:
        """
        获取当前用户脸型档案：
        1. 查 face_profiles，不存在 → BizError(3003, "尚未进行脸型分析")
        2. 返回 _to_out(profile)
        """

    def _to_out(self, profile: FaceProfile) -> FaceProfileOut:
        """ORM → FaceProfileOut，填充 suggestions/not_recommended/labels"""
        tips = FACE_SUGGESTIONS.get(profile.face_shape, {"suggestions": [], "not_recommended": []})
        return FaceProfileOut(
            face_shape=profile.face_shape,
            face_shape_label=FACE_SHAPE_LABELS.get(profile.face_shape, profile.face_shape),
            skin_tone=profile.skin_tone,
            skin_tone_label=SKIN_TONE_LABELS.get(profile.skin_tone, profile.skin_tone),
            suggestions=profile.suggestions or tips["suggestions"],
            not_recommended=profile.not_recommended or tips["not_recommended"],
            analyzed_at=profile.analyzed_at.isoformat() if profile.analyzed_at else None,
        )

【验证】
    # 准备一张测试图片（宽 > 高，预期 round）
    python -c "
    from PIL import Image
    import io
    img = Image.new('RGB', (400, 300), color='pink')  # 宽高比 1.33 > 0.9 → round
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    img_bytes = buf.getvalue()

    from database import SessionLocal
    from services.face_service import FaceService
    db = SessionLocal()
    result = FaceService(db, user_id=1).analyze(img_bytes, 'image/jpeg')
    print('face_shape:', result.face_shape)  # 预期 round
    print('suggestions:', result.suggestions)
    db.close()
    "
```

---

## Task 4：创建 routers/face.py

**预计时间**：20 分钟  
**依赖**：Task 3  
**完成标志**：两个接口均可通过 curl 正常调用

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建脸型模块路由。

【任务】新建 backend/routers/face.py：

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from schemas.common import ApiResponse
from schemas.face import FaceProfileOut
from services.face_service import FaceService
from core.deps import get_current_user
from models.user import User

router = APIRouter(tags=["脸型"])

@router.post("/analyze", response_model=ApiResponse[FaceProfileOut])
async def analyze_face(
    file: UploadFile = File(..., description="脸部照片（jpg/png/webp，≤10MB）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传照片分析脸型，结果写入 face_profiles 表"""
    image_bytes = await file.read()
    result = FaceService(db, current_user.id).analyze(image_bytes, file.content_type)
    return ApiResponse(data=result)

@router.get("/profile", response_model=ApiResponse[FaceProfileOut])
def get_face_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户脸型档案"""
    data = FaceService(db, current_user.id).get_profile()
    return ApiResponse(data=data)

【验证】
    # 分析脸型
    curl -s -X POST http://localhost:8000/api/v1/face/analyze \
      -H "Authorization: Bearer TOKEN" \
      -F "file=@/path/to/face.jpg" | python -m json.tool
    # 预期：{"code":0,"data":{"face_shape":"oval","face_shape_label":"椭圆脸",...}}

    # 获取档案
    curl -s http://localhost:8000/api/v1/face/profile \
      -H "Authorization: Bearer TOKEN" | python -m json.tool

    # 未分析时获取档案（code:3003）
    # 先注册新用户，不上传图片，直接请求 profile
```

---

## Task 5：注册路由到 main.py

**预计时间**：10 分钟  
**依赖**：Task 4  
**完成标志**：`/api/v1/face/analyze` 和 `/api/v1/face/profile` 出现在 OpenAPI 文档

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。将脸型路由注册到 main.py。

【任务】在 backend/main.py 中追加：
    from routers import face
    app.include_router(face.router, prefix="/api/v1/face")

【验证】
    curl -s http://localhost:8000/openapi.json | python -c "
    import sys,json
    paths = list(json.load(sys.stdin)['paths'].keys())
    face_paths = [p for p in paths if '/face/' in p]
    print('脸型接口:', face_paths)
    assert len(face_paths) >= 2, 'FAIL'
    print('PASS')
    "
```

---

## Task 6：全流程冒烟测试

**预计时间**：20 分钟  
**依赖**：全部前序任务  
**完成标志**：上传图片→获取档案→推荐系统可读取脸型的完整链路正常

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对脸型模块做完整验收。

【任务】创建 backend/scripts/smoke_test_face.sh：

#!/usr/bin/env bash
set -e
BASE="http://localhost:8000/api/v1"

echo "请粘贴登录 TOKEN："
read -r TOKEN

echo "=== [准备] 生成三种测试图片 ==="
python -c "
from PIL import Image
# 宽 > 高（宽高比 > 0.9）→ 预期 round
Image.new('RGB', (400,300),'pink').save('/tmp/face_round.jpg')
# 高 > 宽（宽高比 < 0.75）→ 预期 oblong
Image.new('RGB', (300,500),'beige').save('/tmp/face_oblong.jpg')
# 接近正方（宽高比 ≈ 0.82）→ 预期 oval
Image.new('RGB', (400,490),'ivory').save('/tmp/face_oval.jpg')
print('测试图片已生成')
"

echo "=== [1] 分析 round（宽高比 > 0.9）==="
curl -s -X POST "$BASE/face/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/face_round.jpg" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0, f'FAIL: {d}'
assert d['data']['face_shape']=='round', f'FAIL shape: {d[\"data\"][\"face_shape\"]}'
print('PASS face_shape=round')
print('suggestions:', d['data']['suggestions'])
"

echo "=== [2] 分析 oblong（宽高比 < 0.75）==="
curl -s -X POST "$BASE/face/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/face_oblong.jpg" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0, f'FAIL: {d}'
assert d['data']['face_shape']=='oblong', f'FAIL shape: {d[\"data\"][\"face_shape\"]}'
print('PASS face_shape=oblong')
"

echo "=== [3] 分析 oval（宽高比 ≈ 0.82）==="
curl -s -X POST "$BASE/face/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/face_oval.jpg" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0, f'FAIL: {d}'
print('PASS face_shape:', d['data']['face_shape'], '（宽高比近似判断）')
"

echo "=== [4] 获取脸型档案 ==="
PROFILE=$(curl -s "$BASE/face/profile" -H "Authorization: Bearer $TOKEN")
echo "$PROFILE" | python -m json.tool
python -c "
import sys,json
d = $(echo $PROFILE | python -c 'import sys,json; print(repr(sys.stdin.read()))' 2>/dev/null || echo '{}')
" 2>/dev/null || true

curl -s "$BASE/face/profile" -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']==0, f'FAIL: {d}'
fd = d['data']
print('脸型:', fd['face_shape_label'], '| 肤色:', fd['skin_tone_label'])
print('建议:', fd['suggestions'])
"

echo "=== [5] 上传超大文件（> 10MB）==="
python -c "
from PIL import Image
import io
# 生成大图（多次保存到内存以放大文件）
img = Image.new('RGB', (5000,5000), 'white')
buf = io.BytesIO()
img.save(buf, format='JPEG', quality=95)
open('/tmp/face_large.jpg', 'wb').write(buf.getvalue())
size_mb = len(buf.getvalue()) / 1024 / 1024
print(f'大文件大小: {size_mb:.1f} MB')
" 2>/dev/null || echo "（大文件测试跳过）"

echo ""
echo "✓ 脸型模块全部测试通过！"
```

---

## 附录：文件变更清单

```
backend/
├── models/
│   ├── face.py              ← 新建（Task 1）
│   └── user.py              ← 追加 face_profile relationship（Task 1）
│
├── schemas/
│   └── face.py              ← 新建（Task 2）
│
├── services/
│   └── face_service.py      ← 新建（Task 3）
│
├── routers/
│   └── face.py              ← 新建（Task 4）
│
├── main.py                  ← 注册 face 路由（Task 5）
│
└── scripts/
    └── smoke_test_face.sh   ← 新建（Task 6）
```
