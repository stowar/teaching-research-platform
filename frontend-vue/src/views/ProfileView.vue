<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { User as UserIcon, Pencil, Lock, Eye, EyeOff, Loader } from 'lucide-vue-next'

const auth = useAuthStore()
const user = computed(() => auth.user)

const editing = ref(false)
const error = ref('')
const success = ref('')
const loading = ref(false)
const form = ref({ name: '', school: '', title: '' })

function startEdit() {
  form.value = { name: user.value?.name || '', school: user.value?.school || '', title: user.value?.title || '' }
  editing.value = true; error.value = ''; success.value = ''
}
function cancelEdit() { editing.value = false; error.value = '' }
async function saveProfile() {
  error.value = ''; success.value = ''; loading.value = true
  try {
    const payload = {}
    if (form.value.name) payload.name = form.value.name
    if (form.value.school) payload.school = form.value.school
    if (form.value.title) payload.title = form.value.title
    await auth.updateProfile(payload)
    success.value = '保存成功'; editing.value = false
  } catch (e) { error.value = e.message || '保存失败' }
  finally { loading.value = false }
}

const pwdForm = ref({ old: '', new: '', confirm: '' })
const pwdError = ref('')
const pwdSuccess = ref('')
const pwdLoading = ref(false)
const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)

async function changePassword() {
  pwdError.value = ''; pwdSuccess.value = ''
  if (!pwdForm.value.old || !pwdForm.value.new) { pwdError.value = '请输入旧密码和新密码'; return }
  if (pwdForm.value.new.length < 6) { pwdError.value = '新密码至少6位'; return }
  if (pwdForm.value.new !== pwdForm.value.confirm) { pwdError.value = '两次输入的新密码不一致'; return }
  pwdLoading.value = true
  try {
    await auth.updatePassword(pwdForm.value.old, pwdForm.value.new)
    pwdSuccess.value = '密码修改成功'
    pwdForm.value = { old: '', new: '', confirm: '' }
  } catch (e) { pwdError.value = e.message || '密码修改失败' }
  finally { pwdLoading.value = false }
}
</script>

<template>
  <div class="profile-page">
    <div class="page-header">
      <UserIcon class="page-icon" :size="32" />
      <h1>个人中心</h1>
    </div>

    <!-- 基本信息 -->
    <div class="profile-card card">
      <div class="card-header">
        <Pencil class="card-icon" :size="20" />
        <h2>基本信息</h2>
      </div>
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
          <button class="btn btn-primary" @click="startEdit"><Pencil :size="14" /> 编辑资料</button>
        </div>
      </div>
      <form v-else @submit.prevent="saveProfile" class="edit-form">
        <div class="form-group">
          <label>姓名</label>
          <input v-model="form.name" class="form-input" placeholder="请输入姓名" />
        </div>
        <div class="form-group">
          <label>学校</label>
          <input v-model="form.school" class="form-input" placeholder="请输入学校" />
        </div>
        <div class="form-group">
          <label>职称</label>
          <input v-model="form.title" class="form-input" placeholder="请输入职称" />
        </div>
        <div v-if="error" class="alert alert-error" role="alert">{{ error }}</div>
        <div v-if="success" class="alert alert-success" role="status">{{ success }}</div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? '保存中...' : '保存' }}</button>
          <button type="button" class="btn btn-ghost" @click="cancelEdit">取消</button>
        </div>
      </form>
    </div>

    <!-- 修改密码 -->
    <div class="profile-card card">
      <div class="card-header">
        <Lock class="card-icon" :size="20" />
        <h2>修改密码</h2>
      </div>
      <form @submit.prevent="changePassword" class="edit-form">
        <div class="form-group">
          <label>旧密码</label>
          <div class="pwd-wrap">
            <input v-model="pwdForm.old" :type="showOld ? 'text' : 'password'" class="form-input" placeholder="请输入旧密码" />
            <button type="button" class="pw-eye" @click="showOld = !showOld" tabindex="-1"><EyeOff v-if="showOld" :size="18" /><Eye v-else :size="18" /></button>
          </div>
        </div>
        <div class="form-group">
          <label>新密码</label>
          <div class="pwd-wrap">
            <input v-model="pwdForm.new" :type="showNew ? 'text' : 'password'" class="form-input" placeholder="至少6位" />
            <button type="button" class="pw-eye" @click="showNew = !showNew" tabindex="-1"><EyeOff v-if="showNew" :size="18" /><Eye v-else :size="18" /></button>
          </div>
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <div class="pwd-wrap">
            <input v-model="pwdForm.confirm" :type="showConfirm ? 'text' : 'password'" class="form-input" placeholder="请再次输入新密码" />
            <button type="button" class="pw-eye" @click="showConfirm = !showConfirm" tabindex="-1"><EyeOff v-if="showConfirm" :size="18" /><Eye v-else :size="18" /></button>
          </div>
        </div>
        <div v-if="pwdError" class="alert alert-error" role="alert">{{ pwdError }}</div>
        <div v-if="pwdSuccess" class="alert alert-success" role="status">{{ pwdSuccess }}</div>
        <button type="submit" class="btn btn-primary" :disabled="pwdLoading">
          <Loader v-if="pwdLoading" class="icon-spin" :size="16" /> {{ pwdLoading ? '修改中...' : '修改密码' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.profile-page { animation: slide-up-enter 0.5s var(--ease-out) both; }
.page-header { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-6); }
.page-header h1 { font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--text-primary); margin: 0; }
.page-icon { display: inline-flex; align-items: center; }

.profile-card { margin-bottom: var(--space-6); padding: var(--space-6); animation: slide-up-enter 0.6s var(--ease-out) both; }
.profile-card:nth-child(2) { animation-delay: 0.1s; }
.profile-card:nth-child(3) { animation-delay: 0.2s; }

.card-header { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-5); padding-bottom: var(--space-4); border-bottom: 1px solid var(--border-light); }
.card-icon { display: inline-flex; align-items: center; }
.card-header h2 { font-size: var(--text-lg); font-weight: var(--font-bold); color: var(--text-primary); margin: 0; }

.info-list { display: flex; flex-direction: column; gap: var(--space-1); }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: var(--space-3) var(--space-4); border-radius: var(--radius-md); transition: background var(--duration-fast) var(--ease-out); }
.info-row:hover { background: var(--bg-hover); }
.info-label { color: var(--text-secondary); font-size: var(--text-sm); font-weight: var(--font-medium); }
.info-value { color: var(--text-primary); font-weight: var(--font-semibold); font-size: var(--text-sm); }
.role-tag { display: inline-block; padding: var(--space-1) var(--space-3); border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: var(--font-bold); }
.role-admin { background: var(--color-warning-100); color: var(--color-warning-700); }
.role-user { background: var(--color-brand-100); color: var(--color-brand-700); }
.info-actions { margin-top: var(--space-4); padding-top: var(--space-4); border-top: 1px solid var(--border-light); }

.edit-form { max-width: 400px; }
.form-group { margin-bottom: var(--space-4); }
.form-group label { display: block; margin-bottom: var(--space-2); font-size: var(--text-sm); font-weight: var(--font-semibold); color: var(--text-primary); }
.pwd-wrap { position: relative; }
.pw-eye { position: absolute; right: var(--space-3); top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-tertiary); cursor: pointer; padding: 0; display: flex; transition: color var(--duration-fast) var(--ease-out); }
.pw-eye:hover { color: var(--text-primary); }
.icon-spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.form-actions { display: flex; gap: var(--space-3); margin-top: var(--space-2); }

@keyframes slide-up-enter { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) { .info-row { flex-direction: column; align-items: flex-start; gap: var(--space-1); } }
</style>
