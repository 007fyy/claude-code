<template>
  <div class="face-detect-page">

    <!-- 拍照须知弹窗 -->
    <div v-if="showTips" class="tips-overlay">
      <div class="tips-modal">
        <div class="tips-modal-title">📸 拍照前，先看这里</div>
        <div class="tips-modal-sub">这三个错误会让识别翻车 😅</div>

        <div class="tips-cards">
          <div class="tip-card">
            <div class="tip-figure">
              <svg viewBox="0 0 70 90" xmlns="http://www.w3.org/2000/svg">
                <g transform="rotate(28, 35, 22)">
                  <circle cx="35" cy="22" r="15" fill="#FFDAB9" stroke="#333" stroke-width="2"/>
                  <circle cx="30" cy="21" r="2" fill="#333"/>
                  <circle cx="40" cy="21" r="2" fill="#333"/>
                  <path d="M31 28 Q35 32 39 28" fill="none" stroke="#333" stroke-width="1.5"/>
                </g>
                <line x1="35" y1="39" x2="35" y2="62" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="35" y1="47" x2="20" y2="57" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="35" y1="47" x2="50" y2="57" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="35" y1="62" x2="26" y2="80" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="35" y1="62" x2="44" y2="80" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <text x="50" y="20" font-size="16" fill="#E74C3C">↙</text>
              </svg>
            </div>
            <div class="tip-no">❌ 不要低头</div>
            <div class="tip-why">下巴会遮住脸型轮廓<br/>系统以为你是方脸</div>
          </div>

          <div class="tip-card">
            <div class="tip-figure">
              <svg viewBox="0 0 70 90" xmlns="http://www.w3.org/2000/svg">
                <circle cx="35" cy="24" r="15" fill="#FFDAB9" stroke="#333" stroke-width="2"/>
                <path d="M20 20 Q22 7 35 9 Q48 7 50 20 Q46 27 42 20 Q39 13 35 17 Q31 13 28 20 Q24 27 20 20Z" fill="#5D4037"/>
                <circle cx="30" cy="27" r="2" fill="#333"/>
                <circle cx="40" cy="27" r="2" fill="#333"/>
                <path d="M31 32 Q35 35 39 32" fill="none" stroke="#333" stroke-width="1.5"/>
                <text x="27" y="20" font-size="9" fill="#E74C3C" font-weight="bold">?</text>
                <text x="37" y="20" font-size="9" fill="#E74C3C" font-weight="bold">?</text>
                <line x1="35" y1="41" x2="35" y2="64" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="35" y1="48" x2="20" y2="58" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="35" y1="48" x2="50" y2="58" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="35" y1="64" x2="26" y2="82" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="35" y1="64" x2="44" y2="82" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="tip-no">❌ 不要留刘海</div>
            <div class="tip-why">额头被遮住<br/>找不到发际线关键点</div>
          </div>

          <div class="tip-card">
            <div class="tip-figure">
              <svg viewBox="0 0 70 90" xmlns="http://www.w3.org/2000/svg">
                <text x="1" y="22" font-size="13">☀️</text>
                <circle cx="40" cy="24" r="15" fill="#FFDAB9" stroke="#333" stroke-width="2"/>
                <path d="M40 9 A15 15 0 0 1 40 39 Z" fill="rgba(0,0,0,0.28)" stroke="none"/>
                <circle cx="35" cy="23" r="2" fill="#333"/>
                <circle cx="45" cy="23" r="2" fill="#333"/>
                <path d="M35 30 Q40 27 45 30" fill="none" stroke="#333" stroke-width="1.5"/>
                <line x1="40" y1="41" x2="40" y2="64" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="40" y1="48" x2="25" y2="58" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="40" y1="48" x2="55" y2="58" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="40" y1="64" x2="31" y2="82" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="40" y1="64" x2="49" y2="82" stroke="#333" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="tip-no">❌ 不要侧光</div>
            <div class="tip-why">半边脸在阴影里<br/>肤色和轮廓都会偏差</div>
          </div>
        </div>

        <div class="tips-correct">
          <span>✅ 正面朝向</span>
          <span>✅ 额头露出</span>
          <span>✅ 均匀光线</span>
        </div>

        <el-button type="primary" size="large" class="tips-confirm-btn" @click="dismissTips">
          明白了，开始检测 →
        </el-button>
      </div>
    </div>

    <div class="container">
      <div class="page-header">
        <h1 class="page-title"><span>✦</span> 脸型分析</h1>
      </div>

      <!-- 引导阶段 -->
      <div v-if="phase === 'guide'" class="guide-phase">
        <div class="guide-header">
          <h2>让系统更了解你</h2>
          <p>分析一次，永久影响你的推荐</p>
        </div>
        <div class="guide-card">
          <div class="face-illustration">👤</div>
          <ul class="tips">
            <li>正面朝向摄像头，保持光线充足</li>
            <li>头发梳到脑后，露出完整脸型</li>
            <li>保持自然表情，不要低头或仰头</li>
          </ul>
        </div>
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        <div class="guide-actions">
          <el-button type="primary" size="large" class="action-btn" @click="startCamera">
            📷 打开摄像头检测
          </el-button>
          <el-button size="large" class="action-btn action-btn-outline" @click="selectPhoto">
            🖼️ 从相册选择照片
          </el-button>
          <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileSelect" />
        </div>
        <div class="privacy-note">照片仅在本地处理，不会上传至服务器</div>
      </div>

      <!-- 摄像头阶段 -->
      <div v-else-if="phase === 'camera'" class="camera-phase">
        <div class="camera-wrap">
          <video ref="videoRef" playsinline muted style="display:none" />
          <canvas ref="canvasRef" class="camera-canvas" />
          <div class="camera-status" :class="{ ok: faceDetected && !cameraWarning, warn: !!cameraWarning }">
            {{ meshReady ? (cameraWarning || (faceDetected ? '✓ 检测到人脸，点击拍照' : '请将脸部对准椭圆框')) : '模型加载中...' }}
          </div>
        </div>
        <div class="camera-hint">请将脸部放入虚线框内，保持左右对称</div>
        <div class="camera-actions">
          <el-button
            type="primary" size="large" class="capture-btn"
            :disabled="!faceDetected || !meshReady || !!cameraWarning"
            @click="capture"
          >拍照分析</el-button>
          <el-button size="large" @click="cancelCamera">取消</el-button>
        </div>
      </div>

      <!-- 分析中 -->
      <div v-else-if="phase === 'analyzing'" class="analyzing-phase">
        <div class="photo-preview" v-if="photoUrl">
          <img :src="photoUrl" class="preview-img" />
          <div class="scan-line" />
        </div>
        <div class="analyzing-text">正在分析你的脸型特征...</div>
        <el-progress :percentage="analyzeProgress" :stroke-width="8" color="#C4906A" class="progress" />
        <div class="analyze-steps">
          <div class="a-step" :class="{ done: analyzeProgress >= 30 }">识别关键点 {{ analyzeProgress >= 30 ? '✓' : '...' }}</div>
          <div class="a-step" :class="{ done: analyzeProgress >= 65 }">计算脸型比例 {{ analyzeProgress >= 65 ? '✓' : '' }}</div>
          <div class="a-step" :class="{ done: analyzeProgress >= 95 }">分析肤色色调 {{ analyzeProgress >= 95 ? '✓' : '' }}</div>
        </div>
      </div>

      <!-- 结果 -->
      <div v-else-if="phase === 'result'" class="result-phase">
        <div class="result-header-text">分析完成</div>

        <!-- 骨骼连线可视化 -->
        <div class="skeleton-wrap" v-if="savedLandmarks">
          <canvas ref="skeletonCanvasRef" class="skeleton-canvas" />
          <div class="skeleton-label">AI 面部测量线</div>
        </div>
        <div class="avatar-circle" v-else>
          <img v-if="photoUrl" :src="photoUrl" class="avatar-img" />
          <span v-else class="avatar-emoji">👤</span>
        </div>

        <div class="result-main">
          <div class="face-type">你的脸型：{{ result.faceType }}</div>
          <div class="skin-tone">肤色色调：{{ result.skinTone }}</div>
        </div>
        <div class="advice-card">
          <div class="advice-title">适合你的款式特征</div>
          <div v-for="tip in result.goodTips" :key="tip" class="advice-item good">✓ {{ tip }}</div>
          <div class="advice-title" style="margin-top:16px">不太推荐的款式</div>
          <div v-for="tip in result.badTips" :key="tip" class="advice-item bad">✗ {{ tip }}</div>
        </div>

        <!-- 不服来辩 -->
        <div class="correction-card">
          <div class="correction-title">💡 AI 测出您是「{{ FACE_TYPE_DESC[result.faceType] || result.faceType }}」</div>
          <div class="correction-sub">如果觉得不完全准确，可能是发型或光线影响。您认为更偏向于：</div>
          <div class="correction-options">
            <button
              v-for="ft in FACE_TYPES_ALL" :key="ft"
              class="correction-btn"
              :class="{ active: ft === result.faceType }"
              @click="correctFaceType(ft)"
            >{{ ft }}</button>
          </div>
        </div>

        <el-button type="primary" size="large" class="cta-btn" @click="gotoRecommend">
          查看为我专属推荐的款式
        </el-button>
        <el-button link class="retest-btn" @click="retest">重新检测</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { updatePrefs } from '../api/user'

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) { resolve(); return }
    const s = document.createElement('script')
    s.src = src; s.onload = resolve; s.onerror = reject
    document.head.appendChild(s)
  })
}

const router = useRouter()
const showTips = ref(true)
function dismissTips() { showTips.value = false }
const phase = ref('guide')
const photoUrl = ref('')
const analyzeProgress = ref(0)
const errorMsg = ref('')
const faceDetected = ref(false)
const meshReady = ref(false)
const cameraWarning = ref('')
const savedLandmarks = ref(null)
const fileInput = ref(null)
const videoRef = ref(null)
const canvasRef = ref(null)
const skeletonCanvasRef = ref(null)

const FACE_TYPES_ALL = ['椭圆脸', '圆脸', '方脸', '长脸', '心形脸']
const FACE_TYPE_DESC = {
  '椭圆脸': '标准鹅蛋脸', '圆脸': '圆润可爱脸',
  '方脸': '英气方脸', '长脸': '精致长脸', '心形脸': '甜美心形脸',
}

const result = ref({ faceType: '', skinTone: '', goodTips: [], badTips: [] })

const GOOD_TIPS_MAP = {
  '椭圆脸': ['弧形耳环更显温柔', '中长款项链拉伸颈部线条', '金色系饰品更显气色'],
  '圆脸':   ['长款耳坠拉长脸型', 'V形项链修饰轮廓', '简约线条感饰品'],
  '方脸':   ['圆润曲线耳环柔化轮廓', '层次感项链', '珍珠类柔和材质'],
  '长脸':   ['宽型耳环增加横向感', '短款项链平衡比例', '几何感饰品'],
  '心形脸': ['水滴形耳坠平衡额头', '中长款项链', '圆润造型饰品'],
}
const BAD_TIPS_MAP = {
  '椭圆脸': ['过于宽大的几何形耳环'],
  '圆脸':   ['圆形大耳环', '短款贴耳饰品'],
  '方脸':   ['棱角分明的方形耳环', '过长直线型耳坠'],
  '长脸':   ['过长下垂耳坠', '窄细型竖向项链'],
  '心形脸': ['宽大夸张耳环', '过于厚重的项链'],
}

let stream = null
let faceMesh = null
let animFrame = null
let lastLandmarks = null

async function startCamera() {
  errorMsg.value = ''
  phase.value = 'camera'
  await nextTick()
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
    })
    const video = videoRef.value
    video.srcObject = stream
    await video.play()

    const canvas = canvasRef.value
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 480

    await initFaceMesh()
  } catch (e) {
    stopCamera()
    phase.value = 'guide'
    if (e.name === 'NotAllowedError') {
      errorMsg.value = '摄像头权限被拒绝，请在浏览器设置中允许访问摄像头'
    } else {
      errorMsg.value = '无法访问摄像头：' + e.message
    }
  }
}

async function initFaceMesh() {
  await loadScript('/mediapipe/face_mesh/face_mesh.js')
  const FaceMesh = window.FaceMesh
  faceMesh = new FaceMesh({
    locateFile: (file) => `/mediapipe/face_mesh/${file}`,
  })
  faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: false,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  })
  faceMesh.onResults(onResults)
  faceMesh.initialize().then(() => {
    meshReady.value = true
    processFrame()
  })
}

function processFrame() {
  if (phase.value !== 'camera' || !videoRef.value) return
  faceMesh.send({ image: videoRef.value }).then(() => {
    animFrame = requestAnimationFrame(processFrame)
  }).catch(() => {
    animFrame = requestAnimationFrame(processFrame)
  })
}

function onResults(results) {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = canvas.width, h = canvas.height

  ctx.save()
  ctx.scale(-1, 1)
  ctx.translate(-w, 0)
  ctx.drawImage(results.image, 0, 0, w, h)
  ctx.restore()

  const detected = results.multiFaceLandmarks?.length > 0
  drawGuideEllipse(ctx, w, h, detected)

  if (detected) {
    faceDetected.value = true
    lastLandmarks = results.multiFaceLandmarks[0]
    drawMesh(ctx, lastLandmarks, w, h)
    runLiveChecks(lastLandmarks, w, h, ctx)
  } else {
    faceDetected.value = false
    lastLandmarks = null
    cameraWarning.value = ''
  }
}

function drawGuideEllipse(ctx, w, h, detected) {
  const cx = w / 2, cy = h * 0.44
  const rx = w * 0.22, ry = h * 0.34
  ctx.save()
  ctx.setLineDash([10, 7])
  ctx.strokeStyle = detected ? 'rgba(196,144,106,0.85)' : 'rgba(255,255,255,0.45)'
  ctx.lineWidth = 2.5
  ctx.beginPath()
  ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2)
  ctx.stroke()
  ctx.setLineDash([])
  // center axis
  ctx.strokeStyle = detected ? 'rgba(196,144,106,0.35)' : 'rgba(255,255,255,0.2)'
  ctx.lineWidth = 1
  ctx.beginPath(); ctx.moveTo(cx, cy - ry); ctx.lineTo(cx, cy + ry); ctx.stroke()
  // eye hints when no face
  if (!detected) {
    ctx.fillStyle = 'rgba(255,255,255,0.3)'
    ;[[cx - rx * 0.38, cy - ry * 0.08], [cx + rx * 0.38, cy - ry * 0.08]].forEach(([ex, ey]) => {
      ctx.beginPath(); ctx.arc(ex, ey, 5, 0, Math.PI * 2); ctx.fill()
    })
  }
  ctx.restore()
}

function runLiveChecks(lms, w, h, ctx) {
  const px = (idx) => (1 - lms[idx].x) * w
  const py = (idx) => lms[idx].y * h

  // symmetry / angle
  const noseX = px(1)
  const eyeMidX = (px(33) + px(263)) / 2
  const eyeSpan = Math.abs(px(263) - px(33))
  if (eyeSpan > 0 && Math.abs(noseX - eyeMidX) / eyeSpan > 0.18) {
    cameraWarning.value = '请正对镜头，不要侧脸哦'; return
  }

  // distance
  const faceW = Math.abs(px(234) - px(454))
  const ratio = faceW / w
  if (ratio < 0.22) { cameraWarning.value = '请离镜头近一点'; return }
  if (ratio > 0.72) { cameraWarning.value = '请离镜头远一点'; return }

  // brightness
  try {
    const cx = Math.round(px(1)), cy = Math.round(py(1))
    const sz = Math.max(10, Math.round(faceW * 0.3))
    const data = ctx.getImageData(Math.max(0, cx - sz / 2), Math.max(0, cy - sz / 2), sz, sz).data
    let sum = 0
    for (let i = 0; i < data.length; i += 4)
      sum += 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]
    const brightness = sum / (data.length / 4)
    if (brightness < 55) { cameraWarning.value = '光线太暗，请换个明亮的地方'; return }
    if (brightness > 210) { cameraWarning.value = '光线过强，请避开强光直射'; return }
  } catch {}

  cameraWarning.value = ''
}

const FACE_OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109,10]

function drawMesh(ctx, lms, w, h) {
  ctx.strokeStyle = 'rgba(196,144,106,0.7)'
  ctx.lineWidth = 1.5
  ctx.beginPath()
  FACE_OVAL.forEach((idx, i) => {
    const x = (1 - lms[idx].x) * w
    const y = lms[idx].y * h
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  })
  ctx.stroke()

  ctx.fillStyle = 'rgba(196,144,106,0.85)'
  const keyPts = [10, 152, 234, 454, 172, 397, 127, 356, 1, 33, 263]
  for (const idx of keyPts) {
    const x = (1 - lms[idx].x) * w
    const y = lms[idx].y * h
    ctx.beginPath()
    ctx.arc(x, y, 3, 0, Math.PI * 2)
    ctx.fill()
  }
}

function capture() {
  if (!lastLandmarks || !canvasRef.value) return
  const lms = lastLandmarks
  savedLandmarks.value = lms

  const offscreen = document.createElement('canvas')
  offscreen.width = canvasRef.value.width
  offscreen.height = canvasRef.value.height
  offscreen.getContext('2d').drawImage(canvasRef.value, 0, 0)
  photoUrl.value = offscreen.toDataURL('image/jpeg', 0.9)

  stopCamera()
  startAnalyze(lms)
}

function stopCamera() {
  if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null }
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
  faceDetected.value = false
  meshReady.value = false
}

function cancelCamera() {
  stopCamera()
  phase.value = 'guide'
}

function startAnalyze(lms) {
  phase.value = 'analyzing'
  analyzeProgress.value = 0
  const interval = setInterval(() => {
    analyzeProgress.value = Math.min(analyzeProgress.value + 4, 100)
    if (analyzeProgress.value >= 100) {
      clearInterval(interval)
      computeResult(lms)
    }
  }, 50)
}

function computeResult(lms) {
  const FACE_TYPES = ['椭圆脸', '圆脸', '方脸', '长脸', '心形脸']
  let faceType

  if (!lms) {
    faceType = FACE_TYPES[Math.floor(Math.random() * FACE_TYPES.length)]
  } else {
    const dist = (a, b) => Math.hypot(lms[a].x - lms[b].x, lms[a].y - lms[b].y)
    const faceHeight = dist(10, 152)
    const faceWidth = dist(234, 454)
    const jawWidth = dist(172, 397)
    const foreheadWidth = dist(127, 356)
    const ratio = faceWidth / faceHeight
    const jawRatio = jawWidth / faceWidth
    const foreheadRatio = foreheadWidth / faceWidth

    if (ratio < 0.67) {
      faceType = '长脸'
    } else if (ratio > 0.87) {
      faceType = jawRatio > 0.82 ? '方脸' : '圆脸'
    } else if (foreheadRatio > jawRatio + 0.09) {
      faceType = '心形脸'
    } else {
      faceType = '椭圆脸'
    }
  }

  const skinTone = analyzeSkinTone(lms)

  result.value = {
    faceType,
    skinTone,
    goodTips: GOOD_TIPS_MAP[faceType] || [],
    badTips: BAD_TIPS_MAP[faceType] || [],
  }
  localStorage.setItem('faceType', `${faceType} · ${skinTone}`)
  syncFaceProfile(faceType, skinTone)
  setTimeout(() => { phase.value = 'result' }, 400)
}

function analyzeSkinTone(lms) {
  try {
    const canvas = document.createElement('canvas')
    const w = 640, h = 480
    canvas.width = w; canvas.height = h
    const ctx = canvas.getContext('2d')
    const img = new Image()
    img.src = photoUrl.value
    ctx.drawImage(img, 0, 0, w, h)

    // sample cheek landmarks (mirrored x)
    const sampleIdxs = [50, 280, 205, 425]
    let totalR = 0, totalG = 0, totalB = 0, count = 0
    for (const idx of sampleIdxs) {
      const x = Math.round((1 - lms[idx].x) * w)
      const y = Math.round(lms[idx].y * h)
      const px = ctx.getImageData(Math.max(0, x - 3), Math.max(0, y - 3), 7, 7).data
      for (let i = 0; i < px.length; i += 4) {
        totalR += px[i]; totalG += px[i + 1]; totalB += px[i + 2]; count++
      }
    }
    if (count === 0) return '中性色调'
    const r = totalR / count, b = totalB / count
    if (r - b > 25) return '暖色调（黄皮）'
    if (b - r > 10) return '冷色调（白皮）'
    return '中性色调'
  } catch {
    return '中性色调'
  }
}

function selectPhoto() {
  fileInput.value?.click()
}

function onFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''
  photoUrl.value = URL.createObjectURL(file)
  startAnalyze(null)
}

function gotoRecommend() {
  router.push('/ai-guide')
}

function retest() {
  photoUrl.value = ''
  analyzeProgress.value = 0
  savedLandmarks.value = null
  result.value = { faceType: '', skinTone: '', goodTips: [], badTips: [] }
  phase.value = 'guide'
}

function syncFaceProfile(faceType, skinTone) {
  if (!localStorage.getItem('token')) return
  updatePrefs({ face_type: faceType, skin_tone: skinTone }).then(res => {
    if (res?.data) {
      localStorage.setItem('user', JSON.stringify(res.data))
    }
  }).catch(() => {})
}

function correctFaceType(faceType) {
  const prev = result.value.faceType
  result.value = {
    ...result.value,
    faceType,
    goodTips: GOOD_TIPS_MAP[faceType] || [],
    badTips: BAD_TIPS_MAP[faceType] || [],
  }
  localStorage.setItem('faceType', `${faceType} · ${result.value.skinTone}`)
  syncFaceProfile(faceType, result.value.skinTone)
  try {
    const log = JSON.parse(localStorage.getItem('faceTypeCorrections') || '[]')
    log.push({ original: prev, corrected: faceType, ts: Date.now() })
    localStorage.setItem('faceTypeCorrections', JSON.stringify(log))
  } catch {}
}

watch(phase, async (val) => {
  if (val === 'result' && savedLandmarks.value) {
    await nextTick()
    drawSkeleton()
  }
})

async function drawSkeleton() {
  const canvas = skeletonCanvasRef.value
  if (!canvas || !savedLandmarks.value || !photoUrl.value) return
  const lms = savedLandmarks.value
  const W = 640, H = 480
  canvas.width = W; canvas.height = H
  const ctx = canvas.getContext('2d')

  const img = new Image()
  img.src = photoUrl.value
  await new Promise(r => { img.onload = r })
  ctx.drawImage(img, 0, 0, W, H)

  const pt = (idx) => ({ x: (1 - lms[idx].x) * W, y: lms[idx].y * H })

  const drawMeasure = (aIdx, bIdx, color, label) => {
    const a = pt(aIdx), b = pt(bIdx)
    ctx.save()
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.setLineDash([7, 5])
    ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 4
    ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke()
    ctx.setLineDash([])
    ;[a, b].forEach(p => {
      ctx.fillStyle = color
      ctx.beginPath(); ctx.arc(p.x, p.y, 5, 0, Math.PI * 2); ctx.fill()
    })
    const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2
    ctx.font = 'bold 14px sans-serif'; ctx.textAlign = 'center'
    ctx.fillStyle = '#000'; ctx.fillText(label, mx + 1, my - 9)
    ctx.fillStyle = color; ctx.fillText(label, mx, my - 10)
    ctx.restore()
  }

  drawMeasure(234, 454, '#4FC3F7', '脸宽')
  drawMeasure(10,  152, '#81C784', '脸长')
  drawMeasure(172, 397, '#FFB74D', '下颌宽')
  drawMeasure(127, 356, '#CE93D8', '额头宽')
}

onUnmounted(() => stopCamera())
</script>

<style scoped>
.face-detect-page { flex: 1; }
.container { max-width: 800px; margin: 0 auto; padding: 0 32px 60px; }

.page-header { padding: 24px 0 20px; }
.page-title { font-size: 24px; font-weight: 800; color: #1A1714; }
.page-title span { color: #C4906A; }

.guide-phase { padding: 0; }
.guide-header { text-align: center; margin-bottom: 32px; }
.guide-header h2 { font-size: 26px; font-weight: 800; color: #1A1714; margin-bottom: 8px; }
.guide-header p { font-size: 14px; color: #6B6B6B; }
.guide-card {
  background: #fff; border-radius: 20px; padding: 40px 32px;
  text-align: center; margin-bottom: 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.face-illustration { font-size: 80px; margin-bottom: 24px; }
.tips { list-style: none; text-align: left; display: inline-block; padding: 0; }
.tips li { font-size: 15px; color: #6B6B6B; padding: 6px 0 6px 20px; position: relative; }
.tips li::before { content: '✦'; position: absolute; left: 0; color: #C4906A; font-size: 10px; top: 9px; }
.guide-actions { display: flex; gap: 16px; margin-bottom: 24px; }
.action-btn { flex: 1; border-radius: 12px; font-size: 15px; font-weight: 700; }
.action-btn-outline { background: #fff; border: 1.5px solid #EBEBEB; color: #1A1714; }
.action-btn-outline:hover { border-color: #C4906A; color: #C4906A; }
.error-msg { background: #fff2f0; border: 1px solid #ffccc7; border-radius: 8px; padding: 10px 16px; font-size: 13px; color: #cf1322; margin-bottom: 16px; }
.privacy-note { text-align: center; font-size: 12px; color: #B0B0B0; }

.camera-phase { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.camera-wrap {
  position: relative; width: 100%; max-width: 640px;
  border-radius: 20px; overflow: hidden; background: #1A1714;
  box-shadow: 0 4px 24px rgba(0,0,0,.2);
}
.camera-canvas { display: block; width: 100%; aspect-ratio: 4/3; }
.camera-hint { font-size: 13px; color: rgba(255,255,255,0.7); background: rgba(0,0,0,0.45); padding: 5px 16px; border-radius: 20px; }
.camera-status {
  position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%);
  background: rgba(0,0,0,0.55); color: rgba(255,255,255,0.8);
  font-size: 13px; padding: 6px 18px; border-radius: 20px;
  white-space: nowrap; transition: color .3s; max-width: 90%;
}
.camera-status.ok   { color: #C4906A; }
.camera-status.warn { color: #FFD166; }
.camera-actions { display: flex; gap: 16px; }
.capture-btn { min-width: 160px; border-radius: 12px; font-size: 16px; font-weight: 700; }

.analyzing-phase {
  padding: 40px 0; display: flex; flex-direction: column;
  align-items: center; gap: 24px;
}
.photo-preview {
  position: relative; width: 220px; height: 220px;
  border-radius: 50%; overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,.1);
}
.preview-img { width: 100%; height: 100%; object-fit: cover; }
.scan-line {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, transparent 40%, rgba(196,144,106,.3) 50%, transparent 60%);
  animation: scan 2s linear infinite;
}
@keyframes scan { 0% { transform: translateY(-100%); } 100% { transform: translateY(100%); } }
.analyzing-text { font-size: 16px; color: #6B6B6B; }
.progress { width: 100%; max-width: 400px; }
.analyze-steps { width: 100%; max-width: 400px; }
.a-step { font-size: 14px; color: #B0B0B0; padding: 4px 0; }
.a-step.done { color: #67c23a; }

.result-phase {
  padding: 20px 0; display: flex; flex-direction: column;
  align-items: center; gap: 24px;
}
.result-header-text { font-size: 26px; font-weight: 800; color: #1A1714; }
.avatar-circle {
  width: 140px; height: 140px; border-radius: 50%; overflow: hidden;
  border: 4px solid #C4906A; display: flex; align-items: center;
  justify-content: center; background: #F0F0F0;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-emoji { font-size: 64px; }
.result-main { text-align: center; }
.face-type { font-size: 22px; font-weight: 800; color: #1A1714; margin-bottom: 6px; }
.skin-tone { font-size: 15px; color: #6B6B6B; }
.advice-card {
  width: 100%; background: #fff; border-radius: 16px; padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.advice-title { font-size: 14px; font-weight: 600; color: #6B6B6B; margin-bottom: 12px; }
.advice-item { font-size: 14px; padding: 5px 0; }
.advice-item.good { color: #67c23a; }
.advice-item.bad { color: #f56c6c; }
.cta-btn {
  width: 100%; max-width: 400px; border-radius: 12px; font-size: 16px; font-weight: 700;
  background: linear-gradient(135deg, #1A1714, #4A3020); border-color: transparent;
}
.cta-btn:hover { background: linear-gradient(135deg, #2D231A, #6B4226); }
.retest-btn { color: #B0B0B0; font-size: 14px; }

.skeleton-wrap {
  width: 100%; max-width: 480px; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,.15); position: relative;
}
.skeleton-canvas { display: block; width: 100%; aspect-ratio: 4/3; }
.skeleton-label {
  position: absolute; bottom: 10px; right: 14px;
  font-size: 11px; color: rgba(255,255,255,0.7);
  background: rgba(0,0,0,0.45); padding: 3px 10px; border-radius: 10px;
}

.correction-card {
  width: 100%; background: #F9F6F2; border-radius: 16px; padding: 20px 24px;
  border: 1.5px solid #EDE0D4;
}
.correction-title { font-size: 15px; font-weight: 700; color: #1A1714; margin-bottom: 6px; }
.correction-sub   { font-size: 13px; color: #6B6B6B; margin-bottom: 14px; }
.correction-options { display: flex; gap: 10px; flex-wrap: wrap; }
.correction-btn {
  padding: 7px 18px; border-radius: 20px; font-size: 13px; font-weight: 600;
  border: 1.5px solid #DCCFC4; background: #fff; color: #6B6B6B;
  cursor: pointer; transition: all .18s;
}
.correction-btn:hover  { border-color: #C4906A; color: #C4906A; }
.correction-btn.active { border-color: #C4906A; background: #C4906A; color: #fff; }

.tips-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.tips-modal {
  background: #fff; border-radius: 24px; padding: 32px 28px;
  max-width: 580px; width: 100%; text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  animation: modal-in .28s ease;
}
@keyframes modal-in {
  from { transform: scale(0.92); opacity: 0; }
  to   { transform: scale(1);    opacity: 1; }
}
.tips-modal-title { font-size: 20px; font-weight: 800; color: #1A1714; margin-bottom: 6px; }
.tips-modal-sub   { font-size: 14px; color: #6B6B6B; margin-bottom: 24px; }
.tips-cards { display: flex; gap: 14px; margin-bottom: 20px; }
.tip-card {
  flex: 1; background: #FFF8F5; border-radius: 14px;
  padding: 16px 10px; border: 1.5px solid #FFE0CC;
}
.tip-figure { width: 70px; height: 90px; margin: 0 auto 10px; }
.tip-figure svg { width: 100%; height: 100%; }
.tip-no   { font-size: 12px; font-weight: 700; color: #E74C3C; margin-bottom: 5px; }
.tip-why  { font-size: 11px; color: #6B6B6B; line-height: 1.55; }
.tips-correct {
  display: flex; justify-content: center; gap: 18px;
  margin-bottom: 20px; font-size: 13px; font-weight: 600; color: #27AE60;
}
.tips-confirm-btn { width: 100%; border-radius: 12px; font-size: 15px; font-weight: 700; }

</style>
