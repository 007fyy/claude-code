<template>
  <div class="fav-page">
    <div class="container">
      <div class="page-header">
        <button class="back-btn" @click="$router.back()">← 返回</button>
        <h1 class="page-title"><span>✦</span> 我的收藏</h1>
        <span class="fav-count">共 {{ list.length }} 件</span>
      </div>

      <div v-loading="loading" class="goods-grid">
        <div
          v-for="item in list"
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
            <span class="fav-btn active" @click.stop="removeFav(item)">❤️</span>
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

      <el-empty v-if="!loading && list.length === 0" description="还没有收藏的商品哦~" style="padding:80px 0">
        <el-button type="primary" @click="$router.push('/goods')">去逛逛</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useFavorites } from '../composables/useFavorites'

const { toggle, loadAll } = useFavorites()
const list = ref([])
const loading = ref(false)

async function fetchList() {
  loading.value = true
  try {
    list.value = await loadAll(true)
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

async function removeFav(item) {
  try {
    await toggle(item.spu_id)
    list.value = list.value.filter((i) => i.spu_id !== item.spu_id)
    ElMessage.success('已取消收藏')
  } catch {}
}

onMounted(fetchList)
</script>

<style scoped>
.fav-page { flex: 1; }
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
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; }
.page-title span { color: #C4906A; }
.fav-count { font-size: 13px; color: #B0B0B0; margin-left: auto; }

.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px; min-height: 200px;
}

.product-card {
  background: #fff; border-radius: 16px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
  transition: all .28s; cursor: pointer;
  display: flex; flex-direction: column;
}
.product-card:hover { transform: translateY(-6px); box-shadow: 0 12px 48px rgba(0,0,0,.14); }

.product-card-img { width: 100%; aspect-ratio: 1; position: relative; overflow: hidden; }
.card-img { width: 100%; height: 100%; }
.img-err {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: #f0f0f0; color: #bbb; font-size: 48px;
}

.fav-btn {
  position: absolute; top: 10px; right: 10px;
  font-size: 20px; cursor: pointer;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,.3));
  transition: transform .2s;
}
.fav-btn:hover { transform: scale(1.2); }

.product-card-body { padding: 16px; flex: 1; display: flex; flex-direction: column; }
.product-card-name {
  font-size: 14px; font-weight: 600; color: #1A1714;
  line-height: 1.4; margin-bottom: 4px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.product-card-meta { font-size: 12px; color: #6B6B6B; margin-bottom: 8px; }
.product-card-price { margin-top: auto; }
.price-main { font-size: 20px; font-weight: 800; color: #1A1714; }
</style>
