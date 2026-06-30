import { ref } from 'vue'

const current = ref(null)
let _timer = null

export function useAchievementToast() {
  function show(ach) {
    current.value = ach
    clearTimeout(_timer)
    _timer = setTimeout(() => { current.value = null }, 8000)
  }

  return { current, show }
}
