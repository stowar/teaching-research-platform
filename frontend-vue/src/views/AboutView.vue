<script setup>
/**
 * 关于项目 AboutView.vue
 * 展示平台介绍、核心功能、技术栈等信息
 * 使用 Design Tokens 和卡片布局，保持与其他页面一致的视觉语言
 */
import { GraduationCap, Target, Rocket, Wrench, Mail } from 'lucide-vue-next'
</script>

<template>
  <div class="about-page">
    <!-- 页面顶部横幅 -->
    <div class="about-hero" role="banner">
      <div class="hero-content">
        <GraduationCap class="hero-icon" :size="56" aria-hidden="true" />
        <h1>关于项目</h1>
        <p class="hero-subtitle">虚拟教研社区 — 专为职业院校英语教师打造的教研协作平台</p>
      </div>
      <div class="hero-glow" aria-hidden="true"></div>
    </div>

    <!-- 内容卡片区域 -->
    <div class="about-grid">
      <div class="about-card card" style="animation-delay: 0.1s">
        <div class="card-icon" aria-hidden="true" style="background: var(--color-brand-100); color: var(--color-brand-600)"><Target :size="24" /></div>
        <h2>平台介绍</h2>
        <p>聚师成林，研无止境。本平台旨在为英语教师提供教研交流、资源共享、AI赋能的一站式协作环境。</p>
      </div>

      <div class="about-card card" style="animation-delay: 0.2s">
        <div class="card-icon" aria-hidden="true" style="background: var(--color-success-100); color: var(--color-success-600)"><Rocket :size="24" /></div>
        <h2>核心功能</h2>
        <ul>
          <li><strong>教研社区</strong>：发帖讨论、互助答疑、分享教学经验</li>
          <li><strong>教研资料部</strong>：教案课件、真题题库一键下载</li>
          <li><strong>AI聊天室</strong>：智能教研助手，RAG深度检索</li>
          <li><strong>消息中心</strong>：教师互动交流、通知推送</li>
        </ul>
      </div>

      <div class="about-card card" style="animation-delay: 0.3s">
        <div class="card-icon" aria-hidden="true" style="background: var(--color-info-100); color: var(--color-info-600)"><Wrench :size="24" /></div>
        <h2>技术栈</h2>
        <ul>
          <li><strong>后端</strong>：Python + FastAPI</li>
          <li><strong>前端</strong>：Vue 3 + Vite</li>
          <li><strong>数据库</strong>：PostgreSQL</li>
        </ul>
      </div>

      <div class="about-card card" style="animation-delay: 0.4s">
        <div class="card-icon" aria-hidden="true" style="background: var(--color-warning-100); color: var(--color-warning-600)"><Mail :size="24" /></div>
        <h2>联系我们</h2>
        <p>如有任何问题或建议，欢迎通过消息中心与我们联系，我们将尽快回复。</p>
      </div>
    </div>

    <!-- 页脚信息 -->
    <div class="about-footer">
      <span>虚拟教研社区 © 2026</span>
      <span class="footer-dot">·</span>
      <span>All rights reserved</span>
    </div>
  </div>
</template>

<style scoped>
.about-page {
  animation: slide-up-enter 0.5s var(--ease-out) both;
}

.about-hero {
  position: relative;
  background: linear-gradient(135deg, var(--color-brand-900) 0%, var(--color-brand-700) 40%, #7c3aed 100%);
  border-radius: var(--radius-xl);
  padding: var(--space-12) var(--space-8);
  text-align: center;
  color: #ffffff;
  margin-bottom: var(--space-8);
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-icon {
  margin-bottom: var(--space-3);
  display: inline-block;
  animation: bounce-in 0.6s var(--ease-spring) 0.2s both;
}

.about-hero h1 {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--text-3xl);
  font-weight: var(--font-extrabold);
  letter-spacing: -0.02em;
}

.hero-subtitle {
  margin: 0;
  opacity: 0.85;
  font-size: var(--text-base);
}

.hero-glow {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
  border-radius: var(--radius-full);
  pointer-events: none;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-5);
  margin-bottom: var(--space-10);
}

.about-card {
  padding: var(--space-6);
  animation: slide-up-enter 0.5s var(--ease-out) both;
}

.about-card h2 {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: var(--space-3) 0 var(--space-3) 0;
}

.about-card p {
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
  font-size: var(--text-sm);
  margin: 0;
}

.about-card ul {
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
  font-size: var(--text-sm);
  padding-left: var(--space-5);
  margin: 0;
}

.about-card li {
  margin-bottom: var(--space-2);
}

.about-card li strong {
  color: var(--text-primary);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.about-footer {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-2);
}

.footer-dot {
  color: var(--color-gray-300);
}

@keyframes slide-up-enter {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes bounce-in {
  0% { opacity: 0; transform: scale(0.3); }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { opacity: 1; transform: scale(1); }
}

@media (max-width: 768px) {
  .about-grid { grid-template-columns: 1fr; }
  .about-hero { padding: var(--space-8) var(--space-5); }
}
</style>
