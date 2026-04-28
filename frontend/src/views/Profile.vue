<template>
  <div class="profile-page">
    <div class="topbar">
      <span class="title">我的</span>
      <el-button :icon="Setting" circle />
    </div>

    <!-- 用户信息 -->
    <div class="user-card">
      <div class="avatar">👤</div>
      <div class="user-info">
        <div class="user-name">{{ user.nickname || user.phone || '游客' }}</div>
        <div class="user-phone">{{ user.phone || '未登录' }}</div>
      </div>
      <el-button size="small" plain>编辑资料</el-button>
    </div>

    <!-- 我的订单 -->
    <div class="section">
      <div class="section-header">
        <span class="section-title">我的订单</span>
        <span class="view-all" @click="$router.push('/orders')">全部订单 ›</span>
      </div>
      <div class="order-icons">
        <div v-for="item in orderTabs" :key="item.label" class="order-icon-item" @click="$router.push(item.path)">
          <div class="icon-badge-wrap">
            <span class="icon">{{ item.icon }}</span>
            <el-badge v-if="item.count" :value="item.count" class="badge" />
          </div>
          <span class="icon-label">{{ item.label }}</span>
        </div>
      </div>
    </div>

    <!-- 我的服务 -->
    <div class="section">
      <div class="section-title">我的服务</div>
      <div class="menu-list">
        <div class="menu-item" @click="$router.push('/face-detect')">
          <span class="menu-icon">💄</span>
          <span class="menu-label">我的脸型档案</span>
          <span class="menu-value">{{ faceType || '未检测' }}</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">🛍️</span>
          <span class="menu-label">我的收藏</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">📍</span>
          <span class="menu-label">收货地址管理</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">👁️</span>
          <span class="menu-label">浏览历史</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
    </div>

    <!-- 其他 -->
    <div class="section">
      <div class="section-title">其他</div>
      <div class="menu-list">
        <div class="menu-item">
          <span class="menu-icon">💬</span>
          <span class="menu-label">联系客服</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">❓</span>
          <span class="menu-label">常见问题</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item">
          <span class="menu-icon">⚖️</span>
          <span class="menu-label">用户协议 / 隐私政策</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item logout" @click="logout">
          <span class="menu-icon">🚪</span>
          <span class="menu-label">退出登录</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
    </div>

    <BottomTab active="profile" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Setting } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import BottomTab from '../components/BottomTab.vue'
import { getMe } from '@/api/user'

const router = useRouter()

const user = ref({ nickname: '游客', phone: '未登录' })
const faceType = ref('')

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const res = await getMe()
    user.value = res.data
    if (res.data.face_shape) faceType.value = res.data.face_shape
  } catch {
    // token invalid — fall through with defaults
  }
})

const orderTabs = [
  { icon: '⏰', label: '待付款', path: '/orders?status=pending', count: 0 },
  { icon: '📦', label: '待发货', path: '/orders?status=paid',    count: 0 },
  { icon: '🚚', label: '待收货', path: '/orders?status=shipped', count: 0 },
  { icon: '🔄', label: '售后',   path: '/orders?status=refunding', count: 0 },
]

async function logout() {
  await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
.profile-page {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100dvh;
  background: #f7f5f3;
  padding-bottom: 80px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fff;
  margin-bottom: 12px;
}
.title { font-size: 20px; font-weight: 700; color: #333; }

.user-card {
  background: linear-gradient(135deg, #c0876a, #e8b49a);
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  color: #fff;
  margin-bottom: 12px;
}

.avatar { font-size: 52px; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.2); border-radius: 50%; flex-shrink: 0; }
.user-name  { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
.user-phone { font-size: 14px; opacity: 0.85; }

.section {
  background: #fff;
  padding: 16px;
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 14px; }
.view-all { font-size: 13px; color: #c0876a; cursor: pointer; }

.order-icons { display: flex; justify-content: space-around; }

.order-icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 12px;
}

.icon-badge-wrap { position: relative; }
.icon { font-size: 28px; }
.icon-label { font-size: 12px; color: #666; }

.menu-list { display: flex; flex-direction: column; }

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 0;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}
.menu-item:last-child { border-bottom: none; }

.menu-icon { font-size: 20px; width: 28px; text-align: center; }
.menu-label { flex: 1; font-size: 14px; color: #333; }
.menu-value { font-size: 13px; color: #bbb; }
.menu-arrow { font-size: 16px; color: #ccc; }

.logout .menu-label { color: #f56c6c; }
</style>
