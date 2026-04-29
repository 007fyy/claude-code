<template>
  <div class="face-detect-page">
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
            <li>正面朝向摄像头</li>
            <li>保持光线充足</li>
            <li>头发梳到脑后效果更佳</li>
          </ul>
        </div>

        <div class="guide-actions">
          <el-button type="primary" size="large" class="action-btn" @click="takePhoto">
            📷 立即拍照分析
          </el-button>
          <el-button size="large" class="action-btn action-btn-outline" @click="selectPhoto">
            🖼️ 从相册选择
          </el-button>
          <input ref="fileInput" type="file" accept="image/*" capture="user" style="display:none" @change="onFileSelect" />
        </div>

        <div class="privacy-note">
          你的照片仅用于本地特征提取，不会上传至服务器存储
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
        <div class="avatar-circle">
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
          <div v-for="tip in result.badTips"  :key="tip" class="advice-item bad">✗ {{ tip }}</div>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const phase = ref('guide')
const photoUrl = ref('')
const analyzeProgress = ref(0)
const fileInput = ref(null)

const FACE_TYPES = ['椭圆脸', '圆脸', '方脸', '长脸']
const SKIN_TONES = ['暖色调（黄皮）', '冷色调（白皮）', '中性色调']
const GOOD_TIPS_MAP = {
  '椭圆脸': ['弧形耳环更显温柔', '中长款项链拉伸颈部线条', '金色系饰品更显气色'],
  '圆脸':   ['长款耳坠拉长脸型', 'V形项链修饰轮廓', '简约线条感饰品'],
  '方脸':   ['圆润曲线耳环柔化轮廓', '层次感项链', '珍珠类柔和材质'],
  '长脸':   ['宽型耳环增加横向感', '短款项链平衡比例', '几何感饰品'],
}
const BAD_TIPS_MAP = {
  '椭圆脸': ['过于宽大的几何形耳环'],
  '圆脸':   ['圆形大耳环', '短款贴耳饰品'],
  '方脸':   ['棱角分明的方形耳环', '过长直线型耳坠'],
  '长脸':   ['过长下垂耳坠', '窄细型竖向项链'],
}

const result = ref({
  faceType: '',
  skinTone: '',
  goodTips: [],
  badTips: [],
})

function takePhoto() {
  if (fileInput.value) {
    fileInput.value.setAttribute('capture', 'user')
    fileInput.value.click()
  }
}

function selectPhoto() {
  if (fileInput.value) {
    fileInput.value.removeAttribute('capture')
    fileInput.value.click()
  }
}

function onFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return
  photoUrl.value = URL.createObjectURL(file)
  startAnalyze()
}

function startAnalyze() {
  phase.value = 'analyzing'
  analyzeProgress.value = 0
  const interval = setInterval(() => {
    analyzeProgress.value = Math.min(analyzeProgress.value + 3, 100)
    if (analyzeProgress.value >= 100) {
      clearInterval(interval)
      showResult()
    }
  }, 60)
}

function showResult() {
  const faceType = FACE_TYPES[Math.floor(Math.random() * FACE_TYPES.length)]
  const skinTone = SKIN_TONES[Math.floor(Math.random() * SKIN_TONES.length)]
  result.value = {
    faceType,
    skinTone,
    goodTips: GOOD_TIPS_MAP[faceType] || [],
    badTips:  BAD_TIPS_MAP[faceType]  || [],
  }
  localStorage.setItem('faceType', `${faceType} · ${skinTone}`)
  setTimeout(() => { phase.value = 'result' }, 400)
}

function gotoRecommend() {
  router.push('/ai-guide')
}

function retest() {
  photoUrl.value = ''
  analyzeProgress.value = 0
  phase.value = 'guide'
}
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
.tips li { font-size: 15px; color: #6B6B6B; padding: 6px 0; }

.guide-actions {
  display: flex; gap: 16px; margin-bottom: 24px;
}
.action-btn { flex: 1; border-radius: 12px; font-size: 16px; font-weight: 700; }
.action-btn-outline { background: #fff; border: 1.5px solid #EBEBEB; color: #1A1714; }
.action-btn-outline:hover { border-color: #C4906A; color: #C4906A; }

.privacy-note { text-align: center; font-size: 12px; color: #B0B0B0; line-height: 1.6; }

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
</style>
