/**
 * Vue Router 路由配置
 * 定义所有页面路由、路由守卫（权限控制）
 * 使用 createWebHistory 实现 HTML5 History 模式（无 # 号的美观 URL）
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const router = createRouter({
  // 使用 HTML5 History 模式，URL 更美观（无 # 号）
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',          // 路由名称，方便代码中通过名称跳转
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true }  // 元数据：标记此页面需要登录才能访问
    },
    {
      path: '/landing',
      name: 'landing',
      component: () => import('@/views/LandingView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true, hideLayout: true }     // 元数据：仅未登录用户可访问（已登录用户自动跳转到首页）

    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true, hideLayout: true }
    },
    {
      path: '/community',
      name: 'community',
      component: () => import('@/views/CommunityView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/community/create',
      name: 'community-create',
      component: () => import('@/views/PostCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/community/:postId',
      name: 'community-post',
      component: () => import('@/views/PostDetailView.vue'),
    },
    {
      path: '/resources',
      name: 'resources',
      component: () => import('@/views/ResourcesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/ai-chat',
      name: 'ai-chat',
      component: () => import('@/views/AiChatView.vue'),
      meta: { requiresAuth: true, hideLayout: true }
    },
    {
      path: '/sentiment',
      name: 'sentiment',
      component: () => import('@/views/SentimentView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/messages',
      name: 'messages',
      component: () => import('@/views/MessagesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }  // 需要登录 + 管理员权限
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
      meta: { hideLayout: true },
    }
  ]
})

/**
 * 全局前置守卫（路由拦截器）
 * 每次路由切换前执行，用于权限校验：
 * 1. 需要登录但未登录 → 跳转到 landing 页
 * 2. 仅访客页面但已登录 → 跳转到首页
 * 3. 需要管理员权限但非管理员 → 跳转到首页
 */
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // 目标路由需要登录，但用户未登录 → 重定向到 landing
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ name: 'landing' })
  }
  // 目标路由仅访客可访问，但用户已登录 → 重定向到首页
  else if (to.meta.guestOnly && auth.isLoggedIn) {
    next({ name: 'home' })
  }
  // 目标路由需要管理员权限，但用户不是管理员 → 重定向到首页
  else if (to.meta.requiresAdmin && !auth.isAdmin) {
    next({ name: 'home' })
  }
  // 其他情况正常放行
  else {
    next()
  }
})

export default router
