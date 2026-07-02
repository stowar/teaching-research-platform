<script setup>
/**
 * AI 教研助手 — 拼装组件，持有全部状态与逻辑
 */
import { ref, nextTick, onMounted } from 'vue'
import { Lightbulb } from 'lucide-vue-next'
import { useTheme } from '@/composables/useTheme.js'
import axios from 'axios'
import api from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import SessionSidebar from '@/components/chat/SessionSidebar.vue'
import MessageList from '@/components/chat/MessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import InfoSidebar from '@/components/chat/InfoSidebar.vue'
import { useAchievementToast } from '@/composables/useAchievementToast.js'

const auth = useAuthStore()
const { show: showAchievementToast } = useAchievementToast()
const { isDark, toggle } = useTheme()

// ===================== 会话 =====================
const sessions = ref([])
const currentConversationId = ref(null)

async function loadSessions() {
  try {
    const res = await api.get('/ai-chat/conversations')
    sessions.value = res.data || []
  } catch { /* */ }
}

function createSession() {
  sessions.value.forEach(s => (s.active = false))
  currentConversationId.value = null
  saveLastConversation(null)
  stateActivated.value = false
  aiState.value = null
  messages.value = [welcomeMsg()]
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
    if (detail?.messages?.length > 0) {
      messages.value = detail.messages.map(m => ({ id: m.id, role: m.role, content: m.content, timestamp: m.timestamp }))
      stateActivated.value = true
    } else {
      messages.value = [welcomeMsg()]
      stateActivated.value = false
    }
    await msgListRef.value?.scrollToBottom()
  } catch {
    messages.value = [welcomeMsg()]
    stateActivated.value = false
  }
}

async function renameConversation(conv) {
  const title = prompt('新名称：', conv.title)
  if (!title?.trim()) return
  try {
    await api.put(`/ai-chat/conversations/${conv.id}/rename`, { title: title.trim() })
    conv.title = title.trim()
  } catch { /* */ }
}

async function deleteConversation(conv) {
  if (!confirm(`删除会话「${conv.title}」？`)) return
  try {
    await api.delete(`/ai-chat/conversations/${conv.id}`)
    if (currentConversationId.value === conv.id) { currentConversationId.value = null; messages.value = [welcomeMsg()] }
    loadSessions()
  } catch { /* */ }
}

// ===================== 消息 =====================
function welcomeMsg() {
  return { role: 'assistant', content: '你好！我是 AI 教研助手。我可以帮您解答英语教学、课程设计、教研资源等方面的问题。', timestamp: Date.now() }
}

const msgListRef = ref(null)
const inputText = ref('')
const messages = ref([welcomeMsg()])
const loading = ref(false)
const abortController = ref(null)
const imagePreviews = ref([])  // [{ dataUrl, id }]
const aiState = ref(null)
const showFocusHelp = ref(false)
const stateVersion = ref(0)
const stateActivated = ref(false)
const achievements = ref([])
const showMobileSidebar = ref(window.innerWidth > 1024)
const enableSearch = ref(true)
const enableDeepThink = ref(true)
const showMobileInfo = ref(window.innerWidth > 1024)

const quickPrompts = [
  '如何设计一堂高职英语听说课？',
  '请推荐几个适合职校学生的英语教学活动',
  '英语课程思政有哪些切入点？',
  '如何提升学生的职场英语应用能力？'
]

async function scrollToBottom() {
  await msgListRef.value?.scrollToBottom()
}

// ===================== 图片 =====================
let _imgId = 0
const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif', 'image/bmp']
function processImageFile(file) {
  if (!file || !ALLOWED_TYPES.includes(file.type)) return false
  if (file.size > 20 * 1024 * 1024) return false
  const reader = new FileReader()
  reader.onload = () => { imagePreviews.value.push({ dataUrl: reader.result, id: ++_imgId }) }
  reader.readAsDataURL(file)
  return true
}
function handlePaste(e) {
  let had = false
  for (const item of e.clipboardData?.items || []) {
    if (item.type.startsWith('image/')) { e.preventDefault(); processImageFile(item.getAsFile()); had = true }
  }
}
function handleDrop(e) {
  e.preventDefault()
  for (const f of e.dataTransfer?.files || []) { processImageFile(f) }
}
function removeImage(id) { imagePreviews.value = imagePreviews.value.filter(p => p.id !== id) }

// ===================== 发送 =====================
async function sendMessage(text) {
  if ((!text && !imagePreviews.value.length) || loading.value) return
  if (!auth.isLoggedIn) {
    messages.value.push({
      role: 'assistant',
      content: '<div class="login-cta"><div class="login-cta-icon"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--color-brand-600)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v1"/><path d="M9 13v1"/></svg></div><div class="login-cta-text">登录后解锁 AI 教研助手</div><div class="login-cta-sub">人格系统 · 长期记忆 · 智能对话</div><div class="login-cta-actions"><a href="/login" class="login-cta-btn"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" x2="3" y1="12" y2="12"/></svg><span>登录</span></a><a href="/register" class="login-cta-register"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/></svg><span>注册</span></a></div></div>',
      timestamp: Date.now(), loginPrompt: true,
    })
    await scrollToBottom()
    return
  }
  const userMsg = { role: 'user', content: text, timestamp: Date.now() }
  if (imagePreviews.value.length) userMsg.images = imagePreviews.value.map(p => p.dataUrl)
  messages.value.push(userMsg)
  inputText.value = ''
  imagePreviews.value = []
  await scrollToBottom()
  loading.value = true
  const ctrl = new AbortController()
  abortController.value = ctrl

  try {
    const payload = { message: text, conversation_id: currentConversationId.value, model: null, enable_search: enableSearch.value, enable_deep_think: enableDeepThink.value }
    if (userMsg.images) payload.images = userMsg.images
    const res = await api.post('/ai-chat/chat', payload, { signal: ctrl.signal })
    const reply = res.data
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
    if (reply.new_achievements?.length > 0) {
      reply.new_achievements.forEach(ach => { playUnlockSound(ach.tier || 'bronze'); showAchievementToast(ach) })
      loadAchievements()
    }
    if (reply.conversation_id && !currentConversationId.value) {
      currentConversationId.value = reply.conversation_id
      saveLastConversation(reply.conversation_id)
      loadSessions()
    }
    messages.value.push({ role: 'assistant', content: reply.message.content, timestamp: reply.message.timestamp })
  } catch (e) {
    if (axios.isCancel(e) || e?.name === 'AbortError' || e?.code === 'ERR_CANCELED') {
      // 用户主动停止，不发错误消息
    } else {
      messages.value.push({ role: 'assistant', content: '抱歉，出了点问题，请稍后重试。', timestamp: Date.now() })
    }
  } finally {
    loading.value = false
    abortController.value = null
    await scrollToBottom()
  }
}

function stopAI() {
  if (abortController.value) abortController.value.abort()
}

// ===================== 动画 =====================
function animateCounts(target) {
  const start = performance.now()
  function tick() {
    const t = Math.min((performance.now() - start) / 800, 1)
    const e = 1 - Math.pow(1 - t, 3)
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

// ===================== 成就 =====================
let _audioCtx = null
function playUnlockSound(tier) {
  try {
    if (!_audioCtx) _audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    if (_audioCtx.state === 'suspended') _audioCtx.resume()
    const now = _audioCtx.currentTime
    const notes = { gold:[523.25,659.25,783.99], silver:[587.33,783.99], bronze:[783.99], special:[523.25,659.25,783.99,1046.5] }[tier] || [659.25]
    notes.forEach((freq, i) => {
      const osc = _audioCtx.createOscillator(); const gain = _audioCtx.createGain()
      osc.type = tier === 'gold' ? 'triangle' : 'sine'
      osc.frequency.setValueAtTime(freq, now + i * 0.12)
      gain.gain.setValueAtTime(0, now + i * 0.12)
      gain.gain.linearRampToValueAtTime(0.18, now + i * 0.12 + 0.04)
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.12 + 0.5)
      osc.connect(gain); gain.connect(_audioCtx.destination)
      osc.start(now + i * 0.12); osc.stop(now + i * 0.12 + 0.5)
    })
  } catch { /* */ }
}
async function loadAchievements() {
  try { const res = await api.get('/ai-chat/achievements'); achievements.value = res.data?.items || [] } catch { /* */ }
}
async function loadState(convId = null) {
  try {
    const params = convId ? { conversation_id: convId } : {}
    const res = await api.get('/ai-chat/state', { params })
    const data = res.data
    aiState.value = { ...data, engagement: 0, attention: 0 }
    await nextTick(); await new Promise(r => requestAnimationFrame(r))
    aiState.value = data; animateCounts(data); stateVersion.value++
  } catch { /* */ }
}

// ===================== 初始化 =====================
window.addEventListener('resize', () => {
  if (window.innerWidth > 1024) { showMobileSidebar.value = true; showMobileInfo.value = true }
})

onMounted(async () => {
  await loadSessions()
  loadAchievements()
  const last = localStorage.getItem('ai_last_conv')
  if (last) { const c = sessions.value.find(s => s.id === Number(last)); if (c) { switchSession(c); return } }
  loadState()
})
</script>

<template>
  <div class="chat-layout" @paste="handlePaste" @dragover.prevent @drop="handleDrop">
    <button class="mobile-menu-btn left" @click="showMobileSidebar = !showMobileSidebar" title="会话列表">
      {{ showMobileSidebar ? '✕' : '☰' }}
    </button>
    <button class="mobile-menu-btn right" @click="showMobileInfo = !showMobileInfo" title="状态面板">
      {{ showMobileInfo ? '✕' : '◧' }}
    </button>

    <!-- 左侧会话栏 -->
    <SessionSidebar
      v-show="showMobileSidebar"
      class="layout-sidebar"
      :sessions="sessions"
      :current-conversation-id="currentConversationId"
      @select="switchSession"
      @rename="renameConversation"
      @delete="deleteConversation"
      @create="createSession"
    />

    <!-- 中间聊天区 -->
    <main class="chat-main">
      <MessageList ref="msgListRef" :messages="messages" :loading="loading" />

      <!-- 快捷提问 -->
      <div v-if="messages.length <= 1" class="quick-prompts">
        <div class="prompts-label"><Lightbulb :size="12" /><span>试试这样问</span></div>
        <div class="prompts-list">
          <button v-for="(p, i) in quickPrompts" :key="i" class="prompt-chip" @click="sendMessage(p)">{{ p }}</button>
        </div>
      </div>

      <!-- 图片预览 -->
      <div v-if="imagePreviews.length && auth.isLoggedIn" class="img-preview-bar">
        <div v-for="p in imagePreviews" :key="p.id" class="img-preview-item">
          <img :src="p.dataUrl" class="img-preview-thumb" />
          <button class="img-preview-close" @click="removeImage(p.id)">&times;</button>
        </div>
      </div>

      <ChatInput v-if="auth.isLoggedIn" v-model="inputText" :loading="loading"
        :disabled="!inputText.trim() && !imagePreviews.length"
        :enable-search="enableSearch" :enable-deep-think="enableDeepThink"
        @send="sendMessage" @stop="stopAI"
        @toggle-search="enableSearch = !enableSearch"
        @toggle-deep-think="enableDeepThink = !enableDeepThink" />
    </main>

    <!-- 右侧信息栏 -->
    <InfoSidebar
      v-show="showMobileInfo"
      class="layout-sidebar"
      :ai-state="aiState"
      :state-activated="stateActivated"
      :show-focus-help="showFocusHelp"
      :is-dark="isDark"
      @toggle-help="showFocusHelp = !showFocusHelp"
      @toggle-theme="toggle"
    />

  </div>
</template>

<style scoped>
.chat-layout { display:flex; height:100vh; background:var(--bg-page); overflow:hidden; }
.chat-main { flex:1; display:flex; flex-direction:column; min-width:0; background:var(--bg-page); }

/* 快捷提问 */
.quick-prompts { max-width:820px; width:100%; margin:0 auto; padding:0 var(--space-5) var(--space-3); flex-shrink:0; }
.prompts-label { display:inline-flex; align-items:center; gap:var(--space-1); font-size:var(--text-xs); color:var(--text-tertiary); margin-bottom:var(--space-2); }
.prompts-list { display:flex; flex-wrap:wrap; gap:var(--space-2); }
.prompt-chip { padding:var(--space-1) var(--space-3); border-radius:var(--radius-full); border:1px solid var(--border-light); background:var(--bg-card); color:var(--text-secondary); font-size:var(--text-xs); cursor:pointer; transition:all var(--duration-fast) var(--ease-out); }
.prompt-chip:hover { border-color:var(--color-brand-400); color:var(--color-brand-600); background:var(--color-brand-50); transform:translateY(-1px); }
[data-theme="dark"] .prompt-chip:hover { background:rgba(79,70,229,0.1); }

/* 图片预览 */
.img-preview-bar { max-width:720px; margin:0 auto; display:flex; align-items:center; gap:6px; padding:var(--space-2) var(--space-5); flex-wrap:wrap; }
.img-preview-item { position:relative; flex-shrink:0; }
.img-preview-thumb { width:56px; height:56px; object-fit:cover; border-radius:6px; border:1px solid var(--border-light); display:block; }
.img-preview-close { position:absolute; top:-8px; right:-8px; width:22px; height:22px; border-radius:50%; border:none; background:rgba(0,0,0,0.55); color:#fff; font-size:14px; cursor:pointer; display:flex; align-items:center; justify-content:center; padding:0; line-height:1; transition:all var(--duration-fast); }
.img-preview-close:hover { background:rgba(239,68,68,0.85); transform:scale(1.1); }

/* 移动端菜单按钮 */
.mobile-menu-btn { display:none; position:fixed; top:12px; z-index:100; width:32px; height:32px; border-radius:var(--radius-md); border:1px solid var(--border-light); background:var(--bg-card); color:var(--text-secondary); font-size:14px; cursor:pointer; box-shadow:var(--shadow-md); }
.mobile-menu-btn.left { left:12px; }
.mobile-menu-btn.right { right:12px; }

/* ===================== 响应式 ===================== */
@media (max-width: 1280px) {
  .layout-sidebar:last-of-type { display:none; }
}

@media (max-width: 1024px) {
  .chat-layout { position:relative; }
  .mobile-menu-btn { display:flex; align-items:center; justify-content:center; }
  .layout-sidebar { position:fixed; top:0; bottom:0; z-index:50; box-shadow:var(--shadow-lg); transition:transform 0.25s var(--ease-out); }
  .layout-sidebar:first-of-type { left:0; }
  .layout-sidebar:last-of-type { right:0; }
  :deep(.session-sidebar) { position:static; }
  :deep(.info-sidebar) { position:static; }
}

@media (max-width: 768px) {
  .chat-main { padding:0; }
  .messages-scroll { padding:var(--space-3); }
  .message-body { max-width:90%; }
  .quick-prompts { padding:0 var(--space-3) var(--space-2); }
  .input-area { padding:var(--space-2) var(--space-3) var(--space-2); }
}

/* 消息搜索 */
.search-bar { display:flex; align-items:center; gap:6px; padding:8px var(--space-4); border-bottom:1px solid var(--border-light); background:var(--bg-card); animation:search-in 0.2s var(--ease-out); }
.search-input { flex:1; border:none; outline:none; background:var(--bg-page); padding:8px 12px; border-radius:var(--radius-md); font-size:var(--text-sm); color:var(--text-primary); }
.search-input::placeholder { color:var(--text-tertiary); }
.search-clear,.search-close { background:none; border:none; cursor:pointer; padding:4px; display:flex; }
.search-clear { color:var(--text-tertiary); }
.search-close { color:var(--text-secondary); }
.search-results { max-height:260px; overflow-y:auto; border-bottom:1px solid var(--border-light); background:var(--bg-card); animation:search-in 0.25s var(--ease-out); scrollbar-width:thin; scrollbar-color:var(--border-light) transparent; }
.search-item { display:flex; align-items:center; gap:var(--space-2); padding:8px var(--space-4); cursor:pointer; border-bottom:1px solid var(--border-light); transition:background var(--duration-fast); }
.search-item:hover { background:var(--bg-hover); }
.search-item:last-child { border-bottom:none; }
.search-role { font-size:var(--text-xs); font-weight:var(--font-bold); padding:1px 6px; border-radius:var(--radius-full); flex-shrink:0; }
.search-role.user { background:var(--color-brand-100); color:var(--color-brand-700); }
.search-role.assistant { background:var(--color-success-100); color:var(--color-success-700); }
.search-snippet { flex:1; font-size:var(--text-xs); color:var(--text-primary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.search-conv { font-size:11px; color:var(--text-tertiary); flex-shrink:0; max-width:120px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.search-status { padding:12px var(--space-4); font-size:var(--text-xs); color:var(--text-tertiary); text-align:center; }
@keyframes search-in { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
</style>

<style>
/* 登录 CTA — 非 scoped */
.login-cta { text-align:center; padding:var(--space-5) var(--space-2) var(--space-3); max-width:260px; margin:0 auto; animation:cta-enter 0.5s cubic-bezier(0.16,1,0.3,1) both; }
@keyframes cta-enter { from{opacity:0;transform:translateY(12px) scale(0.95)} to{opacity:1;transform:translateY(0) scale(1)} }
.login-cta-icon { margin-bottom:var(--space-3); display:flex; justify-content:center; animation:cta-float 3s ease-in-out infinite; }
@keyframes cta-float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
.login-cta-text { font-size:var(--text-sm); font-weight:var(--font-bold); color:var(--text-primary); margin-bottom:4px; }
.login-cta-sub { font-size:11px; color:var(--text-tertiary); margin-bottom:var(--space-4); }
.login-cta-actions { display:flex; justify-content:center; gap:var(--space-2); }
.login-cta-btn { display:inline-flex; align-items:center; gap:4px; padding:6px 20px; border-radius:var(--radius-md); background:linear-gradient(135deg,var(--color-brand-500),var(--color-brand-600),#6366f1); background-size:200% 200%; animation:cta-shimmer 3s ease infinite; color:#fff!important; text-decoration:none!important; font-size:var(--text-sm); font-weight:var(--font-semibold); box-shadow:0 2px 8px rgba(79,70,229,0.25); transition:box-shadow 0.15s ease-out; }
.login-cta-btn:hover { box-shadow:0 4px 16px rgba(79,70,229,0.4); }
.login-cta-register { display:inline-flex; align-items:center; gap:4px; padding:6px 20px; border-radius:var(--radius-md); border:1px solid var(--border-light); color:var(--text-secondary)!important; text-decoration:none!important; font-size:var(--text-sm); font-weight:var(--font-medium); transition:all 0.15s ease-out; }
.login-cta-register:hover { border-color:var(--color-brand-300); color:var(--color-brand-600)!important; background:var(--color-brand-50); }
@keyframes cta-shimmer { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
</style>
