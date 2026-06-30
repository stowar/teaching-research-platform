<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/api/client.js'
import {
  UserCircle, Heart, MessageCircle, Bell, CheckCheck,
  FileText, Plus, ExternalLink, Eye, MessageSquare, X, Trophy
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const notifications = ref([])
const unreadCount = ref(0)
const myPosts = ref([])
const achievements = ref([])
const unlockedCount = ref(0)
const tierOrder = ref([])
const tierLabel = ref({})
const tierNames = ref({})
const loading = ref(true)

const selectedAch = ref(null)
function openAchDetail(ach) { selectedAch.value = ach }
function closeAchDetail() { selectedAch.value = null }

async function fetchAll() {
  loading.value = true
  try {
    // 通知 + 帖子 + 成就 并行
    const [notifRes, postRes, achRes] = await Promise.all([
      api.get('/community/notifications'),
      api.get('/community/posts', { params: { user_id: auth.user?.id, page_size: 5 } }),
      api.get('/ai-chat/achievements'),
    ])
    notifications.value = notifRes.data?.items || []
    unreadCount.value = notifRes.data?.unread || 0
    myPosts.value = postRes.data?.items || []
    const achData = achRes.data || {}
    achievements.value = achData.items || []
    tierOrder.value = achData.tier_order || []
    tierLabel.value = achData.tier_labels || {}
    tierNames.value = achData.tier_names || {}
    unlockedCount.value = achievements.value.filter(a => a.unlocked).length
  } catch { /* ignore */ }
  finally { loading.value = false }
}

async function markRead(notif) {
  if (notif.is_read) return
  try {
    await api.put(`/community/notifications/${notif.id}/read`)
    notif.is_read = 1
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch { /* ignore */ }
}

async function deleteNotif(notif) {
  try {
    await api.delete(`/community/notifications/${notif.id}`)
    if (!notif.is_read) unreadCount.value = Math.max(0, unreadCount.value - 1)
    notifications.value = notifications.value.filter(n => n.id !== notif.id)
  } catch { /* ignore */ }
}

async function markAllRead() {
  try {
    await api.put('/community/notifications/read-all')
    notifications.value.forEach(n => n.is_read = 1)
    unreadCount.value = 0
  } catch { /* ignore */ }
}

function goToPost(postId) { router.push(`/community/${postId}`) }

function typeIcon(type) { return type === 'like' ? Heart : MessageCircle }
function typeLabel(type) { return type === 'like' ? '赞了' : '评论了' }

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}

onMounted(fetchAll)
</script>

<template>
  <div class="account-page">
    <div class="page-header">
      <UserCircle class="page-icon" :size="32" />
      <h1>个人中心</h1>
    </div>

    <!-- 快捷操作卡 -->
    <div class="action-cards">
      <div class="action-card" @click="router.push('/community/create')"><Plus :size="20" /><span>发布帖子</span></div>
      <div class="action-card" @click="router.push('/community?mine=1')"><FileText :size="20" /><span>我的帖子</span></div>
      <div class="action-card" @click="router.push('/profile')"><UserCircle :size="20" /><span>编辑资料</span></div>
    </div>

    <div v-if="loading" class="section-empty-state">加载中...</div>

    <template v-else>
      <!-- 消息中心 -->
      <div class="account-card card">
        <div class="card-toolbar">
          <div class="toolbar-title">
            <Bell :size="16" />
            <h3>消息中心</h3>
            <span class="unread-badge" v-if="unreadCount">{{ unreadCount }} 条未读</span>
          </div>
          <div class="toolbar-actions">
            <button v-if="unreadCount" class="btn btn-sm btn-text press-feedback" @click="markAllRead"><CheckCheck :size="13" /> 全部已读</button>
          </div>
        </div>
        <div v-if="notifications.length === 0" class="section-empty">
          <Bell :size="32" /><span>暂无消息</span>
          <span class="empty-sub">当有人评论或点赞你的帖子时，你会在这里收到通知</span>
        </div>
        <div v-else class="notif-list">
          <div v-for="notif in notifications" :key="notif.id" :class="['notif-item', { unread: !notif.is_read }]" @click="goToPost(notif.post_id)">
            <div :class="['notif-dot', notif.type]"><component :is="typeIcon(notif.type)" :size="14" /></div>
            <div class="notif-content">
              <div class="notif-main"><strong>{{ notif.sender_name || '匿名' }}</strong><span>{{ typeLabel(notif.type) }}了你的帖子</span><span class="notif-time">{{ formatTime(notif.create_time) }}</span></div>
            </div>
            <div class="notif-actions">
              <span v-if="!notif.is_read" class="unread-dot"></span>
              <button class="btn-del" @click.stop="deleteNotif(notif)" title="删除"><X :size="14" /></button>
            </div>
          </div>
        </div>
      </div>

      <!-- 我的帖子 -->
      <div class="account-card card">
        <div class="card-toolbar">
          <div class="toolbar-title">
            <FileText :size="16" />
            <h3>我的帖子</h3>
          </div>
          <button class="btn btn-sm btn-text press-feedback" @click="router.push('/community?mine=1')">查看全部</button>
        </div>
        <div v-if="myPosts.length === 0" class="section-empty">还没有发过帖子</div>
        <div v-else class="my-post-list">
          <div v-for="post in myPosts" :key="post.id" class="my-post-item" @click="goToPost(post.id)">
            <span class="mp-title">{{ post.title }}</span>
            <span class="mp-meta"><Eye :size="12" />{{ post.view_count }} <Heart :size="12" />{{ post.like_count }} <MessageSquare :size="12" />{{ post.comment_count }}</span>
          </div>
        </div>
      </div>

      <!-- 教学成就 — 只展示已解锁，按品级分组 -->
      <div v-if="unlockedCount > 0" class="account-card card">
        <div class="card-toolbar">
          <div class="toolbar-title">
            <Trophy :size="16" />
            <h3>教学成就</h3>
          </div>
        </div>
        <template v-for="tier in tierOrder" :key="tier">
          <div v-if="achievements.filter(a => a.unlocked && a.tier === tier).length > 0" class="ach-tier-group">
            <h4 class="ach-tier-head" :class="'tier-' + tier">{{ tierNames[tier] }}</h4>
            <div class="ach-grid">
              <div v-for="ach in achievements.filter(a => a.unlocked && a.tier === tier)" :key="ach.id" :class="['ach-item', 'tier-' + ach.tier]" @click="openAchDetail(ach)">
                <span class="ach-emoji">{{ ach.emoji }}</span>
                <div class="ach-text">
                  <span class="ach-name">{{ ach.name }}</span>
                  <span class="ach-desc">{{ ach.desc }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </template>
  </div>

  <!-- 成就详情弹窗 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="selectedAch" class="ach-modal-overlay" @click.self="closeAchDetail">
        <div :class="['ach-modal', 'modal-tier-' + selectedAch.tier]">
          <span class="ach-modal-emoji">{{ selectedAch.emoji }}</span>
          <h3 class="ach-modal-name">{{ selectedAch.name }}</h3>
          <p class="ach-modal-desc">{{ selectedAch.desc }}</p>
          <div class="ach-modal-meta">
            <span class="ach-modal-tier" :class="'tier-' + selectedAch.tier">{{ tierLabel[selectedAch.tier] }}</span>
            <span class="ach-modal-time" v-if="selectedAch.unlock_time">获得于 {{ selectedAch.unlock_time }}</span>
          </div>
          <button class="ach-modal-close" @click="closeAchDetail">确定</button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.account-page { animation:slide-up-enter 0.5s var(--ease-out) both; }
.page-header { display:flex; align-items:center; gap:var(--space-3); margin-bottom:var(--space-6); }
.page-icon { display:inline-flex; align-items:center; color:var(--color-brand-600); }
.page-header h1 { font-size:var(--text-2xl); font-weight:var(--font-bold); color:var(--text-primary); margin:0; }

/* 操作卡 */
.action-cards { display:grid; grid-template-columns:repeat(3, 1fr); gap:var(--space-3); margin-bottom:var(--space-6); }
.action-card { display:flex; flex-direction:column; align-items:center; gap:var(--space-2); padding:var(--space-4); border-radius:var(--radius-lg); background:var(--bg-card); border:1px solid var(--border-light); cursor:pointer; transition:all var(--duration-fast) var(--ease-out); color:var(--text-secondary); font-size:var(--text-sm); }
.action-card:hover { border-color:var(--color-brand-400); color:var(--color-brand-600); box-shadow:var(--shadow-sm); transform:translateY(-1px); }

/* 卡片 — admin 风格 */
.account-card { padding:var(--space-6); margin-bottom:var(--space-5); animation:slide-up-enter 0.6s var(--ease-out) both; }
.account-card:nth-child(2) { animation-delay:0.1s; }
.account-card:nth-child(3) { animation-delay:0.2s; }
.card-toolbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-4); padding-bottom:var(--space-3); border-bottom:1px solid var(--border-light); }
.toolbar-title { display:flex; align-items:center; gap:var(--space-2); color:var(--text-primary); }
.toolbar-title h3 { font-size:var(--text-base); font-weight:var(--font-bold); margin:0; }
.toolbar-actions { display:flex; align-items:center; gap:var(--space-2); }
.section-empty-state { text-align:center; padding:var(--space-8); color:var(--text-tertiary); font-size:var(--text-sm); }
.section-empty { text-align:center; color:var(--text-tertiary); padding:var(--space-8) var(--space-4); display:flex; flex-direction:column; align-items:center; gap:var(--space-2); }
.section-empty .empty-sub { font-size:var(--text-xs); max-width:260px; line-height:1.5; }

.unread-badge { font-size:var(--text-xs); color:var(--color-danger-600); background:var(--color-danger-50); padding:2px var(--space-2); border-radius:var(--radius-full); font-weight:var(--font-semibold); }
.btn-text { font-size:var(--text-xs); color:var(--text-link); background:none; border:none; cursor:pointer; display:inline-flex; align-items:center; gap:3px; }
.btn-text:hover { text-decoration:underline; }
.section-empty { text-align:center; color:var(--text-tertiary); padding:var(--space-8) var(--space-4); display:flex; flex-direction:column; align-items:center; gap:var(--space-2); }
.section-empty .empty-sub { font-size:var(--text-xs); max-width:260px; line-height:1.5; }

/* 通知 */
.notif-list { display:flex; flex-direction:column; gap:var(--space-2); }
.notif-item { display:flex; align-items:center; gap:var(--space-3); padding:var(--space-3); border-radius:var(--radius-md); cursor:pointer; transition:all var(--duration-fast) var(--ease-out); }
.notif-item:hover { background:var(--bg-hover); }
.notif-item.unread { background:var(--color-brand-50); }
.notif-dot { width:36px; height:36px; border-radius:var(--radius-full); display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.notif-dot.comment { background:var(--color-info-100); color:var(--color-info-600); }
.notif-dot.like { background:var(--color-danger-100); color:var(--color-danger-600); }
.notif-content { flex:1; min-width:0; }
.notif-main { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px; font-size:var(--text-sm); color:var(--text-secondary); }
.notif-main strong { color:var(--text-primary); }
.notif-time { font-size:var(--text-xs); color:var(--text-tertiary); margin-left:auto; }
.notif-actions { display:flex; align-items:center; gap:var(--space-2); flex-shrink:0; }
.unread-dot { width:8px; height:8px; border-radius:var(--radius-full); background:var(--color-brand-500); }
.btn-del { background:none; border:none; color:var(--text-tertiary); cursor:pointer; padding:4px; border-radius:var(--radius-sm); transition:all var(--duration-fast) var(--ease-out); opacity:0; }
.notif-item:hover .btn-del { opacity:1; }
.btn-del:hover { color:var(--color-danger-600); background:var(--color-danger-50); }

/* 我的帖子 */
.my-post-list { display:flex; flex-direction:column; }
.my-post-item { display:flex; justify-content:space-between; align-items:center; padding:var(--space-2) var(--space-3); border-radius:var(--radius-md); cursor:pointer; transition:background var(--duration-fast) var(--ease-out); }
.my-post-item:hover { background:var(--bg-hover); }
.mp-title { font-size:var(--text-sm); color:var(--text-primary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; }
.mp-meta { display:flex; align-items:center; gap:3px var(--space-2); font-size:var(--text-xs); color:var(--text-tertiary); flex-shrink:0; margin-left:var(--space-3); }

/* 成就 */
.ach-tier-group { margin-bottom:var(--space-5); }
.ach-tier-head { font-size:11px; font-weight:var(--font-bold); text-transform:uppercase; letter-spacing:0.1em; margin:0 0 var(--space-3) 0; padding:0 0 var(--space-2) 0; border-bottom:2px solid var(--border-light); }
.ach-tier-head.tier-special { color:#a855f7; border-color:rgba(168,85,247,0.25); }
.ach-tier-head.tier-gold { color:#ca8a04; border-color:rgba(202,138,4,0.3); }
.ach-tier-head.tier-silver { color:#475569; border-color:rgba(71,85,105,0.2); }
.ach-tier-head.tier-bronze { color:#b08968; border-color:rgba(176,137,104,0.2); }
.ach-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:8px; }
.ach-item { display:flex; align-items:center; gap:var(--space-2); padding:10px 12px; border-radius:var(--radius-lg); border:2px solid transparent; background:var(--bg-card); transition:all var(--duration-fast) var(--ease-out); cursor:pointer; min-height:72px; }
.ach-item.tier-gold { background:linear-gradient(160deg, #fefdf8, #fdf8e8, #faf0d7); }
.ach-item.tier-silver { background:linear-gradient(135deg, #fcfcfc, #f1f5f9, #e2e8f0); }
.ach-item.tier-bronze { background:linear-gradient(135deg, #fefdfb, #fef9f4, #fef5ec); }
.ach-item.tier-special { position:relative; background:linear-gradient(135deg, #fdf2f8, #ede9fe, #e0f2fe, #fce7f3); background-size:200% 200%; animation:special-bg 4s ease infinite; border:none; }
.ach-item.tier-special::before { content:''; position:absolute; inset:-2px; border-radius:inherit; padding:2px; background:linear-gradient(135deg, #ef4444, #f59e0b, #22c55e, #3b82f6, #a855f7, #ec4899, #ef4444); background-size:200% 200%; animation:special-border 3s ease infinite; -webkit-mask:linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); mask-composite:exclude; pointer-events:none; z-index:0; }
.ach-item.tier-special > * { position:relative; z-index:1; }
@keyframes special-bg { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes special-border { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
.ach-item:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,0.08); }
[data-theme="dark"] .ach-item:hover { box-shadow:0 6px 20px rgba(0,0,0,0.3); }
.ach-emoji { font-size:20px; flex-shrink:0; }
.ach-text { display:flex; flex-direction:column; gap:1px; min-width:0; flex:1; }
.ach-name { font-size:var(--text-xs); font-weight:var(--font-bold); color:var(--text-primary); }
.ach-desc { font-size:11px; color:var(--text-secondary); white-space:pre-line; }

/* 弹窗 */
.ach-modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:1000; backdrop-filter:blur(4px); }
.ach-modal { border-radius:var(--radius-xl); padding:var(--space-8) var(--space-6) var(--space-6); text-align:center; max-width:380px; width:90%; box-shadow:0 16px 64px rgba(0,0,0,0.15); position:relative; }
.ach-modal.modal-tier-gold { background:linear-gradient(160deg, #fffef5, #fffbeb, #fef3c7); border:1px solid rgba(245,158,11,0.25); }
.ach-modal.modal-tier-silver { background:linear-gradient(160deg, #fdfdfd, #f5f5f5, #ececec); border:1px solid rgba(180,180,180,0.3); }
.ach-modal.modal-tier-bronze { background:linear-gradient(160deg, #fefdfb, #fef9f4, #fef5ec); border:1px solid rgba(176,137,104,0.18); }
.ach-modal.modal-tier-special { background:linear-gradient(160deg, #faf5ff, #fdf2f8, #eff6ff); border:2px solid transparent; background-clip:padding-box; }
.ach-modal.modal-tier-special::before { content:''; position:absolute; inset:-2px; border-radius:var(--radius-xl); padding:2px; background:linear-gradient(135deg, #ef4444, #f59e0b, #22c55e, #3b82f6, #a855f7, #ec4899); background-size:300% 300%; animation:ach-rainbow 3s ease infinite; -webkit-mask:linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); mask-composite:exclude; pointer-events:none; z-index:-1; }
.ach-modal-emoji { font-size:56px; display:block; margin-bottom:var(--space-3); }
.ach-modal-name { font-size:var(--text-xl); font-weight:var(--font-extrabold); color:var(--text-primary); margin:0 0 var(--space-2); }
.ach-modal-desc { font-size:var(--text-sm); color:var(--text-secondary); margin:0 0 var(--space-4); line-height:1.8; white-space:pre-line; word-break:break-word; }
.ach-modal-meta { display:flex; align-items:center; justify-content:center; gap:var(--space-3); margin-bottom:var(--space-5); }
.ach-modal-tier { font-size:var(--text-xs); font-weight:var(--font-bold); padding:3px 12px; border-radius:var(--radius-full); }
.ach-modal-tier.tier-gold { background:#fef3c7; color:#92400e; }
.ach-modal-tier.tier-silver { background:#e0e0e0; color:#555; }
.ach-modal-tier.tier-bronze { background:#fef5ec; color:#8b6f4e; }
.ach-modal-tier.tier-special { background:linear-gradient(135deg, #ede9fe, #fce7f3, #e0f2fe); color:#7c3aed; }
.ach-modal-time { font-size:var(--text-xs); color:var(--text-tertiary); }
.ach-modal-close { margin-top:var(--space-2); padding:8px 32px; border-radius:var(--radius-full); border:1px solid var(--border-light); background:var(--bg-card); color:var(--text-primary); font-size:var(--text-sm); cursor:pointer; transition:all var(--duration-fast); }
.ach-modal-close:hover { background:var(--bg-hover); }

.modal-enter-active { transition:all 0.3s cubic-bezier(0.16,1,0.3,1); }
.modal-leave-active { transition:all 0.2s cubic-bezier(0.4,0,0.2,1); }
.modal-enter-from { opacity:0; }
.modal-enter-from .ach-modal { transform:scale(0.9) translateY(16px); }
.modal-leave-to { opacity:0; }
.modal-leave-to .ach-modal { transform:scale(0.95) translateY(8px); }

@keyframes slide-up-enter { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
[data-theme="dark"] .notif-item.unread { background:rgba(99,102,241,0.08); }

/* 暗黑模式成就 */
[data-theme="dark"] .ach-item.tier-gold { background:linear-gradient(160deg, #1e1808, #241e0c, #1a1408); }
[data-theme="dark"] .ach-item.tier-silver { background:linear-gradient(160deg, #1a1a1c, #1e1e22, #18181b); }
[data-theme="dark"] .ach-item.tier-bronze { background:linear-gradient(160deg, #1c1410, #201812, #18100c); }
[data-theme="dark"] .ach-item.tier-special { background:linear-gradient(160deg, #1a1220, #1c1424, #181022); }
[data-theme="dark"] .ach-item .ach-name { color:var(--text-primary); }
[data-theme="dark"] .ach-item.tier-gold .ach-name { color:#e8c574; }
[data-theme="dark"] .ach-item.tier-gold .ach-desc { color:#b8976e; }
[data-theme="dark"] .ach-item.tier-silver .ach-name { color:#cbd5e1; }
[data-theme="dark"] .ach-item.tier-silver .ach-desc { color:#94a3b8; }
[data-theme="dark"] .ach-item.tier-bronze .ach-name { color:#f4b896; }
[data-theme="dark"] .ach-item.tier-bronze .ach-desc { color:#c0814a; }
[data-theme="dark"] .ach-item.tier-special .ach-name { color:#c4b5fd; }
[data-theme="dark"] .ach-item.tier-special .ach-desc { color:#a78bfa; }
[data-theme="dark"] .ach-modal { box-shadow:0 16px 64px rgba(0,0,0,0.4); }
[data-theme="dark"] .ach-modal.modal-tier-gold { background:linear-gradient(160deg, #1e1808, #241e0c, #1a1408); }
[data-theme="dark"] .ach-modal.modal-tier-silver { background:linear-gradient(160deg, #1a1a1c, #1e1e22, #18181b); }
[data-theme="dark"] .ach-modal.modal-tier-bronze { background:linear-gradient(160deg, #1c1410, #201812, #18100c); }
[data-theme="dark"] .ach-modal.modal-tier-special { background:linear-gradient(160deg, #1a1220, #1c1424, #181022); }
[data-theme="dark"] .ach-modal-name { color:#f0f0f0; }
[data-theme="dark"] .ach-modal-desc { color:#a0a0a0; }
[data-theme="dark"] .ach-modal-time { color:#808080; }
[data-theme="dark"] .ach-modal-close { background:rgba(255,255,255,0.06); border-color:rgba(255,255,255,0.1); color:#ccc; }
[data-theme="dark"] .ach-modal-close:hover { background:rgba(255,255,255,0.12); }
[data-theme="dark"] .ach-tier-head.tier-gold { color:#e8c574; border-color:rgba(232,197,116,0.3); }
[data-theme="dark"] .ach-tier-head.tier-silver { color:#cbd5e1; border-color:rgba(203,213,225,0.2); }
[data-theme="dark"] .ach-tier-head.tier-bronze { color:#f4b896; border-color:rgba(244,184,150,0.2); }
[data-theme="dark"] .ach-tier-head.tier-special { color:#c4b5fd; border-color:rgba(196,181,253,0.25); }

@media (max-width: 768px) { .action-cards { grid-template-columns:1fr 1fr 1fr; } .ach-grid { grid-template-columns:1fr 1fr; } }
</style>
