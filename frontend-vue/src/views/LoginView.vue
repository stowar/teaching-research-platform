<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { GraduationCap, Eye, EyeOff, Loader } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const phone = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)
const phoneError = ref('')

// 手机号实时校验
watch(phone, (v) => {
  if (!v) phoneError.value = ''
  else if (!/^1[3-9]\d{9}$/.test(v)) phoneError.value = '手机号格式不正确'
  else phoneError.value = ''
})

async function onSubmit() {
  error.value = ''
  if (!phone.value || !password.value) {
    error.value = '请输入手机号和密码'
    return
  }
  if (phoneError.value) return
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
      <div class="hero-dots" />
      <div class="hero-gradient" />
      <div class="hero-decoration" />
      <div class="hero-decoration-2" />
      <div class="hero-content">
        <GraduationCap class="hero-icon" :size="48" />
        <h1 class="hero-title">虚拟教研社区</h1>
        <p class="hero-subtitle">聚师成林，研无止境</p>
        <div class="hero-slogan">专为职业院校英语教师打造的教研协作平台</div>
      </div>
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
              :class="['form-input', { error: phoneError || (error && !phone) }]"
              autocomplete="tel"
            />
            <span v-if="phoneError" class="field-error">{{ phoneError }}</span>
          </div>

          <div class="form-group">
            <label for="login-password">密码</label>
            <div class="password-wrap">
              <input
                id="login-password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                :class="['form-input', { error: error && !password }]"
                autocomplete="current-password"
              />
              <button type="button" class="pw-toggle" @click="showPassword = !showPassword" tabindex="-1">
                <EyeOff v-if="showPassword" :size="18" />
                <Eye v-else :size="18" />
              </button>
            </div>
          </div>

          <div v-if="error" class="form-error" role="alert">{{ error }}</div>

          <button
            type="submit"
            class="btn btn-block"
            :disabled="loading"
          >
            <Loader v-if="loading" class="icon-spin" :size="18" />
            <span>{{ loading ? '登录中...' : '登录' }}</span>
          </button>
        </form>

        <div class="form-footer">
          <button class="link" @click="router.push('/register')">还没有账号？点击注册</button>
          <button class="link" @click="router.push('/landing')">返回首页</button>
        </div>
      </div>

      <div class="copyright">虚拟教研社区 &copy; 2026</div>
    </div>
  </div>
</template>

<style scoped>
.login-page { display: flex; min-height: 100vh; }

/* ===== Hero ===== */
.login-hero {
  flex: 0 0 45%;
  background: linear-gradient(135deg, var(--color-brand-900) 0%, var(--color-brand-700) 40%, var(--color-brand-600) 100%);
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden; color: #fff;
}
.hero-gradient {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, var(--color-brand-500) 0%, var(--color-brand-400) 30%, var(--color-brand-300) 50%, var(--color-brand-400) 70%, var(--color-brand-500) 100%);
  background-size: 400% 400%;
  animation: gradient-flow 8s ease infinite;
  opacity: 0.35;
}
@keyframes gradient-flow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* 点阵纹理 */
.hero-dots {
  position: absolute; inset: 0; z-index: 0;
  opacity: 0.08;
  background-image: radial-gradient(circle, rgba(255,255,255,1) 1px, transparent 1px);
  background-size: 24px 24px;
}

.hero-decoration {
  position: absolute; bottom: -120px; right: -120px; z-index: 0;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-decoration-2 {
  position: absolute; top: -80px; left: -80px; z-index: 0;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
  border-radius: 50%;
}

.hero-content {
  text-align: center; z-index: 1; padding: var(--space-8);
}
.hero-icon {
  margin-bottom: var(--space-6);
  color: var(--color-brand-300);
  animation: icon-float 3s ease-in-out infinite;
}
@keyframes icon-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.hero-title {
  animation: fade-up 0.8s var(--ease-out) both;
}
.hero-subtitle {
  animation: fade-up 0.8s var(--ease-out) 0.15s both;
}
.hero-slogan {
  animation: fade-up 0.8s var(--ease-out) 0.3s both;
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero-content h1 {
  font-size: var(--text-4xl); font-weight: var(--font-extrabold);
  letter-spacing: -0.02em; margin: 0 0 var(--space-3);
}
.hero-subtitle {
  font-size: var(--text-2xl); font-weight: var(--font-bold);
  color: rgba(255,255,255,0.95); margin: 0 0 var(--space-4);
  letter-spacing: 0.05em;
}
.hero-slogan {
  display: inline-block;
  background: rgba(255,255,255,0.08); backdrop-filter: blur(10px);
  padding: var(--space-2) var(--space-6); border-radius: var(--radius-full);
  font-size: var(--text-sm); color: rgba(255,255,255,0.7);
  border: 1px solid rgba(255,255,255,0.1);
}

/* ===== 表单 ===== */
.login-form-section {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: var(--bg-card); padding: var(--space-8);
  position: relative;
}
.form-wrapper {
  width: 100%; max-width: 400px;
  animation: fade-up 0.6s var(--ease-out) 0.2s both;
}
.form-header { text-align: center; margin-bottom: var(--space-8); }
.form-header h2 {
  font-size: var(--text-2xl); font-weight: var(--font-bold);
  color: var(--text-primary); margin: 0 0 var(--space-1);
}
.form-header p { color: var(--text-secondary); font-size: var(--text-sm); margin: 0; }

.form-group { margin-bottom: var(--space-6); }
.form-group label {
  display: block; margin-bottom: var(--space-2);
  font-size: var(--text-sm); font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.form-input {
  width: 100%; padding: var(--space-3);
  border-radius: 12px;
  border: 1.5px solid var(--border-light);
  background: var(--bg-page);
  color: var(--text-primary); font-size: var(--text-sm);
  line-height: 1.5; outline: none;
  transition: all var(--duration-fast) var(--ease-out);
}
.form-input:focus {
  border-color: rgba(79, 70, 229, 0.5);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
  background: var(--bg-card);
}
.form-input.error {
  border-color: var(--color-danger-500);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.field-error {
  display: block; margin-top: var(--space-1);
  font-size: var(--text-xs); color: var(--color-danger-600);
}
.form-error {
  padding: var(--space-2) var(--space-3);
  border-radius: 12px; margin-bottom: var(--space-4);
  background: var(--color-danger-50); color: var(--color-danger-700);
  font-size: var(--text-sm); border: 1px solid var(--color-danger-200);
}

/* 密码可见切换 */
.password-wrap { position: relative; }
.pw-toggle {
  position: absolute; right: var(--space-3); top: 50%;
  transform: translateY(-50%);
  background: none; border: none; color: var(--text-tertiary);
  cursor: pointer; padding: 0; display: flex;
  transition: color var(--duration-fast) var(--ease-out);
}
.pw-toggle:hover { color: var(--text-primary); }

/* 按钮 */
.btn-block {
  width: 100%; padding: var(--space-3);
  font-size: var(--text-base); font-weight: var(--font-semibold);
  border-radius: 12px; margin-top: var(--space-2); min-height: 48px;
  background: linear-gradient(180deg, var(--color-brand-500) 0%, var(--color-brand-600) 100%);
  border: none; color: #fff; cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25);
  display: inline-flex; align-items: center; justify-content: center;
  gap: var(--space-2);
}
.btn-block:hover:not(:disabled) {
  background: linear-gradient(180deg, var(--color-brand-600) 0%, var(--color-brand-700) 100%);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35);
  transform: translateY(-2px);
}
.btn-block:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 1px 4px rgba(79, 70, 229, 0.15);
}
.btn-block:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }

.icon-spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.form-footer {
  display: flex; flex-direction: column; gap: var(--space-2);
  margin-top: var(--space-6); text-align: center;
}
.link {
  background: none; border: none; color: var(--text-link);
  font-size: var(--text-sm); cursor: pointer; text-decoration: none;
  transition: color var(--duration-fast) var(--ease-out);
}
.link:hover { color: var(--text-link-hover); text-decoration: underline; }

.copyright {
  position: absolute; bottom: var(--space-6);
  color: var(--text-tertiary); font-size: var(--text-xs);
}

@media (max-width: 768px) {
  .login-page { flex-direction: column; }
  .login-hero { flex: none; min-height: 220px; padding: var(--space-6) var(--space-4); }
  .hero-content h1 { font-size: var(--text-3xl); }
  .hero-icon { margin-bottom: var(--space-4); }
  .login-form-section { flex: 1; justify-content: flex-start; padding: var(--space-8) var(--space-5) var(--space-16); }
  .copyright { position: static; margin-top: var(--space-8); }
}
</style>
