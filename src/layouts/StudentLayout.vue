<script setup lang="ts">
import { onMounted } from 'vue'
import {
  Home,
  ClipboardList,
  Timer,
  CalendarDays,
  Bell,
  User,
  Activity,
} from 'lucide-vue-next'
import SideMenu from '@/components/common/SideMenu.vue'
import TopBar from '@/components/common/TopBar.vue'
import { useAuthStore } from '@/stores/auth'
import { useNoticeStore } from '@/stores/notice'
import { useEventStore } from '@/stores/event'
import { useRegistrationStore } from '@/stores/registration'
import { useScoreStore } from '@/stores/score'

const auth = useAuthStore()
const notice = useNoticeStore()
const eventStore = useEventStore()
const regStore = useRegistrationStore()
const scoreStore = useScoreStore()

const menuItems = [
  { path: '/student/home', label: '首页', icon: Home },
  { path: '/student/register', label: '项目报名', icon: ClipboardList },
  { path: '/student/scores', label: '成绩查询', icon: Timer },
  { path: '/student/schedule', label: '我的赛程', icon: CalendarDays },
  { path: '/student/notices', label: '公告通知', icon: Bell },
  { path: '/student/profile', label: '个人中心', icon: User },
]

onMounted(async () => {
  await Promise.all([
    notice.fetchAll(),
    eventStore.fetchAll(),
    regStore.fetchAll(),
    scoreStore.fetchAll(),
  ])
  auth.refresh()
})
</script>

<template>
  <div class="layout">
    <SideMenu :items="menuItems" brand="学生参赛端" :brand-icon="Activity" accent="#F97316" />
    <div class="main">
      <TopBar />
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="page-slide-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped lang="scss">
.layout { display: flex; min-height: 100vh; background: #F4F7FB; }
.main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.content {
  flex: 1;
  padding: 24px 28px 40px;
  min-width: 0;
}
@media (max-width: 900px) {
  .content { padding: 16px; }
}
</style>
