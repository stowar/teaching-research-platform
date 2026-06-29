<script setup>
/**
 * 未登录首页 LandingView.vue
 * 面向访客的宣传页面，使用 stagger 入场动画
 */
import { useRouter } from 'vue-router'
import { GraduationCap, LogIn, UserPlus, Star, MessageSquare, BookOpen, Bot, Brain, Bell } from 'lucide-vue-next'

const router = useRouter()

const highlights = [
  { icon: MessageSquare, title: '教研社区', desc: '发帖讨论、互助答疑、分享教学经验', route: '/community', color: 'var(--color-brand-600)' },
  { icon: Bot, title: 'AI 聊天室', desc: '人格系统 · 长期记忆 · 智能教研助手', route: '/ai-chat', color: '#06b6d4' },
  { icon: Brain, title: '情感分析', desc: '自研模型 · 六层温度体系 · 教学评价洞察', route: '/sentiment', color: '#8b5cf6' },
  { icon: BookOpen, title: '教研资料部', desc: '教案课件、真题题库分类下载', route: '/resources', color: 'var(--color-success-600)' },
  { icon: Bell, title: '个人中心', desc: '消息通知、我的帖子、资料管理', route: '/account', color: 'var(--color-warning-600)' },
]
</script>

<template>
  <div class="landing-page">
    <div class="landing-hero" role="banner">
      <div class="hero-content">
        <GraduationCap class="hero-icon" :size="48" aria-hidden="true" />
        <h1>虚拟教研社区</h1>
        <p class="hero-subtitle">聚师成林，研无止境</p>
        <div class="hero-slogan">专为职业院校英语教师打造的教研协作平台</div>
      </div>
      <div class="hero-dots" aria-hidden="true"></div>
      <div class="hero-gradient" aria-hidden="true"></div>
      <div class="hero-decoration" aria-hidden="true"></div>
      <div class="hero-decoration-2" aria-hidden="true"></div>
    </div>

    <div class="landing-actions">
      <button class="btn btn-primary btn-lg press-feedback" @click="router.push('/login')">
        <LogIn class="icon" :size="18" /> 立即登录
      </button>
      <button class="btn btn-ghost btn-lg press-feedback" @click="router.push('/register')">
        <UserPlus class="icon" :size="18" /> 注册账号
      </button>
    </div>

    <div class="landing-highlights">
      <h2>
        <Star class="highlight-icon" :size="22" aria-hidden="true" />
        平台核心亮点
      </h2>
      <div class="highlight-grid">
        <div
          v-for="(h, idx) in highlights"
          :key="h.title"
          class="highlight-card card card-hover"
          :style="{ animationDelay: `${idx * 120}ms` }"
          @click="router.push(h.route)"
        >
          <component :is="h.icon" class="highlight-emoji" :size="48" aria-hidden="true" />
          <div class="highlight-title">{{ h.title }}</div>
          <div class="highlight-desc">{{ h.desc }}</div>
          <div class="highlight-bar" :style="{ background: h.color }"></div>
          <div class="highlight-link">点击预览 →</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.landing-page {
  padding: var(--space-6) 0;
}

.landing-hero {
  position: relative;
  background: linear-gradient(135deg, var(--color-brand-900) 0%, var(--color-brand-700) 40%, var(--color-brand-600) 100%);
  border-radius: var(--radius-xl);
  padding: var(--space-16) var(--space-8);
  text-align: center;
  color: #ffffff;
  margin-bottom: var(--space-10);
  overflow: hidden;
  animation: slide-up-enter 0.8s var(--ease-out) both;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-icon {
  margin-bottom: var(--space-4);
  display: inline-block;
  color: var(--color-brand-300);
  animation: bounce-in 0.6s var(--ease-spring) 0.3s both, hero-float 3s ease-in-out 1s infinite;
}

.hero-content h1 {
  font-size: var(--text-5xl);
  font-weight: var(--font-extrabold);
  letter-spacing: -0.03em;
  margin-bottom: var(--space-4);
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

.hero-dots {
  position: absolute; inset: 0; z-index: 0;
  opacity: 0.08;
  background-image: radial-gradient(circle, rgba(255,255,255,1) 1px, transparent 1px);
  background-size: 24px 24px;
}

.hero-content h1 { animation: fade-up 0.8s var(--ease-out) both; }
.hero-subtitle { animation: fade-up 0.8s var(--ease-out) 0.15s both; }
.hero-slogan { animation: fade-up 0.8s var(--ease-out) 0.3s both; }
@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero-subtitle {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 var(--space-4);
  letter-spacing: 0.05em;
}

.hero-slogan {
  display: inline-block;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  padding: var(--space-2) var(--space-6);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-decoration {
  position: absolute;
  bottom: -100px;
  right: -100px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
  border-radius: var(--radius-full);
}

.hero-decoration-2 {
  position: absolute;
  top: -60px;
  left: -60px;
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 70%);
  border-radius: var(--radius-full);
}

.landing-actions {
  display: flex;
  justify-content: center;
  gap: var(--space-4);
  margin-bottom: var(--space-12);
  animation: slide-up-enter 0.6s var(--ease-out) 0.2s both;
}

.btn-lg {
  padding: var(--space-3) var(--space-8);
  font-size: var(--text-base);
  border-radius: var(--radius-md);
}

.landing-highlights h2 {
  text-align: center;
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-8);
  animation: slide-up-enter 0.5s var(--ease-out) 0.3s both;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.highlight-icon {
  display: inline-flex;
  align-items: center;
}

.highlight-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-4);
}

.highlight-card {
  padding: var(--space-6) var(--space-4);
  text-align: center;
  animation: slide-up-enter 0.6s var(--ease-out) both;
  cursor: pointer;
}

.highlight-emoji {
  margin-bottom: var(--space-4);
  transition: transform var(--duration-normal) var(--ease-spring);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.highlight-card:hover .highlight-emoji {
  transform: scale(1.2);
}

.highlight-title {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.highlight-desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}

.highlight-bar {
  margin-top: var(--space-3);
  height: 3px;
  border-radius: 2px;
  width: 40%;
  margin-left: auto;
  margin-right: auto;
}

.highlight-link {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  opacity: 0;
  transition: opacity 0.2s;
}

.highlight-card:hover .highlight-link {
  opacity: 1;
}

@keyframes slide-up-enter {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes hero-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes bounce-in {
  0% { opacity: 0; transform: scale(0.3); }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { opacity: 1; transform: scale(1); }
}

@media (max-width: 1024px) {
  .highlight-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .landing-hero { padding: var(--space-10) var(--space-5); }
  .hero-content h1 { font-size: var(--text-4xl); }
  .highlight-grid { grid-template-columns: 1fr; }
  .landing-actions { flex-direction: column; align-items: center; }
}
</style>
