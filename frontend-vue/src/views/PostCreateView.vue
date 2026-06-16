<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/client.js'
import { Send, BookOpen, ArrowLeft } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const editPostId = computed(() => route.params.postId ? Number(route.params.postId) : null)
const isEdit = computed(() => !!editPostId.value)
const draftSaved = ref(false)
const DRAFT_KEY = 'post-draft'

const title = ref('')
const content = ref('')
const categoryId = ref(1)
const isAnonymous = ref(false)
const defaultCategories = [
  { id: 1, name: '教案分享' }, { id: 2, name: '课堂管理' },
  { id: 3, name: '考试命题' }, { id: 4, name: '教学反思' },
  { id: 5, name: '职业英语' }, { id: 6, name: 'AI工具' },
]
const categories = ref([])
const categoryOptions = computed(() => categories.value.length ? categories.value : defaultCategories)
const loading = ref(false)
const error = ref('')

async function fetchCategories() {
  try {
    const res = await api.get('/community/categories')
    // 按 id 去重，防止种子数据重复插入导致下拉框选项重复
    const seen = new Map()
    for (const c of (res.data || [])) seen.set(c.id, c)
    categories.value = [...seen.values()]
  } catch { /* ignore */ }
}

async function fetchPost() {
  if (!isEdit.value) return
  loading.value = true
  try {
    const res = await api.get(`/community/posts/${editPostId.value}`)
    const p = res.data
    title.value = p.title
    content.value = p.content
    categoryId.value = p.category_id
    isAnonymous.value = !!p.is_anonymous
  } catch { /* edit mode fetch fail, fallback to create */ }
  finally { loading.value = false }
}

async function submit() {
  if (!title.value.trim() || !content.value.trim() || loading.value) return
  loading.value = true
  error.value = ''
  const body = {
    title: title.value.trim(),
    content: content.value.trim(),
    category_id: categoryId.value,
    is_anonymous: isAnonymous.value ? 1 : 0
  }
  try {
    if (isEdit.value) {
      await api.put(`/community/posts/${editPostId.value}`, body)
    } else {
      await api.post('/community/posts', body)
    }
    clearDraft()
    router.push('/community')
  } catch (e) {
    error.value = e.message || (isEdit.value ? '编辑失败' : '发布失败')
  } finally {
    loading.value = false
  }
}

// 草稿：自动保存
watch([title, content], () => {
  if (!isEdit.value && (title.value || content.value)) {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ title: title.value, content: content.value }))
    draftSaved.value = true
    setTimeout(() => draftSaved.value = false, 2000)
  }
}, { deep: true })

function loadDraft() {
  if (isEdit.value) return
  try {
    const raw = localStorage.getItem(DRAFT_KEY)
    if (raw) {
      const d = JSON.parse(raw)
      if (d.title) title.value = d.title
      if (d.content) content.value = d.content
      return true
    }
  } catch { return false }
  return false
}

function clearDraft() {
  localStorage.removeItem(DRAFT_KEY)
}

onMounted(() => {
  fetchCategories()
  if (isEdit.value) {
    fetchPost()
  } else {
    loadDraft()
  }
})
</script>

<template>
  <div class="create-page">
    <div class="top-bar">
      <button class="btn-ghost-icon" @click="router.push('/community')">
        <ArrowLeft :size="18" />
      </button>
      <h1>{{ isEdit ? '编辑帖子' : '发布新帖' }}</h1>
    </div>

    <form class="create-form" @submit.prevent="submit">
      <div class="form-group">
        <label>帖子标题</label>
        <input
          v-model="title"
          type="text"
          maxlength="200"
          placeholder="请输入帖子标题（5-200字）"
          class="form-input"
          required
        />
        <span class="char-hint">{{ title.length }}/200</span>
      </div>

      <div class="form-group">
        <label>分类</label>
        <select v-model="categoryId" class="form-input">
          <option v-for="cat in categoryOptions" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>帖子内容</label>
        <textarea
          v-model="content"
          rows="10"
          maxlength="5000"
          placeholder="写下你的教学心得、问题或经验...&#10;&#10;支持 Markdown：**加粗** | # 标题 | - 列表 | `代码`"
          class="form-input"
          required
        />
        <span class="char-hint">{{ content.length }}/5000</span>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="isAnonymous" />
          <span>匿名发布（不会显示您的姓名）</span>
        </label>
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <div class="form-actions">
        <span v-if="draftSaved" class="draft-hint">草稿已保存</span>
        <button type="button" class="btn btn-ghost" @click="router.push('/community')">取消</button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="!title.trim() || !content.trim() || loading"
        >
          <Send :size="14" />
          <span>{{ loading ? (isEdit ? '保存中...' : '发布中...') : (isEdit ? '保存修改' : '发布帖子') }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.create-page {
  max-width: 700px;
  margin: 0 auto;
  animation: slide-up 0.4s var(--ease-out) both;
}

.top-bar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.top-bar h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

.btn-ghost-icon {
  width: 36px; height: 36px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center; justify-content: center;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-ghost-icon:hover { background: var(--bg-hover); color: var(--text-primary); }

.create-form {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.form-input {
  width: 100%;
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  background: var(--bg-page);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-family: inherit;
  line-height: 1.6;
  transition: border-color var(--duration-fast) var(--ease-out);
}

select.form-input { cursor: pointer; }

.form-input:focus {
  outline: none;
  border-color: var(--color-brand-400);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
}

textarea.form-input { resize: vertical; }

.char-hint {
  display: block;
  text-align: right;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: var(--space-1);
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  cursor: pointer;
}
.checkbox-label input[type=\"checkbox\"] {
  width: 16px;
  height: 16px;
  accent-color: var(--color-brand-600);
  cursor: pointer;
}

.alert-error {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: var(--color-danger-50);
  color: var(--color-danger-700);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-light);
}
.draft-hint {
  font-size: var(--text-xs);
  color: var(--color-success-600);
  margin-right: auto;
  animation: fade-in 0.3s var(--ease-out);
}
@keyframes fade-in { from { opacity: 0 } to { opacity: 1 } }

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-5);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-primary { background: var(--color-brand-600); color: #fff; }
.btn-primary:hover { background: var(--color-brand-700); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-ghost { background: transparent; border: 1px solid var(--border-light); color: var(--text-secondary); }
.btn-ghost:hover { background: var(--bg-hover); }

@keyframes slide-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .create-form { padding: var(--space-4); }
}
</style>
