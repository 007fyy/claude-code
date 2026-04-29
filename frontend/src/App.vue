<template>
  <el-config-provider>
    <NavBar v-if="showChrome" />
    <router-view />
    <FooterBar v-if="showChrome" />
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'
import FooterBar from './components/FooterBar.vue'

const route = useRoute()
const showChrome = computed(() => route.meta?.hideChrome !== true)
</script>

<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
body {
  font-family: -apple-system, 'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
  background: #FAF9F7;
  color: #1A1714;
  line-height: 1.6;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
a { color: inherit; text-decoration: none; }
img { display: block; max-width: 100%; }
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
