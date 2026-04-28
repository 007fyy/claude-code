<template>
  <div class="detail-page">
    <div class="topbar" :class="{ scrolled: isScrolled }">
      <el-button :icon="ArrowLeft" circle @click="$router.back()" />
      <span class="nav-title" v-if="isScrolled">{{ goods?.name }}</span>
      <div class="nav-actions">
        <el-button :icon="Share" circle />
        <el-button :icon="Star" circle />
      </div>
    </div>

    <div v-loading="loading" v-if="goods">
      <!-- 图片区 -->
      <el-carousel height="300px" class="goods-carousel" :autoplay="false">
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

      <div class="goods-main">
        <div class="goods-name">{{ goods.name }}</div>
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
          <div class="similar-scroll">
            <div v-for="item in similarGoods" :key="item.spu_id" class="similar-card" @click="$router.push(`/goods/${item.spu_id}`)">
              <el-image :src="item.cover_url" fit="cover" class="similar-img" />
              <div class="similar-name">{{ item.name }}</div>
              <div class="similar-price">¥{{ item.price_range }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-empty v-else-if="!loading" description="商品不存在" />

    <!-- 底部操作 -->
    <div class="bottom-bar" v-if="goods">
      <el-button size="large" class="cart-btn" @click="addCart">加入购物车</el-button>
      <el-button type="primary" size="large" class="buy-btn" @click="buyNow">立即购买</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Share, Star, Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getGoodsDetail, getGoodsList } from '../api/goods'
import { addToCart } from '../api/cart'

const route  = useRoute()
const router = useRouter()

const goods       = ref(null)
const loading     = ref(false)
const skuList     = ref([])
const selectedSku = ref(null)
const activeTab   = ref('detail')
const isScrolled  = ref(false)
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

function onScroll() {
  isScrolled.value = window.scrollY > 200
}

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
  await addToCart({ sku_id: selectedSku.value.sku_id, quantity: 1 })
  ElMessage.success('已加入购物车')
}

function buyNow() {
  if (!selectedSku.value) { ElMessage.warning('请选择规格'); return }
  addToCart({ sku_id: selectedSku.value.sku_id, quantity: 1 }).then(() => {
    router.push('/cart')
  })
}

function tryOn() {
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

onMounted(() => {
  loadDetail()
  loadSimilar()
  window.addEventListener('scroll', onScroll)
})

onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.detail-page {
  max-width: 480px;
  margin: 0 auto;
  background: #f7f5f3;
  min-height: 100dvh;
  padding-bottom: 80px;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: background 0.3s;
  background: transparent;
}

.topbar.scrolled { background: #fff; box-shadow: 0 1px 8px rgba(0,0,0,0.08); }
.nav-title { flex: 1; font-size: 15px; font-weight: 600; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nav-actions { display: flex; gap: 8px; margin-left: auto; }

.goods-carousel { background: #fff; }
.carousel-img { width: 100%; height: 300px; }
.img-err { width: 100%; height: 300px; display: flex; align-items: center; justify-content: center; background: #f0f0f0; color: #bbb; font-size: 48px; }

.ar-entry {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 12px 16px;
  background: linear-gradient(135deg, #c0876a, #e8b49a);
  border-radius: 14px;
  padding: 16px 20px;
  cursor: pointer;
  color: #fff;
}

.ar-icon  { font-size: 28px; }
.ar-title { font-size: 16px; font-weight: 700; }
.ar-sub   { font-size: 13px; opacity: 0.85; }

.goods-main { background: #fff; margin: 0 0 8px; padding: 16px; }

.goods-name { font-size: 18px; font-weight: 700; color: #333; margin-bottom: 10px; }

.price-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.price { font-size: 24px; font-weight: 700; color: #e6564e; }
.rating { font-size: 13px; color: #999; }

.sku-section { background: #f9f9f9; border-radius: 12px; padding: 14px; margin-bottom: 12px; }
.sku-group { margin-bottom: 10px; display: flex; align-items: flex-start; gap: 12px; }
.sku-label { font-size: 13px; color: #888; flex-shrink: 0; padding-top: 6px; }
.sku-options { display: flex; flex-wrap: wrap; gap: 8px; }
.sku-opt {
  padding: 6px 14px;
  border: 1.5px solid #ddd;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.sku-opt.active { border-color: #c0876a; color: #c0876a; background: #fdf6f0; }
.sku-opt.disabled { opacity: 0.4; cursor: not-allowed; }
.stock-info { font-size: 13px; color: #67c23a; }

.face-match {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: linear-gradient(135deg, #fff5ef, #ffe8d6);
  border-radius: 12px;
  padding: 14px;
}

.match-icon { font-size: 24px; }
.match-title { font-size: 14px; font-weight: 600; color: #c0876a; }
.match-sub   { font-size: 13px; color: #888; margin-top: 4px; }

.detail-tabs { background: #fff; margin-top: 0; }

.detail-content { padding: 16px; }
.desc-item { font-size: 14px; color: #555; padding: 6px 0; border-bottom: 1px solid #f5f5f5; }

.review-list { padding: 16px; }
.review-item { margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #f5f5f5; }
.review-user { font-size: 13px; color: #999; margin-bottom: 6px; }
.review-text { font-size: 14px; color: #555; line-height: 1.6; }

.similar-scroll { display: flex; gap: 12px; padding: 16px; overflow-x: auto; scrollbar-width: none; }
.similar-card { flex-shrink: 0; width: 120px; cursor: pointer; }
.similar-img { width: 120px; height: 120px; border-radius: 10px; display: block; }
.similar-name { font-size: 12px; color: #333; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.similar-price { font-size: 13px; font-weight: 700; color: #e6564e; }

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

.cart-btn { flex: 1; border-radius: 24px; border-color: #c0876a; color: #c0876a; }
.buy-btn  { flex: 1; border-radius: 24px; }
</style>
