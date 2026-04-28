# AR 渲染逻辑说明书

## 1. 概述

本系统采用 **2.5D 图像仿射变换** 方案，在 Web 浏览器中基于 MediaPipe FaceMesh 实现饰品的实时虚拟试戴。放弃高成本的 3D 建模，使用透明背景 PNG 素材配合几何变换模拟立体佩戴效果。

**技术栈：** MediaPipe FaceMesh (WASM) + Canvas 2D API + 卡尔曼滤波

---

## 2. MediaPipe FaceMesh 挂载锚点定义

FaceMesh 输出 468 个 3D 关键点（归一化坐标 x, y, z），本系统使用以下关键锚点：

### 2.1 锚点索引表

| 饰品类型 | 挂载点名称 | 主锚点索引 | 辅助锚点索引 | 说明 |
|---|---|---|---|---|
| 耳饰（左耳） | left_ear_lobe | **234** | 227, 137 | 234=左耳垂底部，227/137 用于计算耳朵朝向 |
| 耳饰（右耳） | right_ear_lobe | **454** | 447, 366 | 454=右耳垂底部，447/366 用于计算耳朵朝向 |
| 项链 | neck_center | **152** | 10, 234, 454 | 152=下巴底部，向下偏移作为锁骨估计点 |
| 发饰（头顶） | hair_top | **10** | 338, 109 | 10=额头顶部中心 |
| 耳钉（左耳） | left_ear_top | **234** | 93 | 耳钉位置略高于耳垂 |
| 耳钉（右耳） | right_ear_top | **454** | 323 | |

### 2.2 锚点坐标提取

```javascript
// 从 FaceMesh 结果中提取归一化坐标
function getAnchorPoint(landmarks, index, canvasWidth, canvasHeight) {
    const lm = landmarks[index];
    return {
        x: lm.x * canvasWidth,
        y: lm.y * canvasHeight,
        z: lm.z * canvasWidth  // z 值用于深度估计
    };
}
```

### 2.3 项链挂载点推导

项链挂载点不直接对应 FaceMesh 关键点，需根据下巴点进行偏移计算：

```javascript
function getNecklaceAnchor(landmarks, canvasW, canvasH) {
    const chin = landmarks[152];       // 下巴底部
    const foreHead = landmarks[10];     // 额头顶部
    const faceHeight = Math.abs(chin.y - foreHead.y) * canvasH;

    // 项链挂载点 = 下巴向下偏移 face_height * 0.35
    return {
        x: chin.x * canvasW,
        y: chin.y * canvasH + faceHeight * 0.35,
        z: chin.z * canvasW
    };
}
```

---

## 3. 头部姿态解算（Pitch / Yaw / Roll）

利用 FaceMesh 的 3D 关键点估算头部旋转角，驱动饰品贴图的透视变换。

### 3.1 参考关键点

| 角度 | 计算关键点 | 说明 |
|---|---|---|
| Yaw（偏航/左右转） | 1(鼻尖), 234(左耳), 454(右耳) | 鼻尖相对双耳中点的水平偏移 |
| Pitch（俯仰/上下点头） | 10(额头), 152(下巴) | 面部纵轴与垂直方向的夹角 |
| Roll（翻滚/歪头） | 234(左耳), 454(右耳) | 双耳连线与水平方向的夹角 |

### 3.2 角度计算公式

```javascript
function estimateHeadPose(landmarks) {
    const noseTip   = landmarks[1];
    const leftEar   = landmarks[234];
    const rightEar  = landmarks[454];
    const forehead  = landmarks[10];
    const chin      = landmarks[152];

    // Yaw: 鼻尖相对双耳中点的水平偏移比
    const earMidX = (leftEar.x + rightEar.x) / 2;
    const earDist = Math.abs(leftEar.x - rightEar.x);
    const yaw = Math.asin(
        Math.max(-1, Math.min(1, (noseTip.x - earMidX) / (earDist / 2)))
    );

    // Pitch: 面部纵轴倾斜角
    const pitch = Math.atan2(
        chin.z - forehead.z,
        chin.y - forehead.y
    );

    // Roll: 双耳连线倾斜角
    const roll = Math.atan2(
        rightEar.y - leftEar.y,
        rightEar.x - leftEar.x
    );

    return {
        yaw:   yaw,          // 弧度，正值=右转
        pitch: pitch,         // 弧度，正值=低头
        roll:  roll           // 弧度，正值=右倾
    };
}
```

---

## 4. 2D 贴图仿射变换公式

### 4.1 变换矩阵定义

对于饰品贴图 P，施加以下复合变换将其映射到 Canvas 上的正确位置：

```
P' = T(tx, ty) * R(roll) * S(sx, sy) * K(skew) * P
```

其中：
- **T(tx, ty)**：平移变换，将贴图移动到锚点位置
- **R(roll)**：旋转变换，随头部 Roll 角旋转
- **S(sx, sy)**：缩放变换，基于面部尺寸和距离的动态缩放
- **K(skew)**：非均匀缩放（Skew），模拟侧脸时的透视收缩

### 4.2 各变换分量计算

#### 4.2.1 缩放（Scale）

```javascript
function computeScale(landmarks, skuConfig) {
    const leftEar  = landmarks[234];
    const rightEar = landmarks[454];

    // 双耳间距作为面部宽度参考
    const faceWidth = Math.sqrt(
        Math.pow(rightEar.x - leftEar.x, 2) +
        Math.pow(rightEar.y - leftEar.y, 2)
    );

    // 参考面宽 = 0.30（归一化值，标定时测得）
    const REF_FACE_WIDTH = 0.30;
    const scaleFactor = (faceWidth / REF_FACE_WIDTH) * skuConfig.ar_scale_base;

    return { sx: scaleFactor, sy: scaleFactor };
}
```

#### 4.2.2 旋转（Rotation）

```javascript
function computeRotation(headPose, skuConfig) {
    // 贴图随头部 Roll 角同步旋转
    return headPose.roll + (skuConfig.ar_rotation_offset * Math.PI / 180);
}
```

#### 4.2.3 非均匀缩放/透视模拟（Skew）

侧脸时，近侧饰品应放大、远侧饰品应缩小，模拟透视效果：

```javascript
function computeSkew(headPose, mountSide) {
    const yaw = headPose.yaw;

    // mountSide: 'left' | 'right' | 'center'
    if (mountSide === 'left') {
        // 左耳饰品：右转时缩小（远离摄像头），左转时放大（靠近摄像头）
        return {
            scaleX: 1.0 - 0.3 * Math.sin(yaw),   // Yaw>0 右转，左耳变远
            scaleY: 1.0 - 0.15 * Math.abs(Math.sin(yaw)),
            opacity: Math.max(0.3, 1.0 - 0.7 * Math.max(0, Math.sin(yaw)))
        };
    } else if (mountSide === 'right') {
        // 右耳饰品：左转时缩小，右转时放大
        return {
            scaleX: 1.0 + 0.3 * Math.sin(yaw),
            scaleY: 1.0 - 0.15 * Math.abs(Math.sin(yaw)),
            opacity: Math.max(0.3, 1.0 - 0.7 * Math.max(0, -Math.sin(yaw)))
        };
    } else {
        // 项链等中心饰品：仅做轻微水平压缩
        return {
            scaleX: 1.0 - 0.15 * Math.abs(Math.sin(yaw)),
            scaleY: 1.0,
            opacity: 1.0
        };
    }
}
```

### 4.3 完整渲染流程

```javascript
function renderAccessory(ctx, image, anchor, headPose, skuConfig, mountSide) {
    const scale    = computeScale(landmarks, skuConfig);
    const rotation = computeRotation(headPose, skuConfig);
    const skew     = computeSkew(headPose, mountSide);

    const finalW = image.width  * scale.sx * skew.scaleX;
    const finalH = image.height * scale.sy * skew.scaleY;

    const tx = anchor.x + skuConfig.ar_offset_x * scale.sx;
    const ty = anchor.y + skuConfig.ar_offset_y * scale.sy;

    ctx.save();
    ctx.globalAlpha = skew.opacity;
    ctx.translate(tx, ty);
    ctx.rotate(rotation);
    ctx.drawImage(image, -finalW / 2, -finalH / 2, finalW, finalH);
    ctx.restore();
}
```

---

## 5. 卡尔曼滤波防抖

### 5.1 问题描述

MediaPipe 在逐帧检测中，关键点坐标存在高频噪声（±2~5px 跳变），导致饰品贴图出现可见的抖动/闪烁。

### 5.2 一维卡尔曼滤波模型

对每个锚点的 x, y 坐标分别应用独立的一维卡尔曼滤波器。

**状态变量：** `x_hat`（估计位置）

**模型参数：**
- `Q`（过程噪声协方差）：控制对新观测的信任度。值越大，跟踪越灵敏但越抖；值越小，越平滑但越滞后
- `R`（观测噪声协方差）：MediaPipe 输出的噪声水平估计
- `P`（估计误差协方差）：初始设为较大值

### 5.3 实现伪代码

```javascript
class KalmanFilter1D {
    constructor(Q = 0.001, R = 0.01) {
        this.Q = Q;    // 过程噪声
        this.R = R;    // 观测噪声
        this.P = 1.0;  // 估计误差协方差
        this.x = null;  // 状态估计值（首次观测时初始化）
        this.K = 0;     // 卡尔曼增益
    }

    update(measurement) {
        if (this.x === null) {
            // 首次观测，直接初始化
            this.x = measurement;
            return this.x;
        }

        // ---- 预测步骤 (Predict) ----
        // 假设匀速模型：预测值 = 上一次估计值
        // x_pred = x_hat(k-1)
        // P_pred = P(k-1) + Q
        this.P = this.P + this.Q;

        // ---- 更新步骤 (Update) ----
        // 卡尔曼增益 K = P_pred / (P_pred + R)
        this.K = this.P / (this.P + this.R);

        // 状态更新 x_hat(k) = x_pred + K * (z(k) - x_pred)
        this.x = this.x + this.K * (measurement - this.x);

        // 协方差更新 P(k) = (1 - K) * P_pred
        this.P = (1 - this.K) * this.P;

        return this.x;
    }

    reset() {
        this.x = null;
        this.P = 1.0;
    }
}
```

### 5.4 应用于锚点坐标

```javascript
class AnchorPointSmoother {
    constructor(Q = 0.001, R = 0.015) {
        this.filterX = new KalmanFilter1D(Q, R);
        this.filterY = new KalmanFilter1D(Q, R);
        this.filterZ = new KalmanFilter1D(Q, R);
    }

    smooth(rawPoint) {
        return {
            x: this.filterX.update(rawPoint.x),
            y: this.filterY.update(rawPoint.y),
            z: this.filterZ.update(rawPoint.z)
        };
    }

    reset() {
        this.filterX.reset();
        this.filterY.reset();
        this.filterZ.reset();
    }
}

// 为每个挂载点创建独立的平滑器
const smoothers = {
    leftEar:  new AnchorPointSmoother(0.001, 0.015),
    rightEar: new AnchorPointSmoother(0.001, 0.015),
    neck:     new AnchorPointSmoother(0.001, 0.020),  // 项链位置噪声更大
    hairTop:  new AnchorPointSmoother(0.001, 0.010)
};
```

### 5.5 参数调优建议

| 场景 | Q | R | 效果 |
|---|---|---|---|
| 静态自拍 | 0.0005 | 0.02 | 极度平滑，低延迟容忍 |
| 日常使用（推荐默认） | 0.001 | 0.015 | 平衡平滑度与响应速度 |
| 快速转头 | 0.005 | 0.01 | 高响应，轻微抖动可接受 |

**自适应策略：** 当连续帧间锚点位移超过阈值（如 15px）时，临时增大 Q 值以加快跟踪响应，避免平滑器滞后导致饰品"拖尾"。

```javascript
function adaptiveUpdate(smoother, raw, prevSmoothed, threshold = 15) {
    const dist = Math.sqrt(
        Math.pow(raw.x - prevSmoothed.x, 2) +
        Math.pow(raw.y - prevSmoothed.y, 2)
    );
    if (dist > threshold) {
        // 大幅位移：临时提升过程噪声
        smoother.filterX.Q = 0.05;
        smoother.filterY.Q = 0.05;
    } else {
        smoother.filterX.Q = 0.001;
        smoother.filterY.Q = 0.001;
    }
    return smoother.smooth(raw);
}
```

---

## 6. 完整渲染主循环

```javascript
async function renderLoop(videoElement, canvasElement, skuAsset) {
    const ctx = canvasElement.getContext('2d');
    const faceMesh = new FaceMesh({ /* MediaPipe config */ });

    // 加载 AR 素材
    const accessoryImg = await loadImage(skuAsset.ar_asset_url);

    faceMesh.onResults((results) => {
        if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
            return;  // 未检测到人脸，保持最后一帧
        }

        const landmarks = results.multiFaceLandmarks[0];
        const W = canvasElement.width;
        const H = canvasElement.height;

        // 1. 清除画布，绘制视频帧
        ctx.clearRect(0, 0, W, H);
        ctx.drawImage(videoElement, 0, 0, W, H);

        // 2. 提取原始锚点
        const rawAnchor = getAnchorPoint(landmarks, 234, W, H); // 以左耳为例

        // 3. 卡尔曼滤波平滑
        const smoothedAnchor = smoothers.leftEar.smooth(rawAnchor);

        // 4. 头部姿态解算
        const headPose = estimateHeadPose(landmarks);

        // 5. 渲染饰品
        renderAccessory(ctx, accessoryImg, smoothedAnchor, headPose, skuAsset, 'left');

        // 6. 对称耳饰：同时渲染右耳
        if (skuAsset.is_symmetric) {
            const rawRight = getAnchorPoint(landmarks, 454, W, H);
            const smoothedRight = smoothers.rightEar.smooth(rawRight);
            renderAccessory(ctx, accessoryImg, smoothedRight, headPose, skuAsset, 'right');
        }
    });

    // 启动摄像头帧发送
    const camera = new Camera(videoElement, {
        onFrame: async () => {
            await faceMesh.send({ image: videoElement });
        },
        width: 640,
        height: 480
    });
    camera.start();
}
```

---

## 7. 性能优化策略

| 策略 | 措施 | 目标 |
|---|---|---|
| 分辨率控制 | 摄像头采集 640x480，Canvas 同尺寸 | 降低 GPU 负载 |
| 模型精度选择 | 使用 FaceMesh `lite` 模型（默认） | 减少推理耗时 |
| 帧率限制 | `requestAnimationFrame` 自然限制 60fps | 避免过度渲染 |
| 素材预加载 | 切换 SKU 时预加载下一个 PNG | 消除切换延迟 |
| Web Worker | FaceMesh 推理放入 Worker（如浏览器支持） | 避免阻塞主线程 |
| 关键点裁剪 | 仅提取所需的 6~8 个关键点用于计算 | 减少数据传输 |
