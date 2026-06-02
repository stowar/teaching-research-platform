/**
 * Vue 应用入口文件
 * 负责创建 Vue 应用实例、注册全局插件、初始化状态并挂载到 DOM
 */
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'     // Pinia：Vue 官方推荐的状态管理库
import App from './App.vue'
import router from './router'            // Vue Router：客户端路由管理
import { useAuthStore } from './stores/auth.js'

// 创建 Vue 应用实例
const app = createApp(App)

// 注册 Pinia 状态管理（必须在 useAuthStore 之前注册）
app.use(createPinia())

// 注册 Vue Router 路由
app.use(router)

/**
 * 恢复用户会话
 * 应用启动时从 localStorage 读取之前保存的 token 和用户信息
 * 这样用户刷新页面后不需要重新登录
 */
const authStore = useAuthStore()
authStore.restoreSession()

// 将应用挂载到 index.html 中的 #app 元素上
app.mount('#app')
