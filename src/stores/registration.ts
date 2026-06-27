import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Registration } from '@/types'
import { registrationApi } from '@/api/registration'

export const useRegistrationStore = defineStore('registration', () => {
  const registrations = ref<Registration[]>([])
  const loading = ref(false)

  async function fetchAll(): Promise<void> {
    loading.value = true
    try {
      registrations.value = await registrationApi.list()
    } finally {
      loading.value = false
    }
  }

  async function create(
    payload: Omit<Registration, 'id' | 'createdAt' | 'status'>,
  ): Promise<{ ok: boolean; conflict?: string }> {
    const res = await registrationApi.create(payload)
    if (res.ok) {
      await fetchAll()
      return { ok: true }
    }
    return { ok: false, conflict: res.conflict }
  }

  async function updateStatus(id: string, status: 'approved' | 'rejected'): Promise<void> {
    await registrationApi.updateStatus(id, status)
    await fetchAll()
  }

  async function remove(id: string): Promise<void> {
    await registrationApi.remove(id)
    await fetchAll()
  }

  return { registrations, loading, fetchAll, create, updateStatus, remove }
})
