import type { Score, SportsEvent } from '@/types'

type SortDir = 'asc' | 'desc'

function categorySortDir(category: SportsEvent['category']): SortDir {
  // 田径时间越小越好（升序）；田赛距离/球类分数越大越好（降序）
  if (category === 'track') return 'asc'
  return 'desc'
}

function parseResult(result: string, unit: string): number {
  if (unit.includes('分:秒') || /^\d+:\d+(\.\d+)?$/.test(result)) {
    const [m, s] = result.split(':')
    return parseFloat(m) * 60 + parseFloat(s)
  }
  const num = parseFloat(result)
  return isNaN(num) ? 0 : num
}

export interface RankInput {
  studentId: string
  studentName: string
  class: string
  grade: string
  result: string
}

export interface RankedScore {
  score: RankInput
  rank: number
  isRecordBroken: boolean
  medal?: Score['medal']
}

export function computeRanking(
  results: RankInput[],
  record: string | undefined,
  unit: string,
  category: SportsEvent['category'],
): RankedScore[] {
  const dir = categorySortDir(category)
  const recordValue = record ? parseResult(record, unit) : null

  const sorted = [...results].sort((a, b) => {
    const av = parseResult(a.result, unit)
    const bv = parseResult(b.result, unit)
    return dir === 'asc' ? av - bv : bv - av
  })

  return sorted.map((score, idx) => {
    const rank = idx + 1
    const value = parseResult(score.result, unit)
    const isRecordBroken =
      recordValue !== null &&
      ((dir === 'asc' && value < recordValue) ||
        (dir === 'desc' && value > recordValue))
    let medal: Score['medal'] | undefined
    if (rank === 1) medal = 'gold'
    else if (rank === 2) medal = 'silver'
    else if (rank === 3) medal = 'bronze'
    return { score, rank, isRecordBroken, medal }
  })
}

export function formatRank(rank: number): string {
  return `第${rank}名`
}
