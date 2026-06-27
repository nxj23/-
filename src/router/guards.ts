import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function setupGuards(router: Router): void {
  router.beforeEach((to) => {
    const auth = useAuthStore()
    const publicPages = ['/login']
    const isPublic = publicPages.includes(to.path)

    if (!auth.isLoggedIn && !isPublic) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }

    if (auth.isLoggedIn && to.path === '/login') {
      return auth.isTeacher ? '/teacher/dashboard' : '/student/home'
    }

    if (to.path.startsWith('/teacher') && auth.isLoggedIn && !auth.isTeacher) {
      return '/student/home'
    }
    if (to.path.startsWith('/student') && auth.isLoggedIn && !auth.isStudent) {
      return '/teacher/dashboard'
    }

    if (to.path === '/') {
      if (auth.isLoggedIn) {
        return auth.isTeacher ? '/teacher/dashboard' : '/student/home'
      }
      return '/login'
    }

    return true
  })
}
