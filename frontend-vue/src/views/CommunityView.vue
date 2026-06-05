<script setup>
/**
 * 教研社区 CommunityView.vue
 * 帖子列表 + 分类筛选 + 排序 + 搜索 + 分页
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client.js'
import {
  MessageSquare, Eye, Heart, MessageCircle,
  Search, Plus, Filter, Clock, Flame
} from 'lucide-vue-next'

const router = useRouter()

const posts = ref([])
const categories = ref([])
const loading = ref(true)
const error = ref('')

const activeCategory = ref(null)
const sort = ref('new')
const keyword = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const totalPages = ref(1)

async function fetchCategories() {
  try {
    const res = await api.get('/community/categories')
    categories.value = res.data || []
  } catch { /* 分类接口暂不可用，用默认值 */ }
}

async function fetchPosts() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, page_size: pageSize.value, sort: sort.value }
    if (activeCategory.value) params.category_id = activeCategory.value
    if (keyword.value) params.keyword = keyword.value
    const res = await api.get('/community/posts', { params })
    posts.value = res.data || []
    total.value = res.total || posts.value.length
    totalPages.value = Math.max(1, Math.ceil(total.value / pageSize.value))
  } catch (e) {
    error.value = '加载失败，请检查后端服务'
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  fetchPosts()
}

function onCategoryChange(catId) {
  activeCategory.value = catId
  page.value = 1
  fetchPosts()
}

function onSortChange(s) {
  sort.value = s
  page.value = 1
  fetchPosts()
}

function goToDetail(postId) {
  router.push(`/community/${postId}`)
}

function goToCreate() {
  router.push('/community/create')
}

function prevPage() {
  if (page.value > 1) {
    page.value--
    fetchPosts()
  }
}

function nextPage() {
  if (page.value < totalPages.value) {
    page.value++
    fetchPosts()
  }
}

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchCategories()
  fetchPosts()
})
</script>

<template>
  <div class="community-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <MessageSquare class="page-icon" :size="28" />
        <div>
          <h1>教研社区</h1>
          <p>与全国职业院校英语教师交流教学心得</p>
        </div>
      </div>
      <button class="btn btn-primary" @click="goToCreate">
        <Plus :size="16" />
        <span>发帖</span>
      </button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-input-wrapper">
        <Search :size="16" class="search-icon" />
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索帖子标题或内容..."
          class="search-input"
          @keydown.enter="onSearch"
        />
      </div>
    </div>

    <!-- 分类 Tab -->
    <div class="category-tabs">
      <button
        :class="['tab', { active: activeCategory === null }]"
        @click="onCategoryChange(null)"
      >
        全部
      </button>
      <button
        v-for="cat in categories"
        :key="cat.id"
        :class="['tab', { active: activeCategory === cat.id }]"
        @click="onCategoryChange(cat.id)"
      >
        {{ cat.name }}
      </button>
      <!-- 降级：如果分类接口不可用，显示默认分类 -->
      <template v-if="categories.length === 0">
        <button :class="['tab']">教案分享</button>
        <button :class="['tab']">课堂管理</button>
        <button :class="['tab']">考试命题</button>
        <button :class="['tab']">教学反思</button>
      </template>
    </div>

    <!-- 排序切换 -->
    <div class="sort-bar">
      <span class="sort-label">排序：</span>
      <button
        :class="['sort-btn', { active: sort === 'new' }]"
        @click="onSortChange('new')"
      >
        <Clock :size="14" />
        最新
      </button>
      <button
        :class="['sort-btn', { active: sort === 'hot' }]"
        @click="onSortChange('hot')"
      >
        <Flame :size="14" />
        最热
      </button>
    </div>

    <!-- 加载骨架屏 -->
    <div v-if="loading" class="post-list">
      <div v-for="n in 3" :key="n" class="post-card skeleton">
        <div class="skeleton-line w-60"></div>
        <div class="skeleton-line w-90"></div>
        <div class="skeleton-line w-30"></div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="empty-state">
      <MessageSquare :size="48" />
      <p>{{ error }}</p>
      <button class="btn btn-ghost" @click="fetchPosts">重试</button>
    </div>

    <!-- 空列表 -->
    <div v-else-if="posts.length === 0" class="empty-state">
      <MessageSquare :size="48" />
      <p>还没有帖子，来做第一个发帖的人吧</p>
      <button class="btn btn-primary" @click="goToCreate">
        <Plus :size="16" />
        发布第一帖
      </button>
    </div>

    <!-- 帖子列表 -->
    <div v-else class="post-list">
      <article
        v-for="post in posts"
        :key="post.id"
        class="post-card"
        @click="goToDetail(post.id)"
      >
        <div class="post-top">
          <h3 class="post-title">{{ post.title }}</h3>
          <span v-if="post.is_pinned" class="badge badge-pinned">置顶</span>
          <span v-if="post.is_essence" class="badge badge-essence">精华</span>
        </div>
        <p class="post-excerpt">{{ post.content || '暂无内容' }}</p>
        <div class="post-meta">
          <span class="meta-author">{{ post.author_name || '匿名' }}</span>
          <span class="meta-divider">·</span>
          <span class="meta-time">{{ formatTime(post.create_time) }}</span>
          <span class="meta-divider">·</span>
          <span class="meta-stat"><Eye :size="14" /> {{ post.view_count || 0 }}</span>
          <span class="meta-stat"><Heart :size="14" /> {{ post.like_count || 0 }}</span>
          <span class="meta-stat"><MessageCircle :size="14" /> {{ post.comment_count || 0 }}</span>
        </div>
      </article>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button class="btn btn-ghost btn-sm" :disabled="page === 1" @click="prevPage">上一页</button>
      <span class="page-info">{{ page }} / {{ totalPages }}</span>
      <button class="btn btn-ghost btn-sm" :disabled="page >= totalPages" @click="nextPage">下一页</button>
    </div>
  </div>
</template>

<style scoped>
.community-page {
  max-width: 900px;
  margin: 0 auto;
  animation: slide-up 0.4s var(--ease-out) both;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.page-icon {
  color: #7c3aed;
}

.header-left h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1) 0;
}

.header-left p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-primary {
  background: #7c3aed;
  color: #fff;
}

.btn-primary:hover {
  background: var(--color-brand-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
}

.btn-ghost:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 搜索栏 */
.search-bar {
  margin-bottom: var(--space-4);
}

.search-input-wrapper {
  position: relative;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-input {
  width: 100%;
  padding: var(--space-2) var(--space-4) var(--space-2) 40px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: var(--text-sm);
  line-height: 1.5;
  transition: border-color var(--duration-fast) var(--ease-out);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-brand-400);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

/* 分类 Tab */
.category-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}

.tab {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.tab:hover {
  border-color: var(--color-brand-400);
  color: #7c3aed;
}

.tab.active {
  background: #7c3aed;
  border-color: #7c3aed;
  color: #fff;
}

/* 排序 */
.sort-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}

.sort-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.sort-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.sort-btn:hover {
  color: var(--text-primary);
}

.sort-btn.active {
  background: var(--color-brand-50);
  color: #7c3aed;
  font-weight: var(--font-semibold);
}

/* 帖子列表 */
.post-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.post-card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
}

.post-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-brand-300);
  transform: translateY(-2px);
}

.post-top {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.post-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}

.badge {
  padding: 1px var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.badge-pinned {
  background: var(--color-danger-50);
  color: var(--color-danger-600);
}

.badge-essence {
  background: var(--color-warning-50);
  color: var(--color-warning-700);
}

.post-excerpt {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--space-3) 0;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.meta-author {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.meta-divider {
  color: var(--color-gray-300);
  font-size: var(--text-xs);
}

.meta-time {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.meta-stat {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-16) var(--space-6);
  color: var(--text-tertiary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.empty-state p {
  margin: 0;
  font-size: var(--text-sm);
}

/* 骨架屏 */
.post-card.skeleton {
  cursor: default;
  pointer-events: none;
}

.skeleton-line {
  height: 14px;
  background: var(--color-gray-200);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-2);
  animation: shimmer 1.5s infinite;
}

.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-90 { width: 90%; }
.skeleton-line.w-30 { width: 30%; }

@keyframes shimmer {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  margin-top: var(--space-6);
  padding-bottom: var(--space-8);
}

.page-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}

.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-3);
  }

  .search-input-wrapper {
    max-width: 100%;
  }

  .post-card {
    padding: var(--space-4);
  }
}

/* 暗黑模式 */
[data-theme="dark"] .skeleton-line {
  background: var(--color-gray-700);
}

[data-theme="dark"] .sort-btn.active {
  background: rgba(99, 102, 241, 0.15);
  color: var(--color-brand-300);
}

[data-theme="dark"] .search-input:focus {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}
</style>
