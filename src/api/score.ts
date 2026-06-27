import { mockDb } from './mock'
import type { Score } from '@/types'

export const scoreApi = {
  list: () => mockDb.listScores(),
  save: (payload: Score[]) => mockDb.saveScores(payload),
  classBoard: () => mockDb.classScoreBoard(),
  medalBoard: () => mockDb.medalBoard(),
}
