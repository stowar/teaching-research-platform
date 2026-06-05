<script setup>
/**
 * AI 教研助手 AiChatView.vue（三栏固定布局版）
 * 参考原 Streamlit 页面结构：左侧会话栏 | 中间聊天区 | 右侧说明栏
 * 后续扩展：将 sendMessage 中的 mock 替换为真实 LLM API
 */
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  Bot, Send, User, Plus, MessageSquare,
  RotateCcw, ChevronLeft, Lightbulb, Sparkles,
  Sun, Moon
} from 'lucide-vue-next'
import { useTheme } from '@/composables/useTheme.js'

const router = useRouter()
const { isDark, toggle } = useTheme()

// 会话数据
const sessions = ref([
  { id: 's1', name: 'session_1', active: true },
  { id: 's2', name: 'session_2', active: false }
])
const sessionCount = ref(2)

function createSession() {
  sessionCount.value += 1
  const name = `session_${sessionCount.value}`
  sessions.value.forEach(s => (s.active = false))
  sessions.value.unshift({ id: Date.now().toString(), name, active: true })
  clearChat()
}

function switchSession(session) {
  sessions.value.forEach(s => (s.active = false))
  session.active = true
  // 实际项目中这里应加载对应会话的历史消息
}

// 消息
const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是 AI 教研助手。我可以帮您解答英语教学、课程设计、教研资源等方面的问题。',
    timestamp: Date.now()
  }
])
const input = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const quickPrompts = [
  '如何设计一堂高职英语听说课？',
  '请推荐几个适合职校学生的英语教学活动',
  '英语课程思政有哪些切入点？',
  '如何提升学生的职场英语应用能力？'
]

const mockReplies = [
  '根据您的需求，我建议从以下几个方面入手：\n\n**1. 情境创设**\n结合学生未来职业场景，设计真实的语言使用情境，比如酒店接待、商务谈判、机场登机等。\n\n**2. 任务驱动**\n采用项目式学习（PBL），让学生以小组为单位完成一份英语岗位实训方案。\n\n**3. 分层教学**\n针对不同英语基础的学生，设置基础版、进阶版和挑战版三套任务卡。\n\n需要我为您展开其中某个环节吗？',
  '这是一个很好的教研方向！目前职校英语教学中，比较有效的策略包括：\n\n- **产教融合**：邀请企业导师进课堂，分享真实工作场景的英语表达\n- **数字化工具**：利用 AI 语音评测、VR 情境模拟等技术增强互动性\n- **课证融通**：将教学内容与职业技能等级证书考试对接\n\n您可以结合本校的专业特色，选择 1-2 个点做深度突破。',
  '针对高职学生的特点，课堂活动设计建议遵循 "实用、有趣、可达成" 原则：\n\n**推荐活动：**\n1. **Role Play（角色扮演）**：模拟面试、客户接待等真实场景\n2. **English News Digest**：每周选取 1 条行业英语新闻做速读训练\n3. **Vlog Script Writing**：让学生为校园/实训场景撰写英文短视频脚本\n4. **Peer Teaching（同伴教学）**：优生带动后进生，讲解重点词汇\n\n这些活动投入成本低，但学生参与度高。',
  '课程思政与英语教学的融合，关键在于 "润物细无声"。以下是几个有效的切入点：\n\n**文化自信**：对比中西方节日、礼仪，引导学生讲好中国故事\n**职业精神**：通过商务英语案例，传递诚信、敬业、协作等价值观\n**家国情怀**：选取 "一带一路" 相关的英文素材，拓展国际视野\n**工匠精神**：介绍中国技能大师的国际交流故事，激发职业自豪感\n\n建议每次课融入 1 个思政元素，避免生硬说教。'
]

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function sendMessage(text = input.value.trim()) {
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text, timestamp: Date.now() })
  input.value = ''
  await scrollToBottom()

  loading.value = true
  await scrollToBottom()

  const delay = 600 + Math.random() * 600
  await new Promise(r => setTimeout(r, delay))

  let replyText = mockReplies[Math.floor(Math.random() * mockReplies.length)]
  const lowered = text.toLowerCase()
  if (lowered.includes('听说') || lowered.includes('课堂') || lowered.includes('课')) replyText = mockReplies[0]
  else if (lowered.includes('活动') || lowered.includes('游戏')) replyText = mockReplies[2]
  else if (lowered.includes('思政') || lowered.includes('德育')) replyText = mockReplies[3]
  else if (lowered.includes('策略') || lowered.includes('方法') || lowered.includes('能力')) replyText = mockReplies[1]

  const aiMessage = { role: 'assistant', content: '', timestamp: Date.now(), streaming: true }
  messages.value.push(aiMessage)
  await scrollToBottom()

  const chars = replyText.split('')
  for (let i = 0; i < chars.length; i++) {
    aiMessage.content += chars[i]
    if (i % 3 === 0 || i === chars.length - 1) await scrollToBottom()
    await new Promise(r => setTimeout(r, 15 + Math.random() * 10))
  }
  aiMessage.streaming = false
  loading.value = false
  await scrollToBottom()
}

function clearChat() {
  messages.value = [{
    role: 'assistant',
    content: '你好！我是 AI 教研助手。我可以帮您解答英语教学、课程设计、教研资源等方面的问题。',
    timestamp: Date.now()
  }]
}

function formatTime(ts) {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
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
          :class="['session-item', session.active ? 'active' : '']"
          @click="switchSession(session)"
        >
          <MessageSquare :size="14" />
          <span class="session-name">{{ session.name }}</span>
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
                <pre class="message-text">{{ msg.content }}<span v-if="msg.streaming" class="cursor">|</span></pre>
              </div>
            </div>
          </div>

          <!-- 加载态 -->
          <div v-if="loading && !messages[messages.length - 1]?.streaming" class="message-row assistant">
            <div class="message-avatar">
              <Bot :size="16" />
            </div>
            <div class="message-body">
              <div class="message-meta">
                <span class="meta-name">AI 助手</span>
              </div>
              <div class="message-bubble typing">
                <span class="typing-dot" />
                <span class="typing-dot" />
                <span class="typing-dot" />
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
          <h4>🎯 功能介绍</h4>
          <p>AI 教研助手基于大语言模型，专为职业院校英语教师打造。可协助您完成教案设计、教学策略分析、课程思政融合等教研任务。</p>
        </div>
        <div class="info-section">
          <h4>💡 提问技巧</h4>
          <ul>
            <li>尽量描述具体场景，例如学生年级、专业方向</li>
            <li>可要求按特定格式输出，如表格、清单、流程图</li>
            <li>对不满意的回答可追问细化</li>
          </ul>
        </div>
        <div class="info-section">
          <h4>⚠️ 注意事项</h4>
          <ul>
            <li>AI 生成内容仅供参考，请结合校情学情判断</li>
            <li>涉及敏感政策或隐私数据请谨慎输入</li>
            <li>当前为演示版本，后续将接入 RAG 知识库</li>
          </ul>
        </div>
        <div class="info-section">
          <h4>🚀 快捷指令</h4>
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
  color: #7c3aed;
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
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  color: #7c3aed;
}

.message-row.user .message-avatar {
  background: #7c3aed;
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
  background: linear-gradient(135deg, #7c3aed, var(--color-brand-600));
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

.cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: var(--color-brand-600);
  margin-left: 2px;
  animation: blink 1s step-end infinite;
  vertical-align: text-bottom;
}

.message-row.user .cursor {
  background: rgba(255, 255, 255, 0.8);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: var(--space-2) var(--space-3);
  min-width: 48px;
}

.typing-dot {
  width: 5px;
  height: 5px;
  border-radius: var(--radius-full);
  background: var(--text-tertiary);
  animation: typing-bounce 1.4s infinite ease-in-out both;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
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
  color: #7c3aed;
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
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
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
  background: linear-gradient(135deg, #7c3aed, var(--color-brand-600));
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

/* 响应式：平板以下隐藏右侧说明栏 */
@media (max-width: 1024px) {
  .info-sidebar {
    display: none;
  }
}

/* 响应式：手机隐藏左侧会话栏，做成下拉切换 */
@media (max-width: 768px) {
  .session-sidebar {
    display: none;
  }

  .messages-scroll {
    padding: var(--space-3);
  }

  .message-body {
    max-width: 90%;
  }

  .input-area {
    padding: var(--space-3);
  }
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
  color: #7c3aed;
  background: var(--color-brand-50);
}

/* 暗黑模式 */
[data-theme="dark"] .btn-new:hover {
  background: rgba(99, 102, 241, 0.12);
}

[data-theme="dark"] .session-item.active {
  background: rgba(99, 102, 241, 0.15);
  color: var(--color-brand-300);
}

[data-theme="dark"] .prompt-chip:hover {
  background: rgba(99, 102, 241, 0.1);
}

[data-theme="dark"] .input-wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

[data-theme="dark"] .info-tag {
  background: rgba(99, 102, 241, 0.15);
  color: var(--color-brand-300);
}
</style>
