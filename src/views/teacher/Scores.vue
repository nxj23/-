<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, Save, Download, Trophy, ChevronDown, Medal } from 'lucide-vue-next'
import { useEventStore } from '@/stores/event'
import { useRegistrationStore } from '@/stores/registration'
import { useScoreStore } from '@/stores/score'
import { computeRanking } from '@/utils/rank'
import type { Score, SportsEvent } from '@/types'
import MedalBadge from '@/components/common/MedalBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const eventStore = useEventStore()
const regStore = useRegistrationStore()
const scoreStore = useScoreStore()

const selectedEventId = ref<string>('')
const results = ref<Record<string, string>>({})

const editableEvents = computed(() =>
  eventStore.events.filter((e) => e.registeredCount > 0),
)
const selectedEvent = computed(() =>
  eventStore.events.find((e) => e.id === selectedEventId.value),
)

const approvedRegs = computed(() =>
  regStore.registrations.filter(
    (r) => r.eventId === selectedEventId.value && r.status === 'approved',
  ),
)

const existingScores = computed(() =>
  scoreStore.scores.filter((s) => s.eventId === selectedEventId.value),
)

interface PreviewRow {
  studentId: string
  studentName: string
  class: string
  grade: string
  result: string
  rank: number
  isRecordBroken: boolean
  medal?: Score['medal']
}

const preview = computed<PreviewRow[]>(() => {
  const ev = selectedEvent.value
  if (!ev) return []
  const rows = approvedRegs.value.map((r) => ({
    studentId: r.studentId,
    studentName: r.studentName,
    class: r.class,
    grade: r.grade,
    result: results.value[r.studentId] || '',
    eventId: ev.id,
    eventName: ev.name,
    category: ev.category,
    unit: ev.unit,
  }))
  const filled = rows.filter((r) => r.result.trim() !== '')
  const ranked = computeRanking(filled, ev.record, ev.unit, ev.category)
  const rankMap = new Map(ranked.map((p) => [p.score.studentId, p]))
  return rows.map((r) => {
    const info = rankMap.get(r.studentId)
    return {
      studentId: r.studentId,
      studentName: r.studentName,
      class: r.class,
      grade: r.grade,
      result: r.result,
      rank: info?.rank ?? 0,
      isRecordBroken: info?.isRecordBroken ?? false,
      medal: info?.medal,
    }
  })
})

const filledCount = computed(() => preview.value.filter((p) => p.result).length)
const recordCount = computed(() => preview.value.filter((p) => p.isRecordBroken).length)

watch(selectedEventId, () => { results.value = {} })

function selectFirstEvent(): void {
  if (editableEvents.value.length > 0 && !selectedEventId.value) {
    selectedEventId.value = editableEvents.value[0].id
  }
}
eventStore.$subscribe(() => selectFirstEvent())
selectFirstEvent()

async function handleSave(): Promise<void> {
  const ev = selectedEvent.value
  if (!ev) return
  if (filledCount.value === 0) { ElMessage.warning('请至少录入一条成绩'); return }
  try {
    await ElMessageBox.confirm(
      `确认保存「${ev.name}」成绩？保存后将发布给学生查看，并标记项目为已完赛。`,
      '成绩发布确认',
      { confirmButtonText: '发布成绩', cancelButtonText: '取消', type: 'success' },
    )
    const scores: Score[] = preview.value
      .filter((p) => p.result.trim() !== '')
      .map((p) => ({
        id: 'SC' + Date.now() + p.studentId,
        eventId: ev.id,
        eventName: ev.name,
        category: ev.category,
        studentId: p.studentId,
        studentName: p.studentName,
        class: p.class,
        grade: p.grade,
        result: p.result,
        rank: p.rank,
        isRecordBroken: p.isRecordBroken,
        medal: p.medal,
        unit: ev.unit,
        publishedAt: new Date().toISOString().slice(0, 16).replace('T', ' '),
      }))
    await scoreStore.save(scores)
    ElMessage.success(`已发布 ${scores.length} 条成绩，破纪录 ${scores.filter(s=>s.isRecordBroken).length} 项`)
  } catch { /* cancelled */ }
}

function exportCsv(): void {
  const ev = selectedEvent.value
  if (!ev || filledCount.value === 0) { ElMessage.warning('暂无可导出成绩'); return }
  const header = ['排名', '学号', '姓名', '班级', '成绩', '单位', '奖牌', '破纪录']
  const lines = preview.value
    .filter((p) => p.result)
    .sort((a, b) => a.rank - b.rank)
    .map((p) => [
      p.rank, p.studentId, p.studentName, p.class, p.result, ev.unit,
      p.medal === 'gold' ? '金牌' : p.medal === 'silver' ? '银牌' : p.medal === 'bronze' ? '铜牌' : '',
      p.isRecordBroken ? '是' : '否',
    ].join(','))
  const csv = '\uFEFF' + [header.join(','), ...lines].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${ev.name}_成绩表.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('成绩表已导出')
}

function medalLabel(m?: Score['medal']): string {
  return m === 'gold' ? '金牌' : m === 'silver' ? '银牌' : m === 'bronze' ? '铜牌' : ''
}
</script>

<template>
  <div class="scores-page">
    <div class="page-head">
      <div>
        <h1>成绩录入</h1>
        <p>按项目录入成绩，系统自动排名并检测破纪录</p>
      </div>
      <div class="head-actions">
        <button class="ghost-btn" :disabled="!selectedEvent || filledCount === 0" @click="exportCsv">
          <Download :size="15" /> 导出 CSV
        </button>
        <button class="primary-btn" :disabled="!selectedEvent || filledCount === 0" @click="handleSave">
          <Save :size="15" /> 保存并发布
        </button>
      </div>
    </div>

    <!-- 项目选择 -->
    <div class="event-selector">
      <div class="selector-label">选择项目</div>
      <div class="event-chips">
        <button
          v-for="e in editableEvents"
          :key="e.id"
          class="event-chip"
          :class="{ active: e.id === selectedEventId, finished: e.status === 'finished' }"
          @click="selectedEventId = e.id"
        >
          <span class="chip-name">{{ e.name }}</span>
          <span class="chip-meta">{{ e.registeredCount }} 人 · {{ e.status === 'finished' ? '已完赛' : '待录入' }}</span>
        </button>
        <div v-if="editableEvents.length === 0" class="no-event">暂无可录入成绩的项目</div>
      </div>
    </div>

    <div v-if="selectedEvent" class="score-main">
      <!-- 项目信息条 -->
      <div class="event-info-bar">
        <div class="info-item"><Trophy :size="14" /> {{ selectedEvent.name }}</div>
        <div class="info-item">单位：{{ selectedEvent.unit }}</div>
        <div class="info-item" v-if="selectedEvent.record">校纪录：<span class="tnum record-val">{{ selectedEvent.record }}</span></div>
        <div class="info-spacer" />
        <div class="info-stat"><span class="stat-n tnum">{{ filledCount }}</span>/<span class="tnum">{{ approvedRegs.length }}</span> 已录入</div>
        <div class="info-stat record" v-if="recordCount > 0"><Medal :size="13" /> 破纪录 {{ recordCount }} 项</div>
      </div>

      <!-- 成绩录入表 -->
      <div class="table-card">
        <div v-if="approvedRegs.length === 0" class="empty-wrap">
          <EmptyState :icon="Timer" text="该项目暂无已通过报名" sub="请先在报名审批中通过学生报名" />
        </div>
        <div v-else class="table-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th class="w-rank">排名</th>
                <th>学号</th>
                <th>姓名</th>
                <th>班级</th>
                <th class="w-input">成绩 ({{ selectedEvent.unit }})</th>
                <th>奖牌</th>
                <th>破纪录</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in preview" :key="p.studentId" :class="{ 'row-record': p.isRecordBroken }">
                <td class="rank-cell">
                  <MedalBadge v-if="p.rank && p.rank <= 3" :medal="p.medal" :rank="p.rank" :size="34" />
                  <span v-else-if="p.rank" class="rank-num tnum">{{ p.rank }}</span>
                  <span v-else class="rank-dash">—</span>
                </td>
                <td class="tnum">{{ p.studentId }}</td>
                <td class="name-cell">{{ p.studentName }}</td>
                <td>{{ p.class }}</td>
                <td>
                  <input
                    v-model="results[p.studentId]"
                    class="score-input"
                    :placeholder="`输入${selectedEvent.unit}`"
                  />
                </td>
                <td>
                  <span v-if="p.medal" class="medal-text" :class="`m-${p.medal}`">{{ medalLabel(p.medal) }}</span>
                  <span v-else class="dash">—</span>
                </td>
                <td>
                  <span v-if="p.isRecordBroken" class="record-tag animate-record">破纪录</span>
                  <span v-else class="dash">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 录入说明 -->
      <div class="tips">
        <ChevronDown :size="14" />
        <span>录入提示：田径项目（时间）数值越小排名越靠前；田赛/球类（距离/分数）数值越大越靠前。前三名自动颁发金银铜牌。</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.scores-page { display: flex; flex-direction: column; gap: 18px; }

.page-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }
.head-actions { display: flex; gap: 10px; }
.primary-btn, .ghost-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 16px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer;
  transition: all 0.22s ease;
}
.primary-btn { border: none; background: linear-gradient(135deg, #2563EB, #3B82F6); color: #fff; box-shadow: 0 8px 18px rgba(37,99,235,0.3); }
.primary-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(37,99,235,0.38); }
.ghost-btn { border: 1px solid #E2E8F0; background: #fff; color: #475569; }
.ghost-btn:hover:not(:disabled) { border-color: #2563EB; color: #2563EB; background: #EFF6FF; }
.primary-btn:disabled, .ghost-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.event-selector {
  padding: 16px 18px; background: #fff; border-radius: 14px;
  box-shadow: 0 4px 20px rgba(37,99,235,0.06);
}
.selector-label { font-size: 12px; font-weight: 700; color: #475569; margin-bottom: 10px; letter-spacing: 0.04em; }
.event-chips { display: flex; gap: 10px; flex-wrap: wrap; }
.event-chip {
  display: flex; flex-direction: column; gap: 2px;
  padding: 10px 16px; border-radius: 10px;
  border: 1.5px solid #E2E8F0; background: #fff;
  cursor: pointer; transition: all 0.22s ease;
  text-align: left;
}
.event-chip:hover { border-color: #93C5FD; transform: translateY(-1px); }
.event-chip.active { border-color: #2563EB; background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.event-chip.finished { opacity: 0.7; }
.chip-name { font-size: 13px; font-weight: 700; color: #0F172A; }
.chip-meta { font-size: 11px; color: #64748B; }
.event-chip.active .chip-meta { color: #2563EB; }
.no-event { color: #94A3B8; font-size: 13px; padding: 8px 0; }

.event-info-bar {
  display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
  padding: 14px 20px; background: #fff; border-radius: 12px;
  box-shadow: 0 4px 20px rgba(37,99,235,0.06);
  border-left: 4px solid #F97316;
}
.info-item { font-size: 13px; color: #334155; display: flex; align-items: center; gap: 5px; font-weight: 600; }
.record-val { color: #F97316; font-weight: 800; }
.info-spacer { flex: 1; }
.info-stat { font-size: 13px; color: #475569; font-weight: 600; }
.info-stat .stat-n { font-size: 18px; font-weight: 800; color: #2563EB; }
.info-stat.record { color: #F97316; display: inline-flex; align-items: center; gap: 4px; }

.table-card {
  background: #fff; border-radius: 14px; box-shadow: 0 4px 20px rgba(37,99,235,0.06);
  overflow: hidden;
}
.empty-wrap { padding: 30px; }
.table-scroll { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; min-width: 720px; }
.data-table thead th {
  background: #F8FAFC; color: #475569;
  font-size: 12px; font-weight: 700; text-align: left;
  padding: 12px 14px; border-bottom: 1px solid #E2E8F0; white-space: nowrap;
}
.data-table tbody td {
  padding: 12px 14px; border-bottom: 1px solid #F1F5F9;
  font-size: 13px; color: #334155; vertical-align: middle;
}
.data-table tbody tr:hover { background: #F8FAFC; }
.data-table tbody tr.row-record { background: #FFFBEB; }
.data-table tbody tr.row-record:hover { background: #FEF3C7; }
.w-rank { width: 70px; text-align: center; }
.w-input { width: 180px; }
.rank-cell { text-align: center; }
.rank-num { display: inline-flex; width: 30px; height: 30px; border-radius: 50%; background: #F1F5F9; color: #64748B; font-weight: 700; align-items: center; justify-content: center; }
.rank-dash, .dash { color: #CBD5E1; }
.name-cell { font-weight: 700; color: #0F172A; }
.score-input {
  width: 100%; max-width: 160px;
  padding: 8px 12px; border: 1px solid #E2E8F0; border-radius: 8px;
  font-size: 14px; font-weight: 700; color: #0F172A;
  font-variant-numeric: tabular-nums; outline: none;
  transition: all 0.2s ease;
}
.score-input:focus { border-color: #2563EB; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
.medal-text { font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 6px; }
.medal-text.m-gold { background: #FEF3C7; color: #B45309; }
.medal-text.m-silver { background: #F1F5F9; color: #475569; }
.medal-text.m-bronze { background: #FED7AA; color: #9A3412; }
.record-tag {
  display: inline-block; padding: 3px 10px; border-radius: 12px;
  font-size: 11px; font-weight: 700;
  background: linear-gradient(90deg, #FBBF24, #F59E0B);
  color: #fff;
}

.tips {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px 16px; border-radius: 10px;
  background: #EFF6FF; color: #1E40AF;
  font-size: 12px; line-height: 1.6;
}
</style>
