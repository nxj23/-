<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ClipboardCheck, Timer, CalendarDays, Megaphone,
  Trophy, ChevronRight, TrendingUp, MapPin, Clock,
} from 'lucide-vue-next'
import StatCard from '@/components/common/StatCard.vue'
import CountUp from '@/components/common/CountUp.vue'
import { useAuthStore } from '@/stores/auth'
import { useEventStore } from '@/stores/event'
import { useRegistrationStore } from '@/stores/registration'
import { useScoreStore } from '@/stores/score'
import { useNoticeStore } from '@/stores/notice'

const router = useRouter()
const auth = useAuthStore()
const eventStore = useEventStore()
const regStore = useRegistrationStore()
const scoreStore = useScoreStore()
const noticeStore = useNoticeStore()

const pendingApprovals = computed(
  () => regStore.registrations.filter((r) => r.status === 'pending').length,
)
const today = '2026-06-27'
const todayEvents = computed(
  () => eventStore.events.filter((e) => e.scheduledTime.startsWith(today)).length,
)
const pendingScores = computed(
  () => eventStore.events.filter((e) => e.status !== 'finished' && e.registeredCount > 0).length,
)

const todaySchedule = computed(() =>
  eventStore.events
    .filter((e) => e.scheduledTime.startsWith(today))
    .sort((a, b) => a.scheduledTime.localeCompare(b.scheduledTime)),
)

const recentNotices = computed(() => noticeStore.notices.slice(0, 4))
const recentRecords = computed(() => scoreStore.scores.filter((s) => s.isRecordBroken).slice(0, 4))

const categoryLabel: Record<string, string> = {
  track: '田径', field: '田赛', ball: '球类', fun: '趣味',
}
</script>

<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <section class="hero-banner animate-slide-fade">
      <div class="hero-content">
        <div class="hero-tag">教师工作台</div>
        <h1>{{ auth.user?.name }}，今天赛场见</h1>
        <p>2026 校园运动会 · 第 1 比赛日 · 共 {{ eventStore.events.length }} 个项目，{{ regStore.registrations.length }} 条报名待处理</p>
        <div class="hero-actions">
          <button class="hero-btn primary" @click="router.push('/teacher/approvals')">
            <ClipboardCheck :size="16" /> 报名审批 ({{ pendingApprovals }})
          </button>
          <button class="hero-btn ghost" @click="router.push('/teacher/scores')">
            <Timer :size="16" /> 录入成绩
          </button>
        </div>
      </div>
      <div class="hero-decor">
        <Trophy :size="120" :stroke-width="1" />
      </div>
    </section>

    <!-- 统计卡片 -->
    <section class="stat-grid">
      <div class="animate-slide-fade delay-1">
        <StatCard
          label="待审批报名" :value="pendingApprovals" :icon="ClipboardCheck"
          gradient="linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)" hint="点击进入审批"
        />
      </div>
      <div class="animate-slide-fade delay-2">
        <StatCard
          label="待录入成绩" :value="pendingScores" :icon="Timer"
          gradient="linear-gradient(135deg, #F97316 0%, #FB923C 100%)" hint="未完成项目"
        />
      </div>
      <div class="animate-slide-fade delay-3">
        <StatCard
          label="今日赛程" :value="todayEvents" :icon="CalendarDays"
          gradient="linear-gradient(135deg, #10B981 0%, #34D399 100%)" hint="6月27日"
        />
      </div>
      <div class="animate-slide-fade delay-4">
        <StatCard
          label="系统公告" :value="noticeStore.notices.length" :icon="Megaphone"
          gradient="linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)" hint="已发布"
        />
      </div>
    </section>

    <!-- 双列内容 -->
    <section class="dual-grid">
      <!-- 今日赛程 -->
      <div class="panel animate-slide-fade delay-3">
        <div class="panel-head">
          <div class="panel-title">
            <CalendarDays :size="18" /> 今日赛程
          </div>
          <button class="link-btn" @click="router.push('/teacher/schedule')">查看全部 <ChevronRight :size="14" /></button>
        </div>
        <div class="panel-body">
          <div v-if="todaySchedule.length === 0" class="empty-row">今日暂无赛程</div>
          <div v-for="e in todaySchedule" :key="e.id" class="timeline-row">
            <div class="time-col">
              <div class="time-hm tnum">{{ e.scheduledTime.slice(11, 16) }}</div>
              <div class="time-badge">{{ categoryLabel[e.category] }}</div>
            </div>
            <div class="line-col"><div class="dot" /></div>
            <div class="info-col">
              <div class="info-name">{{ e.name }}</div>
              <div class="info-meta">
                <span><MapPin :size="12" /> {{ e.venue }}</span>
                <span class="quota">名额 {{ e.registeredCount }}/{{ e.quota }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 破纪录 + 公告 -->
      <div class="right-col">
        <div class="panel animate-slide-fade delay-4">
          <div class="panel-head">
            <div class="panel-title"><TrendingUp :size="18" /> 破纪录动态</div>
          </div>
          <div class="panel-body">
            <div v-if="recentRecords.length === 0" class="empty-row">暂无破纪录</div>
            <div v-for="r in recentRecords" :key="r.id" class="record-row">
              <div class="record-medal">破</div>
              <div class="record-info">
                <div class="record-name">{{ r.studentName }} · {{ r.eventName }}</div>
                <div class="record-result tnum">成绩 {{ r.result }}{{ r.unit }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel animate-slide-fade delay-5">
          <div class="panel-head">
            <div class="panel-title"><Megaphone :size="18" /> 最新公告</div>
            <button class="link-btn" @click="router.push('/teacher/notices')">更多 <ChevronRight :size="14" /></button>
          </div>
          <div class="panel-body">
            <div v-if="recentNotices.length === 0" class="empty-row">暂无公告</div>
            <div v-for="n in recentNotices" :key="n.id" class="notice-row" @click="router.push('/teacher/notices')">
              <div class="notice-dot" :class="`level-${n.level}`" />
              <div class="notice-info">
                <div class="notice-title">{{ n.title }}</div>
                <div class="notice-time"><Clock :size="11" /> {{ n.createdAt }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.dashboard { display: flex; flex-direction: column; gap: 22px; }

.hero-banner {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  background: linear-gradient(120deg, #1E3A8A 0%, #2563EB 50%, #F97316 130%);
  padding: 32px 36px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 14px 34px rgba(30, 58, 138, 0.32);
}
.hero-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(8px);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 14px;
}
.hero-content h1 { font-size: 28px; font-weight: 800; margin: 0 0 8px; letter-spacing: 0.02em; }
.hero-content p { font-size: 13px; color: rgba(255,255,255,0.85); margin: 0 0 20px; max-width: 540px; }
.hero-actions { display: flex; gap: 10px; }
.hero-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px;
  border-radius: 10px;
  border: none;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.22s ease;
}
.hero-btn.primary { background: #fff; color: #2563EB; }
.hero-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 8px 18px rgba(0,0,0,0.18); }
.hero-btn.ghost { background: rgba(255,255,255,0.18); color: #fff; border: 1px solid rgba(255,255,255,0.35); }
.hero-btn.ghost:hover { background: rgba(255,255,255,0.28); }
.hero-decor { opacity: 0.18; }
.hero-decor svg { transform: rotate(-10deg); }

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }

.dual-grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 16px; }
.right-col { display: flex; flex-direction: column; gap: 16px; }

.panel {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.07);
  overflow: hidden;
}
.panel-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #F1F5F9;
}
.panel-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 700; color: #0F172A;
}
.link-btn {
  display: inline-flex; align-items: center; gap: 2px;
  background: none; border: none;
  color: #2563EB; font-size: 12px; font-weight: 600;
  cursor: pointer; padding: 0;
}
.link-btn:hover { color: #1D4ED8; }
.panel-body { padding: 14px 20px 18px; }

.timeline-row {
  display: flex; align-items: center; gap: 14px;
  padding: 12px 0;
  border-bottom: 1px dashed #F1F5F9;
}
.timeline-row:last-child { border-bottom: none; }
.time-col { width: 64px; text-align: center; }
.time-hm { font-size: 18px; font-weight: 800; color: #2563EB; }
.time-badge {
  font-size: 10px; padding: 2px 6px; border-radius: 4px;
  background: #EFF6FF; color: #2563EB; margin-top: 4px; display: inline-block;
}
.line-col { position: relative; width: 2px; height: 36px; background: #E2E8F0; }
.dot { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 10px; height: 10px; border-radius: 50%; background: #F97316; border: 2px solid #fff; }
.info-col { flex: 1; }
.info-name { font-size: 14px; font-weight: 700; color: #0F172A; }
.info-meta { display: flex; gap: 14px; font-size: 12px; color: #64748B; margin-top: 4px; }
.info-meta span { display: inline-flex; align-items: center; gap: 3px; }
.quota { color: #F97316; font-weight: 600; }

.empty-row { text-align: center; color: #94A3B8; padding: 24px 0; font-size: 13px; }

.record-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0;
  border-bottom: 1px dashed #F1F5F9;
}
.record-row:last-child { border-bottom: none; }
.record-medal {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, #FBBF24, #F59E0B);
  color: #fff; font-weight: 800; font-size: 13px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 14px rgba(251, 191, 36, 0.4);
}
.record-name { font-size: 13px; font-weight: 700; color: #0F172A; }
.record-result { font-size: 12px; color: #F97316; font-weight: 600; margin-top: 2px; }

.notice-row {
  display: flex; gap: 12px; padding: 10px 0;
  border-bottom: 1px dashed #F1F5F9;
  cursor: pointer;
  transition: background 0.2s;
}
.notice-row:last-child { border-bottom: none; }
.notice-row:hover { background: #F8FAFC; }
.notice-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex: 0 0 auto; }
.notice-dot.level-info { background: #3B82F6; }
.notice-dot.level-success { background: #10B981; }
.notice-dot.level-warning { background: #F59E0B; }
.notice-dot.level-danger { background: #EF4444; }
.notice-title { font-size: 13px; color: #334155; font-weight: 600; line-height: 1.4; }
.notice-time { font-size: 11px; color: #94A3B8; margin-top: 3px; display: inline-flex; align-items: center; gap: 3px; }

@media (max-width: 1100px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .dual-grid { grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
  .stat-grid { grid-template-columns: 1fr; }
  .hero-decor { display: none; }
}
</style>
