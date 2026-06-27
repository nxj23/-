<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Zap, Target, Volleyball, PartyPopper, MapPin, Clock, Users,
  CheckCircle2, Clock3, XCircle, Search, AlertTriangle,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useEventStore } from '@/stores/event'
import { useRegistrationStore } from '@/stores/registration'
import type { EventCategory, SportsEvent } from '@/types'
import EmptyState from '@/components/common/EmptyState.vue'

const auth = useAuthStore()
const eventStore = useEventStore()
const regStore = useRegistrationStore()

const filterCategory = ref<EventCategory | 'all'>('all')
const keyword = ref('')

const categoryMeta: Record<EventCategory, { label: string; color: string; icon: typeof Zap }> = {
  track: { label: '田径', color: '#2563EB', icon: Zap },
  field: { label: '田赛', color: '#F97316', icon: Target },
  ball: { label: '球类', color: '#10B981', icon: Volleyball },
  fun: { label: '趣味', color: '#8B5CF6', icon: PartyPopper },
}

const filtered = computed(() =>
  eventStore.events.filter((e) => {
    if (e.status === 'finished') return false
    if (filterCategory.value !== 'all' && e.category !== filterCategory.value) return false
    if (keyword.value && !e.name.includes(keyword.value)) return false
    return true
  }),
)

function myStatusFor(eventId: string): 'none' | 'pending' | 'approved' | 'rejected' {
  const r = regStore.registrations.find(
    (x) => x.studentId === auth.user?.id && x.eventId === eventId,
  )
  return r?.status ?? 'none'
}

function quotaPercent(e: SportsEvent): number {
  return Math.round((e.registeredCount / e.quota) * 100)
}
function remaining(e: SportsEvent): number {
  return Math.max(0, e.quota - e.registeredCount)
}
const circumference = 2 * Math.PI * 18

async function handleRegister(e: SportsEvent): Promise<void> {
  if (!auth.user) return
  const res = await regStore.create({
    studentId: auth.user.id,
    studentName: auth.user.name,
    class: auth.user.class || '',
    grade: auth.user.grade || '',
    eventId: e.id,
    eventName: e.name,
    scheduledTime: e.scheduledTime,
    venue: e.venue,
  })
  if (res.ok) {
    ElMessage.success(`已报名「${e.name}」，等待教师审批`)
  } else {
    ElMessage.warning(res.conflict || '报名失败')
  }
}
</script>

<template>
  <div class="register-page">
    <div class="page-head">
      <div>
        <h1>项目报名</h1>
        <p>选择心仪的比赛项目在线报名 · 系统自动检测名额与时间冲突</p>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <div class="search-wrap">
        <Search :size="16" class="search-icon" />
        <input v-model="keyword" placeholder="搜索项目名称" />
      </div>
      <div class="filter-group">
        <button
          v-for="(meta, key) in categoryMeta"
          :key="key"
          class="cat-chip"
          :class="{ active: filterCategory === key }"
          :style="filterCategory === key ? { background: meta.color, borderColor: meta.color } : {}"
          @click="filterCategory = key as EventCategory"
        >{{ meta.label }}</button>
        <button class="cat-chip" :class="{ active: filterCategory === 'all' }" @click="filterCategory = 'all'">全部</button>
      </div>
    </div>

    <!-- 项目卡片 -->
    <div v-if="filtered.length > 0" class="card-grid">
      <article
        v-for="(e, i) in filtered"
        :key="e.id"
        class="reg-card animate-slide-fade"
        :style="{ animationDelay: i * 0.04 + 's' }"
      >
        <div class="card-head" :style="{ background: categoryMeta[e.category].color }">
          <div class="cat-icon">
            <component :is="categoryMeta[e.category].icon" :size="22" color="#fff" :stroke-width="2.2" />
          </div>
          <div class="quota-ring">
            <svg width="46" height="46" viewBox="0 0 46 46">
              <circle cx="23" cy="23" r="18" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="4" />
              <circle
                cx="23" cy="23" r="18" fill="none" stroke="#fff" stroke-width="4"
                stroke-linecap="round"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="circumference - (quotaPercent(e) / 100) * circumference"
                transform="rotate(-90 23 23)"
              />
            </svg>
            <div class="ring-text tnum">{{ remaining(e) }}</div>
          </div>
        </div>

        <div class="card-body">
          <div class="title-row">
            <h3>{{ e.name }}</h3>
            <span class="full-tag" v-if="remaining(e) === 0">已满</span>
          </div>
          <div class="meta-list">
            <div class="meta"><MapPin :size="13" /> {{ e.venue }}</div>
            <div class="meta"><Clock :size="13" /> {{ e.scheduledTime }}</div>
            <div class="meta"><Users :size="13" /> {{ e.registeredCount }}/{{ e.quota }} 人</div>
          </div>
          <div v-if="e.record" class="record-line">
            <AlertTriangle :size="12" /> 校纪录 <span class="tnum">{{ e.record }}{{ e.unit }}</span>
          </div>
        </div>

        <div class="card-foot">
          <template v-if="myStatusFor(e.id) === 'none'">
            <button
              v-if="remaining(e) > 0 && e.status === 'open'"
              class="reg-btn primary"
              @click="handleRegister(e)"
            >立即报名</button>
            <button v-else class="reg-btn disabled" disabled>名额已满</button>
          </template>
          <div v-else-if="myStatusFor(e.id) === 'pending'" class="status-chip pending">
            <Clock3 :size="14" /> 审核中
          </div>
          <div v-else-if="myStatusFor(e.id) === 'approved'" class="status-chip approved">
            <CheckCircle2 :size="14" /> 已通过
          </div>
          <div v-else-if="myStatusFor(e.id) === 'rejected'" class="status-chip rejected">
            <XCircle :size="14" /> 已驳回
          </div>
        </div>
      </article>
    </div>
    <div v-else class="empty-card">
      <EmptyState :icon="Zap" text="暂无符合条件的项目" sub="试试调整筛选条件" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-page { display: flex; flex-direction: column; gap: 18px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }

.filter-bar { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; padding: 14px 18px; background: #fff; border-radius: 14px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }
.search-wrap { position: relative; flex: 1; min-width: 180px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94A3B8; }
.search-wrap input { width: 100%; padding: 9px 12px 9px 36px; border: 1px solid #E2E8F0; border-radius: 10px; font-size: 13px; outline: none; }
.search-wrap input:focus { border-color: #2563EB; }
.filter-group { display: flex; gap: 6px; flex-wrap: wrap; }
.cat-chip { padding: 7px 14px; border: 1px solid #E2E8F0; border-radius: 20px; background: #fff; font-size: 12px; font-weight: 600; color: #475569; cursor: pointer; transition: all 0.2s; }
.cat-chip:hover { border-color: #FDBA74; color: #F97316; }
.cat-chip.active { color: #fff; }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 18px; }
.reg-card { background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(37,99,235,0.07); display: flex; flex-direction: column; transition: transform 0.28s cubic-bezier(0.22,1,0.36,1), box-shadow 0.28s; }
.reg-card:hover { transform: translateY(-5px); box-shadow: 0 16px 36px rgba(37,99,235,0.16); }
.card-head { padding: 16px 18px; display: flex; align-items: center; justify-content: space-between; }
.cat-icon { width: 42px; height: 42px; border-radius: 12px; background: rgba(255,255,255,0.22); display: flex; align-items: center; justify-content: center; }
.quota-ring { position: relative; width: 46px; height: 46px; }
.ring-text { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 13px; font-weight: 800; }

.card-body { padding: 16px 18px; flex: 1; }
.title-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.title-row h3 { font-size: 17px; font-weight: 800; color: #0F172A; margin: 0; }
.full-tag { font-size: 11px; padding: 2px 8px; border-radius: 6px; background: #FEF2F2; color: #EF4444; font-weight: 700; }
.meta-list { display: flex; flex-direction: column; gap: 5px; margin-top: 10px; }
.meta { font-size: 12px; color: #64748B; display: flex; align-items: center; gap: 6px; }
.record-line { margin-top: 10px; padding: 6px 10px; border-radius: 8px; background: linear-gradient(90deg, #FFFBEB, #FEF3C7); font-size: 12px; color: #B45309; font-weight: 600; display: inline-flex; align-items: center; gap: 5px; }

.card-foot { padding: 0 18px 16px; }
.reg-btn { width: 100%; padding: 11px 0; border: none; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; transition: all 0.22s ease; }
.reg-btn.primary { background: linear-gradient(135deg, #F97316, #FB923C); color: #fff; box-shadow: 0 8px 18px rgba(249,115,22,0.3); }
.reg-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(249,115,22,0.4); }
.reg-btn.disabled { background: #F1F5F9; color: #94A3B8; cursor: not-allowed; }

.status-chip { display: flex; align-items: center; justify-content: center; gap: 6px; padding: 11px 0; border-radius: 10px; font-size: 13px; font-weight: 700; }
.status-chip.pending { background: #FFF7ED; color: #F97316; }
.status-chip.approved { background: #ECFDF5; color: #10B981; }
.status-chip.rejected { background: #FEF2F2; color: #EF4444; }

.empty-card { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }
</style>
