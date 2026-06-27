<script setup lang="ts">
import { onMounted } from 'vue'
import {
  LayoutDashboard,
  Trophy,
  ClipboardCheck,
  Timer,
  CalendarDays,
  Megaphone,
  BarChart3,
  Medal,
} from 'lucide-vue-next'
import SideMenu from '@/components/common/SideMenu.vue'
import TopBar from '@/components/common/TopBar.vue'
import { useNoticeStore } from '@/stores/notice'
import { useEventStore } from '@/stores/event'
import { useRegistrationStore } from '@/stores/registration'
import { useScoreStore } from '@/stores/score'

const notice = useNoticeStore()
const eventStore = useEventStore()
const regStore = useRegistrationStore()
const scoreStore = useScoreStore()

const menuItems = [
  { path: '/teacher/dashboard', label: '工作台', icon: LayoutDashboard },
  { path: '/teacher/events', label: '赛事管理', icon: Trophy },
  { path: '/teacher/approvals', label: '报名审批', icon: ClipboardCheck },
  { path: '/teacher/scores', label: '成绩录入', icon: Timer },
  { path: '/teacher/schedule', label: '赛程安排', icon: CalendarDays },
  { path: '/teacher/notices', label: '公告管理', icon: Megaphone },
  { path: '/teacher/stats', label: '数据统计', icon: BarChart3 },
]

onMounted(async () => {
  await Promise.all([
    notice.fetchAll(),
    eventStore.fetchAll(),
    regStore.fetchAll(),
    scoreStore.fetchAll(),
  ])
})
</script>

<template>
  <div class="layout">
    <SideMenu :items="menuItems" brand="教师管理端" :brand-icon="Medal" accent="#2563EB" />
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
