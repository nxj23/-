import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notice } from '@/types'
import { noticeApi } from '@/api/notice'

export const useNoticeStore = defineStore('notice', () => {
  const notices = ref<Notice[]>([])
  const loading = ref(false)

  const unreadCount = computed(
    () => notices.value.filter((n) => !n.read).length,
  )

  async function fetchAll(): Promise<void> {
    loading.value = true
    try {
      notices.value = await noticeApi.list()
    } finally {
      loading.value = false
    }
  }

  async function create(payload: Omit<Notice, 'id' | 'createdAt' | 'read'>): Promise<void> {
    await noticeApi.create(payload)
    await fetchAll()
  }

  async function remove(id: string): Promise<void> {
    await noticeApi.remove(id)
    await fetchAll()
  }

  async function markRead(id: string): Promise<void> {
    await noticeApi.markRead(id)
    const n = notices.value.find((x) => x.id === id)
    if (n) n.read = true
  }

  async function markAllRead(target?: string): Promise<void> {
    await noticeApi.markAllRead(target)
    await fetchAll()
  }

  function listForUser(userId: string, role: 'teacher' | 'student'): Notice[] {
    if (role === 'teacher') return notices.value
    return notices.value.filter(
      (n) => n.type === 'system' || n.target === userId,
    )
  }

  return {
    notices,
    loading,
    unreadCount,
    fetchAll,
    create,
    remove,
    markRead,
    markAllRead,
    listForUser,
  }
})
