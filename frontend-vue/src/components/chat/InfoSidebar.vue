<script setup>
import { Moon, Sun } from 'lucide-vue-next'

const props = defineProps({
  aiState: Object,
  stateActivated: Boolean,
  showFocusHelp: Boolean,
  isDark: Boolean,
})

const emit = defineEmits(['toggle-help', 'toggle-theme'])

function focusEmoji(v) { if (v <= 30) return '🌀'; if (v <= 70) return '🎯'; return '🔒' }
function focusLabel(v) { if (v <= 30) return '发散态'; if (v <= 70) return '聚焦态'; return '锁定态' }
</script>

<template>
  <aside class="info-sidebar">
    <div class="info-header"><span class="info-title">AI 教研助手</span></div>
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
                <div class="state-bar" :class="{ 'bar-overdrive': aiState.engagement > 100 }">
                  <div class="state-fill" :class="{ 'fill-overdrive': aiState.engagement > 100 }"
                       :style="{width: Math.min(aiState.engagement, 100) + '%'}" />
                </div>
                <span class="state-num" :class="{ 'num-overdrive': aiState.engagement > 100 }">{{ aiState.engagement }}</span>
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
          <div v-else class="state-locked-overlay"><p>发送第一条消息<br/>唤醒 AI 人格</p></div>
        </div>

        <div class="state-hint-row">
          <p class="state-hint">人格数据仅保存在当前会话</p>
          <button class="help-btn" @click.stop="emit('toggle-help')">?</button>
        </div>

        <div v-if="showFocusHelp" class="help-popover">
          <div class="help-section"><div class="help-row"><span>🎭 语气</span><span>四态自动切换</span></div><div class="help-desc">根据对话氛围自动调整：专业/轻松/鼓励/分析</div></div>
          <div class="help-section"><div class="help-row"><span>❤️ 投入度</span><span>0-100</span></div><div class="help-desc">反映对话深度。分享真实教学案例 +5，追问 +3，认可 +2，敷衍 -3</div></div>
          <div class="help-section"><div class="help-row"><span>👁 关注度</span><span>0-100</span></div><div class="help-desc">对当前话题的锁定程度</div><div class="help-desc">🌀 发散态 0-30 — 话题灵活</div><div class="help-desc">🎯 聚焦态 31-70 — 深入追问</div><div class="help-desc">🔒 锁定态 71-100 — 固执围绕</div></div>
          <div class="help-section"><div class="help-row"><span>⚙️ 技术实现</span></div><div class="help-desc">人格状态机 — 三维度数值实时动态变化</div><div class="help-desc">长期记忆 — 自动存档 · 对话中自然引用</div><div class="help-desc">Function Calling — 11 个 AI 工具自主决策调用</div><div class="help-desc">裁切总结 — 超长对话自动压缩摘要存入记忆</div></div>
        </div>
      </div>

      <!-- 运行数据 -->
      <div class="state-section">
        <div class="section-label">运行数据</div>
        <div class="ai-state-panel" :class="{ 'state-locked': !stateActivated }">
          <div v-if="aiState && stateActivated" class="stats-inline">
            <div class="stat-mini"><span class="stat-num">{{ aiState.silence_hours }}h</span><span class="stat-label">静默</span></div>
            <div class="stat-mini"><span class="stat-num">{{ aiState.memory_count }}</span><span class="stat-label">记忆</span></div>
            <div class="stat-mini"><span class="stat-num">{{ aiState.messages_today }}/{{ aiState.messages_limit }}</span><span class="stat-label">今日</span></div>
          </div>
          <div v-else class="state-locked-overlay"><p>发送第一条消息<br/>解锁运行数据</p></div>
        </div>
      </div>

      <!-- 快捷标签 -->
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

    <div class="info-footer">
      <span class="footer-label">外观</span>
      <button class="theme-toggle" @click="emit('toggle-theme')">
        <Moon v-if="isDark" :size="14" />
        <Sun v-else :size="14" />
        <span>{{ isDark ? '暗黑模式' : '浅色模式' }}</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.info-sidebar { width:240px; flex-shrink:0; display:flex; flex-direction:column; border-left:1px solid var(--border-light); background:var(--bg-card); }
.info-header { padding:var(--space-4); border-bottom:1px solid var(--border-light); }
.info-title { font-size:var(--text-base); font-weight:var(--font-bold); color:var(--text-primary); }
.info-body { flex:1; overflow-y:auto; padding:var(--space-4); display:flex; flex-direction:column; gap:var(--space-5); scrollbar-width:none; }
.info-body::-webkit-scrollbar { display:none; }
.state-section { margin-bottom:var(--space-4); }
.section-label { font-size:var(--text-xs); color:var(--text-tertiary); font-weight:var(--font-semibold); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:var(--space-2); }
.ai-state-panel { padding:var(--space-3) var(--space-4); border-radius:var(--radius-lg); background:var(--bg-page); border:1px solid var(--border-light); }
.state-locked { position:relative; overflow:hidden; }
.state-locked-overlay { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:var(--space-2); padding:var(--space-5) var(--space-3); text-align:center; animation:fade-in-up 0.35s var(--ease-out) both; }
@keyframes fade-in-up { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.state-locked-overlay p { margin:0; font-size:var(--text-xs); color:var(--text-tertiary); line-height:1.6; }
.state-grid { display:flex; flex-direction:column; gap:var(--space-3); }
.state-item { display:flex; align-items:center; gap:var(--space-2); flex-wrap:wrap; }
.state-icon { font-size:14px; flex-shrink:0; }
.state-desc { font-size:var(--text-xs); color:var(--text-secondary); min-width:38px; }
.state-bar-wrap { flex:1; display:flex; align-items:center; gap:var(--space-2); min-width:80px; }
.state-sep { height:1px; background:var(--border-light); margin:0 var(--space-1); }
.state-bar { flex:1; height:4px; border-radius:var(--radius-full); background:var(--border-light); overflow:hidden; }
.state-fill { height:100%; border-radius:var(--radius-full); background:linear-gradient(90deg,var(--color-brand-400),var(--color-brand-600)); width:0; transition:width 1s cubic-bezier(0.34,1.56,0.64,1); }
.state-fill.attention { background:linear-gradient(90deg,var(--color-success-400),var(--color-success-600)); }
.bar-overdrive { box-shadow:0 0 8px rgba(239,68,68,0.5),0 0 20px rgba(239,68,68,0.25); animation:overdrive-glow 1.2s ease-in-out infinite alternate; }
.state-fill.fill-overdrive { width:100%!important; background:linear-gradient(90deg,#ef4444,#dc2626)!important; }
@keyframes overdrive-glow { 0%{box-shadow:0 0 6px rgba(239,68,68,0.3),0 0 14px rgba(239,68,68,0.15)} 100%{box-shadow:0 0 12px rgba(239,68,68,0.6),0 0 28px rgba(239,68,68,0.35)} }
.num-overdrive { color:#ef4444!important; text-shadow:0 0 4px rgba(239,68,68,0.3); }
.state-num { font-size:var(--text-xs); color:var(--text-secondary); font-weight:var(--font-bold); min-width:22px; text-align:right; }
.state-hint-row { display:flex; align-items:center; gap:var(--space-2); margin-top:var(--space-2); }
.state-hint { font-size:10px; color:var(--text-tertiary); font-style:italic; opacity:0.5; margin:0; text-align:left; }
.help-btn { width:15px; height:15px; border-radius:var(--radius-full); border:1px solid var(--border-light); background:transparent; color:var(--text-tertiary); font-size:10px; font-weight:var(--font-bold); cursor:pointer; display:inline-flex; align-items:center; justify-content:center; padding:0; flex-shrink:0; transition:all var(--duration-fast); }
.help-btn:hover { background:var(--color-brand-50); color:var(--color-brand-600); border-color:var(--color-brand-300); }
.help-popover { margin:var(--space-2) 0; padding:var(--space-3); border-radius:var(--radius-md); background:var(--bg-page); border:1px solid var(--border-light); font-size:11px; color:var(--text-secondary); display:flex; flex-direction:column; gap:1px; animation:fade-in-up 0.2s var(--ease-out) both; }
.help-row { display:flex; justify-content:space-between; font-weight:var(--font-semibold); }
.help-desc { font-size:10px; color:var(--text-tertiary); margin-bottom:var(--space-1); padding-left:2px; }
.help-section { padding:var(--space-1) 0; }
.help-section + .help-section { border-top:1px solid var(--border-light); padding-top:var(--space-2); }
.stats-inline { display:flex; gap:var(--space-3); }
.stat-mini { flex:1; text-align:center; padding:var(--space-2) 0; }
.stat-num { display:block; font-size:var(--text-lg); font-weight:var(--font-extrabold); color:var(--text-primary); font-variant-numeric:tabular-nums; }
.stat-label { display:block; font-size:var(--text-xs); color:var(--text-tertiary); margin-top:2px; }
.info-tags { display:flex; flex-wrap:wrap; gap:var(--space-2); }
.info-tag { padding:var(--space-1) var(--space-2); border-radius:var(--radius-full); background:var(--color-brand-50); color:var(--color-brand-700); font-size:var(--text-xs); font-weight:var(--font-medium); transition:all 0.2s var(--ease-out); cursor:default; }
.info-tag:hover { transform:translateY(-1px); box-shadow:0 2px 6px rgba(79,70,229,0.15); }

.tone-badge { padding:2px 10px; border-radius:var(--radius-full); font-size:var(--text-xs); font-weight:var(--font-semibold); transition:all 0.3s var(--ease-out); }
.tone-professional { background:var(--color-brand-50); color:var(--color-brand-700); }
.tone-casual { background:var(--color-success-50); color:var(--color-success-700); }
.tone-encouraging { background:var(--color-warning-50); color:var(--color-warning-700); }
.tone-analytical { background:var(--color-info-50); color:var(--color-info-700); }
.tone-safety { background:var(--color-danger-50); color:var(--color-danger-700); }

.info-footer { padding:var(--space-3) var(--space-4); border-top:1px solid var(--border-light); display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:var(--space-1); }
.footer-label { font-size:var(--text-xs); color:var(--text-tertiary); font-weight:var(--font-medium); }
.theme-toggle { display:inline-flex; align-items:center; gap:var(--space-1); padding:var(--space-1) var(--space-2); border-radius:var(--radius-md); border:1px solid var(--border-light); background:var(--bg-page); color:var(--text-secondary); font-size:var(--text-xs); cursor:pointer; transition:all var(--duration-fast) var(--ease-out); }
.theme-toggle:hover { border-color:var(--color-brand-400); color:var(--color-brand-600); background:var(--color-brand-50); }

[data-theme="dark"] .tone-professional { background:rgba(79,70,229,0.15); color:var(--color-brand-300); }
[data-theme="dark"] .tone-casual { background:rgba(34,197,94,0.15); color:var(--color-success-300); }
[data-theme="dark"] .tone-encouraging { background:rgba(234,179,8,0.15); color:var(--color-warning-300); }
[data-theme="dark"] .tone-analytical { background:rgba(59,130,246,0.15); color:var(--color-info-300); }
[data-theme="dark"] .tone-safety { background:rgba(239,68,68,0.15); color:var(--color-danger-300); }
[data-theme="dark"] .info-tag { background:rgba(79,70,229,0.15); color:var(--color-brand-300); }
</style>
