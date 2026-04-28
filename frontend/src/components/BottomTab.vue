<template>
  <div class="bottom-tab">
    <div
      v-for="tab in tabs"
      :key="tab.name"
      class="tab-item"
      :class="{ active: active === tab.name }"
      @click="$router.push(tab.path)"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

defineProps({ active: { type: String, default: 'home' } })

const tabs = [
  { name: 'home',    icon: '🏠', label: '首页',  path: '/home' },
  { name: 'guide',   icon: '🤖', label: '导购',  path: '/ai-guide' },
  { name: 'ar',      icon: '📷', label: '试戴',  path: '/goods' },
  { name: 'cart',    icon: '🛒', label: '购物车', path: '/cart' },
  { name: 'profile', icon: '👤', label: '我的',  path: '/profile' },
]
</script>

<style scoped>
.bottom-tab {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  display: flex;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  z-index: 200;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
  cursor: pointer;
  gap: 2px;
  transition: color 0.2s;
}

.tab-icon  { font-size: 22px; line-height: 1; }
.tab-label { font-size: 10px; color: #999; }

.tab-item.active .tab-label { color: #c0876a; font-weight: 600; }
</style>
