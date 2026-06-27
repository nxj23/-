<script setup lang="ts">
import { ref, computed } from 'vue'
import { CalendarDays, MapPin, Clock, Users, Shuffle, Printer } from 'lucide-vue-next'
import { useEventStore } from '@/stores/event'
import type { EventCategory } from '@/types'

const store = useEventStore()

const view = ref<'timeline' | 'grid'>('timeline')

const categoryMeta: Record<EventCategory, { label: string; color: string }> = {
  track: { label: '田径', color: '#2563EB' },
  field: { label: '田赛', color: '#F97316' },
  ball: { label: '球类', color: '#10B981' },
  fun: { label: '趣味', color: '#8B5CF6' },
}

const sortedEvents = computed(() =>
  [...store.events].sort((a, b) => a.scheduledTime.localeCompare(b.scheduledTime)),
)

const days = computed(() => {
  const map = new Map<string, typeof sortedEvents.value>()
  sortedEvents.value.forEach((e) => {
    const day = e.scheduledTime.slice(0, 10)
    if (!map.has(day)) map.set(day, [])
    map.get(day)!.push(e)
  })
  return Array.from(map.entries()).map(([day, events]) => ({ day, events }))
})

const venues = computed(() => {
  const set = new Set(store.events.map((e) => e.venue))
  return Array.from(set)
})

const timeSlots = computed(() => {
  const set = new Set(store.events.map((e) => e.scheduledTime))
  return Array.from(set).sort()
})

function eventsAt(venue: string, time: string) {
  return store.events.filter((e) => e.venue === venue && e.scheduledTime === time)
}

const groups = computed(() => {
  const map = new Map<string, typeof store.events>()
  store.events.forEach((e) => {
    const g = e.group || '未分组'
    if (!map.has(g)) map.set(g, [])
    map.get(g)!.push(e)
  })
  return Array.from(map.entries()).map(([group, events]) => ({ group, events }))
})

const drawResults = ref<Record<string, string[]> | null>(null)
function runDraw(): void {
  const result: Record<string, string[]> = {}
  groups.value.forEach(({ group, events }) => {
    const shuffled = [...events].sort(() => Math.random() - 0.5)
    result[group] = shuffled.map((e, i) => `${e.name} → 第${i + 1}场`)
  })
  drawResults.value = result
}

function formatDay(day: string): string {
  return day.replace(/-/g, '/')
}
</script>

<template>
  <div class="schedule-page">
    <div class="page-head">
      <div>
        <h1>赛程安排</h1>
        <p>查看比赛时间场地编排，支持分组抽签</p>
      </div>
      <div class="head-actions">
        <div class="view-switch">
          <button :class="{ active: view === 'timeline' }" @click="view = 'timeline'">时间轴</button>
          <button :class="{ active: view === 'grid' }" @click="view = 'grid'">场地矩阵</button>
        </div>
        <button class="primary-btn" @click="runDraw"><Shuffle :size="15" /> 分组抽签</button>
      </div>
    </div>

    <!-- 时间轴视图 -->
    <div v-if="view === 'timeline'" class="days-wrap">
      <section v-for="(d, di) in days" :key="d.day" class="day-block animate-slide-fade" :style="{ animationDelay: di * 0.06 + 's' }">
        <div class="day-head">
          <div class="day-date">
            <CalendarDays :size="18" />
            <span class="day-text">{{ formatDay(d.day) }}</span>
            <span class="day-count">共 {{ d.events.length }} 场</span>
          </div>
        </div>
        <div class="day-timeline">
          <div v-for="e in d.events" :key="e.id" class="tl-item">
            <div class="tl-time">
              <div class="tl-hm tnum">{{ e.scheduledTime.slice(11, 16) }}</div>
            </div>
            <div class="tl-rail"><div class="tl-dot" :style="{ background: categoryMeta[e.category].color }" /></div>
            <div class="tl-card" :style="{ borderLeftColor: categoryMeta[e.category].color }">
              <div class="tl-top">
                <h3>{{ e.name }}</h3>
                <span class="cat-badge" :style="{ background: categoryMeta[e.category].color }">{{ categoryMeta[e.category].label }}</span>
              </div>
              <div class="tl-meta">
                <span><MapPin :size="13" /> {{ e.venue }}</span>
                <span><Users :size="13" /> {{ e.registeredCount }}/{{ e.quota }}</span>
                <span v-if="e.group">分组 {{ e.group }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 场地矩阵视图 -->
    <div v-else class="grid-card">
      <div class="table-scroll">
        <table class="grid-table">
          <thead>
            <tr>
              <th class="corner">时间 \ 场地</th>
              <th v-for="v in venues" :key="v">{{ v }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in timeSlots" :key="t">
              <td class="time-cell tnum">{{ t.slice(5, 16).replace('-', '/') }}</td>
              <td v-for="v in venues" :key="v" class="venue-cell">
                <div v-for="e in eventsAt(v, t)" :key="e.id" class="grid-event" :style="{ background: categoryMeta[e.category].color + '14', borderColor: categoryMeta[e.category].color }">
                  <div class="ge-name">{{ e.name }}</div>
                  <div class="ge-meta"><Users :size="11" /> {{ e.registeredCount }}/{{ e.quota }}</div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 抽签结果 -->
    <section v-if="drawResults" class="draw-card animate-slide-fade">
      <div class="draw-head">
        <div class="draw-title"><Shuffle :size="18" /> 分组抽签结果</div>
        <button class="ghost-btn" @click="drawResults = null">关闭</button>
      </div>
      <div class="draw-grid">
        <div v-for="(order, group) in drawResults" :key="group" class="draw-col">
          <div class="draw-col-head">{{ group }} 组</div>
          <div v-for="(item, i) in order" :key="i" class="draw-row">
            <span class="draw-no tnum">{{ i + 1 }}</span>
            <span>{{ item }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.schedule-page { display: flex; flex-direction: column; gap: 18px; }

.page-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }
.head-actions { display: flex; gap: 10px; align-items: center; }
.view-switch { display: flex; gap: 4px; background: #F1F5F9; padding: 4px; border-radius: 10px; }
.view-switch button {
  padding: 7px 14px; border: none; background: transparent; border-radius: 7px;
  font-size: 12px; font-weight: 600; color: #64748B; cursor: pointer; transition: all 0.2s;
}
.view-switch button.active { background: #fff; color: #2563EB; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
.primary-btn, .ghost-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 9px 14px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer;
  transition: all 0.22s ease;
}
.primary-btn { border: none; background: linear-gradient(135deg, #F97316, #FB923C); color: #fff; box-shadow: 0 8px 18px rgba(249,115,22,0.3); }
.primary-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(249,115,22,0.38); }
.ghost-btn { border: 1px solid #E2E8F0; background: #fff; color: #475569; }
.ghost-btn:hover { border-color: #EF4444; color: #EF4444; }

.day-block {
  background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06);
  overflow: hidden;
}
.day-head { padding: 16px 22px; border-bottom: 1px solid #F1F5F9; background: linear-gradient(90deg, #EFF6FF, transparent); }
.day-date { display: flex; align-items: center; gap: 10px; color: #1E40AF; font-weight: 700; font-size: 16px; }
.day-count { font-size: 12px; color: #64748B; font-weight: 600; background: #fff; padding: 3px 10px; border-radius: 12px; }

.day-timeline { padding: 18px 22px 22px; }
.tl-item { display: flex; gap: 16px; padding: 10px 0; align-items: stretch; }
.tl-time { width: 56px; text-align: right; padding-top: 12px; }
.tl-hm { font-size: 15px; font-weight: 800; color: #2563EB; }
.tl-rail { position: relative; width: 2px; background: #E2E8F0; }
.tl-dot { position: absolute; top: 16px; left: 50%; transform: translateX(-50%); width: 12px; height: 12px; border-radius: 50%; border: 3px solid #fff; box-shadow: 0 0 0 2px rgba(37,99,235,0.2); }
.tl-card {
  flex: 1; background: #F8FAFC; border-radius: 12px; padding: 14px 18px;
  border-left: 4px solid #2563EB;
  transition: all 0.22s ease;
}
.tl-card:hover { background: #fff; box-shadow: 0 8px 18px rgba(37,99,235,0.1); transform: translateX(4px); }
.tl-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.tl-top h3 { font-size: 15px; font-weight: 800; color: #0F172A; margin: 0; }
.cat-badge { padding: 2px 8px; border-radius: 6px; color: #fff; font-size: 10px; font-weight: 700; }
.tl-meta { display: flex; gap: 16px; margin-top: 8px; font-size: 12px; color: #64748B; }
.tl-meta span { display: inline-flex; align-items: center; gap: 4px; }

.grid-card { background: #fff; border-radius: 14px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); overflow: hidden; }
.table-scroll { overflow-x: auto; }
.grid-table { border-collapse: collapse; min-width: 720px; width: 100%; }
.grid-table thead th {
  background: #F8FAFC; color: #475569; font-size: 12px; font-weight: 700;
  padding: 14px; border-bottom: 1px solid #E2E8F0; text-align: left; white-space: nowrap;
}
.grid-table .corner { background: #2563EB; color: #fff; }
.grid-table tbody td { padding: 12px; border-bottom: 1px solid #F1F5F9; border-right: 1px solid #F1F5F9; vertical-align: top; }
.time-cell { font-weight: 700; color: #2563EB; background: #F8FAFC; white-space: nowrap; }
.venue-cell { min-width: 160px; }
.grid-event {
  padding: 8px 10px; border-radius: 8px; border-left: 3px solid;
  margin-bottom: 6px;
}
.ge-name { font-size: 13px; font-weight: 700; color: #0F172A; }
.ge-meta { font-size: 11px; color: #64748B; margin-top: 3px; display: flex; align-items: center; gap: 3px; }

.draw-card { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); overflow: hidden; }
.draw-head { display: flex; justify-content: space-between; align-items: center; padding: 16px 22px; border-bottom: 1px solid #F1F5F9; }
.draw-title { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 700; color: #0F172A; }
.draw-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; padding: 20px 22px; }
.draw-col { background: #F8FAFC; border-radius: 12px; padding: 14px; }
.draw-col-head { font-size: 14px; font-weight: 800; color: #2563EB; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #E2E8F0; }
.draw-row { display: flex; align-items: center; gap: 10px; padding: 7px 0; font-size: 13px; color: #334155; }
.draw-no { width: 22px; height: 22px; border-radius: 50%; background: #2563EB; color: #fff; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex: 0 0 auto; }
</style>
