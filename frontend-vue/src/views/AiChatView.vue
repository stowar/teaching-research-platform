<script setup>
/**
 * AI 教研助手 AiChatView.vue
 * 对接真实 AI 后端：多人格系统 + 记忆系统 + Function Calling
 */
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  Bot, Send, User, Plus, MessageSquare,
  RotateCcw, ChevronLeft, Lightbulb, Sparkles,
  Sun, Moon
} from 'lucide-vue-next'
import { useTheme } from '@/composables/useTheme.js'
import MarkdownIt from 'markdown-it'
import api from '@/api/client'

const md = new MarkdownIt({ breaks: true, linkify: true })

const router = useRouter()
const { isDark, toggle } = useTheme()

// ===================== 会话 =====================
const sessions = ref([])
const currentConversationId = ref(null)

async function loadSessions() {
  try {
    const res = await api.get('/ai-chat/conversations')
    sessions.value = res.data || []
  } catch { /* 静默失败 */ }
}

function createSession() {
  sessions.value.forEach(s => (s.active = false))
  currentConversationId.value = null
  saveLastConversation(null)
  stateActivated.value = false
  aiState.value = null
  clearChat()
}

function saveLastConversation(id) {
  if (id) localStorage.setItem('ai_last_conv', id)
  else localStorage.removeItem('ai_last_conv')
}

async function switchSession(conv) {
  if (conv.id === currentConversationId.value) return

  sessions.value.forEach(s => (s.active = false))
  conv.active = true
  currentConversationId.value = conv.id
  saveLastConversation(conv.id)
  loadState(conv.id)

  try {
    const res = await api.get(`/ai-chat/conversations/${conv.id}`)
    const detail = res.data
    if (detail && detail.messages && detail.messages.length > 0) {
      messages.value = detail.messages.map(m => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp,
      }))
      stateActivated.value = true
    } else {
      messages.value = [welcomeMsg()]
      stateActivated.value = false
    }
    await scrollToBottom()
  } catch {
    messages.value = [welcomeMsg()]
    stateActivated.value = false
  }
}

async function renameConversation(conv) {
  const title = prompt('新名称：', conv.title)
  if (!title || !title.trim()) return
  try {
    await api.put(`/ai-chat/conversations/${conv.id}/rename`, { title: title.trim() })
    conv.title = title.trim()
  } catch { /* 静默 */ }
}

async function deleteConversation(conv) {
  if (!confirm(`删除会话「${conv.title}」？`)) return
  try {
    await api.delete(`/ai-chat/conversations/${conv.id}`)
    if (currentConversationId.value === conv.id) {
      currentConversationId.value = null
      clearChat()
    }
    loadSessions()
  } catch { /* 静默 */ }
}

// ===================== 消息 =====================
function welcomeMsg() {
  return {
    role: 'assistant',
    content: '你好！我是 AI 教研助手。我可以帮您解答英语教学、课程设计、教研资源等方面的问题。',
    timestamp: Date.now(),
  }
}

const messages = ref([welcomeMsg()])
const input = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const aiState = ref(null)
const showFocusHelp = ref(false)
const stateVersion = ref(0)
const stateActivated = ref(false)

const quickPrompts = [
  '如何设计一堂高职英语听说课？',
  '请推荐几个适合职校学生的英语教学活动',
  '英语课程思政有哪些切入点？',
  '如何提升学生的职场英语应用能力？'
]

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function sendMessage(text = input.value.trim()) {
  if (!text || loading.value) return

  // 显示用户消息
  messages.value.push({ role: 'user', content: text, timestamp: Date.now() })
  input.value = ''
  await scrollToBottom()

  loading.value = true
  await scrollToBottom()

  try {
    const res = await api.post('/ai-chat/chat', {
      message: text,
      conversation_id: currentConversationId.value,
      model: null,
    })

    const reply = res.data
    // 更新 AI 状态面板
    if (reply.state) {
      const s = reply.state
      aiState.value = { ...s, engagement: 0, attention: 0 }
      await nextTick()
      await new Promise(r => requestAnimationFrame(r))
      aiState.value = s
      animateCounts(s)
      stateVersion.value++
    }
    stateActivated.value = true
    // 首次对话 → 后端返回新 conversation_id
    if (reply.conversation_id && !currentConversationId.value) {
      currentConversationId.value = reply.conversation_id
      saveLastConversation(reply.conversation_id)
      loadSessions()
    }

    messages.value.push({
      role: 'assistant',
      content: reply.message.content,
      timestamp: reply.message.timestamp,
    })
    loading.value = false
    await scrollToBottom()
  } catch (e) {
    loading.value = false
    messages.value.push({
      role: 'assistant',
      content: '抱歉，出了点问题，请稍后重试。',
      timestamp: Date.now(),
    })
  } finally {
    await scrollToBottom()
  }
}

function clearChat() {
  messages.value = [welcomeMsg()]
}

function formatTime(ts) {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function focusEmoji(v) {
  if (v <= 30) return '🌀'  // 🌀
  if (v <= 70) return '🎯'  // 🎯
  return '🔒'               // 🔒
}

function focusLabel(v) {
  if (v <= 30) return '发散态'
  if (v <= 70) return '聚焦态'
  return '锁定态'
}

function focusLevel(v) {
  if (v <= 30) return 'open'
  if (v <= 70) return 'focus'
  return 'lock'
}

// 数字从 0 计数到目标值
function animateCounts(target) {
  const start = performance.now()
  const DURATION = 800
  function tick() {
    const t = Math.min((performance.now() - start) / DURATION, 1)
    const e = 1 - Math.pow(1 - t, 3) // easeOutCubic
    aiState.value = {
      ...aiState.value,
      silence_hours: +(target.silence_hours * e).toFixed(1),
      memory_count: Math.round(target.memory_count * e),
      messages_today: Math.round(target.messages_today * e),
    }
    if (t < 1) requestAnimationFrame(tick)
    else aiState.value = { ...target, engagement: aiState.value?.engagement ?? target.engagement, attention: aiState.value?.attention ?? target.attention }
  }
  requestAnimationFrame(tick)
}

// 页面加载时拉会话列表 + AI 状态 + 恢复上次会话
(async () => {
  await loadSessions()
  const lastConv = localStorage.getItem('ai_last_conv')
  if (lastConv) {
    const conv = sessions.value.find(s => s.id === Number(lastConv))
    if (conv) { switchSession(conv); return }
  }
  loadState()
})()

async function loadState(convId = null) {
  try {
    const params = convId ? { conversation_id: convId } : {}
    const res = await api.get('/ai-chat/state', { params })
    const data = res.data
    // 归零 → 渲染 → 目标值，触发进度条 CSS transition
    aiState.value = { ...data, engagement: 0, attention: 0 }
    await nextTick()
    await new Promise(r => requestAnimationFrame(r))
    aiState.value = data
    animateCounts(data)
    stateVersion.value++
  } catch { /* 静默 */ }
}
</script>

<template>
  <div class="chat-layout">
    <!-- 左侧：会话栏 -->
    <aside class="session-sidebar">
      <div class="sidebar-header">
        <span class="sidebar-title">新建会话</span>
        <button class="btn-new" title="新建会话" @click="createSession">
          <Plus :size="16" />
        </button>
      </div>

      <div class="session-list">
        <button
          v-for="session in sessions"
          :key="session.id"
          :class="['session-item', session.id === currentConversationId ? 'active' : '']"
          @click="switchSession(session)"
          @dblclick="renameConversation(session)"
          @contextmenu.prevent="deleteConversation(session)"
        >
          <MessageSquare :size="14" />
          <span class="session-name">{{ session.title }}</span>
          <span class="session-count">{{ session.message_count || 0 }}</span>
        </button>
      </div>

      <div class="session-tips">
        <span>单击切换 · 双击重命名 · 右键删除</span>
      </div>

      <div class="sidebar-footer">
        <button class="btn-back" @click="router.push('/')">
          <ChevronLeft :size="14" />
          <span>返回首页</span>
        </button>
      </div>
    </aside>

    <!-- 中间：聊天区 -->
    <main class="chat-main">
      <!-- 消息列表 -->
      <div ref="messagesContainer" class="messages-scroll">
        <div class="messages-list">
          <div
            v-for="(msg, idx) in messages"
            :key="msg.timestamp + '-' + idx"
            :class="['message-row', msg.role]"
          >
            <div class="message-avatar">
              <Bot v-if="msg.role === 'assistant'" :size="16" />
              <User v-else :size="16" />
            </div>
            <div class="message-body">
              <div class="message-meta">
                <span class="meta-name">{{ msg.role === 'assistant' ? 'AI 助手' : '我' }}</span>
                <span class="meta-time">{{ formatTime(msg.timestamp) }}</span>
              </div>
              <div class="message-bubble" :class="{ 'markdown-body': msg.role === 'assistant' }">
                <div v-if="msg.role === 'assistant'" class="message-text" v-html="md.render(msg.content)" />
                <pre v-else class="message-text">{{ msg.content }}</pre>
              </div>
            </div>
          </div>

          <!-- 加载态 -->
          <div v-if="loading" class="message-row assistant">
            <div class="message-avatar">
              <Bot :size="16" />
            </div>
            <div class="message-body">
              <div class="message-meta">
                <span class="meta-name">AI 助手</span>
              </div>
              <div class="message-bubble thinking-bubble">
                <span class="typing-label">Thinking...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷提问 -->
      <div v-if="messages.length <= 1" class="quick-prompts">
        <div class="prompts-label">
          <Lightbulb :size="12" />
          <span>试试这样问</span>
        </div>
        <div class="prompts-list">
          <button
            v-for="(p, i) in quickPrompts"
            :key="i"
            class="prompt-chip"
            @click="sendMessage(p)"
          >
            {{ p }}
          </button>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <div class="input-toolbar">
          <button class="tool-btn" title="清空对话" @click="clearChat">
            <RotateCcw :size="14" />
          </button>
        </div>
        <div class="input-wrapper">
          <input
            v-model="input"
            type="text"
            placeholder="试试问问我吧！"
            class="chat-input"
            :disabled="loading"
            @keydown.enter.prevent="sendMessage()"
          />
          <button
            class="btn-send"
            :disabled="!input.trim() || loading"
            @click="sendMessage()"
          >
            <Send :size="14" />
          </button>
        </div>
        <div class="input-footer">
          <Sparkles :size="10" />
          <span>AI 生成内容仅供参考</span>
        </div>
      </div>
    </main>

    <!-- 右侧：说明栏 -->
    <aside class="info-sidebar">
      <div class="info-header">
        <span class="info-title">AI 教研助手</span>
      </div>
      <div class="info-body">
        <!-- 人格状态 -->
        <div class="state-section">
          <div class="section-label">人格状态</div>
          <div class="ai-state-panel" :class="{ 'state-locked': !stateActivated }">
            <div v-if="aiState && stateActivated" class="state-grid">
              <div class="state-item">
                <span class="state-icon">&#x1F3AD;</span>
                <span class="state-desc">语气</span>
                <span class="tone-badge" :class="'tone-' + aiState.tone">{{ aiState.tone_label }}</span>
              </div>
              <div class="state-sep" />
              <div class="state-item">
                <span class="state-icon">&#x2764;</span>
                <span class="state-desc">投入度</span>
                <div class="state-bar-wrap">
                  <div class="state-bar" :class="{ 'bar-overdrive': aiState.engagement > 80 }">
                    <div class="state-fill" :class="{ 'fill-overdrive': aiState.engagement > 80 }" :style="{width: Math.min(aiState.engagement, 100) + '%'}" />
                  </div>
                  <span class="state-num" :class="{ 'num-overdrive': aiState.engagement > 80 }">{{ aiState.engagement }}</span>
                </div>
              </div>
              <div class="state-sep" />
              <div class="state-item">
                <span class="state-icon">&#x1F441;</span>
                <span class="state-desc">关注度</span>
                <div class="state-bar-wrap">
                  <div class="state-bar"><div class="state-fill attention" :style="{width: aiState.attention + '%'}" /></div>
                  <span class="state-num">{{ aiState.attention }}</span>
                </div>
              </div>
            </div>
            <div v-else class="state-locked-overlay">
              <p>发送第一条消息<br/>唤醒 AI 人格</p>
            </div>
          </div>
          <div class="state-hint-row">
            <p class="state-hint">人格数据仅保存在当前会话</p>
            <button class="help-btn" @click.stop="showFocusHelp = !showFocusHelp">?</button>
          </div>
          <div v-if="showFocusHelp" class="help-popover">
            <div class="help-section">
              <div class="help-row"><span>🎭 语气</span><span>四态自动切换</span></div>
              <div class="help-desc">根据对话氛围自动调整：专业/轻松/鼓励/分析</div>
            </div>
            <div class="help-section">
              <div class="help-row"><span>❤️ 投入度</span><span>0-100</span></div>
              <div class="help-desc">反映对话深度。分享真实教学案例 +5，追问 +3，认可 +2，敷衍 -3</div>
            </div>
            <div class="help-section">
              <div class="help-row"><span>👁 关注度</span><span>0-100</span></div>
              <div class="help-desc">对当前话题的锁定程度</div>
              <div class="help-desc">🌀 发散态 0-30 — 话题灵活，可接各种方向，不咬住一个点</div>
              <div class="help-desc">🎯 聚焦态 31-70 — 开始咬住话题深入追问，不容易被带跑</div>
              <div class="help-desc">🔒 锁定态 71-100 — 固执围绕当前话题深挖，换话题会拉回来</div>
            </div>
            <div class="help-section">
              <div class="help-row"><span>⚙️ 技术实现</span></div>
              <div class="help-desc">人格状态机 — 三维度数值实时动态变化</div>
              <div class="help-desc">长期记忆 — 自动存档 · 对话中自然引用</div>
              <div class="help-desc">Function Calling — 7 个 AI 工具自主决策调用</div>
              <div class="help-desc">裁切总结 — 超长对话自动压缩摘要存入记忆</div>
            </div>
          </div>
        </div>

        <!-- 运行数据 -->
        <div class="state-section">
          <div class="section-label">运行数据</div>
          <div class="ai-state-panel" :class="{ 'state-locked': !stateActivated }">
            <div v-if="aiState && stateActivated" class="stats-inline">
              <div class="stat-mini">
                <span class="stat-num">{{ aiState.silence_hours }}h</span>
                <span class="stat-label">静默</span>
              </div>
              <div class="stat-mini">
                <span class="stat-num">{{ aiState.memory_count }}</span>
                <span class="stat-label">记忆</span>
              </div>
              <div class="stat-mini">
                <span class="stat-num">{{ aiState.messages_today }}/{{ aiState.messages_limit }}</span>
                <span class="stat-label">今日</span>
              </div>
            </div>
            <div v-else class="state-locked-overlay">
              <p>发送第一条消息<br/>解锁运行数据</p>
            </div>
          </div>
        </div>

        <!-- 快捷提问 -->
        <div class="state-section">
          <div class="section-label">试试这样问</div>
          <div class="info-tags">
            <span class="info-tag">教案设计</span>
            <span class="info-tag">活动推荐</span>
            <span class="info-tag">思政融合</span>
            <span class="info-tag">评价量表</span>
          </div>
        </div>
      </div>

      <!-- 主题切换 -->
      <div class="info-footer">
        <span class="footer-label">外观</span>
        <button class="theme-toggle" @click="toggle">
          <Moon v-if="isDark" :size="14" />
          <Sun v-else :size="14" />
          <span>{{ isDark ? '暗黑模式' : '浅色模式' }}</span>
        </button>
      </div>
    </aside>
  </div>
</template>

<style scoped>
/* 三栏固定布局 */
.chat-layout {
  display: flex;
  height: 100vh;
  background: var(--bg-page);
  overflow: hidden;
}

/* 左侧会话栏 */
.session-sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-light);
  background: var(--bg-card);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.sidebar-title {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.btn-new {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-new:hover {
  background: var(--color-brand-50);
  color: var(--color-brand-600);
  border-color: var(--color-brand-300);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.session-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  text-align: left;
  transition: all var(--duration-fast) var(--ease-out);
  width: 100%;
}

.session-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.session-item.active {
  background: var(--color-brand-50);
  color: var(--color-brand-700);
  font-weight: var(--font-semibold);
}

.session-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-count {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  background: var(--bg-page);
  padding: 0 6px;
  border-radius: var(--radius-full);
}

.session-tips {
  text-align: center;
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--border-light);
  font-size: 11px;
  color: var(--text-tertiary);
}

.sidebar-footer {
  padding: var(--space-3);
  border-top: 1px solid var(--border-light);
}

.btn-back {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: var(--bg-page);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-back:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 中间聊天区 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-page);
}

.messages-scroll {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-5);
}

.messages-list {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.message-row {
  display: flex;
  gap: var(--space-3);
  animation: msg-slide-up 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes msg-slide-up {
  from { opacity: 0; transform: translateY(24px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--color-brand-100);
  color: var(--color-brand-600);
}

.message-row.user .message-avatar {
  background: var(--color-brand-600);
  color: #fff;
}

.message-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-width: 80%;
}

.message-row.user .message-body {
  align-items: flex-end;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.meta-name {
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
}

.message-bubble {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xs);
  line-height: 1.7;
}

.message-row.user .message-bubble {
  background: linear-gradient(135deg, var(--color-brand-500), var(--color-brand-600));
  color: #fff;
  border: none;
}

.message-text {
  margin: 0;
  font-family: inherit;
  font-size: var(--text-sm);
  white-space: pre-wrap;
  word-break: break-word;
  color: inherit;
}

.message-row.user .message-text {
  color: #fff;
}

/* Markdown 渲染样式 */
.markdown-body .message-text :deep(h1),
.markdown-body .message-text :deep(h2),
.markdown-body .message-text :deep(h3) {
  margin: var(--space-3) 0 var(--space-2) 0;
  font-weight: var(--font-bold);
  color: var(--text-primary);
}
.markdown-body .message-text :deep(h1) { font-size: var(--text-xl); }
.markdown-body .message-text :deep(h2) { font-size: var(--text-lg); }
.markdown-body .message-text :deep(h3) { font-size: var(--text-base); }

.markdown-body .message-text :deep(ul),
.markdown-body .message-text :deep(ol) {
  padding-left: var(--space-5);
  margin: var(--space-2) 0;
}

.markdown-body .message-text :deep(li) {
  margin-bottom: var(--space-1);
}

.markdown-body .message-text :deep(code) {
  background: var(--bg-hover);
  padding: 1px 5px;
  border-radius: var(--radius-sm);
  font-size: 0.9em;
  font-family: 'Consolas', 'Monaco', monospace;
}

.markdown-body .message-text :deep(pre) {
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  overflow-x: auto;
  margin: var(--space-2) 0;
}

.markdown-body .message-text :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-body .message-text :deep(strong) {
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.markdown-body .message-text :deep(blockquote) {
  border-left: 3px solid var(--color-brand-400);
  padding-left: var(--space-3);
  margin: var(--space-2) 0;
  color: var(--text-secondary);
  font-style: italic;
}

.markdown-body .message-text :deep(a) {
  color: var(--color-brand-600);
  text-decoration: underline;
}

.markdown-body .message-text :deep(p) {
  margin: var(--space-1) 0;
}

.markdown-body .message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: var(--space-2) 0;
}

.markdown-body .message-text :deep(th),
.markdown-body .message-text :deep(td) {
  border: 1px solid var(--border-light);
  padding: var(--space-1) var(--space-2);
  text-align: left;
  font-size: var(--text-xs);
}

.thinking-bubble {
  padding: var(--space-2) var(--space-3);
}

.typing-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-style: italic;
  animation: thinking-pulse 1.8s ease-in-out infinite;
}

@keyframes thinking-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 快捷提问 */
.quick-prompts {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 var(--space-5) var(--space-3);
  flex-shrink: 0;
  animation: slide-up-enter 0.3s var(--ease-out) both;
  transition: opacity 0.3s var(--ease-out), max-height 0.4s var(--ease-out);
  overflow: hidden;
}

.prompts-label {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-bottom: var(--space-2);
}

.prompts-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.prompt-chip {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-light);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.prompt-chip:hover {
  border-color: var(--color-brand-400);
  color: var(--color-brand-600);
  background: var(--color-brand-50);
  transform: translateY(-1px);
}

/* 输入区 */
.input-area {
  padding: var(--space-3) var(--space-5);
  border-top: 1px solid var(--border-light);
  background: var(--bg-card);
  flex-shrink: 0;
}

.input-toolbar {
  max-width: 720px;
  margin: 0 auto var(--space-2);
  display: flex;
  justify-content: flex-end;
}

.tool-btn {
  width: 26px;
  height: 26px;
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

.tool-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.input-wrapper {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
  background: var(--bg-page);
  transition: box-shadow var(--duration-fast) var(--ease-out), border-color var(--duration-fast) var(--ease-out);
}

.input-wrapper:focus-within {
  border-color: var(--color-brand-400);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
}

.chat-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-primary);
  line-height: 1.5;
}

.chat-input::placeholder {
  color: var(--text-tertiary);
}

.btn-send {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-lg);
  border: none;
  background: linear-gradient(135deg, var(--color-brand-500), var(--color-brand-600));
  color: #fff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s var(--ease-out);
  flex-shrink: 0;
}

.btn-send:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 0 12px rgba(79,70,229,0.3);
}

.btn-send:active:not(:disabled) {
  transform: scale(0.92);
}

.btn-send:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.input-footer {
  max-width: 720px;
  margin: var(--space-1) auto 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* 右侧说明栏 */
.info-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--border-light);
  background: var(--bg-card);
}

.info-header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.info-title {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.info-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.info-section h4 {
  font-size: var(--text-sm);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.info-section p,
.info-section ul {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

.info-section ul {
  padding-left: var(--space-4);
}

.info-section li {
  margin-bottom: var(--space-1);
}

.info-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.info-tag {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
  background: var(--color-brand-50);
  color: var(--color-brand-700);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

/* 动画 */
@keyframes slide-up-enter {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式 */
@media (max-width: 1024px) {
  .info-sidebar { display: none; }
}

@media (max-width: 768px) {
  .session-sidebar { display: none; }
  .messages-scroll { padding: var(--space-3); }
  .message-body { max-width: 90%; }
  .input-area { padding: var(--space-3); }
}

/* AI 状态面板 */
.section-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}

.state-section {
  margin-bottom: var(--space-4);
}

.ai-state-panel {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--bg-page);
  border: 1px solid var(--border-light);
}

.state-locked {
  position: relative;
  overflow: hidden;
}

.state-locked-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-3);
  text-align: center;
  animation: fade-in-up 0.35s var(--ease-out) both;
}

.state-grid {
}

.stats-inline {
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.lock-icon {
  font-size: 22px;
  opacity: 0.5;
}

.state-locked-overlay p {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  line-height: 1.6;
}

.state-hint-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.state-hint {
  font-size: 10px;
  color: var(--text-tertiary);
  font-style: italic;
  opacity: 0.5;
  margin: 0;
  text-align: left;
}

.help-popover .help-section {
  padding: var(--space-1) 0;
}

.help-popover .help-section + .help-section {
  border-top: 1px solid var(--border-light);
  padding-top: var(--space-2);
}

.state-empty {
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  text-align: center;
  padding: var(--space-4) 0;
}

.state-empty p { margin: 0; }

.state-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.state-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.state-icon { font-size: 14px; flex-shrink: 0; }

.state-desc {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  min-width: 38px;
}

.state-bar-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 80px;
}

.state-sep {
  height: 1px;
  background: var(--border-light);
  margin: 0 var(--space-1);
}

.tone-badge {
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.tone-professional { background: var(--color-brand-50); color: var(--color-brand-700); }
.tone-casual { background: var(--color-success-50); color: var(--color-success-700); }
.tone-encouraging { background: var(--color-warning-50); color: var(--color-warning-700); }
.tone-analytical { background: var(--color-info-50); color: var(--color-info-700); }

.state-bar {
  flex: 1;
  height: 4px;
  border-radius: var(--radius-full);
  background: var(--border-light);
  overflow: hidden;
}

.state-fill {
  height: 100%;
  border-radius: var(--radius-full);
  background: linear-gradient(90deg, var(--color-brand-400), var(--color-brand-600));
  width: 0;
  transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: 0.3s;
}

.state-fill.attention {
  background: linear-gradient(90deg, var(--color-success-400), var(--color-success-600));
}

/* Overdrive: 投入度突破 100 */
.bar-overdrive {
  box-shadow: 0 0 6px rgba(239,68,68,0.4), 0 0 12px rgba(239,68,68,0.2);
  animation: overdrive-glow 1.5s ease-in-out infinite alternate;
}

.fill-overdrive {
  background: linear-gradient(90deg, var(--color-danger-400), #ef4444, #dc2626) !important;
}

.num-overdrive {
  color: var(--color-danger-500) !important;
}

@keyframes overdrive-glow {
  0% { box-shadow: 0 0 4px rgba(239,68,68,0.3), 0 0 8px rgba(239,68,68,0.1); }
  100% { box-shadow: 0 0 8px rgba(239,68,68,0.5), 0 0 16px rgba(239,68,68,0.3); }
}

.state-num {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-weight: var(--font-bold);
  min-width: 22px;
  text-align: right;
}

.help-btn {
  width: 15px;
  height: 15px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--text-tertiary);
  font-size: 10px;
  font-weight: var(--font-bold);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
  transition: all var(--duration-fast);
}

.help-btn:hover {
  background: var(--color-brand-50);
  color: var(--color-brand-600);
  border-color: var(--color-brand-300);
}

.help-popover {
  margin: var(--space-2) 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--bg-page);
  border: 1px solid var(--border-light);
  font-size: 11px;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  gap: 1px;
  animation: fade-in-up 0.2s var(--ease-out) both;
}

.help-row {
  display: flex;
  justify-content: space-between;
  font-weight: var(--font-semibold);
}

.help-desc {
  font-size: 10px;
  color: var(--text-tertiary);
  margin-bottom: var(--space-1);
  padding-left: 2px;
}

/* 运行数据 */
.stats-inline {
  display: flex;
  gap: var(--space-3);
}

.stat-mini {
  flex: 1;
  text-align: center;
  padding: var(--space-2) 0;
}

.stat-mini .stat-num {
  display: block;
  font-size: var(--text-lg);
  font-weight: var(--font-extrabold);
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.stat-mini .stat-label {
  display: block;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: 2px;
}

[data-theme="dark"] .tone-professional { background: rgba(79,70,229,0.15); color: var(--color-brand-300); }
[data-theme="dark"] .tone-casual { background: rgba(34,197,94,0.15); color: var(--color-success-300); }
[data-theme="dark"] .tone-encouraging { background: rgba(234,179,8,0.15); color: var(--color-warning-300); }
[data-theme="dark"] .tone-analytical { background: rgba(59,130,246,0.15); color: var(--color-info-300); }

.info-footer {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.footer-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: var(--font-medium);
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: var(--bg-page);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.theme-toggle:hover {
  border-color: var(--color-brand-400);
  color: var(--color-brand-600);
  background: var(--color-brand-50);
}

/* 暗黑模式 */
[data-theme="dark"] .btn-new:hover {
  background: rgba(79, 70, 229, 0.12);
}

[data-theme="dark"] .session-item.active {
  background: rgba(79, 70, 229, 0.15);
  color: var(--color-brand-300);
}

[data-theme="dark"] .prompt-chip:hover {
  background: rgba(79, 70, 229, 0.1);
}

[data-theme="dark"] .input-wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

[data-theme="dark"] .info-tag {
  background: rgba(79, 70, 229, 0.15);
  color: var(--color-brand-300);
}

[data-theme="dark"] .session-count {
  background: rgba(255, 255, 255, 0.06);
}
</style>
