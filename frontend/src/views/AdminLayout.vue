<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span>💎</span> 珑饰管理后台
      </div>

      <nav class="sidebar-nav">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="nav-item">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="admin-user">
          <div class="admin-avatar">{{ (user?.nickname || '管')[0] }}</div>
          <div>
            <div class="admin-name">{{ user?.nickname || '管理员' }}</div>
            <div class="admin-role">超级管理员</div>
          </div>
        </div>
        <el-button link class="logout-btn" @click="logout">退出登录</el-button>
      </div>
    </aside>

    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { DataAnalysis, List, Box, User } from '@element-plus/icons-vue'

const router = useRouter()
const user = computed(() => { try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null } })

const navItems = [
  { path: '/admin/dashboard', label: '数据概览', icon: DataAnalysis },
  { path: '/admin/orders',   label: '订单管理', icon: List },
  { path: '/admin/goods',    label: '商品管理', icon: Box },
  { path: '/admin/users',    label: '用户管理', icon: User },
]

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
.admin-layout { display: flex; height: 100vh; background: #F5F4F2; }

.sidebar {
  width: 220px; flex-shrink: 0;
  background: #1A1714;
  display: flex; flex-direction: column;
  color: #fff;
}
.sidebar-brand {
  padding: 24px 20px 20px;
  font-size: 16px; font-weight: 800;
  border-bottom: 1px solid rgba(255,255,255,.08);
  display: flex; align-items: center; gap: 8px;
}

.sidebar-nav { flex: 1; padding: 12px 0; overflow-y: auto; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 20px; font-size: 14px; color: rgba(255,255,255,.6);
  text-decoration: none; transition: all .15s; border-left: 3px solid transparent;
}
.nav-item:hover { color: #fff; background: rgba(255,255,255,.06); }
.nav-item.router-link-active { color: #C4906A; border-left-color: #C4906A; background: rgba(196,144,106,.1); }

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,.08);
}
.admin-user { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.admin-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: #C4906A; display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; flex-shrink: 0;
}
.admin-name { font-size: 13px; font-weight: 600; color: #fff; }
.admin-role { font-size: 11px; color: rgba(255,255,255,.4); }
.logout-btn { color: rgba(255,255,255,.4); font-size: 12px; padding: 0; }
.logout-btn:hover { color: #f56c6c; }

.admin-main { flex: 1; overflow-y: auto; }
</style>
