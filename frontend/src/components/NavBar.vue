<template>
  <nav class="nav">
    <div class="nav-inner">
      <router-link to="/home" class="nav-logo">💎 珑饰</router-link>

      <ul class="nav-links">
        <li><router-link to="/home" :class="{ active: route.path === '/home' }">首页</router-link></li>
        <li class="has-drop">
          <router-link to="/goods" :class="{ active: route.path.startsWith('/goods') }">
            商品 <span class="drop-arrow">▾</span>
          </router-link>
          <div class="nav-drop">
            <router-link to="/goods?cat=earring"><span class="drop-ic">🌙</span>耳饰</router-link>
            <router-link to="/goods?cat=necklace"><span class="drop-ic">✨</span>项链</router-link>
            <router-link to="/goods?cat=bracelet"><span class="drop-ic">💫</span>手链</router-link>
            <router-link to="/goods?cat=ring"><span class="drop-ic">💍</span>戒指</router-link>
          </div>
        </li>
        <li><router-link to="/ai-guide" :class="{ active: route.path === '/ai-guide' }">AI 选款</router-link></li>
        <li><router-link to="/face-detect" :class="{ active: route.path === '/face-detect' }">脸型测试</router-link></li>
        <li><router-link to="/profile" :class="{ active: route.path.startsWith('/profile') }">会员中心</router-link></li>
      </ul>

      <div class="nav-right">
        <div class="nav-search" @click="$router.push('/goods')">
          <span class="ic">🔍</span>
          <input type="text" placeholder="搜索耳饰、项链、手链..." readonly />
        </div>
        <router-link to="/cart" class="nav-icon-btn" data-tip="购物车">
          🛒
          <span v-if="cartCount > 0" class="badge">{{ cartCount }}</span>
        </router-link>
        <router-link v-if="!isLoggedIn" to="/login" class="nav-user-btn">
          <span class="nav-avatar-placeholder">👤</span> 登录 / 注册
        </router-link>
        <router-link v-else to="/profile" class="nav-user-btn">
          <img v-if="avatarUrl" :src="avatarUrl" class="nav-avatar" />
          <span v-else class="nav-avatar-placeholder">{{ nickname.charAt(0) || '👤' }}</span>
          {{ nickname }}
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getCartList } from '../api/cart'

const route = useRoute()

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const userStore = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const nickname = computed(() => userStore.value.nickname || '我的')
const avatarUrl = computed(() => userStore.value.avatar_url || '')
const cartCount = ref(0)

function refreshUser() {
  try {
    userStore.value = JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    userStore.value = {}
  }
}

async function refreshCart() {
  try {
    const token = localStorage.getItem('token')
    if (!token) { cartCount.value = 0; return }
    const res = await getCartList()
    cartCount.value = res.items?.length || 0
  } catch {
    cartCount.value = 0
  }
}

watch(() => route.path, () => {
  refreshUser()
  refreshCart()
})

onMounted(() => {
  window.addEventListener('storage', refreshUser)
  window.addEventListener('cart-updated', refreshCart)
  refreshCart()
})

onUnmounted(() => {
  window.removeEventListener('storage', refreshUser)
  window.removeEventListener('cart-updated', refreshCart)
})
</script>

<style scoped>
.nav {
  height: 64px;
  background: rgba(255,255,255,.96);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #EBEBEB;
  position: sticky;
  top: 0;
  z-index: 999;
  box-shadow: 0 1px 12px rgba(0,0,0,.06);
}

.nav-inner {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 32px;
  height: 100%;
  display: flex;
  align-items: center;
}

.nav-logo {
  font-size: 22px;
  font-weight: 800;
  color: #1A1714;
  letter-spacing: .5px;
  margin-right: 36px;
  white-space: nowrap;
  text-decoration: none;
}
.nav-logo:hover { color: #9E7050; }

.nav-links {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  list-style: none;
}

.nav-links a {
  font-size: 14px;
  font-weight: 500;
  color: #6B6B6B;
  padding: 6px 14px;
  border-radius: 6px;
  transition: all .18s;
  white-space: nowrap;
  text-decoration: none;
}
.nav-links a:hover { color: #1A1714; background: #FAF9F7; }
.nav-links a.active { color: #1A1714; font-weight: 700; }

.has-drop { position: relative; }
.drop-arrow {
  font-size: 10px;
  opacity: .6;
  transition: transform .2s;
  display: inline-block;
}
.has-drop:hover .drop-arrow { transform: rotate(180deg); }

.nav-drop {
  position: absolute;
  top: calc(100% + 12px);
  left: 50%;
  transform: translateX(-50%) translateY(-6px);
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,.12), 0 0 0 1px rgba(0,0,0,.05);
  padding: 8px;
  min-width: 140px;
  opacity: 0;
  pointer-events: none;
  transition: opacity .18s, transform .18s;
  z-index: 100;
}
.has-drop:hover .nav-drop {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(-50%) translateY(0);
}
.nav-drop a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  font-size: 13px;
  font-weight: 500;
  color: #1A1714;
  border-radius: 8px;
  transition: background .13s, color .13s;
  text-decoration: none;
}
.nav-drop a:hover { background: #F5EDE3; color: #9E7050; }
.drop-ic { font-size: 16px; width: 22px; text-align: center; flex-shrink: 0; }

.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.nav-search {
  display: flex;
  align-items: center;
  background: #F3F3F1;
  border-radius: 8px;
  padding: 7px 14px;
  gap: 8px;
  width: 220px;
  border: 1.5px solid transparent;
  transition: all .2s;
  cursor: pointer;
}
.nav-search:focus-within { border-color: #C4906A; background: white; }
.nav-search input {
  border: none;
  background: transparent;
  font-size: 13px;
  color: #1A1714;
  outline: none;
  flex: 1;
  min-width: 0;
  cursor: pointer;
}
.nav-search input::placeholder { color: #B0B0B0; }
.nav-search .ic { font-size: 15px; color: #B0B0B0; flex-shrink: 0; }

.nav-icon-btn {
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  font-size: 18px;
  color: #6B6B6B;
  transition: all .18s;
  text-decoration: none;
  position: relative;
}
.nav-icon-btn:hover { background: #FAF9F7; color: #1A1714; }
.nav-icon-btn .badge {
  position: absolute;
  top: 4px; right: 3px;
  background: #E74C3C;
  color: white;
  font-size: 10px;
  font-weight: 800;
  min-width: 17px; height: 17px;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 3px;
  border: 1.5px solid white;
}

.nav-user-btn {
  display: flex; align-items: center; gap: 7px;
  font-size: 13px; font-weight: 600;
  color: #6B6B6B;
  padding: 7px 14px;
  border-radius: 8px;
  border: 1.5px solid #EBEBEB;
  transition: all .18s;
  text-decoration: none;
  white-space: nowrap;
}
.nav-user-btn:hover { border-color: #1A1714; color: #1A1714; }

.nav-avatar {
  width: 24px; height: 24px; border-radius: 50%;
  object-fit: cover; flex-shrink: 0;
}
.nav-avatar-placeholder {
  width: 24px; height: 24px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 14px; background: #F0F0F0; flex-shrink: 0;
}
</style>
