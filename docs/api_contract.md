# 前后端接口契约文档

## 总体规范

- 基础路径：`/api/v1`
- 协议：HTTPS
- 数据格式：JSON（`Content-Type: application/json`）
- 认证方式：Bearer Token（JWT），放在 `Authorization` 头中
- 统一响应结构：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 错误码规范：`0` 成功，`1xxx` 参数错误，`2xxx` 业务错误，`3xxx` 系统错误，`4xxx` 认证错误

---

## 1. AI 感知模块

### 1.1 POST `/api/v1/ai/classify-face` — 脸型识别接口

上传用户面部照片，返回脸型分类结果与肤色分析。

**Headers:**
- `Authorization: Bearer {token}`

**Request（multipart/form-data）:**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| image | File | Y | 用户面部照片（jpg/png，最大 5MB） |
| save_result | boolean | N | 是否持久化到 user_face_data，默认 true |

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "face_data_id": 1001,
    "face_shape": "oval",
    "face_shape_vector": {
      "oval": 0.82,
      "round": 0.08,
      "square": 0.04,
      "heart": 0.03,
      "oblong": 0.02,
      "diamond": 0.01
    },
    "skin_tone": {
      "lab": { "L": 65.2, "a": 12.1, "b": 18.3 },
      "category": "warm_yellow"
    },
    "jaw_width_ratio": 0.7823,
    "confidence": 0.9412,
    "model_version": "resnet18_v1"
  }
}
```

**错误码：**
- `1001`：图片格式不支持
- `1002`：图片尺寸超限
- `2001`：未检测到人脸
- `2002`：检测到多张人脸（请上传单人照片）

---

### 1.2 POST `/api/v1/ai/guide/start` — 开始 AI 导购会话

创建一个新的 AI 引导式导购会话。

**Request:**

```json
{
  "face_data_id": 1001
}
```

**Response:**

```json
{
  "code": 0,
  "data": {
    "session_token": "gs_a1b2c3d4e5",
    "current_step": "occasion",
    "question": "你想在什么场合佩戴？",
    "options": [
      { "key": "daily", "label": "日常通勤" },
      { "key": "party", "label": "聚会约会" },
      { "key": "wedding", "label": "婚礼宴会" },
      { "key": "business", "label": "商务正式" }
    ]
  }
}
```

---

### 1.3 POST `/api/v1/ai/guide/next` — 导购会话下一步

用户点选选项后，推进至下一个问题节点或返回推荐结果。

**Request:**

```json
{
  "session_token": "gs_a1b2c3d4e5",
  "selected_key": "party"
}
```

**Response（中间步骤）：**

```json
{
  "code": 0,
  "data": {
    "session_token": "gs_a1b2c3d4e5",
    "current_step": "style",
    "question": "你偏好什么风格？",
    "options": [
      { "key": "minimalist", "label": "简约" },
      { "key": "vintage", "label": "复古" },
      { "key": "bohemian", "label": "波西米亚" },
      { "key": "luxury", "label": "轻奢" }
    ]
  }
}
```

**Response（最终步骤，返回推荐结果）：**

```json
{
  "code": 0,
  "data": {
    "session_token": "gs_a1b2c3d4e5",
    "current_step": "result",
    "intent_tags": ["party", "vintage", "gold"],
    "recommendations": [
      {
        "spu_id": 501,
        "name": "复古法式流苏耳环",
        "cover_url": "/img/spu/501.jpg",
        "price_range": "89.00 - 129.00",
        "match_score": 0.94,
        "match_reasons": ["适合鹅蛋脸", "复古风格匹配", "暖色调衬肤色"],
        "default_sku_id": 5012,
        "ar_available": true
      }
    ]
  }
}
```

---

## 2. 推荐模块

### 2.1 POST `/api/v1/recommend/smart` — 多模态智能推荐

综合用户脸型特征与意图标签，利用余弦相似度从商品库中检索 Top-N 匹配商品。

**Request:**

```json
{
  "face_data_id": 1001,
  "intent_tags": ["party", "vintage"],
  "category": "earring",
  "price_min": 50,
  "price_max": 200,
  "page": 1,
  "page_size": 12
}
```

**算法流程说明：**
1. 从 `user_face_data` 取 `face_shape_vector`（6维）与 `skin_tone_lab`（3维）
2. 将 `intent_tags` 编码为标签向量
3. 拼接为融合特征向量 `F_user = concat(face_vec, skin_vec, intent_vec)`
4. 对商品库中每个 SPU 的 `description_vector` + `style_tags` 编码向量计算余弦相似度
5. 叠加 `match_penalty_matrix` 中该用户脸型对应的惩罚值
6. 按最终得分降序排列，返回 Top-N

**Response:**

```json
{
  "code": 0,
  "data": {
    "total": 56,
    "page": 1,
    "page_size": 12,
    "items": [
      {
        "spu_id": 501,
        "name": "复古法式流苏耳环",
        "category": "earring",
        "cover_url": "/img/spu/501.jpg",
        "price_range": "89.00 - 129.00",
        "style_tags": ["复古", "法式"],
        "match_score": 0.94,
        "match_detail": {
          "face_shape_score": 0.91,
          "style_score": 0.96,
          "skin_tone_score": 0.88,
          "penalty": -0.02
        },
        "default_sku_id": 5012,
        "ar_available": true
      }
    ]
  }
}
```

---

## 3. AR 试戴模块

### 3.1 GET `/api/v1/ar/sku-asset/{sku_id}` — 获取 SKU 的 AR 素材信息

**Response:**

```json
{
  "code": 0,
  "data": {
    "sku_id": 5012,
    "spu_id": 501,
    "mount_type": "ear_lobe",
    "ar_asset_url": "/assets/ar/sku_5012.png",
    "ar_offset_x": 2.5,
    "ar_offset_y": -3.0,
    "ar_scale_base": 1.15,
    "ar_rotation_offset": 0,
    "weight_g": 8.5,
    "is_symmetric": true
  }
}
```

---

## 4. 商品与购物车模块

### 4.1 GET `/api/v1/goods/spu/{spu_id}` — 商品详情

**Response:**

```json
{
  "code": 0,
  "data": {
    "spu_id": 501,
    "name": "复古法式流苏耳环",
    "category": "earring",
    "description": "...",
    "style_tags": ["复古", "法式"],
    "material": "925银",
    "cover_url": "/img/spu/501.jpg",
    "detail_images": ["/img/detail/501_1.jpg", "/img/detail/501_2.jpg"],
    "target_face_shapes": ["oval", "heart"],
    "skus": [
      {
        "sku_id": 5011,
        "sku_name": "银色-短款",
        "color": "银色",
        "size": "3cm",
        "price": 89.00,
        "original_price": 119.00,
        "stock": 52,
        "ar_available": true
      },
      {
        "sku_id": 5012,
        "sku_name": "金色-长款",
        "color": "金色",
        "size": "5cm",
        "price": 129.00,
        "original_price": 159.00,
        "stock": 38,
        "ar_available": true
      }
    ]
  }
}
```

### 4.2 POST `/api/v1/cart/add` — 添加购物车

**Request:**

```json
{
  "sku_id": 5012,
  "quantity": 1
}
```

### 4.3 GET `/api/v1/cart/list` — 购物车列表

### 4.4 PUT `/api/v1/cart/update` — 修改数量/勾选状态

### 4.5 DELETE `/api/v1/cart/remove` — 删除购物车商品

---

## 5. 订单模块

### 5.1 POST `/api/v1/order/create` — 创建订单

从购物车选中项生成订单，执行库存锁定。

**Request:**

```json
{
  "cart_item_ids": [101, 102],
  "receiver_name": "张三",
  "receiver_phone": "13800138000",
  "receiver_address": "北京市朝阳区xxx",
  "remark": "请轻拿轻放"
}
```

**Response:**

```json
{
  "code": 0,
  "data": {
    "order_id": 20001,
    "order_no": "ORD20260427001",
    "total_amount": 218.00,
    "status": "pending_pay",
    "expire_at": "2026-04-27T21:30:00Z"
  }
}
```

**业务规则：**
- 库存扣减：`stock -= qty, frozen_stock += qty`（行级锁）
- 超时未支付（15分钟）：自动释放库存

### 5.2 POST `/api/v1/order/pay` — 模拟支付

**Request:**

```json
{
  "order_id": 20001,
  "pay_method": "mock_wechat"
}
```

### 5.3 GET `/api/v1/order/list` — 订单列表

### 5.4 GET `/api/v1/order/{order_id}` — 订单详情

### 5.5 POST `/api/v1/order/cancel` — 取消订单

---

## 6. 售后/退货模块（逆向物流 + 负反馈）

### 6.1 POST `/api/v1/order/refund/apply` — 申请退货

**Request:**

```json
{
  "order_item_id": 30001,
  "reason_type": "ar_expectation_gap",
  "reason_detail": "耳环实际佩戴效果与AR试戴差距较大，不修饰脸型"
}
```

**Response:**

```json
{
  "code": 0,
  "data": {
    "refund_id": 40001,
    "refund_no": "RFD20260427001",
    "status": "pending_review"
  }
}
```

### 6.2 POST `/api/v1/order/refund-feedback` — 退货负反馈处理接口

当退货完成且原因为佩戴效果不符时，触发负反馈回写，动态调整推荐权重。

**Request（内部调用/管理端触发）：**

```json
{
  "refund_id": 40001
}
```

**处理流程：**
1. 校验 `refund_orders.status = 'refunded'` 且 `reason_type = 'ar_expectation_gap'`
2. 查询 `refund_orders.face_shape_at_purchase` 得到用户脸型
3. 查询对应 SPU 的 `match_penalty_matrix`
4. 对该脸型的惩罚值执行 `penalty -= 0.05`（每次退货降权 5%）
5. 设置下限阈值 `max(penalty, -0.50)` 防止过度惩罚
6. 回写 `goods_spu.match_penalty_matrix`
7. 标记 `refund_orders.feedback_processed = 1`
8. 清除该 SPU 相关的推荐缓存

**Response:**

```json
{
  "code": 0,
  "data": {
    "spu_id": 501,
    "face_shape": "round",
    "old_penalty": -0.10,
    "new_penalty": -0.15,
    "cache_cleared": true
  }
}
```

**错误码：**
- `2010`：退货单状态不满足反馈条件
- `2011`：退货原因非佩戴效果类，无需反馈
- `2012`：反馈已处理，不可重复执行

### 6.3 PUT `/api/v1/order/refund/{refund_id}/review` — 审核退货（管理端）

**Request:**

```json
{
  "action": "approve",
  "review_note": "同意退货"
}
```

### 6.4 PUT `/api/v1/order/refund/{refund_id}/status` — 更新退货状态（管理端）

用于推进逆向物流流程：寄回 -> 入库 -> 退款。

**Request:**

```json
{
  "status": "restocked",
  "return_tracking_no": "SF1234567890"
}
```

**入库时自动执行：** `goods_sku.stock += refund_orders.quantity`

---

## 7. 管理端接口

### 7.1 POST `/api/v1/admin/goods/spu` — 创建 SPU
### 7.2 PUT `/api/v1/admin/goods/spu/{spu_id}` — 编辑 SPU
### 7.3 POST `/api/v1/admin/goods/sku` — 创建 SKU
### 7.4 PUT `/api/v1/admin/goods/sku/{sku_id}` — 编辑 SKU（含 AR 素材配置）
### 7.5 GET `/api/v1/admin/orders` — 订单管理列表
### 7.6 GET `/api/v1/admin/refunds` — 退货管理列表
### 7.7 GET `/api/v1/admin/dashboard` — 数据看板（订单量、退货率、AI转化率）
