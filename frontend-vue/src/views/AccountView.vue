<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/api/client.js'
import {
  UserCircle, Heart, MessageCircle, Bell, CheckCheck,
  FileText, Plus, ExternalLink, Eye, MessageSquare, X
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const notifications = ref([])
const unreadCount = ref(0)
const myPosts = ref([])
const loading = ref(true)

async function fetchAll() {
  loading.value = true
  try {
    // 通知 + 我的帖子 并行
    const [notifRes, postRes] = await Promise.all([
      api.get('/community/notifications'),
      api.get('/community/posts', { params: { user_id: auth.user?.id, page_size: 5 } })
    ])
    notifications.value = notifRes.data || []
    unreadCount.value = notifRes.unread || 0
    myPosts.value = postRes.data || []
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
      <UserCircle class="page-icon" :size="28" />
      <h1>个人中心</h1>
    </div>

    <!-- 快捷操作卡 -->
    <div class="action-cards">
      <div class="action-card" @click="router.push('/community/create')">
        <Plus :size="20" />
        <span>发布帖子</span>
      </div>
      <div class="action-card" @click="router.push('/community?mine=1')">
        <FileText :size="20" />
        <span>我的帖子</span>
      </div>
      <div class="action-card" @click="router.push('/profile')">
        <UserCircle :size="20" />
        <span>编辑资料</span>
      </div>
    </div>

    <div v-if="loading" class="section">
      <div class="section-header"><h3>加载中...</h3></div>
    </div>

    <template v-else>
      <!-- 消息 -->
      <div class="section">
        <div class="section-header">
          <h3><Bell :size="16" /> 消息中心</h3>
          <div class="section-actions">
            <span class="unread-badge" v-if="unreadCount">{{ unreadCount }} 条未读</span>
            <button v-if="unreadCount" class="btn-text" @click="markAllRead"><CheckCheck :size="13" /> 全部已读</button>
          </div>
        </div>
        <div v-if="notifications.length === 0" class="section-empty">
          <Bell :size="32" />
          <span>暂无消息</span>
          <span class="empty-sub">当有人评论或点赞你的帖子时，你会在这里收到通知</span>
        </div>
        <div v-else class="notif-list">
          <div
            v-for="notif in notifications"
            :key="notif.id"
            :class="['notif-item', { unread: !notif.is_read }]"
            @click="goToPost(notif.post_id)"
          >
            <div :class="['notif-dot', notif.type]">
              <component :is="typeIcon(notif.type)" :size="14" />
            </div>
            <div class="notif-content">
              <div class="notif-main">
                <strong>{{ notif.sender_name || '匿名' }}</strong>
                <span>{{ typeLabel(notif.type) }}了你的帖子</span>
                <span class="notif-time">{{ formatTime(notif.create_time) }}</span>
              </div>
            </div>
            <div class="notif-actions">
              <span v-if="!notif.is_read" class="unread-dot"></span>
              <button class="btn-del" @click.stop="deleteNotif(notif)" title="删除"><X :size="14" /></button>
            </div>
          </div>
        </div>
      </div>

      <!-- 我的帖子 -->
      <div class="section">
        <div class="section-header">
          <h3><FileText :size="16" /> 我的帖子</h3>
          <button class="btn-text" @click="router.push('/community?mine=1')">查看全部</button>
        </div>
        <div v-if="myPosts.length === 0" class="section-empty">还没有发过帖子</div>
        <div v-else class="my-post-list">
          <div
            v-for="post in myPosts"
            :key="post.id"
            class="my-post-item"
            @click="goToPost(post.id)"
          >
            <span class="mp-title">{{ post.title }}</span>
            <span class="mp-meta">
              <Eye :size="12" />{{ post.view_count }}
              <Heart :size="12" />{{ post.like_count }}
              <MessageSquare :size="12" />{{ post.comment_count }}
            </span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.account-page {
  max-width: 680px;
  margin: 0 auto;
  animation: slide-up 0.4s var(--ease-out) both;
}
.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-5);
}
.page-icon { color: var(--color-brand-600); }
.page-header h1 { font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--text-primary); margin: 0; }

/* 操作卡 */
.action-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}
.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}
.action-card:hover { border-color: var(--color-brand-400); color: var(--color-brand-600); box-shadow: var(--shadow-sm); transform: translateY(-1px); }

/* 分区 */
.section {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}
.section-header h3 {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0;
}
.section-actions { display: flex; align-items: center; gap: var(--space-2); }
.unread-badge {
  font-size: var(--text-xs);
  color: var(--color-danger-600);
  background: var(--color-danger-50);
  padding: 2px var(--space-2);
  border-radius: var(--radius-full);
  font-weight: var(--font-semibold);
}
.btn-text {
  font-size: var(--text-xs);
  color: var(--text-link);
  background: none; border: none; cursor: pointer;
  display: inline-flex; align-items: center; gap: 3px;
}
.btn-text:hover { text-decoration: underline; }
.section-empty {
  text-align: center; color: var(--text-tertiary); padding: var(--space-8) var(--space-4);
  display: flex; flex-direction: column; align-items: center; gap: var(--space-2);
}
.section-empty .empty-sub { font-size: var(--text-xs); max-width: 260px; line-height: 1.5; }

/* 通知 */
.notif-list { display: flex; flex-direction: column; }
.notif-item {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-3) var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  position: relative;
}
.notif-item:hover { background: var(--bg-hover); }
.notif-item.unread { background: var(--color-brand-50); }
.notif-dot {
  width: 36px; height: 36px;
  border-radius: var(--radius-full);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.notif-dot.comment { background: var(--color-info-100); color: var(--color-info-600); }
.notif-dot.like { background: var(--color-danger-100); color: var(--color-danger-600); }

.notif-content { flex: 1; min-width: 0; }
.notif-main {
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px;
  font-size: var(--text-sm); color: var(--text-secondary);
}
.notif-main strong { color: var(--text-primary); }
.notif-time { font-size: var(--text-xs); color: var(--text-tertiary); margin-left: auto; }

.notif-actions { display: flex; align-items: center; gap: var(--space-2); flex-shrink: 0; }
.unread-dot {
  width: 8px; height: 8px;
  border-radius: var(--radius-full);
  background: var(--color-brand-500);
}
.btn-del {
  background: none; border: none; color: var(--text-tertiary);
  cursor: pointer; padding: 4px; border-radius: var(--radius-sm);
  transition: all var(--duration-fast) var(--ease-out);
  opacity: 0;
}
.notif-item:hover .btn-del { opacity: 1; }
.btn-del:hover { color: var(--color-danger-600); background: var(--color-danger-50); }

/* 我的帖子 */
.my-post-list { display: flex; flex-direction: column; }
.my-post-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}
.my-post-item:hover { background: var(--bg-hover); }
.mp-title { font-size: var(--text-sm); color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.mp-meta { display: flex; align-items: center; gap: 3px var(--space-2); font-size: var(--text-xs); color: var(--text-tertiary); flex-shrink: 0; margin-left: var(--space-3); }

@keyframes slide-up { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

[data-theme="dark"] .notif-item.unread { background: rgba(99,102,241,0.08); }
@media (max-width: 768px) {
  .action-cards { grid-template-columns: 1fr 1fr 1fr; }
}
</style>
