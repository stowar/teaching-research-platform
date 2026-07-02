<script setup>
import { ref, watch, nextTick } from 'vue'
import { Bot, User, FileText } from 'lucide-vue-next'
import MarkdownIt from 'markdown-it'

defineProps({
  messages: Array,
  loading: Boolean,
})

const md = new MarkdownIt({ breaks: true, linkify: true })
const container = ref(null)

function formatTime(ts) {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

async function scrollToBottom() {
  await nextTick()
  if (container.value) container.value.scrollTop = container.value.scrollHeight
}

watch(() => container.value, () => scrollToBottom())

defineExpose({ scrollToBottom, container })
</script>

<template>
  <div ref="container" class="messages-scroll">
    <div class="messages-list">
      <div v-for="(msg, idx) in messages" :key="msg.timestamp + '-' + idx" :id="'msg-' + msg.id" :class="['message-row', msg.role]">
        <div class="message-avatar">
          <Bot v-if="msg.role === 'assistant'" :size="16" />
          <User v-else :size="16" />
        </div>
        <div class="message-body">
          <div class="message-meta">
            <span class="meta-name">{{ msg.role === 'assistant' ? 'AI 助手' : '我' }}</span>
            <span class="meta-time">{{ formatTime(msg.timestamp) }}</span>
          </div>
          <div v-if="msg.images?.length" class="message-images">
            <img v-for="(img, i) in msg.images" :key="i" :src="img" class="msg-img" />
          </div>
          <div v-if="msg.attachments?.length" class="message-attachments">
            <span v-for="(name, i) in msg.attachments" :key="i" class="msg-attach">
              <FileText :size="12" /> {{ name }}
            </span>
          </div>
          <div class="message-bubble" :class="{ 'markdown-body': msg.role === 'assistant' }">
            <div v-if="msg.role === 'assistant'" class="message-text" v-html="msg.loginPrompt ? msg.content : md.render(msg.content)" />
            <pre v-else class="message-text">{{ msg.content }}</pre>
          </div>
        </div>
      </div>
      <div v-if="loading" class="message-row assistant">
        <div class="message-avatar"><Bot :size="16" /></div>
        <div class="message-body">
          <div class="message-meta"><span class="meta-name">AI 助手</span></div>
          <div class="message-bubble thinking-bubble">
            <span class="typing-label">Thinking</span>
            <span class="dot dot-1">●</span>
            <span class="dot dot-2">●</span>
            <span class="dot dot-3">●</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.messages-scroll { flex:1; overflow-y:auto; padding:var(--space-5); scrollbar-width:thin; scrollbar-color:transparent transparent; }
.messages-scroll:hover { scrollbar-color:var(--border-light) transparent; }
.messages-scroll::-webkit-scrollbar { width:3px; }
.messages-scroll::-webkit-scrollbar-thumb { background:transparent; border-radius:2px; }
.messages-scroll:hover::-webkit-scrollbar-thumb { background:var(--border-light); }
.messages-list { max-width:820px; margin:0 auto; display:flex; flex-direction:column; gap:var(--space-4); }
.message-row { display:flex; gap:var(--space-3); animation:msg-in 0.4s cubic-bezier(0.22,0.61,0.36,1) both; }
.message-row:nth-child(1) { animation-delay:0s; }
.message-row:nth-child(2) { animation-delay:0.03s; }
.message-row:nth-child(3) { animation-delay:0.05s; }
.message-row.user { flex-direction:row-reverse; }
@keyframes msg-in { from{opacity:0;transform:translateY(20px) scale(0.96)} to{opacity:1;transform:translateY(0) scale(1)} }
.message-avatar { width:28px; height:28px; border-radius:var(--radius-full); display:flex; align-items:center; justify-content:center; flex-shrink:0; background:var(--color-brand-100); color:var(--color-brand-600); }
.message-row.user .message-avatar { background:var(--color-brand-600); color:#fff; }
.message-body { display:flex; flex-direction:column; gap:2px; max-width:80%; }
.message-row.user .message-body { align-items:flex-end; }
.message-meta { display:flex; align-items:center; gap:var(--space-2); font-size:var(--text-xs); color:var(--text-tertiary); }
.meta-name { font-weight:var(--font-semibold); color:var(--text-secondary); }
.message-bubble { padding:var(--space-2) var(--space-3); border-radius:var(--radius-lg); background:var(--bg-card); border:1px solid var(--border-light); box-shadow:var(--shadow-xs); line-height:1.7; }
.message-row.user .message-bubble { background:linear-gradient(135deg,var(--color-brand-500),var(--color-brand-600)); color:#fff; border:none; }
.message-text { margin:0; font-family:inherit; font-size:var(--text-sm); white-space:pre-wrap; word-break:break-word; color:inherit; }
.message-row.user .message-text { color:#fff; }
.markdown-body .message-text :deep(h1),.markdown-body .message-text :deep(h2),.markdown-body .message-text :deep(h3) { margin:var(--space-3) 0 var(--space-2) 0; font-weight:var(--font-bold); color:var(--text-primary); }
.markdown-body .message-text :deep(h1) { font-size:var(--text-xl); }
.markdown-body .message-text :deep(h2) { font-size:var(--text-lg); }
.markdown-body .message-text :deep(h3) { font-size:var(--text-base); }
.markdown-body .message-text :deep(ul),.markdown-body .message-text :deep(ol) { padding-left:var(--space-5); margin:var(--space-2) 0; }
.markdown-body .message-text :deep(li) { margin-bottom:var(--space-1); }
.markdown-body .message-text :deep(code) { background:var(--bg-hover); padding:1px 5px; border-radius:var(--radius-sm); font-size:0.9em; font-family:'Consolas','Monaco',monospace; }
.markdown-body .message-text :deep(pre) { background:var(--bg-hover); border-radius:var(--radius-md); padding:var(--space-3); overflow-x:auto; margin:var(--space-2) 0; }
.markdown-body .message-text :deep(pre code) { background:none; padding:0; }
.markdown-body .message-text :deep(strong) { font-weight:var(--font-bold); color:var(--text-primary); }
.markdown-body .message-text :deep(blockquote) { border-left:3px solid var(--color-brand-400); padding-left:var(--space-3); margin:var(--space-2) 0; color:var(--text-secondary); font-style:italic; }
.markdown-body .message-text :deep(a) { color:var(--color-brand-600); text-decoration:underline; }
.markdown-body .message-text :deep(p) { margin:var(--space-1) 0; }
.markdown-body .message-text :deep(table) { border-collapse:collapse; width:100%; margin:var(--space-2) 0; }
.markdown-body .message-text :deep(th),.markdown-body .message-text :deep(td) { border:1px solid var(--border-light); padding:var(--space-1) var(--space-2); text-align:left; font-size:var(--text-xs); }
.thinking-bubble { padding:var(--space-2) var(--space-3); display:flex; gap:4px; align-items:center; }
.typing-label { font-size:var(--text-xs); color:var(--text-tertiary); font-style:italic; }
.dot { font-size:5px; color:var(--text-tertiary); animation:dot-bounce 1.4s ease-in-out infinite; }
.dot-2 { animation-delay:0.2s; }
.dot-3 { animation-delay:0.4s; }
@keyframes dot-bounce { 0%,80%,100%{opacity:0.2;transform:translateY(0)} 40%{opacity:1;transform:translateY(-5px)} }
.message-images { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:var(--space-2); }
.msg-img { max-width:240px; max-height:240px; border-radius:var(--radius-md); border:1px solid var(--border-light); object-fit:contain; animation:img-in 0.3s var(--ease-out) both; }
@keyframes img-in { from{opacity:0;transform:scale(0.92)} to{opacity:1;transform:scale(1)} }
.message-attachments { display:flex; flex-wrap:wrap; gap:4px; margin-bottom:var(--space-2); }
.msg-attach {
  display:inline-flex; align-items:center; gap:4px; padding:2px 8px;
  border-radius:var(--radius-sm); background:var(--color-brand-50); color:var(--color-brand-600);
  font-size:11px;
}
[data-theme="dark"] .msg-attach { background:rgba(79,70,229,0.15); color:var(--color-brand-300); }
</style>
