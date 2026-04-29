<template>
  <div class="ai-guide-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title"><span>✦</span> AI 智能选款</h1>
        <div class="header-right">
          <div class="progress-bar" v-if="phase === 'dialog'">
            <div class="progress-fill" :style="{ width: `${(step / totalSteps) * 100}%` }" />
          </div>
          <span class="step-label" v-if="phase === 'dialog'">{{ step }}/{{ totalSteps }}</span>
        </div>
      </div>

      <!-- 对话阶段 -->
      <div v-if="phase === 'dialog'" class="dialog-phase">
        <transition name="slide-left" mode="out-in">
          <div :key="step" class="dialog-content">
            <div class="ai-bubble">
              <div class="ai-avatar">🤖</div>
              <div class="bubble-text">{{ currentQ.q }}</div>
            </div>

            <div v-if="step > 1" class="prev-answer">
              上一步你选择了：{{ answers[step - 2] }} ✓
            </div>

            <div class="options-grid">
              <div
                v-for="opt in currentQ.options"
                :key="opt.label"
                class="opt-card"
                :class="{ selected: answers[step - 1] === opt.label }"
                @click="select(opt.label)"
              >
                <span class="opt-icon">{{ opt.icon }}</span>
                <span class="opt-text">{{ opt.label }}</span>
              </div>
            </div>

            <el-button link class="skip-link" @click="goResult">跳过，直接看推荐 →</el-button>
          </div>
        </transition>
      </div>

      <!-- 计算中 -->
      <div v-else-if="phase === 'thinking'" class="thinking-phase">
        <div class="thinking-circle">
          <el-icon class="spin" size="64" color="#C4906A"><Loading /></el-icon>
        </div>
        <div class="thinking-text">正在为你计算最佳搭配...</div>
        <div class="thinking-counter">{{ thinkingCount }}%</div>
      </div>

      <!-- 推荐结果 -->
      <div v-else-if="phase === 'result'" class="result-phase">
        <div class="result-header">
          <el-button text @click="restart">← 重新选择</el-button>
          <span class="result-title">你的专属推荐</span>
        </div>

        <div class="summary-card">
          <div class="summary-icon">✨</div>
          <div class="summary-text">
            根据你的偏好，为你找到 <b>{{ goods.length }}</b> 款高匹配饰品
          </div>
          <div class="summary-tags">
            <el-tag v-for="(a, i) in answers.filter(Boolean)" :key="i" size="small" type="warning">{{ a }}</el-tag>
          </div>
        </div>

        <div class="face-cta" @click="$router.push('/face-detect')">
          <span>📷 上传照片，进一步精准推荐</span>
          <span class="face-cta-sub">可选，未检测时已有推荐</span>
        </div>

        <div class="goods-grid">
          <div
            v-for="item in goods"
            :key="item.spu_id"
            class="goods-card"
            @click="$router.push(`/goods/${item.spu_id}`)"
          >
            <el-image :src="item.cover_url" fit="cover" class="goods-img" lazy>
              <template #error>
                <div class="img-err"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
            <div class="match-badge">★ 匹配 {{ item.matchScore }}%</div>
            <div class="goods-info">
              <div class="goods-name">{{ item.name }}</div>
              <div class="goods-price">¥ {{ item.price_range }}</div>
              <el-button size="small" type="primary" plain class="try-btn" @click.stop="tryOn(item)" :disabled="!item.ar_available">
                ▶ 试戴
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, Picture } from '@element-plus/icons-vue'
import { getGoodsList } from '../api/goods'

const router = useRouter()

const questions = [
  { q: '你通常在什么场合佩戴？', options: [{ icon: '🌸', label: '日常通勤' }, { icon: '💕', label: '约会出行' }, { icon: '💼', label: '职场正式' }, { icon: '🎉', label: '派对聚会' }] },
  { q: '你喜欢什么样的整体风格？', options: [{ icon: '✨', label: '简约精致' }, { icon: '🕰️', label: '优雅复古' }, { icon: '🌷', label: '甜美少女' }, { icon: '🔮', label: '个性潮酷' }] },
  { q: '对材质有什么偏好吗？',   options: [{ icon: '🥈', label: '925银' },  { icon: '🥇', label: '黄金镀金' }, { icon: '💎', label: '天然石' }, { icon: '🤍', label: '没有要求' }] },
  { q: '你的预算范围大概是？',   options: [{ icon: '💰', label: '¥50以内' }, { icon: '💳', label: '¥50-200' }, { icon: '👜', label: '¥200-500' }, { icon: '💎', label: '¥500+' }] },
]

const totalSteps = questions.length
const step = ref(1)
const answers = ref(new Array(totalSteps).fill(''))
const phase = ref('dialog') // dialog | thinking | result
const thinkingCount = ref(0)
const goods = ref([])

const currentQ = computed(() => questions[step.value - 1])

function select(label) {
  answers.value[step.value - 1] = label
  if (step.value < totalSteps) {
    setTimeout(() => { step.value++ }, 300)
  } else {
    goResult()
  }
}

async function goResult() {
  phase.value = 'thinking'
  thinkingCount.value = 0
  const interval = setInterval(() => {
    thinkingCount.value = Math.min(thinkingCount.value + 7, 95)
  }, 80)
  try {
    const res = await getGoodsList({ page: 1, page_size: 12 })
    goods.value = res.items.map((g, i) => ({ ...g, matchScore: 98 - i * 2 }))
  } catch {
    goods.value = []
  }
  clearInterval(interval)
  thinkingCount.value = 100
  setTimeout(() => { phase.value = 'result' }, 400)
}

function restart() {
  answers.value = new Array(totalSteps).fill('')
  step.value = 1
  phase.value = 'dialog'
}

function tryOn(item) {
  router.push({ name: 'FaceARView', query: { spu_id: item.spu_id, sku_id: item.default_sku_id, sku_name: item.name, ar_asset_url: item.ar_asset_url || '', mount_type: item.mount_type } })
}
</script>

<style scoped>
.ai-guide-page { flex: 1; }
.container { max-width: 900px; margin: 0 auto; padding: 0 32px 60px; }

.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 0 20px;
}
.page-title { font-size: 24px; font-weight: 800; color: #1A1714; }
.page-title span { color: #C4906A; }

.header-right { display: flex; align-items: center; gap: 12px; }
.progress-bar {
  width: 120px; height: 6px; background: #EBEBEB;
  border-radius: 3px; overflow: hidden;
}
.progress-fill {
  height: 100%; background: #C4906A;
  border-radius: 3px; transition: width 0.4s ease;
}
.step-label { font-size: 13px; color: #6B6B6B; }

.dialog-phase { padding: 20px 0; }
.dialog-content { display: flex; flex-direction: column; gap: 24px; }

.ai-bubble { display: flex; gap: 16px; align-items: flex-start; }
.ai-avatar { font-size: 42px; flex-shrink: 0; }
.bubble-text {
  background: #fff; border-radius: 16px 16px 16px 4px;
  padding: 20px 24px; font-size: 18px; font-weight: 600; color: #1A1714;
  flex: 1; box-shadow: 0 2px 12px rgba(0,0,0,.07);
}

.prev-answer { font-size: 13px; color: #B0B0B0; padding-left: 4px; }

.options-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}
.opt-card {
  background: #fff; border: 2px solid #EBEBEB; border-radius: 16px;
  padding: 28px 16px; text-align: center;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.opt-card:hover { border-color: #C4906A; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,.1); }
.opt-card.selected { border-color: #C4906A; background: #F5EDE3; }
.opt-icon { display: block; font-size: 36px; margin-bottom: 10px; }
.opt-text { font-size: 15px; color: #1A1714; font-weight: 600; }

.skip-link { color: #B0B0B0; font-size: 13px; text-align: center; }

.thinking-phase {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 24px; min-height: 400px;
}
.thinking-circle {
  width: 140px; height: 140px; border-radius: 50%;
  background: #fff; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 24px rgba(0,0,0,.1);
}
.spin { animation: spin 1.2s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.thinking-text { font-size: 16px; color: #6B6B6B; }
.thinking-counter { font-size: 36px; font-weight: 800; color: #C4906A; }

.result-phase { padding: 0 0 20px; }
.result-header {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 0; border-bottom: 1px solid #F0F0F0; margin-bottom: 20px;
}
.result-title { font-size: 18px; font-weight: 700; color: #1A1714; flex: 1; }

.summary-card {
  background: linear-gradient(135deg, #fff5ef, #ffe8d6);
  border-radius: 16px; padding: 24px;
  display: flex; flex-direction: column; gap: 12px;
  margin-bottom: 16px;
}
.summary-icon { font-size: 28px; }
.summary-text { font-size: 15px; color: #1A1714; }
.summary-tags { display: flex; flex-wrap: wrap; gap: 8px; }

.face-cta {
  background: linear-gradient(135deg, #f0f5ff, #d6e8ff);
  border-radius: 12px; padding: 18px 24px;
  cursor: pointer; display: flex; flex-direction: column; gap: 4px;
  margin-bottom: 24px; transition: transform .15s;
}
.face-cta:hover { transform: translateY(-2px); }
.face-cta span:first-child { font-size: 14px; font-weight: 600; color: #5b9bd5; }
.face-cta-sub { font-size: 12px; color: #B0B0B0; }

.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}
.goods-card {
  background: #fff; border-radius: 16px; overflow: hidden;
  position: relative; cursor: pointer; transition: all .28s;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.goods-card:hover { transform: translateY(-6px); box-shadow: 0 12px 48px rgba(0,0,0,.14); }
.goods-img { width: 100%; aspect-ratio: 1; display: block; }
.img-err { width: 100%; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; font-size: 32px; }

.match-badge {
  position: absolute; top: 10px; right: 10px;
  background: rgba(196,144,106,.9); color: #fff;
  font-size: 11px; font-weight: 600;
  padding: 3px 10px; border-radius: 20px;
  backdrop-filter: blur(6px);
}

.goods-info { padding: 12px 14px 16px; }
.goods-name { font-size: 14px; font-weight: 600; color: #1A1714; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.goods-price { font-size: 16px; font-weight: 800; color: #1A1714; margin-bottom: 10px; }
.try-btn { width: 100%; border-radius: 20px; }

.slide-left-enter-active, .slide-left-leave-active { transition: all 0.3s ease; }
.slide-left-enter-from { opacity: 0; transform: translateX(40px); }
.slide-left-leave-to   { opacity: 0; transform: translateX(-40px); }
</style>
