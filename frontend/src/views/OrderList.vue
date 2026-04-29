<template>
  <div class="order-list-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title"><span>✦</span> 我的订单</h1>
      </div>

      <el-tabs v-model="activeTab" class="status-tabs" @tab-change="loadOrders">
        <el-tab-pane v-for="tab in tabs" :key="tab.value" :label="tab.label" :name="tab.value" />
      </el-tabs>

      <div v-loading="loading" class="order-cards">
        <div
          v-for="order in orders"
          :key="order.order_id"
          class="order-card"
          @click="$router.push(`/orders/${order.order_id}`)"
        >
          <div class="card-header">
            <span class="status-tag" :class="statusClass(order.status)">{{ statusText(order.status) }}</span>
            <span class="order-date">{{ formatDate(order.created_at) }}</span>
          </div>

          <div v-for="item in (order.items || []).slice(0, 2)" :key="item.sku_id" class="order-item-row">
            <el-image :src="item.cover_url" fit="cover" class="item-img">
              <template #error><div class="img-err"><el-icon><Picture /></el-icon></div></template>
            </el-image>
            <div class="item-info">
              <div class="item-name">{{ item.spu_name }}</div>
              <div class="item-sku">{{ item.sku_name }}</div>
            </div>
            <div class="item-price">¥{{ item.price }} x{{ item.quantity }}</div>
          </div>

          <div class="card-footer">
            <span class="total">共{{ order.item_count || 1 }}件 实付：<b class="price">¥{{ order.total_amount }}</b></span>
            <div class="footer-btns" @click.stop>
              <el-button v-if="order.status === 'shipped'" size="small" @click="reorder(order)">再次购买</el-button>
              <el-button v-if="order.status === 'shipped'" size="small" @click="urge(order)">催单</el-button>
              <el-button v-if="order.status === 'completed'" size="small" @click="$router.push(`/aftersale/apply?order_id=${order.order_id}`)">申请售后</el-button>
              <el-button v-if="order.status === 'completed'" size="small" type="primary">评价</el-button>
            </div>
          </div>
        </div>

        <el-empty v-if="!loading && orders.length === 0" description="暂无订单">
          <el-button type="primary" @click="$router.push('/home')">去逛逛</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getOrderList } from '../api/order'

const route  = useRoute()
const router = useRouter()

const tabs = [
  { label: '全部',   value: '' },
  { label: '待付款', value: 'pending' },
  { label: '待发货', value: 'paid' },
  { label: '待收货', value: 'shipped' },
  { label: '售后',   value: 'refunding' },
]

const activeTab = ref(route.query.status || '')
const orders    = ref([])
const loading   = ref(false)

const STATUS_MAP = {
  pending:    { text: '待付款',  cls: 'yellow' },
  paid:       { text: '待发货',  cls: 'blue' },
  shipped:    { text: '运输中',  cls: 'blue' },
  completed:  { text: '已完成',  cls: 'green' },
  cancelled:  { text: '已取消',  cls: 'gray' },
  refunding:  { text: '售后中',  cls: 'red' },
  refunded:   { text: '已退款',  cls: 'gray' },
}

function statusText(s) { return STATUS_MAP[s]?.text || s }
function statusClass(s){ return STATUS_MAP[s]?.cls  || '' }

function formatDate(str) {
  if (!str) return ''
  return str.slice(0, 10).replace(/-/g, '.')
}

async function loadOrders() {
  loading.value = true
  try {
    const res = await getOrderList({ status: activeTab.value || undefined, page: 1, page_size: 20 })
    orders.value = res.items || []
  } catch {
    orders.value = []
  } finally {
    loading.value = false
  }
}

function reorder(order) {
  ElMessage.success('已加入购物车')
}

function urge(order) {
  ElMessage.success('催单成功，商家将尽快处理')
}

onMounted(loadOrders)
</script>

<style scoped>
.order-list-page { flex: 1; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 32px 60px; }

.page-header { padding: 24px 0 20px; }
.page-title { font-size: 24px; font-weight: 800; color: #1A1714; }
.page-title span { color: #C4906A; }

.status-tabs { margin-bottom: 20px; }

.order-cards { display: flex; flex-direction: column; gap: 16px; }

.order-card {
  background: #fff; border-radius: 16px; padding: 20px 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
  cursor: pointer; transition: all .2s;
}
.order-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,.12); }

.card-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 16px;
}

.status-tag {
  font-size: 13px; font-weight: 600;
  padding: 4px 14px; border-radius: 20px;
}
.status-tag.yellow { background: #fff8e1; color: #e6a817; }
.status-tag.blue   { background: #e8f4fe; color: #409eff; }
.status-tag.green  { background: #e8f8e8; color: #67c23a; }
.status-tag.gray   { background: #f5f5f5; color: #B0B0B0; }
.status-tag.red    { background: #feecec; color: #f56c6c; }

.order-date { font-size: 13px; color: #B0B0B0; }

.order-item-row {
  display: flex; align-items: center; gap: 14px;
  padding: 10px 0; border-bottom: 1px solid #F0F0F0;
}

.item-img { width: 60px; height: 60px; border-radius: 10px; flex-shrink: 0; }
.img-err { width: 60px; height: 60px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; font-size: 20px; }
.item-info { flex: 1; min-width: 0; }
.item-name { font-size: 14px; font-weight: 600; color: #1A1714; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-sku { font-size: 12px; color: #B0B0B0; margin-top: 4px; }
.item-price { font-size: 14px; color: #6B6B6B; flex-shrink: 0; font-weight: 500; }

.card-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 16px;
}
.total { font-size: 14px; color: #6B6B6B; }
.price { color: #1A1714; font-weight: 800; }
.footer-btns { display: flex; gap: 8px; }
</style>
