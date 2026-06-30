<script setup>
defineProps({ achievement: Object })
</script>

<template>
  <Transition name="ach-slide">
    <div v-if="achievement" class="ach-toast-overlay">
      <div :class="['ach-toast-card', 'ach-tier-' + (achievement.tier || 'bronze')]">
        <div :class="['ach-tier-bar', 'tier-' + (achievement.tier || 'bronze')]" />
        <div class="ach-toast-content">
          <span class="ach-toast-emoji">{{ achievement.emoji }}</span>
          <div class="ach-toast-body">
            <div class="ach-toast-title">成就解锁！</div>
            <div class="ach-toast-name">{{ achievement.name }}</div>
            <div class="ach-toast-desc">{{ achievement.desc }}</div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.ach-toast-overlay { position:fixed; bottom:24px; right:0; z-index:1000; pointer-events:none; }
.ach-toast-card {
  display:flex; align-items:stretch; border-radius:0; background:var(--bg-card);
  border:1px solid var(--border-light); overflow:hidden; max-width:380px;
  box-shadow:0 8px 32px rgba(0,0,0,0.12),0 2px 8px rgba(0,0,0,0.06);
}
.ach-tier-gold { box-shadow:0 8px 32px rgba(245,158,11,0.2),0 2px 8px rgba(245,158,11,0.1); }
.ach-tier-silver { box-shadow:0 8px 32px rgba(160,160,160,0.25),0 2px 8px rgba(160,160,160,0.15); }
.ach-tier-bronze { box-shadow:0 8px 32px rgba(212,165,116,0.2),0 2px 8px rgba(212,165,116,0.1); }
.ach-tier-special { border:2px solid transparent; position:relative; }
.ach-tier-special::before {
  content:''; position:absolute; inset:-2px; border-radius:inherit; padding:2px;
  background:linear-gradient(135deg,#ef4444,#f59e0b,#22c55e,#3b82f6,#a855f7,#ec4899);
  background-size:300% 300%; animation:toast-rainbow 3s ease infinite;
  -webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);
  mask-composite:exclude; pointer-events:none; z-index:-1;
}
@keyframes toast-rainbow { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }
.ach-toast-content { display:flex; align-items:center; gap:var(--space-3); padding:var(--space-3) var(--space-4); flex:1; }
.ach-toast-emoji { font-size:32px; flex-shrink:0; }
.ach-toast-body { display:flex; flex-direction:column; gap:1px; min-width:0; }
.ach-toast-title { font-size:10px; font-weight:var(--font-bold); color:var(--text-tertiary); text-transform:uppercase; letter-spacing:0.05em; }
.ach-toast-name { font-size:var(--text-sm); font-weight:var(--font-extrabold); color:var(--text-primary); }
.ach-toast-desc { font-size:var(--text-xs); color:var(--text-secondary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ach-tier-bar { width:6px; flex-shrink:0; }
.ach-tier-bar.tier-gold { background:linear-gradient(180deg,#fef3c7,#f59e0b); }
.ach-tier-bar.tier-silver { background:linear-gradient(180deg,#e0e0e0,#b0b0b0,#d4d4d4); }
.ach-tier-bar.tier-bronze { background:linear-gradient(180deg,#fce4cc,#c0814a); }
.ach-tier-bar.tier-special {
  background:linear-gradient(180deg,#ef4444,#f59e0b,#22c55e,#3b82f6,#a855f7);
  background-size:100% 300%; animation:rainbow-bar 2s ease infinite;
}
@keyframes rainbow-bar { 0%,100%{background-position:0% 0%} 50%{background-position:0% 100%} }
.ach-slide-enter-active { transition:all 0.45s cubic-bezier(0.16,1,0.3,1); }
.ach-slide-leave-active { transition:all 0.35s cubic-bezier(0.4,0,0.2,1); }
.ach-slide-enter-from { opacity:0; transform:translateX(120%); }
.ach-slide-leave-to { opacity:0; transform:translateX(120%); }
</style>
