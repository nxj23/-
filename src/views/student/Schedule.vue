<script setup lang="ts">
import { ref, computed } from 'vue'
import { CalendarDays, MapPin, Clock, Users, CheckCircle2, Clock3, XCircle, Inbox } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useRegistrationStore } from '@/stores/registration'
import type { RegistrationStatus } from '@/types'
import EmptyState from '@/components/common/EmptyState.vue'

const auth = useAuthStore()
const regStore = useRegistrationStore()

const filterStatus = ref<RegistrationStatus | 'all'>('all')

const myRegs = computed(() =>
  regStore.registrations.filter((r) => r.studentId === auth.user?.id),
)

const filtered = computed(() => {
  let list = myRegs.value
  if (filterStatus.value !== 'all') list = list.filter((r) => r.status === filterStatus.value)
  return [...list].sort((a, b) => a.scheduledTime.localeCompare(b.scheduledTime))
})

const summary = computed(() => ({
  total: myRegs.value.length,
  pending: myRegs.value.filter((r) => r.status === 'pending').length,
  approved: myRegs.value.filter((r) => r.status === 'approved').length,
  rejected: myRegs.value.filter((r) => r.status === 'rejected').length,
}))

const statusMeta: Record<RegistrationStatus, { label: string; cls: string; icon: typeof CheckCircle2; color: string }> = {
  pending: { label: '审核中', cls: 'pending', icon: Clock3, color: '#F97316' },
  approved: { label: '已通过', cls: 'approved', icon: CheckCircle2, color: '#10B981' },
  rejected: { label: '已驳回', cls: 'rejected', icon: XCircle, color: '#EF4444' },
}

function groupByDay(list: typeof filtered.value) {
  const map = new Map<string, typeof filtered.value>()
  list.forEach((r) => {
    const day = r.scheduledTime.slice(0, 10)
    if (!map.has(day)) map.set(day, [])
    map.get(day)!.push(r)
  })
  return Array.from(map.entries()).map(([day, items]) => ({ day, items }))
}
const grouped = computed(() => groupByDay(filtered.value))
function formatDay(day: string): string { return day.replace(/-/g, '/') }
</script>

<template>
  <div class="schedule-page">
    <div class="page-head">
      <div>
        <h1>我的赛程</h1>
        <p>个人参赛时间表 · 合理安排比赛与休息</p>
      </div>
    </div>

    <!-- 概览 -->
    <div class="sum-grid">
      <div class="sum-card total"><div class="sn tnum">{{ summary.total }}</div><div class="sl">报名总数</div></div>
      <div class="sum-card pending"><div class="sn tnum">{{ summary.pending }}</div><div class="sl">审核中</div></div>
      <div class="sum-card approved"><div class="sn tnum">{{ summary.approved }}</div><div class="sl">已通过</div></div>
      <div class="sum-card rejected"><div class="sn tnum">{{ summary.rejected }}</div><div class="sl">已驳回</div></div>
    </div>

    <!-- 筛选 -->
    <div class="filter-tabs">
      <button :class="{ active: filterStatus === 'all' }" @click="filterStatus = 'all'">全部</button>
      <button :class="{ active: filterStatus === 'approved' }" @click="filterStatus = 'approved'">已通过</button>
      <button :class="{ active: filterStatus === 'pending' }" @click="filterStatus = 'pending'">审核中</button>
      <button :class="{ active: filterStatus === 'rejected' }" @click="filterStatus = 'rejected'">已驳回</button>
    </div>

    <!-- 时间线 -->
    <div v-if="filtered.length === 0" class="empty-card">
      <EmptyState :icon="Inbox" text="暂无赛程" sub="前往项目报名页面报名参赛" />
    </div>
    <div v-else class="timeline-wrap">
      <section v-for="(g, gi) in grouped" :key="g.day" class="day-section animate-slide-fade" :style="{ animationDelay: gi * 0.06 + 's' }">
        <div class="day-banner">
          <CalendarDays :size="16" />
          <span>{{ formatDay(g.day) }}</span>
          <span class="day-count">{{ g.items.length }} 场</span>
        </div>
        <div class="timeline">
          <div v-for="r in g.items" :key="r.id" class="tl-item" :class="statusMeta[r.status].cls">
            <div class="tl-rail">
              <div class="tl-dot" :style="{ background: statusMeta[r.status].color }" />
            </div>
            <div class="tl-card">
              <div class="tl-time">
                <Clock :size="13" />
                <span class="tnum">{{ r.scheduledTime.slice(11, 16) }}</span>
              </div>
              <div class="tl-name">{{ r.eventName }}</div>
              <div class="tl-meta">
                <span><MapPin :size="12" /> {{ r.venue }}</span>
              </div>
              <div class="tl-status" :class="statusMeta[r.status].cls">
                <component :is="statusMeta[r.status].icon" :size="13" />
                {{ statusMeta[r.status].label }}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped lang="scss">
.schedule-page { display: flex; flex-direction: column; gap: 18px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }

.sum-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.sum-card { padding: 18px 20px; border-radius: 14px; background: #fff; box-shadow: 0 4px 20px rgba(37,99,235,0.06); border-left: 4px solid #94A3B8; }
.sum-card.total { border-left-color: #2563EB; }
.sum-card.pending { border-left-color: #F97316; }
.sum-card.approved { border-left-color: #10B981; }
.sum-card.rejected { border-left-color: #EF4444; }
.sn { font-size: 26px; font-weight: 800; color: #0F172A; }
.sum-card.pending .sn { color: #F97316; }
.sum-card.approved .sn { color: #10B981; }
.sum-card.rejected .sn { color: #EF4444; }
.sl { font-size: 12px; color: #64748B; margin-top: 2px; }

.filter-tabs { display: flex; gap: 4px; background: #fff; padding: 6px; border-radius: 12px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); width: fit-content; }
.filter-tabs button { padding: 8px 16px; border: none; background: transparent; border-radius: 8px; font-size: 13px; font-weight: 600; color: #64748B; cursor: pointer; transition: all 0.2s; }
.filter-tabs button.active { background: linear-gradient(135deg, #F97316, #FB923C); color: #fff; box-shadow: 0 4px 10px rgba(249,115,22,0.3); }

.empty-card { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }

.day-section { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); overflow: hidden; margin-bottom: 14px; }
.day-banner { display: flex; align-items: center; gap: 10px; padding: 14px 22px; background: linear-gradient(90deg, #FFF7ED, transparent); color: #C2410C; font-weight: 700; font-size: 14px; border-bottom: 1px solid #F1F5F9; }
.day-count { font-size: 11px; color: #64748B; font-weight: 600; background: #fff; padding: 2px 8px; border-radius: 10px; }

.timeline { padding: 16px 22px 20px 22px; }
.tl-item { display: flex; gap: 16px; padding: 8px 0; }
.tl-rail { position: relative; width: 2px; background: #E2E8F0; flex: 0 0 2px; }
.tl-dot { position: absolute; top: 14px; left: 50%; transform: translateX(-50%); width: 12px; height: 12px; border-radius: 50%; border: 3px solid #fff; box-shadow: 0 0 0 2px rgba(0,0,0,0.06); }
.tl-card { flex: 1; background: #F8FAFC; border-radius: 12px; padding: 14px 18px; transition: all 0.22s ease; position: relative; }
.tl-card:hover { background: #fff; box-shadow: 0 8px 18px rgba(37,99,235,0.1); transform: translateX(4px); }
.tl-item.approved .tl-card { border-left: 3px solid #10B981; }
.tl-item.pending .tl-card { border-left: 3px solid #F97316; }
.tl-item.rejected .tl-card { border-left: 3px solid #EF4444; opacity: 0.7; }
.tl-time { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #64748B; }
.tl-name { font-size: 16px; font-weight: 800; color: #0F172A; margin: 6px 0 4px; }
.tl-meta { display: flex; gap: 14px; font-size: 12px; color: #64748B; }
.tl-meta span { display: inline-flex; align-items: center; gap: 4px; }
.tl-status { position: absolute; top: 14px; right: 18px; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px; }
.tl-status.approved { background: #ECFDF5; color: #10B981; }
.tl-status.pending { background: #FFF7ED; color: #F97316; }
.tl-status.rejected { background: #FEF2F2; color: #EF4444; }
</style>
