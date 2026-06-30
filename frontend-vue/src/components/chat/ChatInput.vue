<script setup>
import { ref } from 'vue'
import { Send } from 'lucide-vue-next'

const props = defineProps({
  loading: Boolean,
  disabled: Boolean,
  modelValue: String,
})

const emit = defineEmits(['update:modelValue', 'send', 'stop'])
const inputEl = ref(null)

function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

function onSend() {
  emit('send', props.modelValue)
  requestAnimationFrame(() => autoResize())
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    onSend()
  }
}

function onInput(e) {
  emit('update:modelValue', e.target.value)
  autoResize()
}

function resetHeight() { requestAnimationFrame(() => autoResize()) }

defineExpose({ resetHeight })
</script>

<template>
  <div class="input-area">
    <div class="input-wrapper">
      <textarea
        ref="inputEl"
        :value="modelValue"
        placeholder="试试问问我吧！"
        class="chat-input"
        :disabled="loading"
        rows="1"
        @keydown="onKeydown"
        @input="onInput"
      />
      <button
        v-if="!loading"
        class="btn-send"
        :disabled="disabled"
        @click="onSend"
      >
        <Send :size="14" />
      </button>
      <button
        v-else
        class="btn-stop"
        @click="emit('stop')"
      >
        <span class="stop-icon">■</span>
      </button>
    </div>
    <div class="input-footer">
      <span>AI 生成内容仅供参考</span>
    </div>
  </div>
</template>

<style scoped>
.input-area { padding:var(--space-2) var(--space-5) var(--space-3); background:transparent; flex-shrink:0; }
.input-wrapper {
  max-width:820px; margin:0 auto; display:flex; align-items:flex-end; gap:var(--space-1);
  padding:4px 4px 4px 18px; border-radius:28px; border:1px solid var(--border-light);
  background:var(--bg-page);
  transition:box-shadow var(--duration-fast) var(--ease-out), border-color var(--duration-fast) var(--ease-out);
}
.input-wrapper:focus-within { border-color:var(--color-brand-400); box-shadow:0 0 0 3px rgba(79,70,229,0.12); }
.chat-input {
  flex:1; border:none; outline:none; background:transparent; padding:8px 0;
  font-size:13px; color:var(--text-primary); line-height:1.5; resize:none;
  font-family:inherit; min-height:20px; max-height:160px;
  scrollbar-width:thin; scrollbar-color:transparent transparent;
}
.chat-input:hover { scrollbar-color:var(--border-light) transparent; }
.chat-input::-webkit-scrollbar { width:3px; }
.chat-input::-webkit-scrollbar-thumb { background:transparent; border-radius:2px; }
.chat-input:hover::-webkit-scrollbar-thumb { background:var(--border-light); }
.chat-input::placeholder { color:var(--text-tertiary); }
.btn-send {
  width:32px; height:32px; border-radius:var(--radius-lg); border:none;
  background:linear-gradient(135deg,var(--color-brand-500),var(--color-brand-600));
  color:#fff; cursor:pointer; display:inline-flex; align-items:center; justify-content:center;
  transition:all 0.15s var(--ease-out); flex-shrink:0;
}
.btn-send:hover:not(:disabled) { transform:scale(1.08); box-shadow:0 0 12px rgba(79,70,229,0.3); }
.btn-send:active:not(:disabled) { transform:scale(0.92); }
.btn-send:disabled { opacity:0.35; cursor:not-allowed; }

.btn-stop {
  width:32px; height:32px; border-radius:var(--radius-lg); border:none;
  background:#ef4444;
  color:#fff; cursor:pointer; display:inline-flex; align-items:center; justify-content:center;
  transition:all 0.2s var(--ease-out); flex-shrink:0;
  box-shadow:0 0 10px rgba(239,68,68,0.3), 0 0 20px rgba(239,68,68,0.1);
  animation:stop-breathe 2s ease-in-out infinite;
}
.btn-stop:hover { transform:scale(1.08); background:#dc2626; box-shadow:0 0 18px rgba(239,68,68,0.45), 0 0 32px rgba(239,68,68,0.2); }
.btn-stop:active { transform:scale(0.92); }
.stop-icon { font-size:14px; font-weight:var(--font-bold); }
@keyframes stop-breathe { 0%,100%{ box-shadow:0 0 10px rgba(239,68,68,0.3), 0 0 20px rgba(239,68,68,0.1); } 50%{ box-shadow:0 0 18px rgba(239,68,68,0.45), 0 0 30px rgba(239,68,68,0.2); } }
.input-footer { max-width:720px; margin:var(--space-1) auto 0; display:flex; align-items:center; justify-content:center; gap:var(--space-1); font-size:var(--text-xs); color:var(--text-tertiary); }
[data-theme="dark"] .input-wrapper:focus-within { box-shadow:0 0 0 3px rgba(79,70,229,0.2); }
</style>
