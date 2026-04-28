<template>
  <div class="ar-page">
    <!-- 顶部栏 -->
    <div class="ar-header">
      <el-button :icon="ArrowLeft" circle @click="$router.back()" />
      <span class="ar-title">{{ productName }} · AR 试戴</span>
      <el-tag :type="faceDetected ? 'success' : 'info'" size="small">
        {{ faceDetected ? '已检测到人脸' : '请将面部对准摄像头' }}
      </el-tag>
    </div>

    <!-- 主渲染区域 -->
    <div class="ar-container" ref="containerRef">
      <!-- 原始视频（隐藏，仅作 MediaPipe 数据源） -->
      <video ref="videoRef" autoplay playsinline muted class="ar-video" />

      <!-- Canvas 叠加层（输出画面） -->
      <canvas ref="canvasRef" class="ar-canvas" />

      <!-- 加载提示 -->
      <div v-if="status !== 'ready'" class="ar-overlay">
        <el-icon v-if="status === 'error'" size="48" color="#f56c6c"><CircleCloseFilled /></el-icon>
        <el-icon v-else class="loading-spin" size="48" color="#409eff"><Loading /></el-icon>
        <p>{{ statusText }}</p>
      </div>
    </div>

    <!-- 底部提示 -->
    <div class="ar-footer">
      <el-text type="info" size="small">
        素材为占位矩形，AR 素材上传后自动替换
      </el-text>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()

// ── Route params ──────────────────────────────────────────────────────────────
const productName = computed(() => route.query.sku_name || '试戴预览')
const arAssetUrl  = computed(() => route.query.ar_asset_url || null)
const mountType   = computed(() => route.query.mount_type  || 'ear_lobe')

// ── Refs ──────────────────────────────────────────────────────────────────────
const containerRef = ref(null)
const videoRef     = ref(null)
const canvasRef    = ref(null)

const status      = ref('init')        // init | camera | mediapipe | ready | error
const faceDetected = ref(false)

const statusText = computed(() => ({
  init:      '正在初始化…',
  camera:    '正在请求摄像头权限…',
  mediapipe: '正在加载 AI 模型…',
  ready:     '',
  error:     '初始化失败，请检查摄像头权限',
}[status.value]))

// ── State ─────────────────────────────────────────────────────────────────────
let faceMeshInstance = null
let animFrameId      = null
let mediaStream      = null
let arImage          = null

// ── Kalman 1D ──────────────────────────────────────────────────────────────────
class KalmanFilter1D {
  constructor(Q = 0.001, R = 0.015) {
    this.Q = Q; this.R = R; this.P = 1; this.x = null
  }
  update(z) {
    if (this.x === null) { this.x = z; return z }
    this.P += this.Q
    const K = this.P / (this.P + this.R)
    this.x += K * (z - this.x)
    this.P *= (1 - K)
    return this.x
  }
  reset() { this.x = null; this.P = 1 }
}

class AnchorSmoother {
  constructor() {
    this.fx = new KalmanFilter1D()
    this.fy = new KalmanFilter1D()
  }
  smooth(p) { return { x: this.fx.update(p.x), y: this.fy.update(p.y) } }
  reset()   { this.fx.reset(); this.fy.reset() }
}

const smoothers = {
  leftEar:  new AnchorSmoother(),
  rightEar: new AnchorSmoother(),
  center:   new AnchorSmoother(),
}

// ── Camera ────────────────────────────────────────────────────────────────────
async function startCamera() {
  status.value = 'camera'
  const video = videoRef.value
  mediaStream = await navigator.mediaDevices.getUserMedia({
    video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
    audio: false,
  })
  video.srcObject = mediaStream
  await new Promise((resolve) => { video.onloadedmetadata = resolve })
  await video.play()
}

// ── MediaPipe ─────────────────────────────────────────────────────────────────
async function initMediaPipe() {
  status.value = 'mediapipe'
  // Dynamic import so Vite won't bundle WASM
  const { FaceMesh } = await import('@mediapipe/face_mesh')

  faceMeshInstance = new FaceMesh({
    locateFile: (f) =>
      `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh@0.4/${f}`,
  })

  faceMeshInstance.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  })

  faceMeshInstance.onResults(onResults)
  await faceMeshInstance.initialize()
}

// ── Render loop ───────────────────────────────────────────────────────────────
function startRenderLoop() {
  const video  = videoRef.value
  const canvas = canvasRef.value
  status.value = 'ready'

  async function loop() {
    if (video.readyState >= 2) {
      canvas.width  = video.videoWidth  || 640
      canvas.height = video.videoHeight || 480
      try {
        await faceMeshInstance.send({ image: video })
      } catch { /* ignore single-frame errors */ }
    }
    animFrameId = requestAnimationFrame(loop)
  }
  animFrameId = requestAnimationFrame(loop)
}

// ── Results handler ───────────────────────────────────────────────────────────
function onResults(results) {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width, H = canvas.height

  ctx.clearRect(0, 0, W, H)

  // Mirror-flip so it feels like a selfie mirror
  ctx.save()
  ctx.translate(W, 0)
  ctx.scale(-1, 1)
  ctx.drawImage(results.image, 0, 0, W, H)
  ctx.restore()

  if (!results.multiFaceLandmarks?.length) {
    faceDetected.value = false
    drawGuidebox(ctx, W, H)
    return
  }

  faceDetected.value = true
  const lm = results.multiFaceLandmarks[0]

  // Mirror x because we flipped the video
  const mx = (x) => (1 - x) * W
  const py = (y) => y * H

  const anchors = getAnchors(lm, mx, py, W, H)
  drawAccessory(ctx, anchors, W, H)
}

// ── Anchor computation ────────────────────────────────────────────────────────
function getAnchors(lm, mx, py, W, H) {
  if (mountType.value === 'ear_lobe' || mountType.value === 'ear_top') {
    const rawL = { x: mx(lm[234].x), y: py(lm[234].y) }
    const rawR = { x: mx(lm[454].x), y: py(lm[454].y) }
    return {
      left:  smoothers.leftEar.smooth(rawL),
      right: smoothers.rightEar.smooth(rawR),
    }
  }
  if (mountType.value === 'neck') {
    const chin = lm[152], forehead = lm[10]
    const faceH = Math.abs(chin.y - forehead.y) * H
    const raw = { x: mx(chin.x), y: py(chin.y) + faceH * 0.35 }
    return { center: smoothers.center.smooth(raw) }
  }
  if (mountType.value === 'hair') {
    const top = lm[10]
    const raw = { x: mx(top.x), y: py(top.y) - H * 0.04 }
    return { center: smoothers.center.smooth(raw) }
  }
  return { center: { x: W / 2, y: H / 2 } }
}

// ── Draw ───────────────────────────────────────────────────────────────────────
function drawAccessory(ctx, anchors, W, H) {
  if (arImage) {
    drawArImage(ctx, anchors, W, H)
  } else {
    drawPlaceholderBoxes(ctx, anchors, W, H)
  }
}

function drawPlaceholderBoxes(ctx, anchors, W, H) {
  const size = H * 0.07
  ctx.strokeStyle = 'rgba(64,169,255,0.9)'
  ctx.fillStyle   = 'rgba(64,169,255,0.18)'
  ctx.lineWidth   = 2
  ctx.setLineDash([5, 3])

  function box(pt) {
    if (!pt) return
    ctx.beginPath()
    ctx.rect(pt.x - size / 2, pt.y - size / 4, size / 2, size)
    ctx.fill()
    ctx.stroke()
  }

  box(anchors.left)
  box(anchors.right)
  if (anchors.center) {
    const w = H * 0.14, h = H * 0.06
    ctx.beginPath()
    ctx.rect(anchors.center.x - w / 2, anchors.center.y, w, h)
    ctx.fill()
    ctx.stroke()
  }
  ctx.setLineDash([])
}

function drawArImage(ctx, anchors, W, H) {
  const earH = H * 0.12

  function drawAt(pt, flip = false) {
    if (!pt) return
    const w = earH * (arImage.width / arImage.height)
    ctx.save()
    if (flip) {
      ctx.translate(pt.x, pt.y)
      ctx.scale(-1, 1)
      ctx.drawImage(arImage, -w / 2, 0, w, earH)
    } else {
      ctx.drawImage(arImage, pt.x - w / 2, pt.y, w, earH)
    }
    ctx.restore()
  }

  drawAt(anchors.left,  false)
  drawAt(anchors.right, true)

  if (anchors.center) {
    const w = H * 0.15, h = H * 0.06
    ctx.drawImage(arImage, anchors.center.x - w / 2, anchors.center.y, w, h)
  }
}

function drawGuidebox(ctx, W, H) {
  ctx.strokeStyle = 'rgba(64,169,255,0.5)'
  ctx.lineWidth = 2
  ctx.setLineDash([8, 4])
  ctx.strokeRect(W * 0.25, H * 0.15, W * 0.5, H * 0.6)
  ctx.setLineDash([])
  ctx.fillStyle = 'rgba(64,169,255,0.85)'
  ctx.font = `${H * 0.025}px sans-serif`
  ctx.textAlign = 'center'
  ctx.fillText('请将面部对准框内', W / 2, H * 0.79)
}

// ── Preload AR image ──────────────────────────────────────────────────────────
async function loadArImage(url) {
  if (!url) return
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload  = () => resolve(img)
    img.onerror = () => resolve(null)
    img.src = url
  })
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    if (arAssetUrl.value) {
      arImage = await loadArImage(arAssetUrl.value)
    }
    await startCamera()
    await initMediaPipe()
    startRenderLoop()
  } catch (err) {
    console.error('[AR] init failed:', err)
    status.value = 'error'
  }
})

onUnmounted(() => {
  if (animFrameId)      cancelAnimationFrame(animFrameId)
  if (faceMeshInstance) faceMeshInstance.close()
  if (mediaStream)      mediaStream.getTracks().forEach((t) => t.stop())
  Object.values(smoothers).forEach((s) => s.reset())
})
</script>

<style scoped>
.ar-page {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  background: #000;
  color: #fff;
  overflow: hidden;
}

.ar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.7);
  z-index: 10;
  flex-shrink: 0;
}

.ar-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
}

.ar-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.ar-video {
  position: absolute;
  opacity: 0;          /* hidden – only canvas output is shown */
  width: 1px;
  height: 1px;
}

.ar-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.ar-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  background: rgba(0, 0, 0, 0.75);
  font-size: 14px;
  color: #ccc;
}

.loading-spin {
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.ar-footer {
  padding: 8px;
  text-align: center;
  background: rgba(0, 0, 0, 0.6);
  flex-shrink: 0;
}
</style>
