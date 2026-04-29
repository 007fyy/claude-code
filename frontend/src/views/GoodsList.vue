<template>
  <div class="goods-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title"><span>✦</span> 饰品商城</h1>
        <router-link to="/cart" class="cart-link">
          🛒 购物车
          <el-badge v-if="cartCount > 0" :value="cartCount" />
        </router-link>
      </div>

      <!-- 分类筛选 -->
      <div class="filter-bar">
        <span
          v-for="cat in cats"
          :key="cat.value"
          class="chip"
          :class="{ active: category === cat.value }"
          @click="category = cat.value; fetchGoods(1)"
        >{{ cat.label }}</span>
      </div>

      <!-- 商品网格 -->
      <div v-loading="loading" class="goods-grid">
        <div
          v-for="item in goods"
          :key="item.spu_id"
          class="product-card"
          @click="$router.push(`/goods/${item.spu_id}`)"
          shadow="hover"
        >
          <div class="product-card-img">
            <el-image :src="item.cover_url" fit="cover" class="card-img">
              <template #error>
                <div class="img-err"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
            <span class="fav-btn" :class="{ active: isFav(item.spu_id) }" @click.stop="toggleFav(item)">{{ isFav(item.spu_id) ? '❤️' : '🤍' }}</span>
            <span class="try-badge" v-if="item.ar_available" @click.stop="tryOn(item)">📷 AR 试戴</span>
          </div>
          <div class="product-card-body">
            <div class="product-card-name" :title="item.name">{{ item.name }}</div>
            <div class="product-card-meta">
              <span class="material">{{ item.material }}</span>
            </div>
            <div class="tags">
              <span v-for="tag in (item.style_tags || []).slice(0, 3)" :key="tag" class="tag tag-gold">{{ tag }}</span>
            </div>
            <div class="product-card-price">
              <span class="price-main">¥{{ item.price_range }}</span>
            </div>
            <div class="product-card-actions">
              <button class="btn btn-sm btn-lt" @click.stop="addCart(item)">🛒 加购</button>
              <button class="btn btn-sm btn-dark" @click.stop="tryOn(item)" :disabled="!item.ar_available">📷 试戴</button>
            </div>
          </div>
        </div>

        <el-empty v-if="!loading && goods.length === 0" description="暂无商品" />
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          :pager-count="7"
          layout="prev, pager, next, total"
          @current-change="fetchGoods"
          background
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { getGoodsList } from '../api/goods'
import { addToCart, getCartList } from '../api/cart'
import { useFavorites } from '../composables/useFavorites'
import { trackClick } from '../api/tracking'

const router = useRouter()
const { isFav, toggle, ensureLoaded } = useFavorites()

const goods = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)
const category = ref('')
const loading = ref(false)
const cartCount = ref(0)

const cats = [
  { label: '全部', value: '' },
  { label: '耳饰', value: 'earring' },
  { label: '项链', value: 'necklace' },
  { label: '发饰', value: 'hairpin' },
  { label: '手链', value: 'bracelet' },
  { label: '胸针', value: 'brooch' },
]

async function fetchGoods(p = 1) {
  page.value = p
  loading.value = true
  try {
    const res = await getGoodsList({
      category: category.value || undefined,
      page: page.value,
      page_size: pageSize.value,
    })
    goods.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function refreshCartCount() {
  try {
    const res = await getCartList()
    cartCount.value = res.items.length
  } catch {
    // ignore
  }
}

async function addCart(item) {
  if (!item.default_sku_id) {
    ElMessage.warning('该商品暂无可购规格')
    return
  }
  await addToCart({ sku_id: item.default_sku_id, quantity: 1 })
  ElMessage.success('已加入购物车')
  refreshCartCount()
}

function tryOn(item) {
  trackClick('ar_try', item.spu_id, '/goods')
  router.push({
    name: 'FaceARView',
    query: {
      spu_id: item.spu_id,
      sku_id: item.default_sku_id,
      sku_name: item.name,
      ar_asset_url: item.ar_asset_url || '',
      mount_type: item.mount_type,
    },
  })
}

async function toggleFav(item) {
  trackClick('favorite', item.spu_id, '/goods')
  try {
    const faved = await toggle(item.spu_id)
    ElMessage.success(faved ? '已收藏' : '已取消收藏')
  } catch {}
}

onMounted(() => {
  fetchGoods()
  refreshCartCount()
  if (localStorage.getItem('token')) ensureLoaded()
})
</script>

<style scoped>
.goods-page { flex: 1; }

.container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 32px 60px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 0 20px;
}
.page-title {
  font-size: 24px; font-weight: 800; color: #1A1714;
}
.page-title span { color: #C4906A; }
.cart-link {
  font-size: 14px; font-weight: 600; color: #6B6B6B;
  text-decoration: none; transition: color .15s;
}
.cart-link:hover { color: #1A1714; }

.filter-bar {
  display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap;
}
.chip {
  display: inline-flex; align-items: center;
  padding: 8px 20px; border-radius: 20px;
  font-size: 13px; font-weight: 500;
  border: 1.5px solid #EBEBEB; background: #fff; color: #6B6B6B;
  cursor: pointer; transition: all .15s;
}
.chip:hover { border-color: #C4906A; color: #9E7050; }
.chip.active { background: #1A1714; color: white; border-color: #1A1714; }

.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.product-card {
  background: #fff; border-radius: 16px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
  transition: all .28s; cursor: pointer;
  display: flex; flex-direction: column;
}
.product-card:hover { transform: translateY(-6px); box-shadow: 0 12px 48px rgba(0,0,0,.14); }

.product-card-img {
  width: 100%; aspect-ratio: 1; position: relative; overflow: hidden;
}
.card-img { width: 100%; height: 100%; }
.img-err {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: #f0f0f0; color: #bbb; font-size: 48px;
}
.try-badge {
  position: absolute; bottom: 10px; right: 10px;
  background: rgba(0,0,0,.6); color: white;
  font-size: 11px; font-weight: 600;
  padding: 4px 10px; border-radius: 20px;
  backdrop-filter: blur(6px);
  opacity: 0; transform: translateY(4px); transition: all .2s;
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

.product-card-body { padding: 14px 14px 16px; flex: 1; display: flex; flex-direction: column; }
.product-card-name {
  font-size: 14px; font-weight: 600; color: #1A1714;
  line-height: 1.4; margin-bottom: 4px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.product-card-meta { font-size: 12px; color: #6B6B6B; margin-bottom: 6px; }
.tags { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 8px; }
.tag {
  display: inline-block; padding: 3px 9px; border-radius: 5px;
  font-size: 12px; font-weight: 600;
}
.tag-gold { background: #F5EDE3; color: #9E7050; }

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
.btn-dark:disabled { background: #B0B0B0; cursor: not-allowed; transform: none; }
.btn-lt { background: #F5EDE3; color: #9E7050; }
.btn-lt:hover { background: #EEE0CE; }

.pagination { margin-top: 32px; display: flex; justify-content: center; }
</style>
