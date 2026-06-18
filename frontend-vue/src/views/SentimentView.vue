<script setup>
/**
 * 教学评价情感分析 SentimentView.vue
 * 接入自研 PyTorch 模型（Embedding + BiGRU + Attention）
 * 支持单条文本预测、注意力权重可视化热力图
 */
import { ref, watch, nextTick } from 'vue'
import api from '@/api/client.js'
import { Brain, Send, RotateCcw, AlertCircle, TrendingUp, TrendingDown } from 'lucide-vue-next'

const text = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)

const examples = [
  '张老师上课很有激情，讲解深入浅出，课堂气氛很活跃，收获很大。',
  '全程照着PPT念，内容东拉西扯没有重点，纯属浪费时间。',
  '小组讨论环节设计得很好，案例很贴近实际，学到了很多实用的技巧。',
  '老师语速太快了，很多知识点没跟上，听了半节课就不想听了。'
]

async function analyze() {
  if (!text.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const res = await api.post('/sentiment/predict', { text: text.value.trim() })
    result.value = res.data
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

// 根据权重计算背景色强度 — 基于原始 softmax 值，增大对比度
function heatColor(weight, maxWeight) {
  const ratio = maxWeight > 0 ? weight / maxWeight : 0
  const alpha = 0.28 + ratio * 0.60
  return `rgba(79, 70, 229, ${alpha})`
}

function heatTextColor(weight, maxWeight) {
  const ratio = maxWeight > 0 ? weight / maxWeight : 0
  return ratio > 0.5 ? '#fff' : 'var(--text-primary)'
}

function maxAttention(weights) {
  return weights.length ? Math.max(...weights) : 0
}

function avgAttention(weights) {
  return weights.length ? weights.reduce((a, b) => a + b, 0) / weights.length : 0
}

const waveCanvas = ref(null)
const waveTooltip = ref({ show: false, word: '', x: 0, y: 0 })
const hoverIdx = ref(-1)
let wavePoints = []

function drawWave() {
  const canvas = waveCanvas.value
  if (!canvas || !result.value) return
  const ctx = canvas.getContext('2d')
  const w = canvas.offsetWidth
  const h = canvas.offsetHeight
  canvas.width = w * window.devicePixelRatio
  canvas.height = h * window.devicePixelRatio
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio)

  ctx.clearRect(0, 0, w, h)

  const weights = result.value.attn_weights
  const words = result.value.words
  const maxW = maxAttention(weights)
  const n = weights.length
  if (!n || !maxW) return

  const stepX = w / n
  const padTop = 22
  const padBot = 10
  const points = weights.map((v, i) => ({
    x: stepX * i + stepX / 2,
    y: padTop + (h - padTop - padBot) * (1 - v / maxW),
    word: words[i],
    weight: v
  }))
  wavePoints = points

  // 渐变填充
  const grad = ctx.createLinearGradient(0, 0, 0, h)
  grad.addColorStop(0, 'rgba(79,70,229,0.35)')
  grad.addColorStop(0.5, 'rgba(99,102,241,0.12)')
  grad.addColorStop(1, 'rgba(99,102,241,0.02)')

  ctx.beginPath()
  ctx.moveTo(points[0].x, h)
  for (let i = 0; i < points.length; i++) {
    if (i === 0) ctx.lineTo(points[0].x, points[0].y)
    else {
      const cx = (points[i-1].x + points[i].x) / 2
      ctx.bezierCurveTo(cx, points[i-1].y, cx, points[i].y, points[i].x, points[i].y)
    }
  }
  ctx.lineTo(points[points.length-1].x, h)
  ctx.closePath()
  ctx.fillStyle = grad
  ctx.fill()

  // 波浪线
  ctx.beginPath()
  ctx.moveTo(points[0].x, points[0].y)
  for (let i = 1; i < points.length; i++) {
    const cx = (points[i-1].x + points[i].x) / 2
    ctx.bezierCurveTo(cx, points[i-1].y, cx, points[i].y, points[i].x, points[i].y)
  }
  ctx.strokeStyle = 'rgba(79,70,229,0.7)'
  ctx.lineWidth = 1.5
  ctx.stroke()

  // 顶点 + 词标签
  points.forEach((p, i) => {
    const r = i === hoverIdx.value ? 7 : 4
    ctx.beginPath()
    ctx.arc(p.x, p.y, r, 0, Math.PI*2)
    ctx.fillStyle = i === hoverIdx.value ? '#6366f1' : '#4f46e5'
    ctx.fill()
    if (i === hoverIdx.value) {
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 2.5
      ctx.stroke()
    }

    ctx.font = (i === hoverIdx.value ? 'bold 10px' : '9px') + ' "PingFang SC","Microsoft YaHei",sans-serif'
    ctx.fillStyle = '#4338ca'
    ctx.textAlign = 'center'
    ctx.fillText(p.word, p.x, p.y - r - 6)
  })
}

function onWaveMove(e) {
  const canvas = waveCanvas.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const mx = e.clientX - rect.left
  const my = e.clientY - rect.top
  const idx = wavePoints.findIndex(p => Math.hypot(p.x - mx, p.y - my) < 20)
  if (idx !== hoverIdx.value) {
    hoverIdx.value = idx
    drawWave()
  }
  if (idx >= 0) {
    const p = wavePoints[idx]
    waveTooltip.value = { show: true, word: p.word, weight: (p.weight*100).toFixed(1), x: p.x, y: p.y - 28 }
  } else {
    waveTooltip.value = { show: false, word: '', weight: '', x: 0, y: 0 }
  }
}

function onWaveLeave() {
  hoverIdx.value = -1
  waveTooltip.value = { show: false, word: '', weight: '', x: 0, y: 0 }
  drawWave()
}

watch(result, () => nextTick(() => setTimeout(drawWave, 100)))
</script>

<template>
  <div class="sentiment-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <Brain class="page-icon" :size="32" />
      <div class="header-text">
        <h1>教学评价情感分析</h1>
        <p>基于自研 Attention-GRU 模型，洞察学生反馈中的情感倾向与关注重点</p>
        <p class="header-note">当前模型训练数据量有限（600 条），分析结果仅供参考</p>
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

          <!-- 注意力共振图 -->
          <div class="heatmap-section">
            <div class="section-header">
              <span class="section-title">注意力共振图</span>
              <span class="section-desc">波浪越高 = 模型越关注 · 颜色越深 = 权重越大</span>
            </div>
            <div class="heatmap-wrap">
              <canvas ref="waveCanvas" class="wave-canvas" @mousemove="onWaveMove" @mouseleave="onWaveLeave"></canvas>
              <div v-if="waveTooltip.show" class="wave-tip" :style="{ left: waveTooltip.x + 'px', top: waveTooltip.y + 'px' }">
                {{ waveTooltip.word }} <b>{{ waveTooltip.weight }}%</b>
              </div>
            </div>
            <div class="heatmap-header">
              <span class="heatmap-header-title">注意力热力词</span>
              <span class="heatmap-header-desc">颜色越深权重越高 · 数值为注意力百分比</span>
            </div>
            <div class="heatmap">
              <span
                v-for="(word, i) in result.words"
                :key="i"
                class="heat-word"
                :style="{
                  backgroundColor: heatColor(result.attn_weights[i], maxAttention(result.attn_weights)),
                  color: heatTextColor(result.attn_weights[i], maxAttention(result.attn_weights))
                }"
                :title="`权重: ${(result.attn_weights[i] * 100).toFixed(2)}%`"
              >{{ word }}</span>
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
  color: var(--color-brand-600);
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

.header-note {
  font-size: var(--text-xs) !important;
  color: var(--text-tertiary) !important;
  margin-top: var(--space-1) !important;
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
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
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
  color: var(--color-brand-600);
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
  background: linear-gradient(90deg, var(--color-danger-300), var(--color-danger-500));
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

.heatmap-wrap { position: relative; }
.wave-canvas {
  display: block;
  width: 100%;
  height: 150px;
  margin-bottom: var(--space-5);
  cursor: crosshair;
}
.wave-tip {
  position: absolute;
  pointer-events: none;
  background: var(--color-brand-600);
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
  transform: translate(-50%, -100%);
  z-index: 10;
}
.wave-tip b { color: #c7d2fe; }
.heatmap-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}
.heatmap-header-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
}
.heatmap-header-desc {
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
  background: rgba(79, 70, 229, 0.1);
}
</style>
