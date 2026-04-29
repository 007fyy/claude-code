<template>
  <div class="detail-page">
    <div v-loading="loading" v-if="goods" class="container">
      <!-- 面包屑 -->
      <div class="breadcrumb">
        <router-link to="/home">首页</router-link>
        <span class="sep">›</span>
        <router-link to="/goods">商品</router-link>
        <span class="sep">›</span>
        <span class="cur">{{ goods.name }}</span>
      </div>

      <!-- 主体：左图右信息 -->
      <div class="detail-main">
        <div class="detail-left">
          <el-carousel height="500px" class="goods-carousel" :autoplay="false">
            <el-carousel-item v-for="(img, i) in images" :key="i">
              <el-image :src="img" fit="cover" class="carousel-img" :preview-src-list="images" :initial-index="i" preview-teleported>
                <template #error>
                  <div class="img-err"><el-icon><Picture /></el-icon></div>
                </template>
              </el-image>
            </el-carousel-item>
          </el-carousel>

          <!-- AR 试戴入口 -->
          <div class="ar-entry" @click="tryOn">
            <span class="ar-icon">📷</span>
            <div>
              <div class="ar-title">立即虚拟试戴</div>
              <div class="ar-sub">戴上看看效果怎么样 →</div>
            </div>
          </div>
        </div>

        <div class="detail-right">
          <h1 class="goods-name">{{ goods.name }}</h1>
          <div class="price-row">
            <span class="price">¥{{ selectedSku?.price || goods.price_range }}</span>
            <span class="rating">★★★★★ 4.9 · 已售 2.1k</span>
          </div>

          <!-- SKU 选择 -->
          <div class="sku-section" v-if="skuList.length">
            <div class="sku-group">
              <span class="sku-label">规格</span>
              <div class="sku-options">
                <span
                  v-for="s in skuList"
                  :key="s.sku_id"
                  class="sku-opt"
                  :class="{ active: selectedSku?.sku_id === s.sku_id, disabled: s.stock === 0 }"
                  @click="s.stock > 0 && (selectedSku = s)"
                >{{ s.sku_name }}</span>
              </div>
            </div>
            <div class="stock-info">
              库存：{{ selectedSku ? (selectedSku.stock > 0 ? `有货 (${selectedSku.stock}件)` : '暂时缺货') : '请选择规格' }}
            </div>
          </div>

          <!-- 脸型匹配 -->
          <div class="face-match" v-if="faceType">
            <span class="match-icon">✨</span>
            <div>
              <div class="match-title">与你脸型高度匹配</div>
              <div class="match-sub">你是{{ faceType }}，弧形耳环可修饰脸型</div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-btns">
            <button class="btn btn-lg btn-fav" :class="{ active: isFav(route.params.id) }" @click="toggleFav">{{ isFav(route.params.id) ? '❤️ 已收藏' : '🤍 收藏' }}</button>
            <button class="btn btn-lg btn-out-gold" @click="addCart">🛒 加入购物车</button>
            <button class="btn btn-lg btn-dark" @click="buyNow">立即购买</button>
          </div>
        </div>
      </div>

      <!-- 标签页 -->
      <el-tabs class="detail-tabs" v-model="activeTab">
        <el-tab-pane label="商品详情" name="detail">
          <div class="detail-content">
            <div class="desc-item">商品材质：{{ goods.material }}</div>
            <div class="desc-item">适合风格：{{ (goods.style_tags || []).join('、') }}</div>
            <div class="desc-item">适合场合：日常、约会、职场</div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="评价(218)" name="reviews">
          <div class="review-list">
            <div v-for="r in mockReviews" :key="r.id" class="review-item">
              <div class="review-user">{{ r.user }} · ★★★★★</div>
              <div class="review-text">{{ r.text }}</div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="同款推荐" name="similar">
          <div class="similar-grid">
            <div v-for="item in similarGoods" :key="item.spu_id" class="similar-card" @click="$router.push(`/goods/${item.spu_id}`)">
              <el-image :src="item.cover_url" fit="cover" class="similar-img" />
              <div class="similar-name">{{ item.name }}</div>
              <div class="similar-price">¥{{ item.price_range }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-empty v-else-if="!loading" description="商品不存在" style="padding:80px 0" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getGoodsDetail, getGoodsList } from '../api/goods'
import { addToCart } from '../api/cart'
import { useFavorites } from '../composables/useFavorites'
import { trackClick } from '../api/tracking'

const route  = useRoute()
const router = useRouter()
const { isFav, toggle, check } = useFavorites()

const goods       = ref(null)
const loading     = ref(false)
const skuList     = ref([])
const selectedSku = ref(null)
const activeTab   = ref('detail')
const similarGoods = ref([])
const faceType    = ref(localStorage.getItem('faceType') || '')

const images = computed(() => {
  if (!goods.value) return []
  return goods.value.cover_url ? [goods.value.cover_url] : []
})

const mockReviews = [
  { id: 1, user: '小雯', text: '很好看！戴上比想象的更精致，给朋友买了一模一样的。' },
  { id: 2, user: '李M', text: 'AR试戴功能真的超实用，试戴后果断下单，收到货和试戴效果一样！' },
  { id: 3, user: '晴天', text: '质量不错，925银的触感很好，不过敏，值得购买。' },
]

async function loadDetail() {
  loading.value = true
  try {
    const res = await getGoodsDetail(route.params.id)
    goods.value = res.data
    skuList.value = res.data?.skus || []
    if (skuList.value.length) selectedSku.value = skuList.value.find(s => s.stock > 0) || skuList.value[0]
  } catch {
    goods.value = null
  } finally {
    loading.value = false
  }
}

async function loadSimilar() {
  try {
    const res = await getGoodsList({ page: 1, page_size: 6 })
    similarGoods.value = res.items.filter(i => i.spu_id !== route.params.id).slice(0, 5)
  } catch {}
}

async function addCart() {
  if (!selectedSku.value) { ElMessage.warning('请选择规格'); return }
  trackClick('add_cart', selectedSku.value.sku_id, `/goods/${route.params.id}`)
  await addToCart({ sku_id: selectedSku.value.sku_id, quantity: 1 })
  ElMessage.success('已加入购物车')
}

function buyNow() {
  if (!selectedSku.value) { ElMessage.warning('请选择规格'); return }
  trackClick('buy_now', selectedSku.value.sku_id, `/goods/${route.params.id}`)
  addToCart({ sku_id: selectedSku.value.sku_id, quantity: 1 }).then(() => {
    router.push('/cart')
  })
}

function tryOn() {
  trackClick('ar_try', route.params.id, `/goods/${route.params.id}`)
  router.push({
    name: 'FaceARView',
    query: {
      spu_id: goods.value.spu_id,
      sku_id: selectedSku.value?.sku_id || goods.value.default_sku_id,
      sku_name: goods.value.name,
      ar_asset_url: goods.value.ar_asset_url || '',
      mount_type: goods.value.mount_type,
    },
  })
}

async function toggleFav() {
  trackClick('favorite', route.params.id, `/goods/${route.params.id}`)
  try {
    const faved = await toggle(route.params.id)
    ElMessage.success(faved ? '已收藏' : '已取消收藏')
  } catch {}
}

async function loadFavState() {
  try {
    await check(route.params.id)
  } catch {}
}

onMounted(() => {
  loadDetail()
  loadSimilar()
  if (localStorage.getItem('token')) loadFavState()
})
</script>

<style scoped>
.detail-page { flex: 1; }
.container { max-width: 1320px; margin: 0 auto; padding: 0 32px 60px; }

.breadcrumb {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: #6B6B6B; padding: 16px 0 8px;
}
.breadcrumb a { color: #6B6B6B; text-decoration: none; transition: color .15s; }
.breadcrumb a:hover { color: #C4906A; }
.sep { color: #B0B0B0; }
.cur { color: #1A1714; font-weight: 600; }

.detail-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  margin-bottom: 40px;
}

.goods-carousel { border-radius: 16px; overflow: hidden; }
.carousel-img { width: 100%; height: 500px; }
.img-err { width: 100%; height: 500px; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; font-size: 48px; }

.ar-entry {
  display: flex; align-items: center; gap: 14px;
  margin-top: 16px;
  background: linear-gradient(135deg, #C4906A, #e8b49a);
  border-radius: 14px; padding: 18px 24px;
  cursor: pointer; color: #fff; transition: transform .2s;
}
.ar-entry:hover { transform: translateY(-2px); }
.ar-icon { font-size: 28px; }
.ar-title { font-size: 16px; font-weight: 700; }
.ar-sub { font-size: 13px; opacity: .85; }

.goods-name { font-size: 24px; font-weight: 800; color: #1A1714; margin-bottom: 16px; line-height: 1.4; }

.price-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.price { font-size: 28px; font-weight: 800; color: #1A1714; }
.rating { font-size: 13px; color: #B0B0B0; }

.sku-section { background: #FAF9F7; border-radius: 12px; padding: 18px; margin-bottom: 16px; }
.sku-group { margin-bottom: 10px; display: flex; align-items: flex-start; gap: 12px; }
.sku-label { font-size: 13px; color: #6B6B6B; flex-shrink: 0; padding-top: 6px; }
.sku-options { display: flex; flex-wrap: wrap; gap: 8px; }
.sku-opt {
  padding: 8px 18px; border: 1.5px solid #EBEBEB; border-radius: 20px;
  font-size: 13px; cursor: pointer; transition: all .2s;
}
.sku-opt.active { border-color: #C4906A; color: #C4906A; background: #F5EDE3; }
.sku-opt.disabled { opacity: .4; cursor: not-allowed; }
.stock-info { font-size: 13px; color: #27AE60; }

.face-match {
  display: flex; align-items: flex-start; gap: 12px;
  background: linear-gradient(135deg, #fff5ef, #ffe8d6);
  border-radius: 12px; padding: 16px; margin-bottom: 24px;
}
.match-icon { font-size: 24px; }
.match-title { font-size: 14px; font-weight: 600; color: #C4906A; }
.match-sub { font-size: 13px; color: #6B6B6B; margin-top: 4px; }

.action-btns { display: flex; gap: 12px; }
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 7px;
  font-size: 16px; font-weight: 700; border-radius: 12px;
  padding: 15px 32px; transition: all .2s; cursor: pointer; border: none; flex: 1;
}
.btn:hover { transform: translateY(-1px); }
.btn-dark { background: #1A1714; color: white; }
.btn-dark:hover { background: #2D231A; box-shadow: 0 4px 16px rgba(26,23,20,.3); }
.btn-out-gold { background: transparent; color: #C4906A; border: 1.5px solid #C4906A; }
.btn-out-gold:hover { background: #C4906A; color: white; }
.btn-fav { background: #FAF9F7; color: #6B6B6B; border: 1.5px solid #EBEBEB; flex: 0 0 auto; }
.btn-fav:hover { border-color: #C4906A; color: #C4906A; }
.btn-fav.active { background: #FFF0F0; color: #E74C3C; border-color: #E74C3C; }
.btn-lg { padding: 15px 32px; font-size: 16px; }

.detail-tabs { margin-top: 8px; }
.detail-content { padding: 20px 0; }
.desc-item { font-size: 14px; color: #6B6B6B; padding: 8px 0; border-bottom: 1px solid #F0F0F0; }

.review-list { padding: 20px 0; }
.review-item { margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #F0F0F0; }
.review-user { font-size: 13px; color: #B0B0B0; margin-bottom: 6px; }
.review-text { font-size: 14px; color: #6B6B6B; line-height: 1.6; }

.similar-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px; padding: 20px 0;
}
.similar-card { cursor: pointer; transition: transform .2s; }
.similar-card:hover { transform: translateY(-4px); }
.similar-img { width: 100%; aspect-ratio: 1; border-radius: 12px; display: block; }
.similar-name { font-size: 13px; color: #1A1714; margin-top: 8px; font-weight: 500; }
.similar-price { font-size: 15px; font-weight: 700; color: #1A1714; margin-top: 4px; }
</style>
