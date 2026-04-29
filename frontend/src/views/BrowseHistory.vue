<template>
  <div class="history-page">
    <div class="container">
      <div class="page-header">
        <button class="back-btn" @click="$router.back()">← 返回</button>
        <h1 class="page-title"><span>✦</span> 浏览历史</h1>
        <button v-if="groups.length" class="clear-btn" @click="handleClear">清空记录</button>
      </div>

      <div v-loading="loading" class="history-body">
        <div v-for="group in groups" :key="group.date" class="date-group">
          <div class="date-label">{{ group.date }}</div>
          <div class="goods-grid">
            <div
              v-for="item in group.items"
              :key="item.spu_id"
              class="product-card"
              @click="$router.push(`/goods/${item.spu_id}`)"
            >
              <div class="product-card-img">
                <el-image :src="item.cover_url" fit="cover" class="card-img" lazy>
                  <template #error>
                    <div class="img-err"><el-icon><Picture /></el-icon></div>
                  </template>
                </el-image>
              </div>
              <div class="product-card-body">
                <div class="product-card-name">{{ item.name }}</div>
                <div class="product-card-meta">{{ item.material || item.category }}</div>
                <div class="product-card-price">
                  <span class="price-main">¥{{ item.price_range }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <el-empty v-if="!loading && groups.length === 0" description="暂无浏览记录" style="padding:80px 0">
        <el-button type="primary" @click="$router.push('/goods')">去逛逛</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHistoryList, clearHistory } from '../api/history'

const groups = ref([])
const loading = ref(false)

async function fetchHistory() {
  loading.value = true
  try {
    const res = await getHistoryList()
    groups.value = res.data || []
  } catch {
    groups.value = []
  } finally {
    loading.value = false
  }
}

async function handleClear() {
  try {
    await ElMessageBox.confirm('确认清空所有浏览记录？', '提示', { type: 'warning' })
    await clearHistory()
    groups.value = []
    ElMessage.success('已清空')
  } catch {}
}

onMounted(fetchHistory)
</script>

<style scoped>
.history-page { flex: 1; }
.container { max-width: 1320px; margin: 0 auto; padding: 0 32px 60px; }

.page-header {
  display: flex; align-items: center; gap: 16px;
  padding: 24px 0 20px;
}
.back-btn {
  background: none; border: none; font-size: 14px; color: #6B6B6B;
  cursor: pointer; transition: color .15s;
}
.back-btn:hover { color: #C4906A; }
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; flex: 1; }
.page-title span { color: #C4906A; }
.clear-btn {
  background: none; border: 1px solid #E0E0E0; border-radius: 8px;
  padding: 6px 14px; font-size: 13px; color: #6B6B6B;
  cursor: pointer; transition: all .15s;
}
.clear-btn:hover { border-color: #C4906A; color: #C4906A; }

.history-body { min-height: 200px; }

.date-group { margin-bottom: 32px; }
.date-label {
  font-size: 15px; font-weight: 700; color: #1A1714;
  padding: 8px 0 12px;
  border-bottom: 1px solid #F0F0F0;
  margin-bottom: 16px;
}

.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.product-card {
  background: #fff; border-radius: 14px; overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
  transition: all .25s; cursor: pointer;
  display: flex; flex-direction: column;
}
.product-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(0,0,0,.12); }

.product-card-img { width: 100%; aspect-ratio: 1; position: relative; overflow: hidden; }
.card-img { width: 100%; height: 100%; }
.img-err {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: #f0f0f0; color: #bbb; font-size: 40px;
}

.product-card-body { padding: 14px; flex: 1; display: flex; flex-direction: column; }
.product-card-name {
  font-size: 13px; font-weight: 600; color: #1A1714;
  line-height: 1.4; margin-bottom: 4px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.product-card-meta { font-size: 12px; color: #6B6B6B; margin-bottom: 6px; }
.product-card-price { margin-top: auto; }
.price-main { font-size: 18px; font-weight: 800; color: #1A1714; }
</style>
