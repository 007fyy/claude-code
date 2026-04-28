<template>
  <div class="home-page">
    <!-- 顶部导航 -->
    <div class="topbar">
      <div class="logo">✦ 珑饰</div>
      <div class="search-bar" @click="$router.push('/goods')">
        <el-icon><Search /></el-icon>
        <span>搜索饰品款式...</span>
      </div>
      <el-badge :value="cartCount || null" :max="99">
        <el-button :icon="ShoppingCartFull" circle @click="$router.push('/cart')" />
      </el-badge>
    </div>

    <!-- Banner 轮播 -->
    <el-carousel height="180px" class="banner" :interval="3000">
      <el-carousel-item v-for="b in banners" :key="b.text">
        <div class="banner-item" :style="{ background: b.bg }">
          <div class="banner-text">{{ b.text }}</div>
          <div class="banner-sub">{{ b.sub }}</div>
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 功能入口 -->
    <div class="feature-cards">
      <div class="feat-card" @click="$router.push('/ai-guide')">
        <div class="feat-icon">✨</div>
        <div class="feat-title">AI 导购</div>
        <div class="feat-sub">帮我选款</div>
      </div>
      <div class="feat-card feat-card--ar" @click="$router.push('/goods')">
        <div class="feat-icon">📷</div>
        <div class="feat-title">AR 试戴</div>
        <div class="feat-sub">先试后买</div>
      </div>
    </div>

    <!-- 分类标签 -->
    <div class="category-tabs">
      <span
        v-for="cat in categories"
        :key="cat.value"
        class="cat-tab"
        :class="{ active: activeCat === cat.value }"
        @click="switchCat(cat.value)"
      >{{ cat.label }}</span>
    </div>

    <!-- 推荐商品 -->
    <div class="section-title">
      <span>{{ faceType ? `根据你的脸型推荐` : '为你推荐' }}</span>
      <el-tag v-if="faceType" size="small" type="warning">{{ faceType }}</el-tag>
    </div>

    <div v-loading="loading" class="goods-waterfall">
      <div
        v-for="item in goods"
        :key="item.spu_id"
        class="goods-card"
        @click="$router.push(`/goods/${item.spu_id}`)"
      >
        <el-image :src="item.cover_url" fit="cover" class="goods-img" lazy>
          <template #error>
            <div class="img-err"><el-icon><Picture /></el-icon></div>
          </template>
        </el-image>
        <div class="goods-info">
          <div class="goods-name">{{ item.name }}</div>
          <div class="goods-price">¥ {{ item.price_range }}</div>
          <el-button
            size="small"
            type="primary"
            plain
            class="try-btn"
            :disabled="!item.ar_available"
            @click.stop="tryOn(item)"
          >试戴</el-button>
        </div>
      </div>
      <el-empty v-if="!loading && goods.length === 0" description="暂无商品" />
    </div>

    <div v-if="hasMore" class="load-more">
      <el-button :loading="loadingMore" @click="loadMore" link>加载更多</el-button>
    </div>

    <!-- 底部 Tab -->
    <BottomTab active="home" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, ShoppingCartFull, Picture } from '@element-plus/icons-vue'
import { getGoodsList } from '../api/goods'
import { getCartList } from '../api/cart'
import BottomTab from '../components/BottomTab.vue'

const router = useRouter()
const goods = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const page = ref(1)
const hasMore = ref(true)
const cartCount = ref(0)
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
  { text: '新品上市 · 秋冬主打款', sub: '点击查看全系列', bg: 'linear-gradient(135deg,#c0876a,#e8b49a)' },
  { text: '珍珠系列上新', sub: '复古优雅，温柔加倍', bg: 'linear-gradient(135deg,#9b79c8,#c9adf0)' },
  { text: 'AI 为你精准选款', sub: '3步找到最适合你的饰品', bg: 'linear-gradient(135deg,#5b9bd5,#8dc6f5)' },
]

async function fetchGoods(reset = false) {
  if (reset) { page.value = 1; goods.value = [] }
  loading.value = reset
  loadingMore.value = !reset
  try {
    const res = await getGoodsList({ category: activeCat.value || undefined, page: page.value, page_size: 10 })
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
  router.push({ name: 'FaceARView', query: { spu_id: item.spu_id, sku_id: item.default_sku_id, sku_name: item.name, ar_asset_url: item.ar_asset_url || '', mount_type: item.mount_type } })
}

onMounted(async () => {
  fetchGoods(true)
  try {
    const res = await getCartList()
    cartCount.value = res.items.length
  } catch {}
})
</script>

<style scoped>
.home-page {
  max-width: 480px;
  margin: 0 auto;
  background: #f7f5f3;
  min-height: 100dvh;
  padding-bottom: 72px;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 18px;
  font-weight: 700;
  color: #c0876a;
  flex-shrink: 0;
  letter-spacing: 2px;
}

.search-bar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f5f5f5;
  border-radius: 20px;
  padding: 8px 14px;
  color: #bbb;
  font-size: 14px;
  cursor: pointer;
}

.banner { margin-bottom: 0; }

.banner-item {
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.banner-text { font-size: 22px; font-weight: 700; }
.banner-sub  { font-size: 14px; opacity: 0.85; margin-top: 6px; }

.feature-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 16px 16px 8px;
}

.feat-card {
  background: linear-gradient(135deg, #fff5ef, #ffe8d6);
  border-radius: 16px;
  padding: 20px 16px;
  cursor: pointer;
  transition: transform 0.2s;
}

.feat-card:hover { transform: translateY(-2px); }

.feat-card--ar {
  background: linear-gradient(135deg, #f0f5ff, #d6e8ff);
}

.feat-icon { font-size: 28px; margin-bottom: 6px; }
.feat-title { font-size: 16px; font-weight: 700; color: #333; }
.feat-sub   { font-size: 12px; color: #888; margin-top: 2px; }

.category-tabs {
  display: flex;
  gap: 0;
  padding: 8px 16px;
  overflow-x: auto;
  scrollbar-width: none;
}

.cat-tab {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.cat-tab.active {
  background: #c0876a;
  color: #fff;
  font-weight: 600;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px 4px;
  font-size: 15px;
  font-weight: 700;
  color: #333;
}

.goods-waterfall {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 8px 16px;
}

.goods-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}
.goods-card:hover { transform: translateY(-2px); }

.goods-img { width: 100%; height: 160px; display: block; }

.img-err {
  width: 100%;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  color: #bbb;
  font-size: 32px;
}

.goods-info { padding: 10px; }
.goods-name { font-size: 13px; font-weight: 600; color: #333; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.goods-price { font-size: 15px; font-weight: 700; color: #e6564e; margin-bottom: 8px; }
.try-btn { width: 100%; border-radius: 20px; }

.load-more { text-align: center; padding: 12px; }
</style>
