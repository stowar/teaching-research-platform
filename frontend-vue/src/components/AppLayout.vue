<script setup>
/**
 * 全局布局组件 AppLayout.vue
 * 提供应用通用的导航栏（Navbar）和页脚（Footer）
 * 使用 Design Tokens 和 lucide 图标库保证视觉一致性
 */
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useTheme } from '@/composables/useTheme.js'
import { GraduationCap, Sun, Moon, Home, MessageSquare, BookOpen, Bot, Bell, ShieldCheck, Brain } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { isDark, toggle } = useTheme()

const isLoggedIn = computed(() => auth.isLoggedIn)
const user = computed(() => auth.user)
const isAdmin = computed(() => auth.isAdmin)
const activeRoute = computed(() => route.name)
const aiVisited = ref(localStorage.getItem('ai_visited') === '1')
const isNewUser = computed(() => {
  const u = auth.user
  if (!u?.create_time) return false
  const elapsed = Date.now() - new Date(u.create_time).getTime()
  return elapsed < 24 * 3600 * 1000
})
const showAiDot = computed(() => !aiVisited.value && auth.isLoggedIn && isNewUser.value)

function dismissDot() {
  aiVisited.value = true
  localStorage.setItem('ai_visited', '1')
}

const navItems = computed(() => {
  const items = [
    { name: 'home', label: '首页', path: '/', icon: Home },
    { name: 'community', label: '教研社区', path: '/community', icon: MessageSquare },
    { name: 'resources', label: '教研资料部', path: '/resources', icon: BookOpen },
    { name: 'ai-chat', label: 'AI聊天室', path: '/ai-chat', icon: Bot },
    { name: 'sentiment', label: '情感分析', path: '/sentiment', icon: Brain },
    { name: 'account', label: '个人中心', path: '/account', icon: Bell },
  ]
  if (isAdmin.value) {
    items.push({ name: 'admin-users', label: '用户管理', path: '/admin/users', icon: ShieldCheck })
  }
  return items
})

function logout() {
  auth.logout()
  router.push('/landing')
}
</script>

<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <nav class="navbar" role="navigation" aria-label="主导航">
      <div class="nav-brand">
        <GraduationCap class="nav-brand-icon" aria-hidden="true" />
        <span class="nav-brand-text">虚拟教研社区</span>
      </div>

      <div class="nav-links">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          :class="['nav-link', { active: activeRoute === item.name, 'has-dot': item.name === 'ai-chat' && showAiDot }]"
          @click="item.name === 'ai-chat' && dismissDot()"
        >
          <component :is="item.icon" class="nav-link-icon" :size="16" />
          {{ item.label }}
          <span v-if="item.name === 'ai-chat' && showAiDot" class="new-dot" />
        </router-link>
      </div>

      <div class="nav-actions">
        <button class="theme-toggle" @click="toggle" :title="isDark ? '切换到浅色模式' : '切换到深色模式'"
          aria-label="切换主题">
          <Moon v-if="isDark" class="icon" :size="18" />
          <Sun v-else class="icon" :size="18" />
        </button>
        <div class="nav-user">
          <template v-if="isLoggedIn && user">
            <router-link to="/profile" class="user-name">{{ user.name || '教师' }}</router-link>
            <button class="btn btn-ghost" @click="logout">注销</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn btn-primary">登录</router-link>
            <router-link to="/register" class="btn btn-ghost">注册</router-link>
          </template>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <slot />
    </main>

    <footer class="app-footer">
      <router-link to="/about">关于项目</router-link>
      <span class="footer-divider">·</span>
      <span>虚拟教研社区 © 2026</span>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
}

/* 导航栏：玻璃拟态效果 */
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-8);
  height: 64px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-light);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  transition: box-shadow var(--duration-normal) var(--ease-out);
}

.navbar:hover {
  box-shadow: var(--shadow-sm);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: var(--font-bold);
  font-size: var(--text-lg);
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.nav-brand-icon {
  width: 1.6rem;
  height: 1.6rem;
  color: var(--color-brand-600);
}

.nav-links {
  display: flex;
  gap: var(--space-1);
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: var(--font-medium);
  font-size: var(--text-sm);
  transition: all var(--duration-fast) var(--ease-out);
  position: relative;
}

/* 当前页面高亮 + 底部小横条指示器 */
.nav-link.active {
  color: var(--color-brand-600);
  background: var(--color-brand-50);
}

.nav-link:hover:not(.active) {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.nav-link-icon {
  opacity: 0.7;
}

.nav-link.active .nav-link-icon {
  opacity: 1;
}

.nav-link.has-dot {
  position: relative;
}

.new-dot {
  position: absolute;
  top: 4px;
  right: 6px;
  width: 7px;
  height: 7px;
  border-radius: var(--radius-full);
  background: var(--color-danger-500);
  animation: dot-pulse 2s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.theme-toggle {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast) var(--ease-out), transform var(--duration-fast) var(--ease-out);
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.theme-toggle:hover {
  background: var(--bg-hover);
  transform: scale(1.1);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* 暗色模式导航栏适配：半透明深色玻璃，更有质感 */
:global(html[data-theme="dark"]) .navbar {
  background: rgba(30, 41, 59, 0.55);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

:global(html[data-theme="dark"]) .navbar:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

/* 暗色模式下当前页面高亮：更柔和的发光感 */
:global(html[data-theme="dark"]) .nav-link.active {
  background: rgba(79, 70, 229, 0.15);
  color: var(--color-brand-200);
}

/* 暗色模式 Logo 用亮色，白天保持原 Indigo */
:global(html[data-theme="dark"]) .nav-brand-icon {
  color: var(--color-brand-400);
}

/* 暗色模式主题按钮微调 */
:global(html[data-theme="dark"]) .theme-toggle {
  color: var(--text-secondary);
}

:global(html[data-theme="dark"]) .theme-toggle:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
}

.user-name {
  color: var(--text-primary);
  font-weight: var(--font-semibold);
  text-decoration: none;
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast) var(--ease-out);
}

.user-name:hover {
  background: var(--bg-hover);
}

.main-content {
  flex: 1;
  padding: var(--space-6) var(--space-8);
  max-width: var(--container-xl);
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-6);
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  border-top: 1px solid var(--border-light);
}

.app-footer a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--duration-fast) var(--ease-out);
}

.app-footer a:hover {
  color: var(--text-link);
}

.footer-divider {
  color: var(--color-gray-300);
}

/* 响应式 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 var(--space-4);
    height: auto;
    min-height: 56px;
    gap: var(--space-2);
  }

  .nav-links {
    order: 3;
    width: 100%;
    overflow-x: auto;
    padding-bottom: var(--space-2);
  }

  .main-content {
    padding: var(--space-4);
  }
}
</style>
