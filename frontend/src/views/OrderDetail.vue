<template>
  <div class="order-detail-page">
    <div class="container">
      <div class="page-header">
        <el-button text @click="$router.back()">← 返回</el-button>
        <h1 class="page-title">订单详情</h1>
      </div>

      <div v-loading="loading">
        <div v-if="order">
          <div class="logistics-steps">
            <el-steps :active="activeStep" align-center>
              <el-step title="已付款" />
              <el-step title="已发货" />
              <el-step title="运输中" />
              <el-step title="已签收" />
            </el-steps>
          </div>

          <div class="detail-grid">
            <div class="detail-left">
              <div class="section" v-if="order.tracking_no">
                <div class="section-title">物流信息</div>
                <div class="logistics-card">
                  <div class="logistics-no">顺丰快递 {{ order.tracking_no }}</div>
                  <div class="logistics-latest">最新：商品已由商家发出，等待快递揽收</div>
                </div>
              </div>

              <div class="section">
                <div class="section-title">收货信息</div>
                <div class="address-info">
                  <div class="addr-name">{{ order.receiver_name }} {{ order.receiver_phone }}</div>
                  <div class="addr-text">{{ order.receiver_address }}</div>
                </div>
              </div>

              <div class="section">
                <div class="section-title">商品信息</div>
                <div v-for="item in (order.items || [])" :key="item.sku_id" class="order-item">
                  <el-image :src="item.cover_url" fit="cover" class="item-img">
                    <template #error><div class="img-err"><el-icon><Picture /></el-icon></div></template>
                  </el-image>
                  <div class="item-meta">
                    <div class="item-name">{{ item.spu_name }}</div>
                    <div class="item-sku">{{ item.sku_name }} x{{ item.quantity }}</div>
                    <div class="item-price">¥{{ item.price }}</div>
                  </div>
                  <el-button v-if="item.ar_asset_url" size="small" link @click="tryOn(item)">试戴</el-button>
                </div>
              </div>
            </div>

            <div class="detail-right">
              <div class="section order-meta">
                <div class="section-title">订单信息</div>
                <div class="meta-row"><span>订单号</span><span>{{ order.order_no }}</span></div>
                <div class="meta-row"><span>创建时间</span><span>{{ formatDate(order.created_at) }}</span></div>
                <div class="meta-row"><span>状态</span><span class="status-text">{{ statusText(order.status) }}</span></div>
                <div class="meta-row"><span>支付方式</span><span>微信支付</span></div>
                <div class="meta-row total-row"><span>实付金额</span><span class="price">¥{{ order.total_amount }}</span></div>
              </div>

              <div class="action-btns">
                <el-button v-if="order.status === 'pending_pay'" size="large" type="primary" class="action-btn" @click="handlePay">去付款</el-button>
                <el-button v-if="order.status === 'pending_pay'" size="large" class="action-btn" @click="handleCancel">取消订单</el-button>
                <el-button v-if="order.status === 'shipped'" size="large" type="primary" class="action-btn" @click="handleConfirm">确认收货</el-button>
                <el-button v-if="order.status === 'completed'" size="large" class="action-btn" @click="$router.push(`/aftersale/apply?order_id=${order.order_id}`)">申请售后</el-button>
                <el-button size="large" class="action-btn">联系客服</el-button>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-else-if="!loading" description="订单不存在" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderDetail, payOrder, cancelOrder, confirmReceive } from '../api/order'

const route  = useRoute()
const router = useRouter()
const order   = ref(null)
const loading = ref(false)

const STEP_MAP = { pending_pay: 0, paid: 1, shipped: 2, completed: 3 }
const activeStep = computed(() => STEP_MAP[order.value?.status] ?? 0)

const STATUS_MAP = {
  pending_pay: '待付款',
  paid: '待发货',
  shipped: '待收货',
  completed: '已完成',
  cancelled: '已取消',
  refunding: '售后中',
  refunded: '已退款',
}
function statusText(s) { return STATUS_MAP[s] || s }

function formatDate(str) {
  if (!str) return ''
  return str.replace('T', ' ').slice(0, 16)
}

function tryOn(item) {
  router.push({
    name: 'FaceARView',
    query: { sku_id: item.sku_id, sku_name: item.spu_name, ar_asset_url: item.ar_asset_url || '', mount_type: item.mount_type || 'ear_lobe' },
  })
}

async function loadOrder() {
  loading.value = true
  try {
    const res = await getOrderDetail(route.params.id)
    order.value = res.data
  } catch {
    order.value = null
  } finally {
    loading.value = false
  }
}

async function handlePay() {
  try {
    await ElMessageBox.confirm(`确认支付 ¥${order.value.total_amount}？`, '模拟支付', { type: 'info' })
    await payOrder({ order_id: order.value.order_id })
    ElMessage.success('支付成功')
    await loadOrder()
  } catch {}
}

async function handleCancel() {
  try {
    await ElMessageBox.confirm('确认取消该订单？', '提示', { type: 'warning' })
    await cancelOrder(order.value.order_id)
    ElMessage.success('订单已取消')
    await loadOrder()
  } catch {}
}

async function handleConfirm() {
  try {
    await ElMessageBox.confirm('确认已收到商品？', '确认收货', { type: 'info' })
    await confirmReceive(order.value.order_id)
    ElMessage.success('已确认收货')
    await loadOrder()
  } catch {}
}

onMounted(loadOrder)
</script>

<style scoped>
.order-detail-page { flex: 1; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 32px 60px; }

.page-header {
  display: flex; align-items: center; gap: 12px; padding: 24px 0 20px;
}
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; }

.logistics-steps {
  background: #fff; padding: 24px; border-radius: 16px;
  margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,.07);
}

.detail-grid {
  display: grid; grid-template-columns: 1fr 360px; gap: 20px; align-items: start;
}

.section {
  background: #fff; border-radius: 16px; padding: 20px 24px;
  margin-bottom: 16px; box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.section-title { font-size: 15px; font-weight: 700; color: #1A1714; margin-bottom: 14px; }

.logistics-card {
  background: #FAF9F7; border-radius: 12px; padding: 14px 16px;
}
.logistics-no { font-size: 13px; color: #6B6B6B; margin-bottom: 6px; }
.logistics-latest { font-size: 13px; color: #B0B0B0; }

.addr-name { font-size: 15px; font-weight: 600; color: #1A1714; margin-bottom: 6px; }
.addr-text { font-size: 13px; color: #6B6B6B; line-height: 1.6; }

.order-item {
  display: flex; align-items: center; gap: 14px;
  padding: 10px 0; border-bottom: 1px solid #F0F0F0;
}
.order-item:last-child { border-bottom: none; }
.item-img { width: 64px; height: 64px; border-radius: 10px; flex-shrink: 0; }
.img-err { width: 64px; height: 64px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; }
.item-meta { flex: 1; min-width: 0; }
.item-name { font-size: 14px; font-weight: 600; color: #1A1714; margin-bottom: 4px; }
.item-sku { font-size: 12px; color: #B0B0B0; margin-bottom: 4px; }
.item-price { font-size: 14px; color: #1A1714; font-weight: 700; }

.meta-row {
  display: flex; justify-content: space-between;
  font-size: 14px; color: #6B6B6B; padding: 8px 0;
  border-bottom: 1px solid #F0F0F0;
}
.meta-row:last-child { border-bottom: none; }
.total-row { font-weight: 700; }
.price { color: #1A1714; font-weight: 800; }

.action-btns { display: flex; flex-direction: column; gap: 10px; }
.action-btn { width: 100%; border-radius: 12px; }
</style>
