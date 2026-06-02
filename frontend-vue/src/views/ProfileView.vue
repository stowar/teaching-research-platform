<script setup>
/**
 * 个人中心 ProfileView.vue
 * 展示和编辑当前用户的个人信息，以及修改密码功能
 * 使用 Design Tokens 和 lucide 图标库保证视觉一致性
 */
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { User as UserIcon, Pencil, Lock } from 'lucide-vue-next'

const auth = useAuthStore()

const user = computed(() => auth.user)

const editing = ref(false)
const error = ref('')
const success = ref('')
const loading = ref(false)

const form = ref({
  name: '',
  school: '',
  title: ''
})

function startEdit() {
  form.value = {
    name: user.value?.name || '',
    school: user.value?.school || '',
    title: user.value?.title || ''
  }
  editing.value = true
  error.value = ''
  success.value = ''
}

function cancelEdit() {
  editing.value = false
  error.value = ''
}

async function saveProfile() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const payload = {}
    if (form.value.name) payload.name = form.value.name
    if (form.value.school) payload.school = form.value.school
    if (form.value.title) payload.title = form.value.title

    await auth.updateProfile(payload)
    success.value = '保存成功'
    editing.value = false
  } catch (e) {
    error.value = e.message || '保存失败'
  } finally {
    loading.value = false
  }
}

const pwdForm = ref({ old: '', new: '', confirm: '' })
const pwdError = ref('')
const pwdSuccess = ref('')
const pwdLoading = ref(false)

async function changePassword() {
  pwdError.value = ''
  pwdSuccess.value = ''

  if (!pwdForm.value.old || !pwdForm.value.new) {
    pwdError.value = '请输入旧密码和新密码'
    return
  }
  if (pwdForm.value.new !== pwdForm.value.confirm) {
    pwdError.value = '两次输入的新密码不一致'
    return
  }

  pwdLoading.value = true
  try {
    await auth.updatePassword(pwdForm.value.old, pwdForm.value.new)
    pwdSuccess.value = '密码修改成功'
    pwdForm.value = { old: '', new: '', confirm: '' }
  } catch (e) {
    pwdError.value = e.message || '密码修改失败'
  } finally {
    pwdLoading.value = false
  }
}
</script>

<template>
  <div class="profile-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <UserIcon class="page-icon" :size="32" aria-hidden="true" />
      <h1>个人中心</h1>
    </div>

    <!-- 基本信息卡片 -->
    <div class="profile-card card">
      <div class="card-header">
        <Pencil class="card-icon" :size="20" aria-hidden="true" />
        <h2>基本信息</h2>
      </div>

      <!-- 只读模式：展示用户信息列表 -->
      <div v-if="!editing" class="info-list">
        <div class="info-row"><span class="info-label">手机号</span><span class="info-value">{{ user?.phone }}</span></div>
        <div class="info-row"><span class="info-label">姓名</span><span class="info-value">{{ user?.name || '-' }}</span></div>
        <div class="info-row"><span class="info-label">学校</span><span class="info-value">{{ user?.school || '-' }}</span></div>
        <div class="info-row"><span class="info-label">职称</span><span class="info-value">{{ user?.title || '-' }}</span></div>
        <div class="info-row">
          <span class="info-label">角色</span>
          <span class="info-value"><span :class="['role-tag', user?.role === 'admin' ? 'role-admin' : 'role-user']">{{ user?.role === 'admin' ? '管理员' : '教师' }}</span></span>
        </div>
        <div class="info-actions">
          <button class="btn btn-primary press-feedback" @click="startEdit">
            <Pencil class="icon" :size="14" /> 编辑资料
          </button>
        </div>
      </div>

      <!-- 编辑模式：显示表单 -->
      <form v-else @submit.prevent="saveProfile" class="edit-form">
        <div class="form-group">
          <label for="profile-name">姓名</label>
          <input id="profile-name" v-model="form.name" type="text" class="form-input" placeholder="请输入姓名" />
        </div>
        <div class="form-group">
          <label for="profile-school">学校</label>
          <input id="profile-school" v-model="form.school" type="text" class="form-input" placeholder="请输入学校" />
        </div>
        <div class="form-group">
          <label for="profile-title">职称</label>
          <input id="profile-title" v-model="form.title" type="text" class="form-input" placeholder="请输入职称" />
        </div>
        <div v-if="error" class="alert alert-error" role="alert">{{ error }}</div>
        <div v-if="success" class="alert alert-success" role="status">{{ success }}</div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary press-feedback" :disabled="loading">
            <span v-if="loading" class="spinner spinner-sm" aria-hidden="true"></span>
            <span>{{ loading ? '保存中...' : '保存' }}</span>
          </button>
          <button type="button" class="btn btn-ghost" @click="cancelEdit">取消</button>
        </div>
      </form>
    </div>

    <!-- 修改密码卡片 -->
    <div class="profile-card card">
      <div class="card-header">
        <Lock class="card-icon" :size="20" aria-hidden="true" />
        <h2>修改密码</h2>
      </div>

      <form @submit.prevent="changePassword" class="edit-form">
        <div class="form-group">
          <label for="pwd-old">旧密码</label>
          <input id="pwd-old" v-model="pwdForm.old" type="password" class="form-input" placeholder="请输入旧密码" autocomplete="current-password" />
        </div>
        <div class="form-group">
          <label for="pwd-new">新密码</label>
          <input id="pwd-new" v-model="pwdForm.new" type="password" class="form-input" placeholder="请输入新密码" autocomplete="new-password" />
        </div>
        <div class="form-group">
          <label for="pwd-confirm">确认新密码</label>
          <input id="pwd-confirm" v-model="pwdForm.confirm" type="password" class="form-input" placeholder="请再次输入新密码" autocomplete="new-password" />
        </div>
        <div v-if="pwdError" class="alert alert-error" role="alert">{{ pwdError }}</div>
        <div v-if="pwdSuccess" class="alert alert-success" role="status">{{ pwdSuccess }}</div>
        <button type="submit" class="btn btn-primary press-feedback" :disabled="pwdLoading">
          <span v-if="pwdLoading" class="spinner spinner-sm" aria-hidden="true"></span>
          <span>{{ pwdLoading ? '修改中...' : '修改密码' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  animation: slide-up-enter 0.5s var(--ease-out) both;
}

.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
  animation: slide-up-enter 0.5s var(--ease-out) both;
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

.profile-card {
  margin-bottom: var(--space-6);
  padding: var(--space-6);
  animation: slide-up-enter 0.6s var(--ease-out) both;
}

.profile-card:nth-child(2) {
  animation-delay: 0.1s;
}

.profile-card:nth-child(3) {
  animation-delay: 0.2s;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.card-icon {
  display: inline-flex;
  align-items: center;
}

.card-header h2 {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

/* 信息列表 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast) var(--ease-out);
}

.info-row:hover {
  background: var(--bg-hover);
}

.info-label {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.info-value {
  color: var(--text-primary);
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}

.role-tag {
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

.info-actions {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-light);
}

.edit-form {
  max-width: 480px;
}

.form-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

@keyframes slide-up-enter {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-1);
  }
}
</style>
