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
    path: '/profile/history',
    name: 'BrowseHistory',
    component: () => import('../views/BrowseHistory.vue'),
    meta: { title: '浏览历史', requireAuth: true },
  },
  {
    path: '/profile/address',
    name: 'AddressManage',
    component: () => import('../views/AddressManage.vue'),
    meta: { title: '收货地址管理', requireAuth: true },
  },
  {
    path: '/admin',
    component: () => import('../views/AdminLayout.vue'),
    meta: { requireAuth: true, requireAdmin: true, hideChrome: true },
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('../views/AdminDashboard.vue'), meta: { title: '数据概览' } },
      { path: 'orders',    name: 'AdminOrders',    component: () => import('../views/AdminOrders.vue'),    meta: { title: '订单管理' } },
      { path: 'goods',     name: 'AdminGoods',     component: () => import('../views/AdminGoods.vue'),     meta: { title: '商品管理' } },
    ],
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
  const user  = (() => { try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null } })()
  const isAdmin = user?.role === 'admin'

  // 未登录 → 跳登录页
  const needAuth = to.matched.some((r) => r.meta.requireAuth)
  if (needAuth && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // 非管理员访问 /admin/* → 跳首页
  const needAdmin = to.matched.some((r) => r.meta.requireAdmin)
  if (needAdmin && !isAdmin) {
    return '/home'
  }

  // 已登录访问 /login → 按角色跳转
  if (to.path === '/login' && token) {
    return isAdmin ? '/admin/dashboard' : '/home'
  }

  // 管理员访问需要用户身份的页面（个人中心、订单等）→ 跳后台
  const isAdminRoute = to.matched.some((r) => r.meta.requireAdmin)
  const isUserOnlyRoute = to.matched.some((r) => r.meta.requireAuth) && !isAdminRoute
  if (isAdmin && token && isUserOnlyRoute) {
    return '/admin/dashboard'
  }
})

router.afterEach((to) => {
  document.title = to.meta.title || '珑饰'
  pageEnterTime = Date.now()
  lastPath = to.fullPath
  trackPageView(to.fullPath)
})

export default router
