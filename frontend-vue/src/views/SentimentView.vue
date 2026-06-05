<script setup>
/**
 * 教学评价情感分析 SentimentView.vue
 * 接入自研 PyTorch 模型（Embedding + BiGRU + Attention）
 * 支持单条文本预测、注意力权重可视化热力图
 */
import { ref } from 'vue'
import api from '@/api/client.js'
import { Brain, Send, RotateCcw, AlertCircle, TrendingUp, TrendingDown } from 'lucide-vue-next'

const text = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)

const examples = [
  '老师讲课特别生动，课堂气氛很活跃，学到了很多实用的英语表达技巧。',
  '这节课内容有点难，语速太快了，很多知识点没跟上，希望老师能放慢节奏。',
  '非常喜欢这种互动式教学，小组讨论让我们有更多开口说英语的机会。',
  '课件制作精美，但课堂练习时间太少，感觉听懂了但一做题就不会。'
]

async function analyze() {
  if (!text.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const data = await api.post('/sentiment/predict', { text: text.value.trim() })
    result.value = data
  } catch (e) {
    error.value = e.message || '分析失败，请检查后端服务是否启动'
  } finally {
    loading.value = false
  }
}

function useExample(t) {
  text.value = t
  analyze()
}

function clear() {
  text.value = ''
  result.value = null
  error.value = ''
}

// 根据权重计算背景色强度
function heatColor(weight) {
  // 使用品牌色 indigo，透明度随权重变化
  const alpha = 0.15 + weight * 0.55
  return `rgba(99, 102, 241, ${alpha})`
}

function heatTextColor(weight) {
  return weight > 0.5 ? '#fff' : 'var(--text-primary)'
}
</script>

<template>
  <div class="sentiment-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <Brain class="page-icon" :size="32" />
      <div class="header-text">
        <h1>教学评价情感分析</h1>
        <p>基于自研 Attention-GRU 模型，洞察学生反馈中的情感倾向与关注重点</p>
      </div>
    </div>

    <div class="content-grid">
      <!-- 左侧输入区 -->
      <div class="input-panel">
        <div class="panel-header">
          <span class="panel-title">输入评价文本</span>
          <button class="btn-icon" title="清空" @click="clear">
            <RotateCcw :size="14" />
          </button>
        </div>

        <textarea
          v-model="text"
          class="text-input"
          rows="6"
          placeholder="请输入学生评课留言、教学反思或课堂反馈..."
          :disabled="loading"
        />

        <button
          class="btn btn-primary btn-block"
          :disabled="!text.trim() || loading"
          @click="analyze"
        >
          <span v-if="loading" class="spinner spinner-sm" />
          <Send v-else :size="14" />
          <span>{{ loading ? '分析中...' : '开始分析' }}</span>
        </button>

        <div v-if="error" class="alert alert-error">
          <AlertCircle :size="14" />
          <span>{{ error }}</span>
        </div>

        <div class="examples-section">
          <span class="examples-label">快捷示例</span>
          <div class="examples-list">
            <button
              v-for="(ex, i) in examples"
              :key="i"
              class="example-chip"
              @click="useExample(ex)"
            >
              {{ ex.length > 20 ? ex.slice(0, 20) + '...' : ex }}
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧结果区 -->
      <div class="result-panel">
        <div v-if="!result && !loading" class="result-empty">
          <Brain :size="48" />
          <p>输入评价文本后，模型将自动分析情感倾向与关键词权重</p>
        </div>

        <div v-else-if="result" class="result-body">
          <!-- 情感总览 -->
          <div class="sentiment-overview">
            <div :class="['sentiment-badge', result.sentiment === '正面好评' ? 'positive' : 'negative']">
              <TrendingUp v-if="result.sentiment === '正面好评'" :size="20" />
              <TrendingDown v-else :size="20" />
              <span>{{ result.sentiment }}</span>
            </div>

            <div class="prob-bars">
              <div class="prob-row">
                <span class="prob-label">正面概率</span>
                <div class="prob-track">
                  <div class="prob-fill positive" :style="{ width: result.pos_prob * 100 + '%' }"></div>
                </div>
                <span class="prob-value">{{ (result.pos_prob * 100).toFixed(1) }}%</span>
              </div>
              <div class="prob-row">
                <span class="prob-label">负面概率</span>
                <div class="prob-track">
                  <div class="prob-fill negative" :style="{ width: result.neg_prob * 100 + '%' }"></div>
                </div>
                <span class="prob-value">{{ (result.neg_prob * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <!-- 注意力热力图 -->
          <div class="heatmap-section">
            <div class="section-header">
              <span class="section-title">注意力热力图</span>
              <span class="section-desc">颜色越深，模型越关注该词</span>
            </div>
            <div class="heatmap">
              <span
                v-for="(word, i) in result.words"
                :key="i"
                class="heat-word"
                :style="{
                  backgroundColor: heatColor(result.attn_weights[i]),
                  color: heatTextColor(result.attn_weights[i])
                }"
                :title="`权重: ${(result.attn_weights[i] * 100).toFixed(1)}%`"
              >
                {{ word }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sentiment-page {
  animation: slide-up-enter 0.4s var(--ease-out) both;
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.page-icon {
  color: #7c3aed;
  flex-shrink: 0;
}

.header-text h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1) 0;
}

.header-text p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
}

/* 输入面板 */
.input-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.panel-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.btn-icon {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.text-input {
  width: 100%;
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  background: var(--bg-page);
  color: var(--text-primary);
  font-size: var(--text-sm);
  line-height: 1.6;
  resize: vertical;
  font-family: inherit;
  margin-bottom: var(--space-3);
  transition: border-color var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out);
}

.text-input:focus {
  outline: none;
  border-color: var(--color-brand-400);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.text-input::placeholder {
  color: var(--text-tertiary);
}

.btn-block {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3);
  font-size: var(--text-sm);
  border-radius: var(--radius-lg);
}

.alert {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.alert-error {
  background: var(--color-danger-50);
  color: var(--color-danger-700);
  border: 1px solid var(--color-danger-200);
}

.examples-section {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-light);
}

.examples-label {
  display: block;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-tertiary);
  margin-bottom: var(--space-2);
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.example-chip {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: var(--bg-page);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
  text-align: left;
  transition: all var(--duration-fast) var(--ease-out);
  line-height: 1.5;
}

.example-chip:hover {
  border-color: var(--color-brand-400);
  color: #7c3aed;
  background: var(--color-brand-50);
}

/* 结果面板 */
.result-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  min-height: 320px;
}

.result-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 280px;
  color: var(--text-tertiary);
  text-align: center;
  gap: var(--space-3);
}

.result-empty p {
  font-size: var(--text-sm);
  max-width: 240px;
  margin: 0;
}

.result-body {
  animation: slide-up-enter 0.3s var(--ease-out) both;
}

/* 情感总览 */
.sentiment-overview {
  text-align: center;
  margin-bottom: var(--space-5);
}

.sentiment-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-5);
  border-radius: var(--radius-full);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-4);
}

.sentiment-badge.positive {
  background: var(--color-success-50);
  color: var(--color-success-700);
  border: 1px solid var(--color-success-200);
}

.sentiment-badge.negative {
  background: var(--color-danger-50);
  color: var(--color-danger-700);
  border: 1px solid var(--color-danger-200);
}

.prob-bars {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.prob-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.prob-label {
  width: 60px;
  font-size: var(--text-xs);
  color: var(--text-secondary);
  text-align: right;
  flex-shrink: 0;
}

.prob-track {
  flex: 1;
  height: 10px;
  background: var(--bg-hover);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.prob-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.8s var(--ease-out);
}

.prob-fill.positive {
  background: linear-gradient(90deg, var(--color-success-400), var(--color-success-500));
}

.prob-fill.negative {
  background: linear-gradient(90deg, var(--color-danger-400), var(--color-danger-500));
}

.prob-value {
  width: 48px;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  text-align: right;
  flex-shrink: 0;
}

/* 热力图 */
.heatmap-section {
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-light);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.section-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.section-desc {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.heatmap {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.heat-word {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: transform var(--duration-fast) var(--ease-out);
  cursor: default;
}

.heat-word:hover {
  transform: scale(1.05);
  z-index: 1;
}

/* 动画 */
@keyframes slide-up-enter {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式 */
@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* 暗黑模式 */
[data-theme="dark"] .sentiment-badge.positive {
  background: rgba(34, 197, 94, 0.12);
  border-color: rgba(34, 197, 94, 0.25);
}

[data-theme="dark"] .sentiment-badge.negative {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.25);
}

[data-theme="dark"] .example-chip:hover {
  background: rgba(99, 102, 241, 0.1);
}
</style>
