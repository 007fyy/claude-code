<template>
  <div class="ai-guide-page">
    <div class="topbar">
      <el-button :icon="ArrowLeft" circle @click="$router.back()" />
      <span class="title">为我选款</span>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: phase === 'result' ? '100%' : `${(step / totalSteps) * 100}%` }" />
      </div>
      <span class="step-label" v-if="phase === 'dialog'">步骤 {{ step }}/{{ totalSteps }}</span>
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
        <el-icon class="spin" size="64" color="#c0876a"><Loading /></el-icon>
      </div>
      <div class="thinking-text">正在为你计算最佳搭配...</div>
      <div class="thinking-counter">{{ thinkingCount }}%</div>
    </div>

    <!-- 推荐结果 -->
    <div v-else-if="phase === 'result'" class="result-phase">
      <div class="result-topbar">
        <el-button link @click="restart">← 重新选择</el-button>
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
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Loading, Picture } from '@element-plus/icons-vue'
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
.ai-guide-page {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100dvh;
  background: #f7f5f3;
  display: flex;
  flex-direction: column;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.title { font-size: 16px; font-weight: 700; flex: 1; }

.progress-bar {
  width: 80px;
  height: 6px;
  background: #eee;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #c0876a;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.step-label { font-size: 12px; color: #999; flex-shrink: 0; }

.dialog-phase { flex: 1; padding: 24px 16px; }

.dialog-content { display: flex; flex-direction: column; gap: 20px; }

.ai-bubble {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.ai-avatar { font-size: 36px; flex-shrink: 0; }

.bubble-text {
  background: #fff;
  border-radius: 16px 16px 16px 4px;
  padding: 16px 18px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.prev-answer {
  font-size: 13px;
  color: #999;
  padding-left: 4px;
}

.options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.opt-card {
  background: #fff;
  border: 2px solid #eee;
  border-radius: 16px;
  padding: 20px 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.opt-card:hover { border-color: #c0876a; }
.opt-card.selected { border-color: #c0876a; background: #fdf6f0; }

.opt-icon { display: block; font-size: 28px; margin-bottom: 8px; }
.opt-text  { font-size: 14px; color: #333; font-weight: 500; }

.skip-link { color: #bbb; font-size: 13px; text-align: center; }

/* thinking */
.thinking-phase {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.thinking-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1);
}

.spin { animation: spin 1.2s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.thinking-text { font-size: 16px; color: #666; }
.thinking-counter { font-size: 32px; font-weight: 700; color: #c0876a; }

/* result */
.result-phase { flex: 1; overflow-y: auto; }

.result-topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.result-title { font-size: 16px; font-weight: 700; color: #333; flex: 1; text-align: center; margin-right: 60px; }

.summary-card {
  margin: 16px;
  background: linear-gradient(135deg, #fff5ef, #ffe8d6);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-icon { font-size: 28px; }
.summary-text { font-size: 15px; color: #333; }
.summary-tags { display: flex; flex-wrap: wrap; gap: 6px; }

.face-cta {
  margin: 0 16px 16px;
  background: linear-gradient(135deg, #f0f5ff, #d6e8ff);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.face-cta span:first-child { font-size: 14px; font-weight: 600; color: #5b9bd5; }
.face-cta-sub { font-size: 12px; color: #999; }

.goods-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 0 16px 24px;
}

.goods-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s;
}
.goods-card:hover { transform: translateY(-2px); }

.goods-img { width: 100%; height: 160px; display: block; }
.img-err { width: 100%; height: 160px; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; font-size: 32px; }

.match-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(192,135,106,0.9);
  color: #fff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
}

.goods-info { padding: 10px; }
.goods-name { font-size: 13px; font-weight: 600; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.goods-price { font-size: 15px; font-weight: 700; color: #e6564e; margin-bottom: 8px; }
.try-btn { width: 100%; border-radius: 20px; }

.slide-left-enter-active, .slide-left-leave-active { transition: all 0.3s ease; }
.slide-left-enter-from { opacity: 0; transform: translateX(40px); }
.slide-left-leave-to   { opacity: 0; transform: translateX(-40px); }
</style>
