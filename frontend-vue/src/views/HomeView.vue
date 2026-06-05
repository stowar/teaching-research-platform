<script setup>
/**
 * 已登录首页 HomeView.vue
 * 使用 Design Tokens 和 stagger 动画，打造精致的仪表板体验
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import {
  Hand, LayoutDashboard, Megaphone, ClipboardList, Sparkles,
  MessageSquare, BookOpen, Bot, Users, Mail, Info, ShieldCheck,
  Plus, Trash2, Calendar, User as UserIcon
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

const user = computed(() => auth.user)
const userName = computed(() => user.value?.name || '教师')
const userSchool = computed(() => user.value?.school || '虚拟教研社区')
const userRole = computed(() => user.value?.role || 'user')
const roleLabel = computed(() => userRole.value === 'admin' ? '管理员' : '教师用户')

const notices = ref([
  { title: '高中英语阅读教学研讨会', content: '本周五下午2:00在教学楼A301开展，请各备课组准时参加', time: '2026-06-05 14:00', tag: '活动', tagClass: 'tag-activity' },
  { title: '期中考试质量分析会', content: '各备课组请准备好质量分析材料，周一上午交教务处', time: '2026-06-08 09:00', tag: '紧急', tagClass: 'tag-urgent' },
  { title: '人教版新教材培训', content: '新教材使用培训，请全体英语教师参加', time: '2026-06-10 08:30', tag: '培训', tagClass: 'tag-normal' },
])

const memoItems = ref([
  { id: 1, text: '准备下周英语研讨会PPT', done: false },
  { id: 2, text: '提交期中考试分析报告', done: false },
  { id: 3, text: '参加新教材培训会议', done: true },
])
const memoNextId = ref(4)
const newTask = ref('')

const todoCount = computed(() => memoItems.value.filter(i => !i.done).length)
const urgentCount = computed(() => notices.value.filter(n => n.tag === '紧急').length)

function addTask() {
  const text = newTask.value.trim()
  if (!text) return
  memoItems.value.push({ id: memoNextId.value++, text, done: false })
  newTask.value = ''
}

function deleteTask(id) {
  memoItems.value = memoItems.value.filter(i => i.id !== id)
}

function clearDone() {
  memoItems.value = memoItems.value.filter(i => !i.done)
}

const features = [
  { icon: MessageSquare, title: '教研社区', desc: '发帖讨论、互助答疑、分享教学经验', color: 'var(--color-brand-600)', route: 'community' },
  { icon: BookOpen, title: '教研资料部', desc: '教案课件、真题题库一键下载', color: '#7c3aed', route: 'resources' },
  { icon: Bot, title: 'AI聊天室', desc: '智能教研助手，RAG深度检索', color: '#06b6d4', route: 'ai-chat' },
  { icon: Users, title: '集体备课', desc: '课程共建、协同开发、资源共享', color: '#10b981', route: 'community' },
  { icon: Mail, title: '消息中心', desc: '教师互动交流、通知推送', color: '#f59e0b', route: 'messages' },
  { icon: Info, title: '关于项目', desc: '平台介绍、使用说明、更新记录', color: '#64748b', route: 'about' },
]

const adminFeature = { icon: ShieldCheck, title: '用户管理', desc: '账号权限、信息审核、状态管理', color: '#ef4444', route: 'admin-users' }

const allFeatures = computed(() => {
  if (userRole.value === 'admin') return [...features, adminFeature]
  return features
})
</script>

<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <div class="hero-banner" role="banner">
      <Hand class="hero-icon" :size="56" aria-hidden="true" />
      <h1>欢迎回来，{{ userName }}老师</h1>
      <p class="hero-school">{{ userSchool }}</p>
      <div class="hero-badge">
        <ShieldCheck v-if="userRole === 'admin'" class="icon" :size="14" />
        <UserIcon v-else class="icon" :size="14" />
        {{ roleLabel }}
      </div>
      <div class="hero-glow" aria-hidden="true"></div>
    </div>

    <!-- 工作台 -->
    <div class="section-title">
      <LayoutDashboard class="section-icon" :size="20" aria-hidden="true" />
      <span>工作台</span>
    </div>
    <div class="dashboard-grid">
      <!-- 活动通知 -->
      <div class="widget-box card">
        <div class="widget-header">
          <Megaphone class="widget-icon" :size="18" aria-hidden="true" />
          <span class="widget-title">活动通知</span>
          <span v-if="urgentCount > 0" class="widget-badge badge-urgent">{{ urgentCount }} 条紧急</span>
        </div>
        <div class="widget-body">
          <div v-for="(notice, idx) in notices" :key="notice.title" class="notice-item" :style="{ animationDelay: `${idx * 60}ms` }">
            <div class="notice-title">
              {{ notice.title }}
              <span class="notice-tag" :class="notice.tagClass">{{ notice.tag }}</span>
            </div>
            <div class="notice-content">{{ notice.content }}</div>
            <div class="notice-meta">
              <Calendar class="icon" :size="14" aria-hidden="true" /> {{ notice.time }}
            </div>
          </div>
        </div>
      </div>

      <!-- 备忘录 -->
      <div class="widget-box card">
        <div class="widget-header">
          <ClipboardList class="widget-icon" :size="18" aria-hidden="true" />
          <span class="widget-title">我的备忘录</span>
          <span class="widget-badge badge-todo">{{ todoCount }} 待办</span>
        </div>
        <div class="widget-body">
          <div v-for="item in memoItems" :key="item.id" :class="['memo-item', { 'memo-done': item.done }]">
            <input type="checkbox" v-model="item.done" :aria-label="item.done ? '标记为未完成' : '标记为已完成'" />
            <span class="memo-text">{{ item.text }}</span>
            <button class="memo-del" @click="deleteTask(item.id)" aria-label="删除任务">✕</button>
          </div>
          <div class="memo-add">
            <input v-model="newTask" type="text" placeholder="输入新任务后按回车..." @keyup.enter="addTask" class="form-input" />
            <div class="memo-actions">
              <button class="btn btn-primary btn-sm" @click="addTask"><Plus class="icon" :size="14" /> 添加</button>
              <button class="btn btn-ghost btn-sm" @click="clearDone"><Trash2 class="icon" :size="14" /> 清空已完成</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心功能 -->
    <div class="section-title">
      <Sparkles class="section-icon" :size="20" aria-hidden="true" />
      <span>核心功能</span>
    </div>
    <div class="feature-grid">
      <div v-for="(feat, idx) in allFeatures" :key="feat.title" class="feature-card card card-hover" @click="router.push({ name: feat.route })" :style="{ animationDelay: `${idx * 80}ms` }">
        <div class="accent-bar" :style="{ background: feat.color }"></div>
        <component :is="feat.icon" class="feature-icon" :size="40" aria-hidden="true" />
        <div class="feature-title">{{ feat.title }}</div>
        <div class="feature-desc">{{ feat.desc }}</div>
        <button class="btn btn-ghost btn-sm feature-btn">进入 ▶</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 欢迎横幅 */
.hero-banner {
  position: relative;
  background: linear-gradient(135deg, #312e81 0%, var(--color-brand-700) 40%, #7c3aed 100%);
  border-radius: var(--radius-xl);
  padding: var(--space-10) var(--space-8);
  color: #ffffff;
  margin-bottom: var(--space-8);
  box-shadow: var(--shadow-brand-lg);
  text-align: center;
  overflow: hidden;
  animation: slide-up-enter 0.7s var(--ease-out) both;
}

.hero-icon {
  margin-bottom: var(--space-3);
  display: inline-block;
  animation: bounce-in 0.6s var(--ease-spring) 0.2s both;
}

.hero-banner h1 {
  margin: 0;
  font-size: var(--text-3xl);
  font-weight: var(--font-extrabold);
  letter-spacing: -0.02em;
}

.hero-school {
  margin: var(--space-2) 0 0 0;
  opacity: 0.85;
  font-size: var(--text-lg);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: var(--space-2) var(--space-5);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  margin-top: var(--space-4);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-glow {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
  border-radius: var(--radius-full);
  pointer-events: none;
}

/* 区块标题 */
.section-title {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: var(--space-8) 0 var(--space-4) 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  animation: slide-up-enter 0.5s var(--ease-out) 0.1s both;
}

.section-icon {
  display: inline-flex;
  align-items: center;
}

/* 工作台两栏 */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
  animation: slide-up-enter 0.6s var(--ease-out) 0.2s both;
}

.widget-box {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.widget-header {
  background: var(--bg-hover);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.widget-icon {
  display: inline-flex;
  align-items: center;
}

.widget-title {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  flex: 1;
}

.widget-badge {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-weight: var(--font-bold);
}

.badge-urgent { background: var(--color-danger-100); color: var(--color-danger-700); }
.badge-todo { background: var(--color-brand-100); color: var(--color-brand-700); }

.widget-body {
  padding: var(--space-4) var(--space-5);
  flex: 1;
}

/* 通知项 */
.notice-item {
  padding: var(--space-4);
  margin-bottom: var(--space-3);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border-left: 5px solid var(--color-gray-400);
  transition: all var(--duration-normal) var(--ease-out);
  box-shadow: var(--shadow-sm);
  animation: slide-up-enter 0.5s var(--ease-out) both;
}

.notice-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-md);
  border-left-color: var(--color-gray-600);
}

.notice-title {
  font-weight: var(--font-bold);
  color: var(--text-primary);
  font-size: var(--text-sm);
  margin-bottom: var(--space-1);
}

.notice-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}

.notice-meta {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: var(--space-2);
  font-weight: var(--font-medium);
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
}

.notice-tag {
  display: inline-block;
  font-size: var(--text-xs);
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: var(--space-2);
  font-weight: var(--font-bold);
}

.tag-urgent { background: var(--color-danger-100); color: var(--color-danger-700); }
.tag-normal { background: var(--color-info-100); color: var(--color-info-700); }
.tag-activity { background: var(--color-success-100); color: var(--color-success-700); }

/* 备忘录 */
.memo-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-2);
  border-radius: var(--radius-md);
  background: var(--color-success-50);
  border-left: 4px solid var(--color-success-500);
  transition: all var(--duration-fast) var(--ease-out);
}

.memo-item:hover {
  background: var(--color-success-100);
}

.memo-done {
  opacity: 0.5;
  text-decoration: line-through;
  background: var(--bg-hover);
  border-left-color: var(--color-gray-400);
}

.memo-text {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.memo-del {
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.memo-del:hover {
  color: var(--color-danger-500);
  background: var(--color-danger-50);
}

.memo-add {
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px dashed var(--border-light);
}

.memo-add input {
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
}

.memo-actions {
  display: flex;
  gap: var(--space-2);
}

/* 功能网格 */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  animation: slide-up-enter 0.6s var(--ease-out) 0.3s both;
}

.feature-card {
  padding: var(--space-6) var(--space-4);
  text-align: center;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  animation: slide-up-enter 0.5s var(--ease-out) both;
}

.accent-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.feature-icon {
  margin-bottom: var(--space-3);
  transition: transform var(--duration-normal) var(--ease-spring);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.feature-card:hover .feature-icon {
  transform: scale(1.15);
}

.feature-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.feature-desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}

.feature-btn {
  margin-top: var(--space-4);
}

/* 动画 */
@keyframes slide-up-enter {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes bounce-in {
  0% { opacity: 0; transform: scale(0.3); }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { opacity: 1; transform: scale(1); }
}

/* 响应式 */
@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .feature-grid { grid-template-columns: 1fr; }
  .hero-banner h1 { font-size: var(--text-2xl); }
  .hero-banner { padding: var(--space-8) var(--space-5); }
}
</style>
