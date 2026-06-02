/**
 * 主题管理组合式函数 useTheme.js
 * 支持亮色/暗色/跟随系统三种模式，持久化保存用户偏好
 * 切换时自动为 html 根元素添加/移除 data-theme="dark" 属性
 */
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'app-theme'

// 检测系统是否偏好暗色模式
const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)')

// 从 localStorage 读取初始主题，默认跟随系统
const currentTheme = ref(localStorage.getItem(STORAGE_KEY) || 'auto')

/**
 * 应用主题到 HTML 根元素
 * @param {'light'|'dark'|'auto'} theme
 */
function applyTheme(theme) {
  const root = document.documentElement
  const isDark = theme === 'dark' || (theme === 'auto' && systemPrefersDark.matches)
  if (isDark) {
    root.setAttribute('data-theme', 'dark')
  } else {
    root.removeAttribute('data-theme')
  }
}

// 初始化：页面加载时立即应用主题，防止闪烁
applyTheme(currentTheme.value)

// 监听系统主题变化（当用户选择"跟随系统"时自动切换）
systemPrefersDark.addEventListener('change', () => {
  if (currentTheme.value === 'auto') {
    applyTheme('auto')
  }
})

// 持久化：每次切换后保存到 localStorage
watch(currentTheme, (val) => {
  localStorage.setItem(STORAGE_KEY, val)
  applyTheme(val)
})

export function useTheme() {
  /**
   * 是否处于暗色模式（考虑自动跟随系统的场景）
   */
  const isDark = computed(() => {
    if (currentTheme.value === 'dark') return true
    if (currentTheme.value === 'light') return false
    return systemPrefersDark.matches
  })

  /**
   * 切换主题：暗色 ↔ 亮色
   * 如果当前是"跟随系统"，则根据当前实际状态决定切到亮色还是暗色
   */
  function toggle() {
    currentTheme.value = isDark.value ? 'light' : 'dark'
  }

  return {
    theme: currentTheme,
    isDark,
    toggle
  }
}
