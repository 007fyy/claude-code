<template>
  <div class="goods-page">
    <!-- 顶部导航 -->
    <div class="topbar">
      <h1 class="logo">✦ 饰品商城</h1>
      <el-button type="primary" plain @click="$router.push('/cart')">
        <el-icon><ShoppingCart /></el-icon>
        购物车
        <el-badge v-if="cartCount > 0" :value="cartCount" class="badge-dot" />
      </el-button>
    </div>

    <!-- 分类筛选 -->
    <div class="filter-bar">
      <el-radio-group v-model="category" @change="fetchGoods(1)">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="earring">耳饰</el-radio-button>
        <el-radio-button label="necklace">项链</el-radio-button>
        <el-radio-button label="hairpin">发饰</el-radio-button>
        <el-radio-button label="bracelet">手链</el-radio-button>
        <el-radio-button label="brooch">胸针</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 商品网格 -->
    <div v-loading="loading" class="goods-grid">
      <el-card
        v-for="item in goods"
        :key="item.spu_id"
        class="goods-card"
        shadow="hover"
      >
        <el-image
          :src="item.cover_url"
          fit="cover"
          class="goods-img"
          :preview-src-list="[item.cover_url]"
          preview-teleported
        >
          <template #error>
            <div class="img-placeholder"><el-icon><Picture /></el-icon></div>
          </template>
        </el-image>

        <div class="goods-body">
          <div class="goods-name" :title="item.name">{{ item.name }}</div>
          <div class="goods-meta">
            <span class="material">{{ item.material }}</span>
          </div>
          <div class="tags">
            <el-tag
              v-for="tag in (item.style_tags || []).slice(0, 3)"
              :key="tag"
              size="small"
              type="info"
              effect="plain"
            >{{ tag }}</el-tag>
          </div>
          <div class="price">¥ {{ item.price_range }}</div>
          <div class="actions">
            <el-button size="small" @click="addCart(item)">
              <el-icon><ShoppingCartFull /></el-icon>
              加购
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click="tryOn(item)"
              :disabled="!item.ar_available"
            >
              <el-icon><Camera /></el-icon>
              AR 试戴
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 无数据 -->
      <el-empty v-if="!loading && goods.length === 0" description="暂无商品" />
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        :pager-count="5"
        layout="prev, pager, next, total"
        @current-change="fetchGoods"
        background
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getGoodsList } from '../api/goods'
import { addToCart, getCartList } from '../api/cart'

const router = useRouter()

const goods = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)
const category = ref('')
const loading = ref(false)
const cartCount = ref(0)

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

onMounted(() => {
  fetchGoods()
  refreshCartCount()
})
</script>

<style scoped>
.goods-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px 40px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px;
  position: relative;
}

.logo {
  font-size: 22px;
  font-weight: 700;
  color: #333;
  letter-spacing: 2px;
}

.badge-dot {
  margin-left: 4px;
}

.filter-bar {
  margin-bottom: 20px;
}

.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  min-height: 200px;
}

.goods-card {
  cursor: default;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.2s;
}

.goods-card:hover {
  transform: translateY(-2px);
}

.goods-img {
  width: 100%;
  height: 200px;
  display: block;
}

.img-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  font-size: 40px;
  color: #bbb;
}

.goods-body {
  padding: 12px;
}

.goods-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.goods-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
}

.tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.price {
  font-size: 16px;
  font-weight: 700;
  color: #e6564e;
  margin-bottom: 10px;
}

.actions {
  display: flex;
  gap: 8px;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
