<template>
  <div class="admin-orders-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title"><span>✦</span> 订单管理（管理员）</h1>
      </div>

      <el-tabs v-model="activeTab" class="status-tabs" @tab-change="loadOrders">
        <el-tab-pane v-for="tab in tabs" :key="tab.value" :label="tab.label" :name="tab.value" />
      </el-tabs>

      <div v-loading="loading" class="order-cards">
        <div v-for="order in orders" :key="order.order_id" class="order-card">
          <div class="card-header">
            <span class="order-no">{{ order.order_no }}</span>
            <span class="status-tag" :class="statusClass(order.status)">{{ statusText(order.status) }}</span>
            <span class="order-date">{{ formatDate(order.created_at) }}</span>
          </div>

          <div class="order-info">
            <span>收货人：{{ order.receiver_name }}</span>
            <span>电话：{{ order.receiver_phone || '-' }}</span>
            <span>地址：{{ order.receiver_address }}</span>
          </div>

          <div v-for="item in order.items" :key="item.sku_name" class="order-item-row">
            <el-image :src="item.cover_url" fit="cover" class="item-img">
              <template #error><div class="img-err">📷</div></template>
            </el-image>
            <div class="item-info">
              <div class="item-name">{{ item.spu_name }}</div>
              <div class="item-sku">{{ item.sku_name }} x{{ item.quantity }}</div>
            </div>
            <div class="item-price">¥{{ item.subtotal }}</div>
          </div>

          <div class="card-footer">
            <span class="total">合计：<b>¥{{ order.total_amount }}</b></span>
            <div class="footer-btns">
              <el-button v-if="order.status === 'paid'" type="primary" size="small" @click="handleShip(order)">确认发货</el-button>
              <el-button v-if="order.status === 'shipped'" type="success" size="small" @click="handleComplete(order)">确认收货</el-button>
              <el-button v-if="order.status === 'refunding'" type="warning" size="small" @click="handleRefund(order)">同意退款</el-button>
            </div>
          </div>
        </div>

        <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminOrderList, adminShipOrder, adminCompleteOrder, adminApproveRefund } from '../api/order'

const tabs = [
  { label: '全部',   value: '' },
  { label: '待发货', value: 'paid' },
  { label: '待收货', value: 'shipped' },
  { label: '售后中', value: 'refunding' },
  { label: '已完成', value: 'completed' },
]

const activeTab = ref('')
const orders = ref([])
const loading = ref(false)

const STATUS_MAP = {
  pending_pay: { text: '待付款', cls: 'yellow' },
  paid:        { text: '待发货', cls: 'blue' },
  shipped:     { text: '待收货', cls: 'blue' },
  completed:   { text: '已完成', cls: 'green' },
  cancelled:   { text: '已取消', cls: 'gray' },
  refunding:   { text: '售后中', cls: 'red' },
  refunded:    { text: '已退款', cls: 'gray' },
}

function statusText(s) { return STATUS_MAP[s]?.text || s }
function statusClass(s) { return STATUS_MAP[s]?.cls || '' }
function formatDate(str) { return str ? str.slice(0, 16).replace('T', ' ') : '' }

async function loadOrders() {
  loading.value = true
  try {
    const res = await adminOrderList({ status: activeTab.value || undefined, page: 1, page_size: 50 })
    orders.value = res.items || []
  } catch {
    orders.value = []
  } finally {
    loading.value = false
  }
}

async function handleShip(order) {
  try {
    await ElMessageBox.confirm(`确认发货订单 ${order.order_no}？`, '发货确认')
    await adminShipOrder(order.order_id)
    ElMessage.success('已发货')
    await loadOrders()
  } catch {}
}

async function handleComplete(order) {
  try {
    await ElMessageBox.confirm(`确认该订单已送达？`, '确认收货')
    await adminCompleteOrder(order.order_id)
    ElMessage.success('已确认收货')
    await loadOrders()
  } catch {}
}

async function handleRefund(order) {
  try {
    await ElMessageBox.confirm(`确认同意退款 ¥${order.total_amount}？`, '退款审批', { type: 'warning' })
    await adminApproveRefund(order.order_id)
    ElMessage.success('已同意退款')
    await loadOrders()
  } catch {}
}

onMounted(loadOrders)
</script>

<style scoped>
.admin-orders-page { flex: 1; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 32px 60px; }

.page-header { padding: 24px 0 20px; }
.page-title { font-size: 24px; font-weight: 800; color: #1A1714; }
.page-title span { color: #C4906A; }

.status-tabs { margin-bottom: 20px; }

.order-cards { display: flex; flex-direction: column; gap: 16px; }

.order-card {
  background: #fff; border-radius: 16px; padding: 20px 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
}

.card-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 12px;
}
.order-no { font-size: 13px; color: #6B6B6B; font-family: monospace; }
.order-date { font-size: 13px; color: #B0B0B0; margin-left: auto; }

.status-tag {
  font-size: 12px; font-weight: 600;
  padding: 3px 12px; border-radius: 16px;
}
.status-tag.yellow { background: #fff8e1; color: #e6a817; }
.status-tag.blue   { background: #e8f4fe; color: #409eff; }
.status-tag.green  { background: #e8f8e8; color: #67c23a; }
.status-tag.gray   { background: #f5f5f5; color: #B0B0B0; }
.status-tag.red    { background: #feecec; color: #f56c6c; }

.order-info {
  display: flex; gap: 24px; font-size: 13px; color: #6B6B6B;
  padding: 8px 0; border-bottom: 1px solid #F0F0F0; margin-bottom: 8px;
}

.order-item-row {
  display: flex; align-items: center; gap: 14px;
  padding: 8px 0; border-bottom: 1px solid #F0F0F0;
}
.item-img { width: 50px; height: 50px; border-radius: 8px; flex-shrink: 0; }
.img-err { width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; background: #f0f0f0; border-radius: 8px; }
.item-info { flex: 1; min-width: 0; }
.item-name { font-size: 13px; font-weight: 600; color: #1A1714; }
.item-sku { font-size: 12px; color: #B0B0B0; margin-top: 2px; }
.item-price { font-size: 14px; font-weight: 600; color: #1A1714; }

.card-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 14px;
}
.total { font-size: 14px; color: #6B6B6B; }
.total b { color: #1A1714; font-weight: 800; }
.footer-btns { display: flex; gap: 8px; }
</style>
