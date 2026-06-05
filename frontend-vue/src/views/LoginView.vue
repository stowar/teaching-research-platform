<script setup>
/**
 * 登录页面 LoginView.vue
 * 左右分屏布局，使用 Design Tokens 和动画库
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { GraduationCap } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const phone = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  if (!phone.value || !password.value) {
    error.value = '请输入手机号和密码'
    return
  }
  loading.value = true
  try {
    const res = await auth.login(phone.value, password.value)
    if (res.code === 200) {
      router.push('/')
    } else {
      error.value = res.msg || '登录失败'
    }
  } catch (e) {
    error.value = e.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <!-- 左侧 Hero -->
    <div class="login-hero" aria-hidden="true">
      <div class="hero-content">
        <GraduationCap class="hero-icon" :size="48" aria-hidden="true" />
        <h1>虚拟教研社区</h1>
        <p class="hero-subtitle">聚师成林，研无止境</p>
        <div class="hero-slogan">专为职业院校英语教师打造的教研协作平台</div>
      </div>
      <div class="hero-decoration"></div>
      <div class="hero-decoration-2"></div>
    </div>

    <!-- 右侧表单 -->
    <div class="login-form-section">
      <div class="form-wrapper">
        <div class="form-header">
          <h2>欢迎登录</h2>
          <p>请使用您的账号密码登录系统</p>
        </div>

        <form @submit.prevent="onSubmit">
          <div class="form-group">
            <label for="login-phone">手机号</label>
            <input
              id="login-phone"
              v-model="phone"
              type="text"
              maxlength="11"
              placeholder="请输入手机号"
              class="form-input"
              autocomplete="tel"
            />
          </div>
          <div class="form-group">
            <label for="login-password">密码</label>
            <input
              id="login-password"
              v-model="password"
              type="password"
              placeholder="请输入密码"
              class="form-input"
              autocomplete="current-password"
            />
          </div>
          <div v-if="error" class="alert alert-error" role="alert">{{ error }}</div>
          <button
            type="submit"
            class="btn btn-primary btn-block press-feedback"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner spinner-sm" aria-hidden="true"></span>
            <span>{{ loading ? '登录中...' : '登录' }}</span>
          </button>
        </form>

        <div class="form-footer">
          <button class="link" @click="router.push('/register')">
            还没有账号？点击注册
          </button>
          <button class="link" @click="router.push('/landing')">
            返回首页
          </button>
        </div>
      </div>

      <div class="copyright">虚拟教研社区 © 2026</div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
}

.login-hero {
  flex: 0 0 45%;
  background: linear-gradient(135deg, var(--color-gray-900) 0%, #312e81 40%, #7c3aed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  color: #ffffff;
}

.hero-content {
  text-align: center;
  z-index: 1;
  padding: var(--space-8);
  animation: slide-up-enter 0.8s var(--ease-out) both;
}

.hero-icon {
  margin-bottom: var(--space-6);
}

.hero-content h1 {
  font-size: var(--text-4xl);
  font-weight: var(--font-extrabold);
  letter-spacing: -0.02em;
  margin: 0 0 var(--space-3) 0;
}

.hero-subtitle {
  font-size: var(--text-xl);
  opacity: 0.85;
  margin: 0 0 var(--space-6) 0;
}

.hero-slogan {
  display: inline-block;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: var(--space-2) var(--space-6);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-decoration {
  position: absolute;
  bottom: -120px;
  right: -120px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
  border-radius: var(--radius-full);
}

.hero-decoration-2 {
  position: absolute;
  top: -80px;
  left: -80px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 70%);
  border-radius: var(--radius-full);
}

.login-form-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  background: var(--bg-card);
  padding: var(--space-8);
}

.form-wrapper {
  width: 100%;
  max-width: 380px;
  animation: slide-up-enter 0.6s var(--ease-out) 0.15s both;
}

.form-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.form-header h2 {
  font-size: var(--text-2xl);
  color: var(--text-primary);
  margin: 0 0 var(--space-1) 0;
  font-weight: var(--font-bold);
}

.form-header p {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  margin: 0;
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.form-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-top: var(--space-6);
  text-align: center;
}

.link {
  background: none;
  border: none;
  color: var(--text-link);
  font-size: var(--text-sm);
  cursor: pointer;
  text-decoration: none;
  transition: color var(--duration-fast) var(--ease-out);
}

.link:hover {
  color: var(--text-link-hover);
  text-decoration: underline;
}

.copyright {
  position: absolute;
  bottom: var(--space-6);
  color: var(--text-tertiary);
  font-size: var(--text-xs);
}

.btn-block {
  width: 100%;
  padding: var(--space-3);
  font-size: var(--text-base);
  border-radius: var(--radius-md);
  margin-top: var(--space-2);
  min-height: 48px;
}

@keyframes slide-up-enter {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }

  .login-hero {
    flex: none;
    min-height: 220px;
    padding: var(--space-6) var(--space-4);
  }

  .hero-content h1 {
    font-size: var(--text-3xl);
  }

  .hero-icon {
    font-size: var(--text-4xl);
    margin-bottom: var(--space-4);
  }

  .login-form-section {
    flex: 1;
    justify-content: flex-start;
    padding: var(--space-8) var(--space-5) var(--space-16);
  }

  .copyright {
    position: static;
    margin-top: var(--space-8);
  }
}
</style>
