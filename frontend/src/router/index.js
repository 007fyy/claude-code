import { createRouter, createWebHistory } from 'vue-router'
import { trackPageView, trackPageLeave } from '../api/tracking'

const routes = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录 / 注册', hideChrome: true },
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '珑饰' },
  },
  {
    path: '/ai-guide',
    name: 'AIGuide',
    component: () => import('../views/AIGuide.vue'),
    meta: { title: 'AI 导购' },
  },
  {
    path: '/face-detect',
    name: 'FaceDetect',
    component: () => import('../views/FaceDetect.vue'),
    meta: { title: '脸型分析' },
  },
  {
    path: '/goods',
    name: 'GoodsList',
    component: () => import('../views/GoodsList.vue'),
    meta: { title: '商品列表' },
  },
  {
    path: '/goods/:id',
    name: 'GoodsDetail',
    component: () => import('../views/GoodsDetail.vue'),
    meta: { title: '商品详情' },
  },
  {
    path: '/ar',
    name: 'FaceARView',
    component: () => import('../views/FaceARView.vue'),
    meta: { title: 'AR 试戴', hideChrome: true },
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('../views/Cart.vue'),
    meta: { title: '购物车', requireAuth: true },
  },
  {
    path: '/payment-result',
    name: 'PaymentResult',
    component: () => import('../views/PaymentResult.vue'),
    meta: { title: '支付结果', requireAuth: true },
  },
  {
    path: '/orders',
    name: 'OrderList',
    component: () => import('../views/OrderList.vue'),
    meta: { title: '我的订单', requireAuth: true },
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('../views/OrderDetail.vue'),
    meta: { title: '订单详情', requireAuth: true },
  },
  {
    path: '/aftersale/apply',
    name: 'AftersaleApply',
    component: () => import('../views/AftersaleApply.vue'),
    meta: { title: '申请售后', requireAuth: true },
  },
  {
    path: '/aftersale/:id',
    name: 'AftersaleProgress',
    component: () => import('../views/AftersaleProgress.vue'),
    meta: { title: '售后进度', requireAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '个人中心', requireAuth: true },
  },
  {
    path: '/profile/edit',
    name: 'ProfileEdit',
    component: () => import('../views/ProfileEdit.vue'),
    meta: { title: '编辑资料', requireAuth: true },
  },
  {
    path: '/profile/favorites',
    name: 'FavoriteList',
    component: () => import('../views/FavoriteList.vue'),
    meta: { title: '我的收藏', requireAuth: true },
  },
  {
    path: '/profile/address',
    name: 'AddressManage',
    component: () => import('../views/AddressManage.vue'),
    meta: { title: '收货地址管理', requireAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

let pageEnterTime = null
let lastPath = null

router.beforeEach((to, from) => {
  if (lastPath && pageEnterTime) {
    const duration = Date.now() - pageEnterTime
    trackPageLeave(lastPath, duration)
  }

  const token = localStorage.getItem('token')
  const needAuth = to.matched.some((r) => r.meta.requireAuth)
  if (needAuth && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.path === '/login' && token) {
    return '/home'
  }
})

router.afterEach((to) => {
  document.title = to.meta.title || '珑饰'
  pageEnterTime = Date.now()
  lastPath = to.fullPath
  trackPageView(to.fullPath)
})

export default router
