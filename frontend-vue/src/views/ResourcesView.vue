<script setup>
/**
 * 教研资料部 ResourcesView.vue（占位页面）
 * 计划功能：教案课件、真题题库一键下载
 * 使用统一的占位页面设计风格，保持视觉一致性
 */
import { BookOpen, Construction } from 'lucide-vue-next'
</script>

<template>
  <div class="placeholder-page">
    <div class="placeholder-hero" aria-hidden="true">
      <div class="hero-glow"></div>
    </div>
    <BookOpen class="placeholder-icon" :size="64" aria-hidden="true" />
    <h1>教研资料部</h1>
    <p class="placeholder-desc">教案课件、真题题库一键下载</p>
    <div class="placeholder-hint">
      <Construction class="hint-icon" :size="16" aria-hidden="true" />
      <span>功能开发中，敬请期待...</span>
    </div>
  </div>
</template>

<style scoped>
.placeholder-page {
  text-align: center;
  padding: var(--space-16) var(--space-6);
  position: relative;
  overflow: hidden;
  animation: slide-up-enter 0.6s var(--ease-out) both;
}

.placeholder-hero {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 280px;
  background: linear-gradient(135deg, var(--color-brand-900) 0%, var(--color-brand-700) 40%, #7c3aed 100%);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
  overflow: hidden;
}

.hero-glow {
  position: absolute;
  bottom: -50%;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
  border-radius: var(--radius-full);
}

.placeholder-icon {
  position: relative;
  margin-bottom: var(--space-4);
  display: inline-block;
  animation: bounce-in 0.7s var(--ease-spring) 0.2s both;
  z-index: 1;
  color: #ffffff;
}

.placeholder-page h1 {
  position: relative;
  font-size: var(--text-3xl);
  font-weight: var(--font-extrabold);
  color: #ffffff;
  margin: 0 0 var(--space-2) 0;
  z-index: 1;
  letter-spacing: -0.02em;
}

.placeholder-desc {
  position: relative;
  font-size: var(--text-lg);
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
  z-index: 1;
}

.placeholder-hint {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-10);
  padding: var(--space-3) var(--space-6);
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  box-shadow: var(--shadow-sm);
  z-index: 1;
  animation: slide-up-enter 0.5s var(--ease-out) 0.4s both;
}

.hint-icon {
  display: inline-flex;
  align-items: center;
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
  .placeholder-hero { height: 240px; }
  .placeholder-page { padding: var(--space-12) var(--space-4); }
}
</style>
