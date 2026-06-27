import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SportsEvent } from '@/types'
import { eventApi } from '@/api/event'

export const useEventStore = defineStore('event', () => {
  const events = ref<SportsEvent[]>([])
  const loading = ref(false)

  async function fetchAll(): Promise<void> {
    loading.value = true
    try {
      events.value = await eventApi.list()
    } finally {
      loading.value = false
    }
  }

  async function create(payload: Omit<SportsEvent, 'id' | 'registeredCount'>): Promise<void> {
    await eventApi.create(payload)
    await fetchAll()
  }

  async function update(id: string, patch: Partial<SportsEvent>): Promise<void> {
    await eventApi.update(id, patch)
    await fetchAll()
  }

  async function remove(id: string): Promise<void> {
    await eventApi.remove(id)
    await fetchAll()
  }

  return { events, loading, fetchAll, create, update, remove }
})
