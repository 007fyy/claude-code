import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录 / 注册' },
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
    meta: { title: 'AR 试戴' },
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('../views/Cart.vue'),
    meta: { title: '购物车' },
  },
  {
    path: '/payment-result',
    name: 'PaymentResult',
    component: () => import('../views/PaymentResult.vue'),
    meta: { title: '支付结果' },
  },
  {
    path: '/orders',
    name: 'OrderList',
    component: () => import('../views/OrderList.vue'),
    meta: { title: '我的订单' },
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('../views/OrderDetail.vue'),
    meta: { title: '订单详情' },
  },
  {
    path: '/aftersale/apply',
    name: 'AftersaleApply',
    component: () => import('../views/AftersaleApply.vue'),
    meta: { title: '申请售后' },
  },
  {
    path: '/aftersale/:id',
    name: 'AftersaleProgress',
    component: () => import('../views/AftersaleProgress.vue'),
    meta: { title: '售后进度' },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '个人中心' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const publicRoutes = ['/login']
  if (!token && !publicRoutes.includes(to.path)) {
    return '/login'
  }
})

router.afterEach((to) => {
  document.title = to.meta.title || '珑饰'
})

export default router
