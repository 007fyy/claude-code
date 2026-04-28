<template>
  <div class="result-page">
    <div class="result-content">
      <div class="status-icon">✅</div>
      <h2 class="status-title">支付成功！</h2>
      <div class="order-amount">订单金额：¥{{ amount }}</div>
      <div class="delivery-estimate">预计送达：{{ estimatedDelivery }}</div>

      <div class="divider" />

      <div class="order-no">订单号：{{ orderNo }}</div>

      <div class="actions">
        <el-button type="primary" size="large" class="action-btn" @click="$router.push(`/orders/${orderId}`)">
          查看订单详情
        </el-button>
        <el-button size="large" class="action-btn" @click="$router.push('/home')">
          继续购物
        </el-button>
      </div>
    </div>

    <div class="recommend-section">
      <div class="rec-title">─ 试戴过这些，你可能也喜欢 ─</div>
      <div class="rec-list">
        <div
          v-for="item in recommended"
          :key="item.spu_id"
          class="rec-card"
          @click="$router.push(`/goods/${item.spu_id}`)"
        >
          <el-image :src="item.cover_url" fit="cover" class="rec-img" lazy>
            <template #error>
              <div class="img-err"><el-icon><Picture /></el-icon></div>
            </template>
          </el-image>
          <div class="rec-price">¥{{ item.price_range }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Picture } from '@element-plus/icons-vue'
import { getGoodsList } from '../api/goods'

const route = useRoute()

const orderId  = ref(route.query.order_id || '')
const orderNo  = ref(route.query.order_no || 'LP' + Date.now())
const amount   = ref(route.query.amount || '0.00')
const recommended = ref([])

const now = new Date()
const d1 = new Date(now); d1.setDate(d1.getDate() + 3)
const d2 = new Date(now); d2.setDate(d2.getDate() + 5)
const fmt = (d) => `${d.getMonth() + 1}月${d.getDate()}日`
const estimatedDelivery = `${fmt(d1)}-${fmt(d2)}`

onMounted(async () => {
  try {
    const res = await getGoodsList({ page: 1, page_size: 6 })
    recommended.value = res.items.slice(0, 5)
  } catch {}
})
</script>

<style scoped>
.result-page {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100dvh;
  background: #f7f5f3;
  padding-bottom: 40px;
}

.result-content {
  background: #fff;
  margin: 0 0 16px;
  padding: 60px 24px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.status-icon  { font-size: 72px; line-height: 1; }
.status-title { font-size: 26px; font-weight: 700; color: #333; }
.order-amount { font-size: 18px; color: #e6564e; font-weight: 600; }
.delivery-estimate { font-size: 14px; color: #888; }

.divider {
  width: 80%;
  border-top: 1px dashed #eee;
  margin: 8px 0;
}

.order-no { font-size: 13px; color: #bbb; }

.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  margin-top: 12px;
}

.action-btn { width: 100%; border-radius: 24px; }

.recommend-section { padding: 0 16px; }
.rec-title { font-size: 14px; color: #999; text-align: center; margin-bottom: 16px; }

.rec-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  scrollbar-width: none;
}

.rec-card { flex-shrink: 0; width: 120px; cursor: pointer; }
.rec-img { width: 120px; height: 120px; border-radius: 10px; display: block; }
.img-err { width: 120px; height: 120px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; font-size: 28px; }
.rec-price { font-size: 13px; font-weight: 700; color: #e6564e; margin-top: 6px; text-align: center; }
</style>
