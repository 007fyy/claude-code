<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1 class="page-title"><span>✦</span> 数据概览</h1>
    </div>

    <div class="stat-grid" v-loading="loading">
      <div v-for="c in cards" :key="c.key" class="stat-card">
        <div class="stat-icon" :style="{ background: c.bg }">
          <el-icon :size="22" color="#fff"><component :is="c.icon" /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-val">{{ stats[c.key] ?? '—' }}</div>
          <div class="stat-label">{{ c.label }}</div>
        </div>
      </div>
    </div>

    <div class="quick-links">
      <el-button type="primary" @click="$router.push('/admin/orders')">处理待发货订单</el-button>
      <el-button @click="$router.push('/admin/goods')">管理商品</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ShoppingCart, Box, User, Tickets } from '@element-plus/icons-vue'
import { adminListGoods } from '@/api/goods'
import http from '@/api/http'

const loading = ref(false)
const stats = ref({})

const cards = [
  { key: 'total_orders',   label: '累计订单',   icon: ShoppingCart, bg: '#4A90D9' },
  { key: 'pending_ship',   label: '待发货',     icon: Tickets,      bg: '#E6A23C' },
  { key: 'total_products', label: '在售商品',   icon: Box,          bg: '#67C23A' },
  { key: 'total_users',    label: '注册用户',   icon: User,         bg: '#C4906A' },
]

onMounted(async () => {
  loading.value = true
  try {
    const res = await http.get('/goods/admin/stats')
    stats.value = res.data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard-page { padding: 28px 32px; }
.page-header { margin-bottom: 28px; }
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; }
.page-title span { color: #C4906A; margin-right: 8px; }

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
.stat-card {
  background: #fff; border-radius: 14px; padding: 20px;
  display: flex; align-items: center; gap: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
}
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-val { font-size: 28px; font-weight: 800; color: #1A1714; line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 13px; color: #999; }

.quick-links { display: flex; gap: 12px; }
</style>
