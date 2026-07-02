<script setup>
import { ref } from 'vue'
import { Send, Brain, Image, FileUp, X } from 'lucide-vue-next'

const props = defineProps({
  loading: Boolean,
  disabled: Boolean,
  modelValue: String,
  enableSearch: Boolean,
  enableDeepThink: Boolean,
})

const emit = defineEmits([
  'update:modelValue', 'send', 'stop',
  'toggle-search', 'toggle-deep-think',
])
const inputEl = ref(null)
const imageInput = ref(null)
const fileInput = ref(null)
const attachments = ref([])  // [{ id, name, type, dataUrl, base64 }]

function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

function onSend() {
  emit('send', props.modelValue, attachments.value)
  attachments.value = []
  requestAnimationFrame(() => autoResize())
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    onSend()
  }
}

function onPaste(e) {
  const items = e.clipboardData?.items
  if (!items) return
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      e.preventDefault()
      const file = item.getAsFile()
      readFile(file, 'image')
    }
  }
}

function onInput(e) {
  emit('update:modelValue', e.target.value)
  autoResize()
}

function resetHeight() { requestAnimationFrame(() => autoResize()) }

// ── 文件选择 ──────────────────────────────

function readFile(file, type) {
  const reader = new FileReader()
  reader.onload = () => {
    const base64 = reader.result.split(',')[1]
    attachments.value.push({
      id: Date.now(), name: file.name, type,
      dataUrl: reader.result, base64,
    })
  }
  reader.readAsDataURL(file)
}

function onImagePick(e) {
  for (const f of e.target.files) readFile(f, 'image')
  imageInput.value.value = ''
}

function onFilePick(e) {
  for (const f of e.target.files) readFile(f, 'doc')
  fileInput.value.value = ''
}

function removeAttachment(id) {
  attachments.value = attachments.value.filter(a => a.id !== id)
}

function attachmentLabel(a) {
  if (a.type === 'image') return 'image'
  if (a.name.endsWith('.pdf')) return 'PDF'
  if (a.name.match(/\.(docx?|ppt|pptx)$/i)) return 'doc'
  return 'file'
}

defineExpose({ resetHeight })
</script>

<template>
  <div class="input-area">
    <!-- 附件预览 -->
    <div v-if="attachments.length" class="attach-preview">
      <div v-for="a in attachments" :key="a.id" class="attach-chip">
        <img v-if="a.type === 'image'" :src="a.dataUrl" class="attach-thumb" />
        <span v-else class="attach-icon">{{ attachmentLabel(a) }}</span>
        <span class="attach-name">{{ a.name }}</span>
        <button class="attach-remove" @click="removeAttachment(a.id)"><X :size="10" /></button>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-wrapper">
      <textarea
        ref="inputEl"
        :value="modelValue"
        placeholder="试试问问我吧！"
        class="chat-input"
        rows="1"
        @keydown="onKeydown"
        @input="onInput"
        @paste="onPaste"
      />
      <button
        v-if="!loading"
        class="btn-send"
        :disabled="disabled && !attachments.length"
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

    <!-- 工具栏 -->
    <div class="input-toolbar">
      <div class="toolbar-left">
        <input ref="imageInput" type="file" accept="image/*" multiple hidden @change="onImagePick" />
        <button class="tool-btn" title="上传图片" @click="imageInput.click()">
          <Image :size="15" />
        </button>
        <input ref="fileInput" type="file" accept=".pdf,.doc,.docx,.ppt,.pptx" multiple hidden @change="onFilePick" />
        <button class="tool-btn" title="上传文件" @click="fileInput.click()">
          <FileUp :size="15" />
        </button>
      </div>
      <div class="toolbar-right">
        <button
          class="tool-btn-toggle"
          :class="{ active: enableDeepThink }"
          title="深度思考"
          @click="emit('toggle-deep-think')"
        >
          <Brain :size="13" />
          <span class="toggle-label">深度思考</span>
        </button>
      </div>
    </div>

    <div class="input-footer">
      <span>AI 生成内容仅供参考</span>
    </div>
  </div>
</template>

<style scoped>
.input-area { padding:var(--space-2) var(--space-5) var(--space-3); background:transparent; flex-shrink:0; }

/* ── 附件预览 ── */
.attach-preview {
  max-width:820px; margin:0 auto var(--space-1); display:flex; flex-wrap:wrap; gap:6px;
}
.attach-chip {
  display:inline-flex; align-items:center; gap:4px; padding:2px 6px 2px 2px;
  border-radius:var(--radius-lg); border:1px solid var(--border-light);
  background:var(--bg-page); font-size:11px; color:var(--text-secondary);
}
.attach-thumb { width:24px; height:24px; object-fit:cover; border-radius:var(--radius-sm); }
.attach-icon {
  width:24px; height:24px; display:inline-flex; align-items:center; justify-content:center;
  background:var(--color-brand-50); color:var(--color-brand-600); border-radius:var(--radius-sm);
  font-size:9px; font-weight:var(--font-bold); text-transform:uppercase;
}
[data-theme="dark"] .attach-icon { background:rgba(79,70,229,0.15); color:var(--color-brand-300); }
.attach-name { max-width:80px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.attach-remove {
  width:14px; height:14px; border:none; background:transparent; color:var(--text-tertiary);
  cursor:pointer; display:inline-flex; align-items:center; justify-content:center; padding:0;
}
.attach-remove:hover { color:var(--color-danger); }

/* ── 输入框 ── */
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
}
.chat-input::placeholder { color:var(--text-tertiary); }

/* ── 工具栏 ── */
.input-toolbar {
  max-width:820px; margin:6px auto 0; display:flex; align-items:center; justify-content:space-between;
}
.toolbar-left { display:flex; gap:2px; }
.toolbar-right { display:flex; gap:2px; }
.tool-btn {
  height:28px; padding:0 8px; border:none; border-radius:var(--radius-md); background:transparent;
  color:var(--text-tertiary); cursor:pointer; display:inline-flex; align-items:center; gap:4px;
  transition:all 0.15s; font-size:12px;
}
.tool-btn:hover { color:var(--color-brand-500); background:var(--color-brand-50); }
[data-theme="dark"] .tool-btn:hover { background:rgba(79,70,229,0.1); }
.tool-btn-toggle {
  height:28px; padding:0 8px; border:1px solid var(--border-light); border-radius:var(--radius-lg);
  background:transparent; color:var(--text-tertiary); cursor:pointer;
  display:inline-flex; align-items:center; gap:4px; font-size:12px;
  transition:all 0.15s var(--ease-out);
}
.tool-btn-toggle:hover { border-color:var(--color-brand-300); color:var(--color-brand-500); }
.tool-btn-toggle.active { border-color:var(--color-brand-400); background:var(--color-brand-50); color:var(--color-brand-600); }
[data-theme="dark"] .tool-btn-toggle.active { background:rgba(79,70,229,0.15); color:var(--color-brand-300); border-color:var(--color-brand-400); }

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