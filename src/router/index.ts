import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { setupGuards } from './guards'

import Login from '@/views/Login.vue'
import TeacherLayout from '@/layouts/TeacherLayout.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'

import TeacherDashboard from '@/views/teacher/Dashboard.vue'
import TeacherEvents from '@/views/teacher/Events.vue'
import TeacherApprovals from '@/views/teacher/Approvals.vue'
import TeacherScores from '@/views/teacher/Scores.vue'
import TeacherSchedule from '@/views/teacher/Schedule.vue'
import TeacherNotices from '@/views/teacher/Notices.vue'
import TeacherStats from '@/views/teacher/Stats.vue'

import StudentHome from '@/views/student/Home.vue'
import StudentRegister from '@/views/student/Register.vue'
import StudentScores from '@/views/student/Scores.vue'
import StudentSchedule from '@/views/student/Schedule.vue'
import StudentNotices from '@/views/student/Notices.vue'
import StudentProfile from '@/views/student/Profile.vue'

import NotFound from '@/views/NotFound.vue'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: Login, meta: { title: '登录' } },
  {
    path: '/teacher',
    component: TeacherLayout,
    redirect: '/teacher/dashboard',
    children: [
      { path: 'dashboard', name: 'teacher-dashboard', component: TeacherDashboard, meta: { title: '工作台' } },
      { path: 'events', name: 'teacher-events', component: TeacherEvents, meta: { title: '赛事管理' } },
      { path: 'approvals', name: 'teacher-approvals', component: TeacherApprovals, meta: { title: '报名审批' } },
      { path: 'scores', name: 'teacher-scores', component: TeacherScores, meta: { title: '成绩录入' } },
      { path: 'schedule', name: 'teacher-schedule', component: TeacherSchedule, meta: { title: '赛程安排' } },
      { path: 'notices', name: 'teacher-notices', component: TeacherNotices, meta: { title: '公告管理' } },
      { path: 'stats', name: 'teacher-stats', component: TeacherStats, meta: { title: '数据统计' } },
    ],
  },
  {
    path: '/student',
    component: StudentLayout,
    redirect: '/student/home',
    children: [
      { path: 'home', name: 'student-home', component: StudentHome, meta: { title: '首页' } },
      { path: 'register', name: 'student-register', component: StudentRegister, meta: { title: '项目报名' } },
      { path: 'scores', name: 'student-scores', component: StudentScores, meta: { title: '成绩查询' } },
      { path: 'schedule', name: 'student-schedule', component: StudentSchedule, meta: { title: '我的赛程' } },
      { path: 'notices', name: 'student-notices', component: StudentNotices, meta: { title: '公告通知' } },
      { path: 'profile', name: 'student-profile', component: StudentProfile, meta: { title: '个人中心' } },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound, meta: { title: '页面未找到' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

setupGuards(router)

router.afterEach((to) => {
  const title = (to.meta.title as string) || ''
  document.title = title ? `${title} · 校园运动会管理系统` : '校园运动会管理系统'
})

export default router
