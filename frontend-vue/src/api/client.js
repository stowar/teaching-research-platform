/**
 * 统一 API 客户端封装
 * 使用 axios 创建实例，统一处理请求头、认证和错误响应
 */
import axios from 'axios'

// 后端服务地址：开发用 localhost，生产用相对路径（通过 Nginx 代理）
const BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : ''
const API_PREFIX = '/api/v1'

const api = axios.create({
  baseURL: `${BASE_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 * 每次发送请求前自动从 localStorage 读取 token 并添加到请求头
 * 这样所有需要认证的接口都会自动携带 JWT Token
 */
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * 响应拦截器
 * 统一处理后端返回的错误状态码
 * - 401：token 过期或无效，清除登录状态并跳转到登录页
 * - 403：无权限访问
 * - 其他错误：提取后端返回的错误信息并抛出
 */
api.interceptors.response.use(
  // 成功响应：直接返回 response.data，这样调用方可以直接拿到数据
  (response) => response.data,
  // 错误响应：根据状态码做不同处理
  (error) => {
    const status = error.response?.status
    const data = error.response?.data

    // 401 未授权：token 失效，清除本地存储的登录信息并跳转
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }

    // 403 禁止访问：用户无权限
    if (status === 403) {
      return Promise.reject(new Error('您没有权限访问该页面'))
    }

    // 其他错误：提取后端返回的 msg 或 detail 字段作为错误信息
    const msg = data?.msg || data?.detail || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

export default api
