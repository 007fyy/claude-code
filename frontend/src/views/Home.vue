<template>
  <div class="home-page">
    <!-- Banner 轮播 -->
    <el-carousel height="400px" class="banner" :interval="3000">
      <el-carousel-item v-for="b in banners" :key="b.text">
        <div class="banner-item" :style="{ background: b.bg }">
          <div class="banner-text">{{ b.text }}</div>
          <div class="banner-sub">{{ b.sub }}</div>
        </div>
      </el-carousel-item>
    </el-carousel>

    <div class="container">
      <!-- 功能入口 -->
      <div class="feature-cards">
        <div class="feat-card" @click="$router.push('/ai-guide')">
          <div class="feat-icon">✨</div>
          <div class="feat-title">AI 智能导购</div>
          <div class="feat-sub">4 步问答，精准匹配个性化推荐</div>
        </div>
        <div class="feat-card feat-card--ar" @click="$router.push('/goods')">
          <div class="feat-icon">📷</div>
          <div class="feat-title">AR 虚拟试戴</div>
          <div class="feat-sub">实时摄像头叠加，买前先试</div>
        </div>
        <div class="feat-card feat-card--face" @click="$router.push('/face-detect')">
          <div class="feat-icon">👤</div>
          <div class="feat-title">脸型精准匹配</div>
          <div class="feat-sub">AI 分析脸型，推荐最适合的款式</div>
        </div>
        <div class="feat-card feat-card--vip" @click="$router.push('/profile')">
          <div class="feat-icon">💎</div>
          <div class="feat-title">会员中心</div>
          <div class="feat-sub">专属优惠，积分兑换</div>
        </div>
      </div>

      <!-- 分类标签 -->
      <div class="section-head">
        <div class="section-title">
          <span>✦</span> {{ faceType ? '根据你的脸型推荐' : '为你推荐' }}
          <el-tag v-if="faceType" size="small" type="warning" style="margin-left:8px">{{ faceType }}</el-tag>
        </div>
        <router-link to="/goods" class="section-more">查看全部 →</router-link>
      </div>

      <div class="category-tabs">
        <span
          v-for="cat in categories"
          :key="cat.value"
          class="chip"
          :class="{ active: activeCat === cat.value }"
          @click="switchCat(cat.value)"
        >{{ cat.label }}</span>
      </div>

      <!-- 商品网格 -->
      <div v-loading="loading" class="goods-grid">
        <div
          v-for="item in goods"
          :key="item.spu_id"
          class="product-card"
          @click="goDetail(item)"
        >
          <div class="product-card-img">
            <el-image :src="item.cover_url" fit="cover" class="card-img" lazy>
              <template #error>
                <div class="img-err"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
            <span class="fav-btn" :class="{ active: isFav(item.spu_id) }" @click.stop="toggleFav(item)">{{ isFav(item.spu_id) ? '❤️' : '🤍' }}</span>
            <span class="try-badge" v-if="item.ar_available" @click.stop="tryOn(item)">📷 试戴</span>
          </div>
          <div class="product-card-body">
            <div class="product-card-name">{{ item.name }}</div>
            <div class="product-card-sub">{{ item.material }}</div>
            <div class="product-card-price">
              <span class="price-main">¥{{ item.price_range }}</span>
            </div>
            <div class="product-card-actions">
              <button class="btn btn-sm btn-lt" @click.stop="addCart(item)">🛒 加购</button>
              <button class="btn btn-sm btn-dark" @click.stop="buyNow(item)">立即购买</button>
            </div>
          </div>
        </div>
        <el-empty v-if="!loading && goods.length === 0" description="暂无商品" />
      </div>

      <div v-if="hasMore" class="load-more">
        <el-button :loading="loadingMore" @click="loadMore">加载更多</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getGoodsList } from '../api/goods'
import { addToCart } from '../api/cart'
import { useFavorites } from '../composables/useFavorites'
import { trackClick } from '../api/tracking'

const router = useRouter()
const { isFav, toggle, ensureLoaded } = useFavorites()
const goods = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const page = ref(1)
const hasMore = ref(true)
const activeCat = ref('')
const faceType = ref(localStorage.getItem('faceType') || '')

const categories = [
  { label: '全部', value: '' },
  { label: '耳饰', value: 'earring' },
  { label: '项链', value: 'necklace' },
  { label: '手链', value: 'bracelet' },
  { label: '戒指', value: 'ring' },
  { label: '套装', value: 'set' },
]

const banners = [
  { text: '新品上市 · 秋冬主打款', sub: '点击查看全系列', bg: 'linear-gradient(135deg,#1A1714,#4A3020)' },
  { text: '珍珠系列上新', sub: '复古优雅，温柔加倍', bg: 'linear-gradient(135deg,#9b79c8,#c9adf0)' },
  { text: 'AI 为你精准选款', sub: '3步找到最适合你的饰品', bg: 'linear-gradient(135deg,#C4906A,#e8b49a)' },
]

async function fetchGoods(reset = false) {
  if (reset) { page.value = 1; goods.value = [] }
  loading.value = reset
  loadingMore.value = !reset
  try {
    const res = await getGoodsList({ category: activeCat.value || undefined, page: page.value, page_size: 12 })
    goods.value = reset ? res.items : [...goods.value, ...res.items]
    hasMore.value = goods.value.length < res.total
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function switchCat(val) {
  activeCat.value = val
  fetchGoods(true)
}

function loadMore() {
  page.value++
  fetchGoods(false)
}

function tryOn(item) {
  trackClick('ar_try', item.spu_id, '/home')
  router.push({ name: 'FaceARView', query: { spu_id: item.spu_id, sku_id: item.default_sku_id, sku_name: item.name, ar_asset_url: item.ar_asset_url || '', mount_type: item.mount_type } })
}

function goDetail(item) {
  trackClick('goods', item.spu_id, '/home')
  router.push(`/goods/${item.spu_id}`)
}

async function toggleFav(item) {
  trackClick('favorite', item.spu_id, '/home')
  try {
    const faved = await toggle(item.spu_id)
    ElMessage.success(faved ? '已收藏' : '已取消收藏')
  } catch {}
}

async function addCart(item) {
  trackClick('add_cart', item.spu_id, '/home')
  if (!item.default_sku_id) { ElMessage.warning('该商品暂无可购规格'); return }
  await addToCart({ sku_id: item.default_sku_id, quantity: 1 })
  ElMessage.success('已加入购物车')
}

function buyNow(item) {
  trackClick('buy_now', item.spu_id, '/home')
  if (!item.default_sku_id) { ElMessage.warning('该商品暂无可购规格'); return }
  addToCart({ sku_id: item.default_sku_id, quantity: 1 }).then(() => router.push('/cart'))
}

onMounted(() => {
  fetchGoods(true)
  if (localStorage.getItem('token')) ensureLoaded()
})
</script>

<style scoped>
.home-page { flex: 1; }

.banner-item {
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.banner-text { font-size: 36px; font-weight: 800; letter-spacing: 1px; }
.banner-sub { font-size: 16px; opacity: .8; margin-top: 10px; }

.container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 32px 60px;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin: -40px 0 40px;
  position: relative;
  z-index: 1;
}

.feat-card {
  background: linear-gradient(135deg, #fff5ef, #ffe8d6);
  border-radius: 16px;
  padding: 28px 24px;
  cursor: pointer;
  transition: all .25s;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.feat-card:hover { transform: translateY(-4px); box-shadow: 0 12px 48px rgba(0,0,0,.14); }
.feat-card--ar { background: linear-gradient(135deg, #f0f5ff, #d6e8ff); }
.feat-card--face { background: linear-gradient(135deg, #f5f0ff, #e8d6ff); }
.feat-card--vip { background: linear-gradient(135deg, #fff0f5, #ffd6e8); }

.feat-icon { font-size: 32px; margin-bottom: 10px; }
.feat-title { font-size: 16px; font-weight: 700; color: #1A1714; margin-bottom: 4px; }
.feat-sub { font-size: 13px; color: #6B6B6B; }

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 20px;
}
.section-title {
  font-size: 22px;
  font-weight: 800;
  color: #1A1714;
}
.section-title span { color: #C4906A; margin-right: 6px; }
.section-more {
  font-size: 13px;
  color: #6B6B6B;
  text-decoration: none;
  transition: color .15s;
}
.section-more:hover { color: #C4906A; }

.category-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.chip {
  display: inline-flex;
  align-items: center;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  border: 1.5px solid #EBEBEB;
  background: #fff;
  color: #6B6B6B;
  cursor: pointer;
  transition: all .15s;
}
.chip:hover { border-color: #C4906A; color: #9E7050; }
.chip.active { background: #1A1714; color: white; border-color: #1A1714; }

.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.product-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
  transition: all .28s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}
.product-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 48px rgba(0,0,0,.14);
}

.product-card-img {
  width: 100%;
  aspect-ratio: 1;
  position: relative;
  overflow: hidden;
}
.card-img { width: 100%; height: 100%; }
.img-err {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: #f0f0f0; color: #bbb; font-size: 48px;
}

.try-badge {
  position: absolute;
  bottom: 10px; right: 10px;
  background: rgba(0,0,0,.6);
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 20px;
  backdrop-filter: blur(6px);
  opacity: 0;
  transform: translateY(4px);
  transition: all .2s;
  cursor: pointer;
}
.product-card:hover .try-badge { opacity: 1; transform: translateY(0); }

.fav-btn {
  position: absolute; top: 10px; right: 10px;
  font-size: 20px; cursor: pointer;
  opacity: 0; transition: all .2s;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,.3));
}
.product-card:hover .fav-btn { opacity: 1; }
.fav-btn.active { opacity: 1; }

.product-card-body { padding: 16px; flex: 1; display: flex; flex-direction: column; }
.product-card-name {
  font-size: 14px; font-weight: 600; color: #1A1714;
  line-height: 1.4; margin-bottom: 4px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.product-card-sub { font-size: 12px; color: #6B6B6B; margin-bottom: 8px; }
.product-card-price { margin-bottom: 10px; }
.price-main { font-size: 20px; font-weight: 800; color: #1A1714; }

.product-card-actions {
  display: flex; gap: 8px; margin-top: auto;
  opacity: 0; transform: translateY(4px); transition: all .22s;
}
.product-card:hover .product-card-actions { opacity: 1; transform: translateY(0); }

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 4px;
  font-size: 13px; font-weight: 700; border-radius: 8px;
  padding: 8px 18px; transition: all .2s; cursor: pointer; border: none;
}
.btn:hover { transform: translateY(-1px); }
.btn-sm { padding: 6px 14px; font-size: 12px; }
.btn-dark { background: #1A1714; color: white; }
.btn-dark:hover { background: #2D231A; }
.btn-lt { background: #F5EDE3; color: #9E7050; }
.btn-lt:hover { background: #EEE0CE; }

.load-more { text-align: center; padding: 24px; }
</style>
