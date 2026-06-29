<script setup>
/**
 * 用户管理 AdminView.vue（仅管理员可见）
 * 展示所有用户的列表信息，支持禁用/启用用户操作
 * 使用 Design Tokens、加载骨架屏、空状态插画，提升视觉品质
 */
import { ref, onMounted } from 'vue'
import api from '@/api/client.js'
import { ShieldCheck, RefreshCw, Inbox, Unlock } from 'lucide-vue-next'

const users = ref([])
const loading = ref(false)
const error = ref('')
const message = ref('')

async function fetchUsers() {
  loading.value = true
  error.value = ''
  message.value = ''
  try {
    const res = await api.get('/admin/')
    users.value = res.data || res || []
  } catch (e) {
    error.value = e.message || '获取用户列表失败'
  } finally {
    loading.value = false
  }
}

async function disableUser(id) {
  if (!confirm('确定要禁用该用户吗？')) return
  try {
    await api.delete(`/admin/${id}`)
    message.value = '已禁用用户'
    await fetchUsers()
  } catch (e) {
    error.value = e.message || '操作失败'
  }
}

async function enableUser(id) {
  try {
    await api.put(`/admin/${id}/enable`)
    message.value = '已启用用户'
    await fetchUsers()
  } catch (e) {
    error.value = e.message || '操作失败'
  }
}

async function unlockQuota(id) {
  if (!confirm('解锁该用户本日配额？')) return
  try {
    await api.post(`/ai-chat/admin/unlock-user`, null, { params: { user_id: id } })
    message.value = `已解锁用户 ${id} 的本日配额`
  } catch (e) {
    error.value = e.message || '操作失败'
  }
}

onMounted(fetchUsers)
</script>

<template>
  <div class="admin-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <ShieldCheck class="page-icon" :size="32" aria-hidden="true" />
      <h1>用户管理</h1>
    </div>

    <!-- 提示信息区域 -->
    <div v-if="error" class="alert alert-error" role="alert">{{ error }}</div>
    <div v-if="message" class="alert alert-success" role="status">{{ message }}</div>

    <div class="admin-card card">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-info">
          共 <strong>{{ users.length }}</strong> 位用户
        </div>
        <button class="btn btn-primary btn-sm press-feedback" @click="fetchUsers" :disabled="loading">
          <span v-if="loading" class="spinner spinner-sm" aria-hidden="true"></span>
          <span v-else><RefreshCw class="icon" :size="14" /></span>
          <span>{{ loading ? '加载中...' : '刷新列表' }}</span>
        </button>
      </div>

      <!-- 加载骨架屏 -->
      <div v-if="loading && users.length === 0" class="skeleton-table">
        <div v-for="n in 6" :key="n" class="skeleton-row">
          <div class="skeleton-cell" style="width: 40px"></div>
          <div class="skeleton-cell" style="width: 100px"></div>
          <div class="skeleton-cell" style="width: 80px"></div>
          <div class="skeleton-cell" style="width: 120px"></div>
          <div class="skeleton-cell" style="width: 80px"></div>
          <div class="skeleton-cell" style="width: 60px"></div>
          <div class="skeleton-cell" style="width: 60px"></div>
          <div class="skeleton-cell" style="width: 70px"></div>
        </div>
      </div>

      <!-- 用户数据表格 -->
      <div v-else-if="users.length > 0" class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>手机号</th>
              <th>姓名</th>
              <th>学校</th>
              <th>职称</th>
              <th>角色</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(u, idx) in users" :key="u.id" :style="{ animationDelay: `${idx * 40}ms` }">
              <td>{{ u.id }}</td>
              <td>{{ u.phone }}</td>
              <td>{{ u.name }}</td>
              <td>{{ u.school || '-' }}</td>
              <td>{{ u.title || '-' }}</td>
              <td>
                <span :class="['role-badge', u.role === 'admin' ? 'role-admin' : 'role-user']">
                  {{ u.role === 'admin' ? '管理员' : '教师' }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', u.status === 1 ? 'status-active' : 'status-disabled']">
                  {{ u.status === 1 ? '正常' : '已禁用' }}
                </span>
              </td>
              <td>
                <button
                  v-if="u.status === 1"
                  class="btn btn-sm btn-danger press-feedback"
                  @click="disableUser(u.id)"
                >
                  禁用
                </button>
                <button
                  v-else
                  class="btn btn-sm btn-success press-feedback"
                  @click="enableUser(u.id)"
                >
                  启用
                </button>
                <button
                  v-if="u.role !== 'admin'"
                  class="btn btn-sm btn-outline press-feedback"
                  style="margin-left: 6px"
                  @click="unlockQuota(u.id)"
                  title="解锁本日AI配额"
                >
                  <Unlock :size="12" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading && users.length === 0" class="empty-state">
        <Inbox class="empty-icon" :size="48" aria-hidden="true" />
        <div class="empty-title">暂无用户数据</div>
        <div class="empty-desc">当前系统中还没有注册用户</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-page {
  animation: slide-up-enter 0.5s var(--ease-out) both;
}

.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.page-icon {
  display: inline-flex;
  align-items: center;
}

.page-header h1 {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

.admin-card {
  padding: var(--space-6);
  animation: slide-up-enter 0.6s var(--ease-out) 0.1s both;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.toolbar-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.toolbar-info strong {
  color: var(--text-primary);
}

/* 表格容器：移动端横向滚动 */
.table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
  min-width: 700px;
}

.data-table th,
.data-table td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.data-table th {
  font-weight: var(--font-bold);
  color: var(--text-secondary);
  background: var(--bg-hover);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.data-table tbody tr {
  transition: background var(--duration-fast) var(--ease-out);
  animation: slide-up-enter 0.4s var(--ease-out) both;
}

.data-table tbody tr:hover td {
  background: var(--bg-hover);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

/* 角色和状态标签 */
.role-badge,
.status-badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}

.role-admin {
  background: var(--color-warning-100);
  color: var(--color-warning-700);
}

.role-user {
  background: var(--color-brand-100);
  color: var(--color-brand-700);
}

.status-active {
  background: var(--color-success-100);
  color: var(--color-success-700);
}

.status-disabled {
  background: var(--color-danger-100);
  color: var(--color-danger-700);
}

/* 骨架屏 */
.skeleton-table {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.skeleton-row {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.skeleton-cell {
  height: 16px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--bg-hover) 25%, var(--bg-card) 50%, var(--bg-hover) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-12) var(--space-6);
  color: var(--text-secondary);
}

.empty-icon {
  margin-bottom: var(--space-4);
  opacity: 0.6;
  display: inline-flex;
  align-items: center;
}

.empty-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.empty-desc {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

@keyframes slide-up-enter {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
