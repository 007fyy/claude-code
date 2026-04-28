<template>
  <div class="progress-page">
    <div class="topbar">
      <el-button :icon="ArrowLeft" circle @click="$router.back()" />
      <span class="title">售后进度</span>
    </div>

    <div class="status-header">
      <div class="status-label">退货退款 · {{ currentStatusText }}</div>
    </div>

    <!-- 进度条 -->
    <div class="steps-section">
      <el-steps :active="activeStep" align-center>
        <el-step title="已申请" :description="applyDate" />
        <el-step title="审核通过" />
        <el-step title="已寄回" />
        <el-step title="退款到账" :description="activeStep < 3 ? '预计5-7天' : ''" />
      </el-steps>
    </div>

    <!-- 当前状态说明 -->
    <div class="section">
      <div class="section-title">当前状态说明</div>
      <div class="status-card">
        <div class="status-icon">{{ statusIcon }}</div>
        <div class="status-desc">{{ statusDesc }}</div>
        <div class="status-sub">{{ statusSub }}</div>
      </div>

      <!-- 审核通过后显示退货地址 -->
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

    <!-- 处理记录 -->
    <div class="section">
      <div class="section-title">处理记录</div>
      <div v-for="log in logs" :key="log.time" class="log-item">
        <span class="log-time">{{ log.time }}</span>
        <span class="log-text">{{ log.text }}</span>
      </div>
    </div>

    <!-- 底部操作 -->
    <div class="bottom-bar">
      <el-button size="large" class="action-btn">联系客服</el-button>
      <el-button size="large" class="action-btn" type="danger" plain v-if="activeStep === 0" @click="cancelApply">撤销申请</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
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
.progress-page {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100dvh;
  background: #f7f5f3;
  padding-bottom: 80px;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
}
.title { font-size: 16px; font-weight: 700; }

.status-header {
  background: linear-gradient(135deg, #c0876a, #e8b49a);
  padding: 16px 20px;
  color: #fff;
}
.status-label { font-size: 16px; font-weight: 700; }

.steps-section {
  background: #fff;
  padding: 24px 8px;
  margin-bottom: 12px;
}

.section {
  background: #fff;
  padding: 16px;
  margin-bottom: 12px;
}
.section-title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 14px; }

.status-card {
  background: #f9f9f9;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.status-icon { font-size: 28px; }
.status-desc { font-size: 15px; font-weight: 600; color: #333; }
.status-sub  { font-size: 13px; color: #888; }

.return-address {
  margin-top: 16px;
  background: #f0f7ff;
  border-radius: 10px;
  padding: 14px;
}

.addr-title { font-size: 13px; font-weight: 600; color: #5b9bd5; margin-bottom: 6px; }
.addr-text  { font-size: 14px; color: #333; margin-bottom: 4px; line-height: 1.6; }
.addr-phone { font-size: 13px; color: #888; margin-bottom: 12px; }
.tracking-input { margin-top: 8px; }

.log-item {
  display: flex;
  gap: 12px;
  font-size: 13px;
  padding: 6px 0;
  border-bottom: 1px solid #f5f5f5;
}
.log-item:last-child { border-bottom: none; }
.log-time { color: #bbb; flex-shrink: 0; }
.log-text { color: #555; }

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  z-index: 100;
}

.action-btn { flex: 1; border-radius: 24px; }
</style>
