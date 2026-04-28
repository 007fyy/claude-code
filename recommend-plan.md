# recommend-plan.md — 珑饰推荐引擎模块开发计划

**模块范围**：基于规则的个性化商品推荐（脸型匹配 + 偏好标签 + 算法反馈权重 + 预算过滤）  
**技术栈**：FastAPI + SQLAlchemy + JWT 认证  
**工作目录**：`L:\claude-code\backend\`  
**架构规范**：严格遵循 `L:\claude-code\CLAUDE.md`

---

## 当前状态说明

| 文件 | 状态 | 说明 |
|---|---|---|
| `schemas/recommend.py` | ❌ 缺失 | 需新建 |
| `services/recommend_service.py` | ❌ 缺失 | 需新建评分引擎 |
| `routers/recommend.py` | ❌ 缺失 | 需新建 GET /list 接口 |

---

## 任务总览

| # | 任务 | 预计时间 | 依赖 |
|---|---|---|---|
| 1 | 实现评分引擎核心逻辑 | 40 min | goods-plan、face-plan、user-plan |
| 2 | 创建 RecommendService（冷启动处理 + 分页） | 30 min | 1 |
| 3 | 创建 routers/recommend.py | 15 min | 2 |
| 4 | 注册路由到 main.py | 10 min | 3 |
| 5 | 全流程冒烟测试 | 20 min | 全部 |

---

## Task 1：实现评分引擎核心逻辑

**预计时间**：40 分钟  
**依赖**：goods_spu 表存在、face_profiles 表存在、users 表存在  
**完成标志**：给定 spu 列表和用户画像，评分函数输出正确排序

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在实现推荐评分引擎。

【CLAUDE.md 推荐评分规则（规则引擎，非 ML）】

score = spu.sort_weight
      + (20 if user.face_shape in spu.target_face_shapes else 0)
      + spu.face_weight_penalty.get(user.face_shape, 0)   # 可为负数
      + sum(10 for tag in spu.occasion_tags if tag in user.occasion_prefs)
      + sum(10 for tag in spu.style_tags    if tag in user.style_prefs)
      # 预算不匹配则整体排除

预算过滤规则（user.budget_pref 格式为 "50-200"，代表最低 SKU 价格在此范围）：
- budget_pref == None：不过滤
- 解析为 min_budget, max_budget
- spu 下所有 SKU 的最低价 price_min：price_min < min_budget 或 price_min > max_budget → 排除该 spu

冷启动：用户无脸型档案或无偏好时，score = sort_weight，按默认排序返回。

【任务】创建 backend/services/recommend_service.py：

from sqlalchemy.orm import Session
from models.goods import GoodsSpu, GoodsSku
from models.face import FaceProfile
from models.user import User
from schemas.goods import GoodsListItem  # 复用商品列表 Schema（已在 goods-plan 中创建）
from config import BizError

# 预算字符串解析
def _parse_budget(budget_pref: str | None) -> tuple[float, float] | None:
    """解析 "50-200" → (50.0, 200.0)，解析失败返回 None"""
    ...

# 单个 SPU 评分
def _score_spu(
    spu: GoodsSpu,
    face_shape: str | None,
    style_prefs: list | None,
    occasion_prefs: list | None,
) -> int:
    """
    计算 spu 的推荐得分：
    score = spu.sort_weight
           + (20 if face_shape and face_shape in (spu.target_face_shapes or []) else 0)
           + (spu.face_weight_penalty or {}).get(face_shape, 0)
           + sum(10 for t in (spu.occasion_tags or []) if t in (occasion_prefs or []))
           + sum(10 for t in (spu.style_tags or []) if t in (style_prefs or []))
    """
    ...

# 预算过滤
def _passes_budget(spu: GoodsSpu, budget: tuple[float, float] | None) -> bool:
    """
    检查 spu 是否通过预算过滤：
    - budget 为 None → 直接通过
    - spu.skus 的最低价在 [min_budget, max_budget] 之间 → 通过
    - 否则过滤掉
    """
    ...

【验证】
    python -c "
    from services.recommend_service import _score_spu, _parse_budget

    # 测试评分
    class MockSpu:
        sort_weight = 100
        target_face_shapes = ['oval', 'oblong']
        face_weight_penalty = {'oval': -5}
        style_tags = ['优雅复古', '简约精致']
        occasion_tags = ['约会出行']

    score = _score_spu(
        MockSpu(),
        face_shape='oval',
        style_prefs=['优雅复古', '法式轻奢'],
        occasion_prefs=['约会出行', '日常通勤']
    )
    # 预期：100 + 20 + (-5) + 10 + 10 = 135
    print('score:', score)
    assert score == 135, f'FAIL: {score}'

    # 测试预算解析
    assert _parse_budget('50-200') == (50.0, 200.0)
    assert _parse_budget(None) is None
    print('PASS')
    "
```

---

## Task 2：创建 RecommendService（含冷启动和分页）

**预计时间**：30 分钟  
**依赖**：Task 1  
**完成标志**：调用 service.recommend() 返回带评分排序的商品列表

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。在 recommend_service.py 中实现完整的推荐服务类。

【任务】在 backend/services/recommend_service.py 中补充：

class RecommendService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def recommend(
        self,
        category: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        个性化推荐：
        1. 查询当前用户（获取 style_prefs、occasion_prefs、budget_pref）
        2. 查询 face_profiles（获取 face_shape）
           找不到 → 冷启动：face_shape=None（评分只用 sort_weight）
        3. 查询所有 status="on" 的 GoodsSpu（eager load skus）
           若 category 不为 None，则加 WHERE category=category
        4. 预算过滤：_passes_budget(spu, budget)
        5. 评分排序：sorted(spus, key=lambda s: _score_spu(...), reverse=True)
        6. 分页切片：result = scored[offset:offset+page_size]
        7. 构建响应：
           {
             "total": len(scored),
             "page": page,
             "page_size": page_size,
             "items": [_spu_to_item(spu) for spu in result],
             "is_personalized": face_shape is not None or has_prefs,
           }
        """

    def _spu_to_item(self, spu: GoodsSpu) -> dict:
        """
        SPU → 推荐列表条目：
        {
          spu_id, name, category, cover_url, mount_type,
          price_min (所有 SKU 最低价), price_max (最高价),
          style_tags, occasion_tags, target_face_shapes,
          ar_available (是否有 SKU 的 ar_asset_url 非空)
        }
        注：复用 GoodsListItem Schema（在 goods-plan 中定义）
        """
        ...

【验证】
    python -c "
    from database import SessionLocal
    from services.recommend_service import RecommendService
    db = SessionLocal()
    svc = RecommendService(db, user_id=1)
    result = svc.recommend(page=1, page_size=5)
    print('total:', result['total'])
    print('is_personalized:', result['is_personalized'])
    print('top 3 items:')
    for item in result['items'][:3]:
        print(' ', item['name'], '| score category:', item['category'])
    db.close()
    "
```

---

## Task 3：创建 routers/recommend.py

**预计时间**：15 分钟  
**依赖**：Task 2  
**完成标志**：`GET /api/v1/recommend/list` 返回排序后的商品列表

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在创建推荐路由。

【任务】新建 backend/routers/recommend.py：

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.common import ApiResponse
from services.recommend_service import RecommendService
from core.deps import get_current_user
from models.user import User

router = APIRouter(tags=["推荐"])

@router.get("/list", response_model=ApiResponse[dict])
def recommend_list(
    category: str | None = Query(None, description="商品分类筛选：earring/necklace/bracelet/ring/set"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    个性化推荐商品列表：
    - 已有脸型档案 → 脸型匹配加分
    - 已有用户偏好 → 风格/场合标签加分
    - 算法反馈降权 → 自动降低退货率高的脸型-商品组合权重
    - 无档案/偏好 → 冷启动：按 sort_weight 排序
    """
    data = RecommendService(db, current_user.id).recommend(
        category=category,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=data)

【验证】
    # 有脸型档案（已分析过）
    curl -s "http://localhost:8000/api/v1/recommend/list?page=1&page_size=5" \
      -H "Authorization: Bearer TOKEN" | python -m json.tool

    # 验证 is_personalized 字段
    curl -s "http://localhost:8000/api/v1/recommend/list" \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    print('total:', d['total'], '| is_personalized:', d['is_personalized'])
    print('top item:', d['items'][0]['name'] if d['items'] else 'empty')
    "

    # 按分类筛选
    curl -s "http://localhost:8000/api/v1/recommend/list?category=earring" \
      -H "Authorization: Bearer TOKEN" | python -c "
    import sys,json; d=json.load(sys.stdin)['data']
    cats = set(i['category'] for i in d['items'])
    assert cats <= {'earring'}, f'FAIL: {cats}'
    print('PASS category filter:', cats)
    "
```

---

## Task 4：注册路由到 main.py

**预计时间**：10 分钟  
**依赖**：Task 3  
**完成标志**：`/api/v1/recommend/list` 出现在 OpenAPI 文档

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。将推荐路由注册到 main.py。

【任务】在 backend/main.py 中追加：
    from routers import recommend
    app.include_router(recommend.router, prefix="/api/v1/recommend")

【验证】
    curl -s http://localhost:8000/openapi.json | python -c "
    import sys,json
    paths = list(json.load(sys.stdin)['paths'].keys())
    rec = [p for p in paths if 'recommend' in p]
    print('推荐接口:', rec)
    assert len(rec) >= 1, 'FAIL'
    print('PASS')
    "
```

---

## Task 5：全流程冒烟测试

**预计时间**：20 分钟  
**依赖**：全部前序任务  
**完成标志**：有/无档案时推荐结果不同，算法反馈后排名变化

**AI 提示词**：

```
你是珑饰电商平台的后端工程师。现在对推荐模块做完整验收。

【任务】创建 backend/scripts/smoke_test_recommend.sh：

#!/usr/bin/env bash
set -e
BASE="http://localhost:8000/api/v1"

echo "请粘贴登录 TOKEN："
read -r TOKEN

echo "=== [1] 冷启动推荐（尚未分析脸型）==="
curl -s "$BASE/recommend/list?page_size=3" -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)['data']
print('total:', d['total'], '| is_personalized:', d['is_personalized'])
print('冷启动 top3:')
for i in d['items'][:3]: print(' ', i['name'])
"

echo "=== [2] 上传脸型档案（oval）==="
python -c "
from PIL import Image
Image.new('RGB', (400,490),'ivory').save('/tmp/rec_oval.jpg')
print('oval 测试图已生成')
"
curl -s -X POST "$BASE/face/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/rec_oval.jpg" | python -c "
import sys,json; d=json.load(sys.stdin)
print('脸型:', d['data']['face_shape'], d['data']['face_shape_label'])
"

echo "=== [3] 个性化推荐（有脸型）==="
curl -s "$BASE/recommend/list?page_size=5" -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)['data']
print('is_personalized:', d['is_personalized'])
print('个性化 top5:')
for i in d['items'][:5]: print(' ', i['name'], '| face shapes:', i.get('target_face_shapes'))
"

echo "=== [4] 按类别筛选（耳环）==="
curl -s "$BASE/recommend/list?category=earring&page_size=3" \
  -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; d=json.load(sys.stdin)['data']
cats = set(i['category'] for i in d['items'])
assert not cats - {'earring'}, f'FAIL: {cats}'
print('PASS earring filter:', len(d['items']), '件')
"

echo "=== [5] 分页测试 ==="
PAGE1=$(curl -s "$BASE/recommend/list?page=1&page_size=3" \
  -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; items=json.load(sys.stdin)['data']['items']
print(','.join(str(i['spu_id']) for i in items))
")
PAGE2=$(curl -s "$BASE/recommend/list?page=2&page_size=3" \
  -H "Authorization: Bearer $TOKEN" | python -c "
import sys,json; items=json.load(sys.stdin)['data']['items']
print(','.join(str(i['spu_id']) for i in items))
")
python -c "
p1='$PAGE1'; p2='$PAGE2'
s1=set(p1.split(',')) if p1 else set()
s2=set(p2.split(',')) if p2 else set()
assert not (s1 & s2), f'FAIL 分页重叠: {s1 & s2}'
print('PASS 分页无重叠 page1:', p1, 'page2:', p2)
"

echo ""
echo "✓ 推荐模块全部测试通过！"
```

---

## 附录：文件变更清单

```
backend/
├── services/
│   └── recommend_service.py      ← 新建（Task 1、2）
│
├── routers/
│   └── recommend.py              ← 新建（Task 3）
│
├── main.py                       ← 注册 recommend 路由（Task 4）
│
└── scripts/
    └── smoke_test_recommend.sh   ← 新建（Task 5）
```

## 附录：评分示例

| 条件 | 分值 |
|---|---|
| spu.sort_weight（基础分） | 100 |
| 脸型匹配（face_shape in target_face_shapes） | +20 |
| 算法反馈降权（每次 effect_mismatch 退款后） | -5（累积） |
| 场合标签命中（每个） | +10 |
| 风格标签命中（每个） | +10 |

**示例**：oval 脸型用户，偏好「优雅复古」+「约会出行」，对一款 sort_weight=100、target_face_shapes=["oval"]、style_tags=["优雅复古"]、occasion_tags=["约会出行"] 的商品：

```
score = 100 + 20 + 0 + 10 + 10 = 140
```

若该用户之前因「佩戴效果不符」退货过该商品一次：

```
score = 100 + 20 + (-5) + 10 + 10 = 135
```
