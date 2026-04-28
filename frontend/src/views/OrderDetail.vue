<template>
  <div class="order-detail-page">
    <div class="topbar">
      <el-button :icon="ArrowLeft" circle @click="$router.back()" />
      <span class="title">订单详情</span>
    </div>

    <div v-loading="loading">
      <div v-if="order">
        <!-- 物流进度 -->
        <div class="logistics-steps">
          <el-steps :active="activeStep" align-center>
            <el-step title="已付款" />
            <el-step title="已发货" />
            <el-step title="运输中" />
            <el-step title="已签收" />
          </el-steps>
        </div>

        <!-- 物流信息 -->
        <div class="section" v-if="order.tracking_no">
          <div class="section-title">📦 物流信息</div>
          <div class="logistics-card">
            <div class="logistics-no">顺丰快递 {{ order.tracking_no }}</div>
            <div class="logistics-latest">最新：商品已由商家发出，等待快递揽收</div>
          </div>
        </div>

        <!-- 收货地址 -->
        <div class="section">
          <div class="section-title">📍 收货信息</div>
          <div class="address-info">
            <div class="addr-name">{{ order.receiver_name }} {{ order.receiver_phone }}</div>
            <div class="addr-text">{{ order.receiver_address }}</div>
          </div>
        </div>

        <!-- 商品 -->
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
            <el-button
              v-if="item.ar_asset_url"
              size="small"
              link
              @click="tryOn(item)"
            >试戴</el-button>
          </div>
        </div>

        <!-- 订单信息 -->
        <div class="section order-meta">
          <div class="meta-row"><span>订单号</span><span>{{ order.order_no }}</span></div>
          <div class="meta-row"><span>创建时间</span><span>{{ formatDate(order.created_at) }}</span></div>
          <div class="meta-row"><span>支付方式</span><span>微信支付</span></div>
          <div class="meta-row total-row"><span>实付金额</span><span class="price">¥{{ order.total_amount }}</span></div>
        </div>
      </div>

      <el-empty v-else-if="!loading" description="订单不存在" />
    </div>

    <!-- 底部操作 -->
    <div class="bottom-bar" v-if="order">
      <el-button size="large" class="action-btn" @click="$router.push(`/aftersale/apply?order_id=${order.order_id}`)">
        申请售后
      </el-button>
      <el-button size="large" class="action-btn">联系客服</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Picture } from '@element-plus/icons-vue'
import { getOrderDetail } from '../api/order'

const route  = useRoute()
const router = useRouter()
const order   = ref(null)
const loading = ref(false)

const STEP_MAP = { pending: 0, paid: 1, shipped: 2, completed: 3 }
const activeStep = computed(() => STEP_MAP[order.value?.status] ?? 0)

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

onMounted(async () => {
  loading.value = true
  try {
    order.value = await getOrderDetail(route.params.id)
  } catch {
    order.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.order-detail-page {
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
  margin-bottom: 12px;
}
.title { font-size: 16px; font-weight: 700; }

.logistics-steps {
  background: #fff;
  padding: 20px 16px;
  margin-bottom: 12px;
}

.section {
  background: #fff;
  margin-bottom: 12px;
  padding: 16px;
}

.section-title { font-size: 14px; font-weight: 600; color: #555; margin-bottom: 12px; }

.logistics-card {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 12px 14px;
}

.logistics-no { font-size: 13px; color: #666; margin-bottom: 6px; }
.logistics-latest { font-size: 13px; color: #999; }

.address-info {}
.addr-name { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 6px; }
.addr-text { font-size: 13px; color: #777; line-height: 1.6; }

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}
.order-item:last-child { border-bottom: none; }

.item-img { width: 60px; height: 60px; border-radius: 8px; flex-shrink: 0; }
.img-err { width: 60px; height: 60px; border-radius: 8px; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; }
.item-meta { flex: 1; min-width: 0; }
.item-name  { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
.item-sku   { font-size: 12px; color: #999; margin-bottom: 4px; }
.item-price { font-size: 14px; color: #e6564e; font-weight: 600; }

.order-meta {}
.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
  padding: 6px 0;
  border-bottom: 1px solid #f5f5f5;
}
.meta-row:last-child { border-bottom: none; }
.total-row { font-weight: 600; }
.price { color: #e6564e; }

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
