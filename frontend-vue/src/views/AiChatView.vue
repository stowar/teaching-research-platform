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
import api from '@/api/client'

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
  clearChat()
}

async function switchSession(conv) {
  sessions.value.forEach(s => (s.active = false))
  conv.active = true
  currentConversationId.value = conv.id

  try {
    const res = await api.get(`/ai-chat/conversations/${conv.id}`)
    const detail = res.data
    if (detail && detail.messages) {
      messages.value = detail.messages.map(m => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp,
      }))
    }
  } catch {
    messages.value = [welcomeMsg()]
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
      model: 'deepseek-chat',
    })

    const reply = res.data
    // 首次对话 → 后端返回新 conversation_id
    if (reply.conversation_id && !currentConversationId.value) {
      currentConversationId.value = reply.conversation_id
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

// 页面加载时拉会话列表
loadSessions()
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
          @contextmenu.prevent="deleteConversation(session)"
        >
          <MessageSquare :size="14" />
          <span class="session-name">{{ session.title }}</span>
          <span class="session-count">{{ session.message_count || 0 }}</span>
        </button>
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
            :key="idx"
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
              <div class="message-bubble">
                <pre class="message-text">{{ msg.content }}</pre>
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
        <span class="info-title">使用说明</span>
      </div>
      <div class="info-body">
        <div class="info-section">
          <h4>功能介绍</h4>
          <p>AI 教研助手搭载人格系统和长期记忆，能记住你的研究方向、教学习惯和偏好。越聊越懂你。</p>
        </div>
        <div class="info-section">
          <h4>使用技巧</h4>
          <ul>
            <li>尽量描述具体场景，例如学生年级、专业方向</li>
            <li>可要求按特定格式输出，如表格、清单</li>
            <li>对不满意的回答可追问细化</li>
            <li>右击会话可删除</li>
          </ul>
        </div>
        <div class="info-section">
          <h4>快捷指令</h4>
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
  animation: slide-up-enter 0.25s var(--ease-out) both;
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
  transition: all var(--duration-fast) var(--ease-out);
  flex-shrink: 0;
}

.btn-send:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: var(--shadow-sm);
}

.btn-send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
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

.info-footer {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
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
