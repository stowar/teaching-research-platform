<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from './components/AppLayout.vue'
import AchievementToast from './components/chat/AchievementToast.vue'
import { useAchievementToast } from './composables/useAchievementToast.js'

const route = useRoute()
const hideLayout = computed(() => route.meta.hideLayout)
const { current: toastAch } = useAchievementToast()
</script>

<template>
  <component :is="hideLayout ? 'div' : AppLayout">
    <router-view v-slot="{ Component }">
      <transition name="slide-up" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </component>

  <!-- 全局成就弹窗 -->
  <Teleport to="body">
    <Transition name="ach-slide">
      <AchievementToast v-if="toastAch" :achievement="toastAch" />
    </Transition>
  </Teleport>
</template>
