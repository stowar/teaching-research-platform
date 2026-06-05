<script setup>
/**
 * 帖子详情页 PostDetailView.vue
 * 帖子内容 + 评论列表 + 点赞 + 发表评论
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/api/client.js'
import {
  Eye, Heart, MessageCircle, Send, ArrowLeft,
  Clock, User, Trash2, Award, Pin
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const postId = computed(() => Number(route.params.postId))

const post = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref('')

const commentContent = ref('')
const liked = ref(false)
const submitting = ref(false)
const commentLoading = ref(false)

async function fetchPost() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get(`/community/posts/${postId.value}`)
    post.value = res.data
    document.title = res.data?.title + ' - 教研社区' || '帖子详情'
  } catch (e) {
    error.value = '帖子不存在或已被删除'
  } finally {
    loading.value = false
  }
}

async function fetchComments() {
  commentLoading.value = true
  try {
    const res = await api.get(`/community/posts/${postId.value}/comments`)
    comments.value = res.data || []
  } catch { /* ignore */ }
  finally { commentLoading.value = false }
}

async function fetchLikeStatus() {
  if (!auth.isLoggedIn) return
  try {
    const res = await api.get(`/community/posts/${postId.value}/like`)
    liked.value = res.data?.liked || false
  } catch { /* ignore */ }
}

async function toggleLike() {
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  try {
    const res = await api.post(`/community/posts/${postId.value}/like`)
    liked.value = res.liked || false
    if (post.value) {
      post.value.like_count = (post.value.like_count || 0) + (res.liked ? 1 : -1)
    }
  } catch { /* ignore */ }
}

async function submitComment() {
  if (!commentContent.value.trim() || submitting.value) return
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  submitting.value = true
  try {
    await api.post(`/community/posts/${postId.value}/comments`, {
      content: commentContent.value.trim(),
      parent_id: null
    })
    commentContent.value = ''
    if (post.value) {
      post.value.comment_count = (post.value.comment_count || 0) + 1
    }
    await fetchComments()
  } catch { /* ignore */ }
  finally { submitting.value = false }
}

async function deletePost() {
  if (!confirm('确认删除这篇帖子？')) return
  try {
    await api.delete(`/community/posts/${postId.value}`)
    router.push('/community')
  } catch { /* ignore */ }
}

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN') + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  fetchPost()
  fetchComments()
  fetchLikeStatus()
})
</script>

<template>
  <div class="detail-page">
    <!-- 加载 -->
    <div v-if="loading" class="loading-wrap">
      <div class="skeleton-line w-60"></div>
      <div class="skeleton-line w-90"></div>
      <div class="skeleton-line w-90"></div>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="empty-state">
      <MessageCircle :size="48" />
      <p>{{ error }}</p>
      <button class="btn btn-ghost" @click="router.push('/community')">返回社区</button>
    </div>

    <!-- 帖子内容 -->
    <template v-else-if="post">
      <div class="top-bar">
        <button class="btn-ghost-icon" @click="router.push('/community')">
          <ArrowLeft :size="18" />
        </button>
      </div>

      <article class="post-detail">
        <div class="post-header">
          <div class="post-badges">
            <span v-if="post.is_pinned" class="badge badge-pin"><Pin :size="12" /> 置顶</span>
            <span v-if="post.is_essence" class="badge badge-ess"><Award :size="12" /> 精华</span>
          </div>
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="post-meta">
            <span class="meta-author"><User :size="14" /> {{ post.author_name || '匿名' }}</span>
            <span class="meta-divider">·</span>
            <span class="meta-time"><Clock :size="14" /> {{ formatTime(post.create_time) }}</span>
            <span class="meta-divider">·</span>
            <span class="meta-category">{{ post.category_id || '未分类' }}</span>
          </div>
        </div>

        <div class="post-content">
          <pre class="content-text">{{ post.content }}</pre>
        </div>

        <div class="post-stats">
          <span><Eye :size="14" /> {{ post.view_count || 0 }}</span>
          <span><Heart :size="14" /> {{ post.like_count || 0 }}</span>
          <span><MessageCircle :size="14" /> {{ post.comment_count || 0 }}</span>
          <button
            v-if="auth.isLoggedIn && (auth.user?.id === post.user_id || auth.isAdmin)"
            class="btn-ghost-icon btn-danger"
            @click="deletePost"
          >
            <Trash2 :size="14" />
          </button>
        </div>

        <!-- 点赞按钮 -->
        <div class="action-bar">
          <button
            :class="['btn-like', { active: liked }]"
            @click="toggleLike"
          >
            <Heart :size="16" :fill="liked ? 'currentColor' : 'none'" />
            <span>{{ liked ? '已点赞' : '点赞' }}</span>
          </button>
        </div>
      </article>

      <!-- 评论列表 -->
      <section class="comments-section">
        <h3>评论 ({{ comments.length }})</h3>

        <div v-if="commentLoading" class="comments-loading">
          <div class="skeleton-line w-90"></div>
          <div class="skeleton-line w-60"></div>
        </div>

        <div v-else-if="comments.length === 0" class="comments-empty">
          <MessageCircle :size="24" />
          <p>还没有评论，来发表第一条吧</p>
        </div>

        <div v-else class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-card">
            <div class="comment-header">
              <span class="comment-author">{{ comment.author_name || '匿名' }}</span>
              <span class="comment-time">{{ formatTime(comment.create_time) }}</span>
            </div>
            <p class="comment-content">{{ comment.content }}</p>
          </div>
        </div>

        <!-- 发表评论 -->
        <div v-if="auth.isLoggedIn" class="comment-form">
          <textarea
            v-model="commentContent"
            class="comment-input"
            rows="3"
            placeholder="写下你的评论..."
            maxlength="500"
          />
          <div class="comment-form-actions">
            <span class="char-count">{{ commentContent.length }}/500</span>
            <button
              class="btn btn-primary"
              :disabled="!commentContent.trim() || submitting"
              @click="submitComment"
            >
              <Send :size="14" />
              <span>{{ submitting ? '发送中...' : '发表评论' }}</span>
            </button>
          </div>
        </div>
        <div v-else class="login-hint">
          <button class="link" @click="router.push('/login')">登录</button> 后即可评论
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.detail-page {
  max-width: 800px;
  margin: 0 auto;
  animation: slide-up 0.35s var(--ease-out) both;
}

.top-bar {
  margin-bottom: var(--space-4);
}

.btn-ghost-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-ghost-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-ghost-icon.btn-danger:hover {
  background: var(--color-danger-50);
  color: var(--color-danger-600);
  border-color: var(--color-danger-300);
}

.post-detail {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}

.post-badges {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 1px var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.badge-pin { background: var(--color-danger-50); color: var(--color-danger-600); }
.badge-ess { background: var(--color-warning-50); color: var(--color-warning-700); }

.post-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-extrabold);
  color: var(--text-primary);
  margin: 0 0 var(--space-3) 0;
  letter-spacing: -0.01em;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  margin-bottom: var(--space-5);
}

.meta-author, .meta-time { display: inline-flex; align-items: center; gap: 4px; }
.meta-divider { color: var(--color-gray-300); }

.post-content {
  padding: var(--space-5) 0;
  border-top: 1px solid var(--border-light);
  border-bottom: 1px solid var(--border-light);
  margin-bottom: var(--space-4);
}

.content-text {
  font-family: inherit;
  font-size: var(--text-base);
  color: var(--text-primary);
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

.post-stats {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.post-stats span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.action-bar {
  text-align: center;
  margin-top: var(--space-4);
}

.btn-like {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-6);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-light);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-like:hover { border-color: var(--color-danger-300); color: var(--color-danger-600); }
.btn-like.active { background: var(--color-danger-50); border-color: var(--color-danger-400); color: var(--color-danger-600); }

/* 评论 */
.comments-section {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
}

.comments-section h3 {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.comments-empty {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-tertiary);
}

.comments-empty p { font-size: var(--text-sm); margin: var(--space-2) 0 0; }

.comments-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.comment-card {
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  background: var(--bg-page);
  border: 1px solid var(--border-light);
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}

.comment-author { font-size: var(--text-xs); font-weight: var(--font-semibold); color: var(--text-primary); }
.comment-time { font-size: var(--text-xs); color: var(--text-tertiary); }

.comment-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.comment-form {
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--border-light);
}

.comment-input {
  width: 100%;
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  background: var(--bg-page);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-family: inherit;
  resize: vertical;
  line-height: 1.6;
}

.comment-input:focus { outline: none; border-color: var(--color-brand-400); box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12); }

.comment-form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.char-count { font-size: var(--text-xs); color: var(--text-tertiary); }

.login-hint {
  text-align: center;
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--border-light);
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.link { background: none; border: none; color: var(--text-link); cursor: pointer; font-size: inherit; }
.link:hover { text-decoration: underline; }

.btn { display: inline-flex; align-items: center; gap: var(--space-1); padding: var(--space-2) var(--space-4); border-radius: var(--radius-md); font-size: var(--text-sm); font-weight: var(--font-semibold); border: none; cursor: pointer; }
.btn-primary { background: #7c3aed; color: #fff; }
.btn-primary:hover { background: var(--color-brand-700); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-ghost { background: transparent; border: 1px solid var(--border-light); color: var(--text-secondary); }

.empty-state { text-align: center; padding: var(--space-16) var(--space-6); color: var(--text-tertiary); }
.empty-state p { margin: var(--space-3) 0; }

.loading-wrap { padding: var(--space-16); }
.skeleton-line { height: 14px; background: var(--color-gray-200); border-radius: var(--radius-md); margin-bottom: var(--space-3); animation: shimmer 1.5s infinite; }
.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-90 { width: 90%; }

@keyframes shimmer {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .post-detail { padding: var(--space-4); }
  .post-title { font-size: var(--text-xl); }
}

[data-theme="dark"] .skeleton-line { background: var(--color-gray-700); }
</style>
