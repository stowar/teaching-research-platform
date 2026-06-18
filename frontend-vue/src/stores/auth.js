/**
 * 用户认证状态管理（Pinia Store）
 * 使用 Vue 3 Composition API 风格定义 Store
 * 负责管理登录状态、用户信息、token 的持久化存储
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/api/client.js'

// 定义 auth store，第一个参数 'auth' 是 store 的唯一标识
export const useAuthStore = defineStore('auth', () => {
  /**
   * 响应式状态（State）
   * token：JWT 令牌，从 localStorage 初始化（页面刷新后自动恢复）
   * user：当前登录用户信息对象
   */
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  /**
   * 计算属性（Getters）
   * isLoggedIn：根据 token 是否存在判断用户是否已登录
   * isAdmin：根据用户角色判断是否为管理员
   */
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  /**
   * 用户登录
   * @param {string} phone - 手机号
   * @param {string} password - 密码
   * 登录成功后保存 token 和用户信息到 localStorage，实现持久化登录
   */
  async function login(phone, password) {
    const res = await api.post('/auth/login', { phone, password })
    if (res.code === 200) {
      token.value = res.data.access_token
      user.value = res.data.user
      localStorage.setItem('token', res.data.access_token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
    }
    return res
  }

  /**
   * 用户注册
   * @param {Object} data - 注册表单数据（phone, password, name, school, title）
   */
  async function register(data) {
    return api.post('/auth/register', data)
  }

  /**
   * 获取当前登录用户信息
   * 从后端 /users/me 接口拉取最新用户信息并更新本地状态
   */
  async function fetchUser() {
    const res = await api.get('/users/me')
    // 后端可能直接返回用户对象或包裹在 {code, data} 中
    if (res.code === 200 || res.id) {
      user.value = res.code === 200 ? res.data : res
      localStorage.setItem('user', JSON.stringify(user.value))
    }
    return res
  }

  /**
   * 更新当前用户个人资料
   * @param {Object} data - 需要更新的字段（name, school, title）
   */
  async function updateProfile(data) {
    const res = await api.put('/users/me', data)
    if (res.code === 200 || res.id) {
      user.value = res.code === 200 ? res.data : res
      localStorage.setItem('user', JSON.stringify(user.value))
    }
    return res
  }

  /**
   * 修改当前用户密码
   * @param {string} oldPassword - 旧密码
   * @param {string} newPassword - 新密码
   */
  async function updatePassword(oldPassword, newPassword) {
    return api.put('/users/password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  }

  /**
   * 注销登录
   * 清除所有本地存储的认证信息，状态恢复为未登录
   */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  /**
   * 恢复会话
   * 应用启动时从 localStorage 恢复 token 和用户信息
   * 这样用户刷新页面后不需要重新登录
   */
  function restoreSession() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (savedToken) {
      token.value = savedToken
      try {
        user.value = JSON.parse(savedUser)
      } catch {
        // 如果存储的用户信息不是有效 JSON，则重置为 null
        user.value = null
      }
    }
  }

  // 暴露给组件使用的状态和方法
  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    login,
    register,
    fetchUser,
    updateProfile,
    updatePassword,
    logout,
    restoreSession
  }
})
