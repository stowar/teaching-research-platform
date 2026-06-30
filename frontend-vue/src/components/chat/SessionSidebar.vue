<script setup>
import { Plus, MessageSquare, ChevronLeft } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

defineProps({
  sessions: Array,
  currentConversationId: [Number, null],
})

const emit = defineEmits(['select', 'rename', 'delete', 'create'])
const router = useRouter()
</script>

<template>
  <aside class="session-sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">新建会话</span>
      <button class="btn-new" title="新建会话" @click="emit('create')">
        <Plus :size="16" />
      </button>
    </div>
    <div class="session-list">
      <button
        v-for="s in sessions"
        :key="s.id"
        :class="['session-item', s.id === currentConversationId ? 'active' : '']"
        @click="emit('select', s)"
        @dblclick="emit('rename', s)"
        @contextmenu.prevent="emit('delete', s)"
      >
        <MessageSquare :size="14" />
        <span class="session-name">{{ s.title }}</span>
        <span class="session-count">{{ s.message_count || 0 }}</span>
      </button>
    </div>
    <div class="session-tips"><span>单击切换 · 双击重命名 · 右键删除</span></div>
    <div class="sidebar-footer">
      <button class="btn-back" @click="router.push('/')">
        <ChevronLeft :size="14" />
        <span>返回首页</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.session-sidebar { width:200px; flex-shrink:0; display:flex; flex-direction:column; border-right:1px solid var(--border-light); background:var(--bg-card); }
.sidebar-header { display:flex; align-items:center; justify-content:space-between; padding:var(--space-4); border-bottom:1px solid var(--border-light); }
.sidebar-title { font-size:var(--text-base); font-weight:var(--font-bold); color:var(--text-primary); }
.btn-new { width:28px; height:28px; border-radius:var(--radius-md); border:1px solid var(--border-light); background:transparent; color:var(--text-secondary); cursor:pointer; display:inline-flex; align-items:center; justify-content:center; transition:all var(--duration-fast) var(--ease-out); }
.btn-new:hover { background:var(--color-brand-50); color:var(--color-brand-600); border-color:var(--color-brand-300); }
.session-list { flex:1; overflow-y:auto; padding:var(--space-2); display:flex; flex-direction:column; gap:var(--space-1); scrollbar-width:none; }
.session-list::-webkit-scrollbar { display:none; }
.session-item { display:flex; align-items:center; gap:var(--space-2); padding:var(--space-2) var(--space-3); border-radius:var(--radius-md); border:none; background:transparent; color:var(--text-secondary); font-size:var(--text-sm); cursor:pointer; text-align:left; transition:all var(--duration-fast) var(--ease-out); width:100%; }
.session-item:hover { background:var(--bg-hover); color:var(--text-primary); }
.session-item.active { background:var(--color-brand-50); color:var(--color-brand-700); font-weight:var(--font-semibold); }
.session-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.session-count { font-size:var(--text-xs); color:var(--text-tertiary); background:var(--bg-page); padding:0 6px; border-radius:var(--radius-full); }
.session-tips { text-align:center; padding:var(--space-2) var(--space-3); border-top:1px solid var(--border-light); font-size:11px; color:var(--text-tertiary); }
.sidebar-footer { padding:var(--space-3); border-top:1px solid var(--border-light); }
.btn-back { width:100%; display:inline-flex; align-items:center; justify-content:center; gap:var(--space-1); padding:var(--space-2) var(--space-3); border-radius:var(--radius-md); border:1px solid var(--border-light); background:var(--bg-page); color:var(--text-secondary); font-size:var(--text-sm); cursor:pointer; transition:all var(--duration-fast) var(--ease-out); }
.btn-back:hover { background:var(--bg-hover); color:var(--text-primary); }
[data-theme="dark"] .btn-new:hover { background:rgba(79,70,229,0.12); }
[data-theme="dark"] .session-item.active { background:rgba(79,70,229,0.15); color:var(--color-brand-300); }
[data-theme="dark"] .session-count { background:rgba(255,255,255,0.06); }
</style>
