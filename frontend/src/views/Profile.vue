<template>
  <div class="profile-page">
    <div class="container">
      <div class="profile-layout">
        <!-- 左侧 -->
        <div class="profile-sidebar">
          <div class="user-card">
            <div class="avatar">{{ user.avatar_url ? '' : '👤' }}</div>
            <div class="user-info">
              <div class="user-name">{{ user.nickname || '未设置昵称' }}</div>
              <div class="user-sig" v-if="user.signature">{{ user.signature }}</div>
              <div class="user-email">{{ user.email || '未登录' }}</div>
            </div>
            <el-button size="small" plain @click="$router.push('/profile/edit')">编辑资料</el-button>
          </div>

          <div class="menu-list">
            <div class="menu-item" @click="$router.push('/face-detect')">
              <span class="menu-icon">💄</span>
              <span class="menu-label">我的脸型档案</span>
              <span class="menu-value">{{ faceType || '未检测' }}</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item" @click="$router.push('/profile/favorites')">
              <span class="menu-icon">🛍️</span>
              <span class="menu-label">我的收藏</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item" @click="$router.push('/profile/address')">
              <span class="menu-icon">📍</span>
              <span class="menu-label">收货地址管理</span>
              <span class="menu-arrow">›</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">👁️</span>
              <span class="menu-label">浏览历史</span>
              <span class="menu-arrow">›</span>
            </div>
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

        <!-- 右侧 -->
        <div class="profile-main">
          <div class="section">
            <div class="section-header">
              <span class="section-title">我的订单</span>
              <span class="view-all" @click="$router.push('/orders')">全部订单 →</span>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { getMe } from '@/api/user'

const router = useRouter()
const user = ref({ nickname: '', email: '' })
const faceType = ref('')

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const res = await getMe()
    user.value = res.data
    if (res.data.face_shape) faceType.value = res.data.face_shape
  } catch {}
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
.profile-page { flex: 1; }
.container { max-width: 1320px; margin: 0 auto; padding: 32px; }

.profile-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: start;
}

.profile-sidebar {
  display: flex; flex-direction: column; gap: 16px;
}

.user-card {
  background: linear-gradient(135deg, #C4906A, #e8b49a);
  padding: 28px 24px;
  border-radius: 16px;
  display: flex; flex-direction: column; align-items: center;
  gap: 12px; color: #fff; text-align: center;
}
.avatar {
  font-size: 52px; width: 72px; height: 72px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,.2); border-radius: 50%;
}
.user-name { font-size: 18px; font-weight: 700; }
.user-sig { font-size: 13px; opacity: .85; font-style: italic; }
.user-email { font-size: 14px; opacity: .85; }

.menu-list {
  background: #fff; border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
  overflow: hidden;
}
.menu-item {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid #F0F0F0;
  cursor: pointer; transition: background .15s;
}
.menu-item:last-child { border-bottom: none; }
.menu-item:hover { background: #FAF9F7; }
.menu-icon { font-size: 18px; width: 28px; text-align: center; }
.menu-label { flex: 1; font-size: 14px; color: #1A1714; }
.menu-value { font-size: 13px; color: #B0B0B0; }
.menu-arrow { font-size: 16px; color: #EBEBEB; }
.logout .menu-label { color: #E74C3C; }

.profile-main { display: flex; flex-direction: column; gap: 16px; }

.section {
  background: #fff; border-radius: 16px; padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.section-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}
.section-title { font-size: 16px; font-weight: 700; color: #1A1714; }
.view-all { font-size: 13px; color: #C4906A; cursor: pointer; }

.order-icons { display: flex; justify-content: space-around; }
.order-icon-item {
  display: flex; flex-direction: column; align-items: center;
  gap: 8px; cursor: pointer; padding: 12px 20px;
  border-radius: 12px; transition: background .15s;
}
.order-icon-item:hover { background: #FAF9F7; }
.icon-badge-wrap { position: relative; }
.icon { font-size: 32px; }
.icon-label { font-size: 13px; color: #6B6B6B; }
</style>
