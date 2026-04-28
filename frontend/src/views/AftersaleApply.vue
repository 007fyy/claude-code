<template>
  <div class="aftersale-apply-page">
    <div class="topbar">
      <el-button :icon="ArrowLeft" circle @click="$router.back()" />
      <span class="title">申请售后</span>
    </div>

    <el-form :model="form" ref="formRef" class="apply-form">
      <!-- 售后方式 -->
      <div class="section">
        <div class="section-title">选择售后方式</div>
        <el-radio-group v-model="form.type" class="type-group">
          <el-radio label="refund">退货退款</el-radio>
          <el-radio label="exchange">换货</el-radio>
        </el-radio-group>
      </div>

      <!-- 退货原因 -->
      <div class="section">
        <div class="section-title">退货原因（必选）</div>
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

      <!-- 上传图片 -->
      <div class="section">
        <div class="section-title">上传图片（选填，最多3张）</div>
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
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { applyRefund } from '../api/order'

const route     = useRoute()
const router    = useRouter()
const formRef   = ref(null)
const photoInput = ref(null)
const submitting = ref(false)
const photos = ref([null, null, null])

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
  submitting.value = true
  try {
    const res = await applyRefund({
      order_id: route.query.order_id,
      type:     form.value.type,
      reason:   form.value.reason,
      remark:   form.value.remark,
    })
    ElMessage.success('申请已提交，商家将在24小时内处理')
    const aftersaleId = res?.data?.aftersale_id || route.query.order_id
    router.replace(`/aftersale/${aftersaleId}`)
  } catch {
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.aftersale-apply-page {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100dvh;
  background: #f7f5f3;
  padding-bottom: 40px;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  margin-bottom: 12px;
}
.title { font-size: 16px; font-weight: 700; }

.apply-form { padding: 0 0 24px; }

.section {
  background: #fff;
  padding: 16px;
  margin-bottom: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 14px;
}

.type-group { display: flex; gap: 32px; }

.reason-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reason-radio { margin-right: 0; }

.remark-area { margin-top: 16px; }
.remark-label { font-size: 14px; color: #666; margin-bottom: 8px; }

.upload-area { display: flex; gap: 12px; }

.upload-slot {
  width: 90px;
  height: 90px;
  border: 2px dashed #ddd;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
}

.upload-slot:hover { border-color: #c0876a; }

.upload-placeholder { font-size: 28px; color: #ccc; }
.uploaded-img { width: 100%; height: 100%; object-fit: cover; }

.submit-btn {
  display: block;
  width: calc(100% - 32px);
  margin: 0 16px;
  border-radius: 24px;
  font-size: 16px;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
