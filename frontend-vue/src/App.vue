<script setup>
/**
 * 根组件 App.vue
 * 使用 Vue Router 的 v-slot + Transition 实现全站页面过渡动画
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from './components/AppLayout.vue'

const route = useRoute()
const hideLayout = computed(() => route.meta.hideLayout)
</script>

<template>
  <component :is="hideLayout ? 'div' : AppLayout">
    <!--
      Vue Router v-slot 模式：获取当前匹配的组件
      Transition 包裹 router-view，实现页面切换时的淡入上滑动画
      mode="out-in"：先让旧页面离开，新页面再进入，避免同时渲染两个页面
    -->
    <router-view v-slot="{ Component }">
      <transition name="slide-up" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </component>
</template>
