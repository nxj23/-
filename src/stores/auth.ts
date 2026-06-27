import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(authApi.currentUser())
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)
  const role = computed(() => user.value?.role)
  const isTeacher = computed(() => role.value === 'teacher')
  const isStudent = computed(() => role.value === 'student')

  async function login(account: string, password: string): Promise<boolean> {
    loading.value = true
    try {
      const u = await authApi.login(account, password)
      if (u) {
        user.value = u
        return true
      }
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    await authApi.logout()
    user.value = null
  }

  function refresh(): void {
    user.value = authApi.currentUser()
  }

  return { user, loading, isLoggedIn, role, isTeacher, isStudent, login, logout, refresh }
})
