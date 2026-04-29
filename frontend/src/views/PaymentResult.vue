<template>
  <div class="result-page">
    <div class="container">
      <div class="result-card">
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
          <el-button size="large" class="action-btn action-btn-outline" @click="$router.push('/home')">
            继续购物
          </el-button>
        </div>
      </div>

      <div class="recommend-section">
        <div class="rec-title">试戴过这些，你可能也喜欢</div>
        <div class="rec-grid">
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
            <div class="rec-name">{{ item.name }}</div>
            <div class="rec-price">¥{{ item.price_range }}</div>
          </div>
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
.result-page { flex: 1; }
.container { max-width: 800px; margin: 0 auto; padding: 32px 32px 60px; }

.result-card {
  background: #fff; border-radius: 16px; padding: 48px 40px;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07); margin-bottom: 32px;
}

.status-icon { font-size: 72px; line-height: 1; }
.status-title { font-size: 26px; font-weight: 800; color: #1A1714; }
.order-amount { font-size: 18px; color: #C4906A; font-weight: 700; }
.delivery-estimate { font-size: 14px; color: #6B6B6B; }

.divider { width: 80%; border-top: 1px dashed #EBEBEB; margin: 8px 0; }
.order-no { font-size: 13px; color: #B0B0B0; }

.actions { display: flex; gap: 16px; width: 100%; max-width: 400px; margin-top: 16px; }
.action-btn { flex: 1; border-radius: 12px; font-weight: 700; }
.action-btn-outline { background: #fff; border: 1.5px solid #EBEBEB; color: #1A1714; }
.action-btn-outline:hover { border-color: #C4906A; color: #C4906A; }

.recommend-section {}
.rec-title { font-size: 16px; font-weight: 700; color: #1A1714; text-align: center; margin-bottom: 20px; }

.rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}
.rec-card {
  cursor: pointer; transition: transform .2s;
  background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
}
.rec-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }
.rec-img { width: 100%; aspect-ratio: 1; display: block; }
.img-err { width: 100%; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; font-size: 28px; }
.rec-name { font-size: 13px; font-weight: 500; color: #1A1714; padding: 8px 10px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rec-price { font-size: 15px; font-weight: 800; color: #1A1714; padding: 4px 10px 10px; }
</style>
