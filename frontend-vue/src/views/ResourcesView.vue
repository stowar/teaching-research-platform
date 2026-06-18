<script setup>
/**
 * 教研资料部 ResourcesView.vue
 * 当前为占位展示页面，说明功能规划与迭代状态
 */
import { BookOpen, FileText, Download, Search, Tag, Clock } from 'lucide-vue-next'

const planned = [
  { icon: FileText, title: '教案课件', desc: '按学段/学科分类浏览与下载' },
  { icon: Search, title: '真题题库', desc: '关键词检索，一键导出打印版' },
  { icon: Tag, title: '标签体系', desc: '多维度标签筛选，精准定位资源' },
  { icon: Download, title: '批量下载', desc: '勾选多份资料打包下载' },
]
</script>

<template>
  <div class="resources-page">
    <!-- Hero -->
    <div class="hero">
      <div class="hero-bg">
        <div class="hero-gradient"></div>
        <div class="hero-dots"></div>
      </div>
      <BookOpen class="hero-icon" :size="48" aria-hidden="true" />
      <h1>教研资料部</h1>
      <p class="hero-desc">教案课件、真题题库一站式下载与共享</p>
    </div>

    <!-- 规划说明 -->
    <div class="notice card">
      <Clock :size="18" />
      <div>
        <strong>功能规划中</strong>
        <p>本模块已完成数据表设计与 API 架构预留，前端交互页面将在下一迭代周期开发。当前教研资料可通过社区模块的帖子附件临时分发。</p>
      </div>
    </div>

    <!-- 规划功能卡片 -->
    <div class="plan-grid">
      <div v-for="item in planned" :key="item.title" class="plan-card card">
        <div class="plan-icon"><component :is="item.icon" :size="22" /></div>
        <h3>{{ item.title }}</h3>
        <p>{{ item.desc }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.resources-page {
  max-width: 800px;
  margin: 0 auto;
  animation: slide-up 0.5s var(--ease-out) both;
}

/* Hero */
.hero {
  position: relative;
  text-align: center;
  padding: var(--space-12) var(--space-6);
  margin-bottom: var(--space-6);
  border-radius: var(--radius-xl);
  overflow: hidden;
}
.hero-bg {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, var(--color-brand-900) 0%, var(--color-brand-700) 40%, var(--color-brand-600) 100%);
}
.hero-gradient {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, var(--color-brand-500) 0%, var(--color-brand-400) 30%, var(--color-brand-300) 50%, var(--color-brand-400) 70%, var(--color-brand-500) 100%);
  background-size: 400% 400%;
  animation: gradient-flow 8s ease infinite;
  opacity: 0.3;
}
@keyframes gradient-flow {
  0%,100% { background-position:0% 50%; }
  50% { background-position:100% 50%; }
}
.hero-dots {
  position: absolute; inset: 0;
  opacity: 0.06;
  background-image: radial-gradient(circle, #fff 1px, transparent 1px);
  background-size: 24px 24px;
}
.hero-icon {
  position: relative; z-index: 1;
  color: var(--color-brand-300);
  margin-bottom: var(--space-3);
  animation: bounce-in 0.6s var(--ease-spring) 0.2s both, hero-float 3s ease-in-out 1s infinite;
}
@keyframes hero-float {
  0%,100% { transform:translateY(0); }
  50% { transform:translateY(-6px); }
}
.hero h1 {
  position: relative; z-index: 1;
  font-size: var(--text-3xl);
  font-weight: var(--font-extrabold);
  color: #ffffff;
  margin: 0 0 var(--space-2) 0;
  letter-spacing: -0.02em;
}
.hero-desc {
  position: relative; z-index: 1;
  font-size: var(--text-base);
  color: rgba(255,255,255,0.8);
  margin: 0;
}

/* 说明条 */
.notice {
  display: flex; align-items: flex-start; gap: var(--space-3);
  margin-bottom: var(--space-5);
  padding: var(--space-4) var(--space-5);
  background: var(--color-brand-50);
  border: 1px solid var(--color-brand-200);
}
.notice strong {
  font-size: var(--text-sm);
  color: var(--color-brand-700);
}
.notice p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: var(--space-1) 0 0;
  line-height: var(--leading-relaxed);
}
.notice svg {
  color: var(--color-brand-500);
  flex-shrink: 0;
  margin-top: 1px;
}

/* 规划卡片 */
.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}
.plan-card {
  padding: var(--space-5);
  text-align: center;
  animation: slide-up 0.5s var(--ease-out) both;
}
.plan-card:nth-child(1) { animation-delay: 0.05s; }
.plan-card:nth-child(2) { animation-delay: 0.1s; }
.plan-card:nth-child(3) { animation-delay: 0.15s; }
.plan-card:nth-child(4) { animation-delay: 0.2s; }
.plan-icon {
  width: 48px; height: 48px;
  border-radius: var(--radius-lg);
  background: var(--color-brand-100);
  color: var(--color-brand-600);
  display: inline-flex; align-items: center; justify-content: center;
  margin-bottom: var(--space-3);
}
.plan-card h3 {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
}
.plan-card p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: var(--leading-relaxed);
}

/* 暗色 */
[data-theme="dark"] .notice {
  background: rgba(99,102,241,0.08);
  border-color: rgba(99,102,241,0.15);
}
[data-theme="dark"] .notice strong { color: var(--color-brand-300); }

/* 动画 */
@keyframes slide-up { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes bounce-in {
  0% { opacity:0; transform:scale(0.3); }
  50% { transform:scale(1.05); }
  70% { transform:scale(0.9); }
  100% { opacity:1; transform:scale(1); }
}

@media (max-width: 768px) {
  .plan-grid { grid-template-columns: 1fr; }
  .hero { padding: var(--space-8) var(--space-4); }
}
</style>
