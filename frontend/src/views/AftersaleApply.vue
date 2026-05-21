<template>
  <div class="aftersale-apply-page">
    <div class="container">
      <div class="page-header">
        <el-button text @click="$router.back()">← 返回</el-button>
        <h1 class="page-title">申请售后</h1>
      </div>

      <div class="apply-card">
        <el-form :model="form" ref="formRef" class="apply-form">
          <div class="form-section">
            <div class="form-section-title">选择售后方式</div>
            <el-radio-group v-model="form.type" class="type-group">
              <el-radio label="refund">退货退款</el-radio>
              <el-radio label="exchange">换货</el-radio>
            </el-radio-group>
          </div>

          <div class="form-section">
            <div class="form-section-title">退货原因（必选）</div>
            <el-radio-group v-model="form.reason" class="reason-group" @change="onReasonChange">
              <el-radio v-for="r in reasons" :key="r.value" :label="r.value" class="reason-radio">
                {{ r.label }}
              </el-radio>
            </el-radio-group>

            <transition name="fade">
              <div v-if="form.reason" class="remark-area">
                <div class="remark-label">补充说明（选填）</div>
                <el-input
                  v-model="form.remark"
                  type="textarea"
                  :rows="3"
                  :placeholder="remarkPlaceholder"
                />
              </div>
            </transition>
          </div>

          <div class="form-section">
            <div class="form-section-title">上传图片（选填，最多3张）</div>
            <div class="upload-area">
              <div
                v-for="i in 3"
                :key="i"
                class="upload-slot"
                @click="triggerUpload(i)"
              >
                <img v-if="photos[i - 1]" :src="photos[i - 1]" class="uploaded-img" />
                <div v-else class="upload-placeholder">＋</div>
              </div>
              <input ref="photoInput" type="file" accept="image/*" multiple style="display:none" @change="onPhotoSelect" />
            </div>
          </div>

          <el-button type="primary" size="large" class="submit-btn" :loading="submitting" @click="submit">
            提交申请
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { applyRefund } from '../api/order'

const route     = useRoute()
const router    = useRouter()
const formRef   = ref(null)
const photoInput = ref(null)
const submitting = ref(false)
const photos = ref([null, null, null])

// order_item_id comes from route query (set by OrderDetail.vue when clicking 申请售后)
const orderItemId = computed(() => Number(route.query.order_item_id))

const form = ref({
  type:   'refund',
  reason: '',
  remark: '',
})

const reasons = [
  { value: 'quality',   label: '商品质量问题' },
  { value: 'mismatch',  label: '与描述不符' },
  { value: 'effect',    label: '佩戴效果不符合预期' },
  { value: 'size',      label: '尺寸/规格不合适' },
  { value: 'dislike',   label: '不喜欢/不想要了' },
  { value: 'other',     label: '其他' },
]

const remarkPlaceholder = computed(() => {
  if (form.value.reason === 'effect') return '请简单描述哪里不合适，帮助我们优化推荐'
  return '可选，简单描述情况'
})

function onReasonChange() {}

function triggerUpload() {
  photoInput.value?.click()
}

function onPhotoSelect(e) {
  const files = Array.from(e.target.files || [])
  const emptySlots = photos.value.filter(p => !p).length
  files.slice(0, emptySlots).forEach(f => {
    const idx = photos.value.findIndex(p => !p)
    if (idx !== -1) photos.value[idx] = URL.createObjectURL(f)
  })
}

async function submit() {
  if (!form.value.reason) { ElMessage.warning('请选择退货原因'); return }
  if (!orderItemId.value) { ElMessage.error('缺少订单商品信息，请从订单详情页进入'); return }
  submitting.value = true
  try {
    const res = await applyRefund({
      order_item_id: orderItemId.value,
      reason_type:   form.value.reason,
      reason_detail: form.value.remark,
    })
    ElMessage.success('申请已提交，商家将在24小时内处理')
    const refundId = res?.data?.refund_id
    router.replace(`/aftersale/${refundId}`)
  } catch {
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.aftersale-apply-page { flex: 1; }
.container { max-width: 720px; margin: 0 auto; padding: 0 32px 60px; }

.page-header {
  display: flex; align-items: center; gap: 12px; padding: 24px 0 20px;
}
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; }

.apply-card {
  background: #fff; border-radius: 16px; padding: 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
}

.form-section { margin-bottom: 28px; }
.form-section-title {
  font-size: 16px; font-weight: 700; color: #1A1714;
  margin-bottom: 16px; padding-bottom: 10px;
  border-bottom: 1px solid #F0F0F0;
}

.type-group { display: flex; gap: 32px; }
.reason-group { display: flex; flex-direction: column; gap: 12px; }
.reason-radio { margin-right: 0; }

.remark-area { margin-top: 16px; }
.remark-label { font-size: 14px; color: #6B6B6B; margin-bottom: 8px; }

.upload-area { display: flex; gap: 16px; }
.upload-slot {
  width: 100px; height: 100px; border: 2px dashed #EBEBEB;
  border-radius: 12px; display: flex; align-items: center;
  justify-content: center; cursor: pointer; overflow: hidden;
  transition: border-color .15s;
}
.upload-slot:hover { border-color: #C4906A; }
.upload-placeholder { font-size: 28px; color: #B0B0B0; }
.uploaded-img { width: 100%; height: 100%; object-fit: cover; }

.submit-btn {
  width: 100%; border-radius: 12px; font-size: 16px; font-weight: 700;
  background: linear-gradient(135deg, #1A1714, #4A3020); border-color: transparent;
}
.submit-btn:hover { background: linear-gradient(135deg, #2D231A, #6B4226); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
