<template>
  <div class="progress-page">
    <div class="container">
      <div class="page-header">
        <el-button text @click="$router.back()">← 返回</el-button>
        <h1 class="page-title">售后进度</h1>
      </div>

      <div class="status-banner">
        <div class="status-label">退货退款 · {{ currentStatusText }}</div>
      </div>

      <div class="steps-card">
        <el-steps :active="activeStep" align-center>
          <el-step title="已申请" :description="applyDate" />
          <el-step title="审核通过" />
          <el-step title="已寄回" />
          <el-step title="退款到账" :description="activeStep < 3 ? '预计5-7天' : ''" />
        </el-steps>
      </div>

      <div class="content-grid">
        <div class="content-left">
          <div class="section">
            <div class="section-title">当前状态说明</div>
            <div class="status-card">
              <div class="status-icon">{{ statusIcon }}</div>
              <div class="status-desc">{{ statusDesc }}</div>
              <div class="status-sub">{{ statusSub }}</div>
            </div>

            <div v-if="activeStep >= 1" class="return-address">
              <div class="addr-title">退货地址</div>
              <div class="addr-text">浙江省杭州市余杭区某某路100号 珑饰仓库（收）</div>
              <div class="addr-phone">0571-88888888</div>
              <el-input
                v-if="activeStep === 1"
                v-model="trackingNo"
                placeholder="填写快递单号（寄出后填写）"
                class="tracking-input"
              >
                <template #append>
                  <el-button @click="submitTracking" :loading="submittingTracking">确认</el-button>
                </template>
              </el-input>
            </div>
          </div>
        </div>

        <div class="content-right">
          <div class="section">
            <div class="section-title">处理记录</div>
            <div v-for="log in logs" :key="log.time" class="log-item">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-text">{{ log.text }}</span>
            </div>
          </div>

          <div class="action-btns">
            <el-button size="large" class="action-btn">联系客服</el-button>
            <el-button size="large" class="action-btn" type="danger" plain v-if="activeStep === 0" @click="cancelApply">撤销申请</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const activeStep = ref(0)
const trackingNo = ref('')
const submittingTracking = ref(false)

const now = new Date()
const applyDate = `${now.getMonth() + 1}-${now.getDate()}`

const STATUS_LIST = [
  { text: '待审核',   icon: '⏳', desc: '等待商家审核', sub: '预计 24 小时内完成' },
  { text: '待寄回',   icon: '📦', desc: '请将商品邮寄至下方地址', sub: '寄出后请填写快递单号' },
  { text: '待入库',   icon: '🔍', desc: '等待商家确认收货', sub: '确认后将尽快处理退款' },
  { text: '退款完成', icon: '✅', desc: '退款已处理完成', sub: '退款将在1-3个工作日到账' },
]

const currentStatusText = computed(() => STATUS_LIST[activeStep.value]?.text)
const statusIcon        = computed(() => STATUS_LIST[activeStep.value]?.icon)
const statusDesc        = computed(() => STATUS_LIST[activeStep.value]?.desc)
const statusSub         = computed(() => STATUS_LIST[activeStep.value]?.sub)

const logs = computed(() => {
  const base = [{ time: `${applyDate} 14:55`, text: '用户提交申请' }]
  if (activeStep.value >= 1) base.push({ time: `${applyDate} 16:20`, text: '商家审核通过' })
  if (activeStep.value >= 2) base.push({ time: `${applyDate} 20:10`, text: '用户已寄回，快递单号已填写' })
  if (activeStep.value >= 3) base.push({ time: `${applyDate} 次日`, text: '退款已处理，等待到账' })
  return base.reverse()
})

function submitTracking() {
  if (!trackingNo.value.trim()) { ElMessage.warning('请填写快递单号'); return }
  submittingTracking.value = true
  setTimeout(() => {
    submittingTracking.value = false
    activeStep.value = 2
    ElMessage.success('快递单号已提交')
  }, 800)
}

async function cancelApply() {
  await ElMessageBox.confirm('确认撤销售后申请？', '提示', { type: 'warning' })
  ElMessage.success('申请已撤销')
  router.back()
}
</script>

<style scoped>
.progress-page { flex: 1; }
.container { max-width: 900px; margin: 0 auto; padding: 0 32px 60px; }

.page-header {
  display: flex; align-items: center; gap: 12px; padding: 24px 0 20px;
}
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; }

.status-banner {
  background: linear-gradient(135deg, #C4906A, #e8b49a);
  padding: 20px 24px; border-radius: 16px; color: #fff; margin-bottom: 20px;
}
.status-label { font-size: 18px; font-weight: 700; }

.steps-card {
  background: #fff; padding: 24px; border-radius: 16px;
  margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,.07);
}

.content-grid {
  display: grid; grid-template-columns: 1fr 320px; gap: 20px; align-items: start;
}

.section {
  background: #fff; border-radius: 16px; padding: 20px 24px;
  margin-bottom: 16px; box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.section-title { font-size: 15px; font-weight: 700; color: #1A1714; margin-bottom: 14px; }

.status-card {
  background: #FAF9F7; border-radius: 12px; padding: 18px;
  display: flex; flex-direction: column; gap: 6px;
}
.status-icon { font-size: 28px; }
.status-desc { font-size: 15px; font-weight: 600; color: #1A1714; }
.status-sub { font-size: 13px; color: #6B6B6B; }

.return-address {
  margin-top: 16px; background: #f0f7ff;
  border-radius: 12px; padding: 16px;
}
.addr-title { font-size: 13px; font-weight: 600; color: #5b9bd5; margin-bottom: 6px; }
.addr-text { font-size: 14px; color: #1A1714; margin-bottom: 4px; line-height: 1.6; }
.addr-phone { font-size: 13px; color: #6B6B6B; margin-bottom: 12px; }
.tracking-input { margin-top: 8px; }

.log-item {
  display: flex; gap: 14px; font-size: 13px;
  padding: 8px 0; border-bottom: 1px solid #F0F0F0;
}
.log-item:last-child { border-bottom: none; }
.log-time { color: #B0B0B0; flex-shrink: 0; }
.log-text { color: #6B6B6B; }

.action-btns { display: flex; flex-direction: column; gap: 10px; }
.action-btn { width: 100%; border-radius: 12px; }
</style>
