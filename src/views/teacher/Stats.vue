<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, GridComponent, LegendComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart3, Medal, TrendingUp, Users, Trophy } from 'lucide-vue-next'
import { useScoreStore } from '@/stores/score'
import { useEventStore } from '@/stores/event'
import { useRegistrationStore } from '@/stores/registration'
import MedalBadge from '@/components/common/MedalBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import type { ClassScore, MedalStat } from '@/types'

echarts.use([BarChart, PieChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const scoreStore = useScoreStore()
const eventStore = useEventStore()
const regStore = useRegistrationStore()

const participationChart = ref<HTMLDivElement | null>(null)
const classMedalChart = ref<HTMLDivElement | null>(null)
let participationInst: echarts.ECharts | null = null
let classMedalInst: echarts.ECharts | null = null

const classBoard = computed<ClassScore[]>(() => scoreStore.classBoard)
const medalBoard = computed<MedalStat[]>(() => scoreStore.medalBoard)

const top3 = computed(() => classBoard.value.slice(0, 3))
const podiumOrder = computed(() => {
  const [first, second, third] = top3.value
  return [second, first, third].filter(Boolean) as ClassScore[]
})

const participationData = computed(() => {
  const list = eventStore.events.map((e) => ({
    name: e.name,
    rate: e.quota > 0 ? Math.round((e.registeredCount / e.quota) * 100) : 0,
    registered: e.registeredCount,
    quota: e.quota,
  }))
  const high = list.filter((d) => d.rate >= 80).length
  const mid = list.filter((d) => d.rate >= 50 && d.rate < 80).length
  const low = list.filter((d) => d.rate < 50).length
  return { list, high, mid, low, total: list.length }
})

const summary = computed(() => ({
  classes: classBoard.value.length,
  medals: scoreStore.scores.filter((s) => s.medal).length,
  records: scoreStore.scores.filter((s) => s.isRecordBroken).length,
  participants: new Set(regStore.registrations.filter(r => r.status === 'approved').map((r) => r.studentId)).size,
}))

function renderCharts(): void {
  if (participationChart.value) {
    participationInst?.dispose()
    participationInst = echarts.init(participationChart.value)
    participationInst.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: 12, right: 24, top: 24, bottom: 8, containLabel: true },
      xAxis: {
        type: 'value', max: 100, axisLabel: { formatter: '{value}%', color: '#94A3B8', fontSize: 11 },
        splitLine: { lineStyle: { color: '#F1F5F9' } },
      },
      yAxis: {
        type: 'category',
        data: participationData.value.list.map((d) => d.name).reverse(),
        axisLabel: { color: '#475569', fontSize: 11 },
        axisLine: { lineStyle: { color: '#E2E8F0' } },
      },
      series: [{
        type: 'bar',
        data: participationData.value.list.map((d) => d.rate).reverse(),
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: (p: { value: number }) => {
            if (p.value >= 80) return new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#10B981' }, { offset: 1, color: '#34D399' },
            ])
            if (p.value >= 50) return new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#F97316' }, { offset: 1, color: '#FB923C' },
            ])
            return new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#EF4444' }, { offset: 1, color: '#F87171' },
            ])
          },
        },
        label: { show: true, position: 'right', formatter: '{c}%', color: '#475569', fontSize: 11, fontWeight: 600 },
        barWidth: '60%',
      }],
    })
  }

  if (classMedalChart.value && classBoard.value.length > 0) {
    classMedalInst?.dispose()
    classMedalInst = echarts.init(classMedalChart.value)
    classMedalInst.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['金牌', '银牌', '铜牌'], top: 0, textStyle: { color: '#64748B', fontSize: 11 } },
      grid: { left: 12, right: 16, top: 36, bottom: 8, containLabel: true },
      xAxis: {
        type: 'category',
        data: classBoard.value.map((c) => c.class),
        axisLabel: { color: '#475569', fontSize: 11, interval: 0, rotate: 0 },
        axisLine: { lineStyle: { color: '#E2E8F0' } },
      },
      yAxis: {
        type: 'value', axisLabel: { color: '#94A3B8', fontSize: 11 },
        splitLine: { lineStyle: { color: '#F1F5F9' } },
      },
      series: [
        { name: '金牌', type: 'bar', data: classBoard.value.map((c) => c.gold), itemStyle: { color: '#FBBF24', borderRadius: [4, 4, 0, 0] }, barGap: '20%' },
        { name: '银牌', type: 'bar', data: classBoard.value.map((c) => c.silver), itemStyle: { color: '#9CA3AF', borderRadius: [4, 4, 0, 0] } },
        { name: '铜牌', type: 'bar', data: classBoard.value.map((c) => c.bronze), itemStyle: { color: '#B45309', borderRadius: [4, 4, 0, 0] } },
      ],
    })
  }
}

function handleResize(): void {
  participationInst?.resize()
  classMedalInst?.resize()
}

onMounted(async () => {
  await scoreStore.fetchBoards()
  await nextTick()
  renderCharts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  participationInst?.dispose()
  classMedalInst?.dispose()
})

watch([classBoard, participationData], () => nextTick(renderCharts))

function medalColor(m: 'gold' | 'silver' | 'bronze'): string {
  return m === 'gold' ? '#FBBF24' : m === 'silver' ? '#9CA3AF' : '#B45309'
}
</script>

<template>
  <div class="stats-page">
    <div class="page-head">
      <div>
        <h1>数据统计</h1>
        <p>班级积分榜 · 个人奖牌榜 · 项目参与率分析</p>
      </div>
    </div>

    <!-- 汇总 -->
    <div class="summary-grid">
      <div class="sum-card"><div class="sum-ic" style="background:linear-gradient(135deg,#2563EB,#3B82F6)"><Trophy :size="20" color="#fff" /></div><div><div class="sum-n tnum">{{ summary.classes }}</div><div class="sum-l">上榜班级</div></div></div>
      <div class="sum-card"><div class="sum-ic" style="background:linear-gradient(135deg,#FBBF24,#F59E0B)"><Medal :size="20" color="#fff" /></div><div><div class="sum-n tnum">{{ summary.medals }}</div><div class="sum-l">奖牌总数</div></div></div>
      <div class="sum-card"><div class="sum-ic" style="background:linear-gradient(135deg,#F97316,#FB923C)"><TrendingUp :size="20" color="#fff" /></div><div><div class="sum-n tnum">{{ summary.records }}</div><div class="sum-l">破纪录次数</div></div></div>
      <div class="sum-card"><div class="sum-ic" style="background:linear-gradient(135deg,#10B981,#34D399)"><Users :size="20" color="#fff" /></div><div><div class="sum-n tnum">{{ summary.participants }}</div><div class="sum-l">参赛选手</div></div></div>
    </div>

    <!-- 班级积分榜 + 领奖台 -->
    <section class="panel">
      <div class="panel-head">
        <div class="panel-title"><Trophy :size="18" /> 班级积分榜</div>
        <div class="panel-hint">积分规则：金 3 / 银 2 / 铜 1</div>
      </div>
      <div v-if="classBoard.length === 0" class="empty-wrap"><EmptyState :icon="Trophy" text="暂无班级积分数据" sub="成绩发布后将自动统计" /></div>
      <template v-else>
        <!-- 领奖台 -->
        <div class="podium">
          <div v-for="(c, i) in podiumOrder" :key="c.class" class="podium-col" :class="`rank-${4 - (podiumOrder.length - i)}`">
            <div class="podium-medal"><MedalBadge :medal="(4 - (podiumOrder.length - i)) === 1 ? 'gold' : (4 - (podiumOrder.length - i)) === 2 ? 'silver' : 'bronze'" :rank="4 - (podiumOrder.length - i)" :size="44" /></div>
            <div class="podium-class">{{ c.class }}</div>
            <div class="podium-score tnum">{{ c.total }} 分</div>
            <div class="podium-block" :style="{ height: (4 - (podiumOrder.length - i)) === 1 ? '110px' : (4 - (podiumOrder.length - i)) === 2 ? '80px' : '60px' }" />
          </div>
        </div>
        <!-- 完整表格 -->
        <div class="table-scroll">
          <table class="data-table">
            <thead>
              <tr><th class="w-rank">排名</th><th>班级</th><th>年级</th><th>金牌</th><th>银牌</th><th>铜牌</th><th>总积分</th></tr>
            </thead>
            <tbody>
              <tr v-for="(c, i) in classBoard" :key="c.class">
                <td class="rank-cell">
                  <span v-if="i < 3" class="rank-dot" :style="{ background: medalColor(['gold','silver','bronze'][i] as 'gold') }">{{ i + 1 }}</span>
                  <span v-else class="rank-plain tnum">{{ i + 1 }}</span>
                </td>
                <td class="name-cell">{{ c.class }}</td>
                <td>{{ c.grade }}</td>
                <td><span class="m-pill m-gold tnum">{{ c.gold }}</span></td>
                <td><span class="m-pill m-silver tnum">{{ c.silver }}</span></td>
                <td><span class="m-pill m-bronze tnum">{{ c.bronze }}</span></td>
                <td class="total-cell tnum">{{ c.total }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </section>

    <div class="dual-grid">
      <!-- 个人奖牌榜 -->
      <section class="panel">
        <div class="panel-head"><div class="panel-title"><Medal :size="18" /> 个人奖牌榜</div></div>
        <div v-if="medalBoard.length === 0" class="empty-wrap"><EmptyState :icon="Medal" text="暂无奖牌数据" /></div>
        <div v-else class="medal-list">
          <div v-for="(m, i) in medalBoard" :key="m.studentId" class="medal-row" :class="{ top: i < 3 }">
            <div class="m-rank">
              <span v-if="i < 3" class="rank-dot" :style="{ background: medalColor(['gold','silver','bronze'][i] as 'gold') }">{{ i + 1 }}</span>
              <span v-else class="rank-plain tnum">{{ i + 1 }}</span>
            </div>
            <div class="m-avatar">{{ m.studentName.charAt(0) }}</div>
            <div class="m-info">
              <div class="m-name">{{ m.studentName }}</div>
              <div class="m-class">{{ m.class }}</div>
            </div>
            <div class="m-counts">
              <span class="mc gold"><span class="mc-n tnum">{{ m.gold }}</span>金</span>
              <span class="mc silver"><span class="mc-n tnum">{{ m.silver }}</span>银</span>
              <span class="mc bronze"><span class="mc-n tnum">{{ m.bronze }}</span>铜</span>
            </div>
            <div class="m-total tnum">{{ m.total }}</div>
          </div>
        </div>
      </section>

      <!-- 项目参与率 -->
      <section class="panel">
        <div class="panel-head">
          <div class="panel-title"><BarChart3 :size="18" /> 项目参与率</div>
          <div class="rate-legend">
            <span class="lg green">≥80%</span><span class="lg orange">50-79%</span><span class="lg red">&lt;50%</span>
          </div>
        </div>
        <div ref="participationChart" class="chart-box" />
      </section>
    </div>

    <!-- 班级奖牌分布 -->
    <section class="panel">
      <div class="panel-head"><div class="panel-title"><TrendingUp :size="18" /> 班级奖牌分布</div></div>
      <div v-if="classBoard.length === 0" class="empty-wrap"><EmptyState :icon="TrendingUp" text="暂无数据" /></div>
      <div v-else ref="classMedalChart" class="chart-box wide" />
    </section>
  </div>
</template>

<style scoped lang="scss">
.stats-page { display: flex; flex-direction: column; gap: 18px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }

.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.sum-card { display: flex; align-items: center; gap: 14px; padding: 18px 20px; background: #fff; border-radius: 14px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }
.sum-ic { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 14px rgba(37,99,235,0.2); }
.sum-n { font-size: 24px; font-weight: 800; color: #0F172A; }
.sum-l { font-size: 12px; color: #64748B; margin-top: 2px; }

.panel { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); overflow: hidden; }
.panel-head { display: flex; align-items: center; justify-content: space-between; padding: 16px 22px; border-bottom: 1px solid #F1F5F9; }
.panel-title { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 700; color: #0F172A; }
.panel-hint { font-size: 12px; color: #64748B; }
.empty-wrap { padding: 30px; }

.podium { display: flex; align-items: flex-end; justify-content: center; gap: 24px; padding: 28px 22px 0; }
.podium-col { display: flex; flex-direction: column; align-items: center; min-width: 110px; }
.podium-medal { margin-bottom: 8px; }
.podium-class { font-size: 14px; font-weight: 800; color: #0F172A; }
.podium-score { font-size: 13px; color: #F97316; font-weight: 700; margin: 4px 0 10px; }
.podium-block { width: 100%; border-radius: 10px 10px 0 0; background: linear-gradient(180deg, #EFF6FF, #DBEAFE); border-bottom: 3px solid #2563EB; }
.podium-col.rank-1 .podium-block { background: linear-gradient(180deg, #FEF3C7, #FBBF24); border-bottom-color: #F59E0B; }
.podium-col.rank-2 .podium-block { background: linear-gradient(180deg, #F1F5F9, #CBD5E1); border-bottom-color: #94A3B8; }
.podium-col.rank-3 .podium-block { background: linear-gradient(180deg, #FED7AA, #FB923C); border-bottom-color: #C2410C; }

.table-scroll { overflow-x: auto; padding: 8px 22px 18px; }
.data-table { width: 100%; border-collapse: collapse; min-width: 560px; }
.data-table thead th { background: #F8FAFC; color: #475569; font-size: 12px; font-weight: 700; padding: 10px 14px; border-bottom: 1px solid #E2E8F0; text-align: left; }
.data-table tbody td { padding: 11px 14px; border-bottom: 1px solid #F1F5F9; font-size: 13px; color: #334155; }
.data-table tbody tr:hover { background: #F8FAFC; }
.w-rank { width: 60px; }
.rank-cell .rank-dot { display: inline-flex; width: 26px; height: 26px; border-radius: 50%; color: #fff; font-weight: 700; font-size: 12px; align-items: center; justify-content: center; }
.rank-cell .rank-plain { color: #64748B; font-weight: 700; }
.name-cell { font-weight: 700; color: #0F172A; }
.m-pill { display: inline-block; min-width: 26px; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: 700; text-align: center; }
.m-pill.m-gold { background: #FEF3C7; color: #B45309; }
.m-pill.m-silver { background: #F1F5F9; color: #475569; }
.m-pill.m-bronze { background: #FED7AA; color: #9A3412; }
.total-cell { font-size: 15px; font-weight: 800; color: #F97316; }

.dual-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.medal-list { padding: 8px 18px 18px; max-height: 360px; overflow-y: auto; }
.medal-row { display: flex; align-items: center; gap: 12px; padding: 10px 8px; border-bottom: 1px solid #F1F5F9; }
.medal-row:last-child { border-bottom: none; }
.medal-row.top { background: linear-gradient(90deg, #FFFBEB, transparent); border-radius: 10px; }
.m-rank { width: 28px; }
.m-rank .rank-dot { display: inline-flex; width: 26px; height: 26px; border-radius: 50%; color: #fff; font-weight: 700; font-size: 12px; align-items: center; justify-content: center; }
.m-rank .rank-plain { color: #64748B; font-weight: 700; font-size: 13px; }
.m-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #2563EB, #F97316); color: #fff; font-weight: 700; display: flex; align-items: center; justify-content: center; flex: 0 0 auto; }
.m-info { flex: 1; min-width: 0; }
.m-name { font-size: 13px; font-weight: 700; color: #0F172A; }
.m-class { font-size: 11px; color: #94A3B8; }
.m-counts { display: flex; gap: 6px; }
.mc { font-size: 11px; padding: 3px 7px; border-radius: 6px; font-weight: 600; }
.mc.gold { background: #FEF3C7; color: #B45309; }
.mc.silver { background: #F1F5F9; color: #475569; }
.mc.bronze { background: #FED7AA; color: #9A3412; }
.mc-n { font-weight: 800; margin-right: 2px; }
.m-total { font-size: 18px; font-weight: 800; color: #F97316; min-width: 32px; text-align: right; }

.rate-legend { display: flex; gap: 8px; font-size: 11px; }
.rate-legend .lg { padding: 2px 8px; border-radius: 5px; font-weight: 600; }
.rate-legend .green { background: #ECFDF5; color: #10B981; }
.rate-legend .orange { background: #FFF7ED; color: #F97316; }
.rate-legend .red { background: #FEF2F2; color: #EF4444; }

.chart-box { height: 320px; padding: 14px 18px; }
.chart-box.wide { height: 280px; }

@media (max-width: 1100px) {
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
  .dual-grid { grid-template-columns: 1fr; }
}
</style>
