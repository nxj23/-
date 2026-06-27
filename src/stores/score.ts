import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Score, ClassScore, MedalStat } from '@/types'
import { scoreApi } from '@/api/score'

export const useScoreStore = defineStore('score', () => {
  const scores = ref<Score[]>([])
  const classBoard = ref<ClassScore[]>([])
  const medalBoard = ref<MedalStat[]>([])
  const loading = ref(false)

  async function fetchAll(): Promise<void> {
    loading.value = true
    try {
      scores.value = await scoreApi.list()
    } finally {
      loading.value = false
    }
  }

  async function save(payload: Score[]): Promise<void> {
    await scoreApi.save(payload)
    await fetchAll()
    await fetchBoards()
  }

  async function fetchBoards(): Promise<void> {
    classBoard.value = await scoreApi.classBoard()
    medalBoard.value = await scoreApi.medalBoard()
  }

  return { scores, classBoard, medalBoard, loading, fetchAll, save, fetchBoards }
})
