<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ClipboardList, Timer, CalendarDays, Bell, Trophy, ChevronRight,
  MapPin, Clock, Users, Medal, Zap, Award,
} from 'lucide-vue-next'
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

const myRegs = computed(() =>
  regStore.registrations.filter((r) => r.studentId === auth.user?.id),
)
const myApproved = computed(() => myRegs.value.filter((r) => r.status === 'approved'))
const myScores = computed(() =>
  scoreStore.scores.filter((s) => s.studentId === auth.user?.id),
)
const myMedals = computed(() => myScores.value.filter((s) => s.medal))
const myRecords = computed(() => myScores.value.filter((s) => s.isRecordBroken))

const openEvents = computed(() =>
  eventStore.events.filter((e) => e.status === 'open' && e.registeredCount < e.quota).slice(0, 4),
)
const myNotices = computed(() =>
  noticeStore.listForUser(auth.user?.id || '', 'student').slice(0, 4),
)
const upcomingSchedule = computed(() =>
  [...myApproved.value]
    .sort((a, b) => a.scheduledTime.localeCompare(b.scheduledTime))
    .slice(0, 3),
)

const categoryLabel: Record<string, string> = { track: '田径', field: '田赛', ball: '球类', fun: '趣味' }
</script>

<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <section class="hero animate-slide-fade">
      <div class="hero-bg" />
      <div class="hero-content">
        <div class="hero-hi">{{ auth.user?.name }} · {{ auth.user?.class }}</div>
        <h1>今天，为荣誉而战</h1>
        <p>2026 校园运动会 · 已报名 {{ myRegs.length }} 项 · 已获奖牌 {{ myMedals.length }} 枚</p>
        <div class="hero-actions">
          <button class="hero-btn primary" @click="router.push('/student/register')">
            <ClipboardList :size="16" /> 立即报名
          </button>
          <button class="hero-btn ghost" @click="router.push('/student/scores')">
            <Trophy :size="16" /> 我的成绩
          </button>
        </div>
      </div>
      <div class="hero-emoji"><Trophy :size="130" :stroke-width="0.8" /></div>
    </section>

    <!-- 数据卡片 -->
    <section class="stat-grid">
      <div class="mini-stat animate-slide-fade delay-1" @click="router.push('/student/register')">
        <div class="ms-icon" style="background:linear-gradient(135deg,#2563EB,#3B82F6)"><ClipboardList :size="20" color="#fff" /></div>
        <div class="ms-body"><div class="ms-n"><CountUp :end="myRegs.length" /></div><div class="ms-l">已报项目</div></div>
      </div>
      <div class="mini-stat animate-slide-fade delay-2" @click="router.push('/student/schedule')">
        <div class="ms-icon" style="background:linear-gradient(135deg,#10B981,#34D399)"><CalendarDays :size="20" color="#fff" /></div>
        <div class="ms-body"><div class="ms-n"><CountUp :end="myApproved.length" /></div><div class="ms-l">参赛项目</div></div>
      </div>
      <div class="mini-stat animate-slide-fade delay-3" @click="router.push('/student/scores')">
        <div class="ms-icon" style="background:linear-gradient(135deg,#FBBF24,#F59E0B)"><Medal :size="20" color="#fff" /></div>
        <div class="ms-body"><div class="ms-n"><CountUp :end="myMedals.length" /></div><div class="ms-l">获得奖牌</div></div>
      </div>
      <div class="mini-stat animate-slide-fade delay-4" @click="router.push('/student/notices')">
        <div class="ms-icon" style="background:linear-gradient(135deg,#8B5CF6,#A78BFA)"><Bell :size="20" color="#fff" /></div>
        <div class="ms-body"><div class="ms-n"><CountUp :end="noticeStore.unreadCount" /></div><div class="ms-l">未读消息</div></div>
      </div>
    </section>

    <div class="dual-grid">
      <!-- 我的赛程 -->
      <section class="panel animate-slide-fade delay-3">
        <div class="panel-head">
          <div class="panel-title"><CalendarDays :size="18" /> 即将到来</div>
          <button class="link-btn" @click="router.push('/student/schedule')">全部赛程 <ChevronRight :size="14" /></button>
        </div>
        <div class="panel-body">
          <div v-if="upcomingSchedule.length === 0" class="empty-row">暂无即将到来的赛程</div>
          <div v-for="r in upcomingSchedule" :key="r.id" class="sched-row">
            <div class="sched-time">
              <div class="sched-hm tnum">{{ r.scheduledTime.slice(11, 16) }}</div>
              <div class="sched-day">{{ r.scheduledTime.slice(5, 10) }}</div>
            </div>
            <div class="sched-info">
              <div class="sched-name">{{ r.eventName }}</div>
              <div class="sched-meta"><span><MapPin :size="12" /> {{ r.venue }}</span></div>
            </div>
            <div class="sched-go"><ChevronRight :size="16" /></div>
          </div>
        </div>
      </section>

      <!-- 我的成绩 -->
      <section class="panel animate-slide-fade delay-4">
        <div class="panel-head">
          <div class="panel-title"><Trophy :size="18" /> 我的成绩</div>
          <button class="link-btn" @click="router.push('/student/scores')">查看全部 <ChevronRight :size="14" /></button>
        </div>
        <div class="panel-body">
          <div v-if="myScores.length === 0" class="empty-row">暂无成绩，比赛结束后将展示在此</div>
          <div v-for="s in myScores.slice(0, 4)" :key="s.id" class="score-row" :class="{ record: s.isRecordBroken }">
            <div class="sc-medal">
              <Medal v-if="s.medal === 'gold'" :size="22" color="#F59E0B" />
              <Medal v-else-if="s.medal === 'silver'" :size="22" color="#9CA3AF" />
              <Medal v-else-if="s.medal === 'bronze'" :size="22" color="#B45309" />
              <Award v-else :size="18" color="#94A3B8" />
            </div>
            <div class="sc-info">
              <div class="sc-name">{{ s.eventName }}</div>
              <div class="sc-rank">第 {{ s.rank }} 名</div>
            </div>
            <div class="sc-result">
              <div class="sc-val tnum">{{ s.result }}<span class="sc-unit">{{ s.unit }}</span></div>
              <div v-if="s.isRecordBroken" class="sc-record">破纪录</div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 热门报名 + 公告 -->
    <div class="dual-grid">
      <section class="panel animate-slide-fade delay-5">
        <div class="panel-head">
          <div class="panel-title"><Zap :size="18" /> 热门报名</div>
          <button class="link-btn" @click="router.push('/student/register')">去报名 <ChevronRight :size="14" /></button>
        </div>
        <div class="panel-body">
          <div v-if="openEvents.length === 0" class="empty-row">暂无开放报名项目</div>
          <div v-for="e in openEvents" :key="e.id" class="event-row" @click="router.push('/student/register')">
            <div class="ev-tag" :class="e.category">{{ categoryLabel[e.category] }}</div>
            <div class="ev-info">
              <div class="ev-name">{{ e.name }}</div>
              <div class="ev-meta"><Clock :size="11" /> {{ e.scheduledTime.slice(5, 16) }}</div>
            </div>
            <div class="ev-quota">
              <div class="ev-num tnum">{{ e.quota - e.registeredCount }}</div>
              <div class="ev-l">余</div>
            </div>
          </div>
        </div>
      </section>

      <section class="panel animate-slide-fade delay-6">
        <div class="panel-head">
          <div class="panel-title"><Bell :size="18" /> 最新通知</div>
          <button class="link-btn" @click="router.push('/student/notices')">更多 <ChevronRight :size="14" /></button>
        </div>
        <div class="panel-body">
          <div v-if="myNotices.length === 0" class="empty-row">暂无通知</div>
          <div v-for="n in myNotices" :key="n.id" class="notice-row" @click="router.push('/student/notices')">
            <div class="nt-dot" :class="`level-${n.level}`" />
            <div class="nt-info">
              <div class="nt-title">{{ n.title }}</div>
              <div class="nt-time">{{ n.createdAt }}</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped lang="scss">
.home-page { display: flex; flex-direction: column; gap: 20px; }

.hero {
  position: relative; overflow: hidden;
  border-radius: 20px;
  padding: 36px 40px;
  color: #fff;
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(120deg, #F97316 0%, #EA580C 45%, #1E3A8A 130%);
  box-shadow: 0 14px 34px rgba(249, 115, 22, 0.32);
}
.hero-bg {
  position: absolute; inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.18), transparent 50%);
}
.hero-content { position: relative; z-index: 2; }
.hero-hi { font-size: 13px; opacity: 0.9; margin-bottom: 6px; letter-spacing: 0.04em; }
.hero-content h1 { font-size: 30px; font-weight: 900; margin: 0 0 8px; letter-spacing: 0.02em; }
.hero-content p { font-size: 13px; opacity: 0.9; margin: 0 0 20px; }
.hero-actions { display: flex; gap: 10px; }
.hero-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; border-radius: 10px; border: none;
  font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.22s ease;
}
.hero-btn.primary { background: #fff; color: #F97316; }
.hero-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 8px 18px rgba(0,0,0,0.2); }
.hero-btn.ghost { background: rgba(255,255,255,0.2); color: #fff; border: 1px solid rgba(255,255,255,0.4); }
.hero-btn.ghost:hover { background: rgba(255,255,255,0.3); }
.hero-emoji { position: relative; z-index: 1; opacity: 0.2; }
.hero-emoji svg { transform: rotate(-8deg); }

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.mini-stat {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 20px; background: #fff; border-radius: 14px;
  box-shadow: 0 4px 20px rgba(37,99,235,0.06);
  cursor: pointer; transition: all 0.22s ease;
}
.mini-stat:hover { transform: translateY(-3px); box-shadow: 0 12px 26px rgba(37,99,235,0.14); }
.ms-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 14px rgba(37,99,235,0.2); flex: 0 0 auto; }
.ms-n { font-size: 24px; font-weight: 800; color: #0F172A; line-height: 1; }
.ms-l { font-size: 12px; color: #64748B; margin-top: 4px; }

.dual-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.panel { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); overflow: hidden; }
.panel-head { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #F1F5F9; }
.panel-title { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 700; color: #0F172A; }
.link-btn { display: inline-flex; align-items: center; gap: 2px; background: none; border: none; color: #F97316; font-size: 12px; font-weight: 600; cursor: pointer; padding: 0; }
.link-btn:hover { color: #EA580C; }
.panel-body { padding: 12px 20px 18px; }
.empty-row { text-align: center; color: #94A3B8; padding: 24px 0; font-size: 13px; }

.sched-row { display: flex; align-items: center; gap: 14px; padding: 12px 0; border-bottom: 1px dashed #F1F5F9; cursor: pointer; }
.sched-row:last-child { border-bottom: none; }
.sched-row:hover { background: #F8FAFC; margin: 0 -20px; padding: 12px 20px; }
.sched-time { width: 56px; text-align: center; }
.sched-hm { font-size: 17px; font-weight: 800; color: #F97316; }
.sched-day { font-size: 11px; color: #94A3B8; }
.sched-info { flex: 1; }
.sched-name { font-size: 14px; font-weight: 700; color: #0F172A; }
.sched-meta { font-size: 12px; color: #64748B; margin-top: 4px; }
.sched-meta span { display: inline-flex; align-items: center; gap: 3px; }
.sched-go { color: #CBD5E1; }

.score-row { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px dashed #F1F5F9; }
.score-row:last-child { border-bottom: none; }
.score-row.record { background: linear-gradient(90deg, #FFFBEB, transparent); border-radius: 10px; padding: 12px 10px; margin: 0 -10px; }
.sc-medal { width: 36px; display: flex; justify-content: center; }
.sc-info { flex: 1; }
.sc-name { font-size: 14px; font-weight: 700; color: #0F172A; }
.sc-rank { font-size: 12px; color: #64748B; margin-top: 2px; }
.sc-result { text-align: right; }
.sc-val { font-size: 18px; font-weight: 800; color: #2563EB; }
.sc-unit { font-size: 11px; color: #94A3B8; margin-left: 3px; }
.sc-record { font-size: 10px; color: #F97316; font-weight: 700; background: #FFF7ED; padding: 1px 6px; border-radius: 4px; display: inline-block; margin-top: 2px; }

.event-row { display: flex; align-items: center; gap: 12px; padding: 11px 0; border-bottom: 1px dashed #F1F5F9; cursor: pointer; }
.event-row:last-child { border-bottom: none; }
.event-row:hover { background: #F8FAFC; margin: 0 -20px; padding: 11px 20px; }
.ev-tag { font-size: 10px; padding: 3px 8px; border-radius: 5px; font-weight: 700; flex: 0 0 auto; }
.ev-tag.track { background: #EFF6FF; color: #2563EB; }
.ev-tag.field { background: #FFF7ED; color: #F97316; }
.ev-tag.ball { background: #ECFDF5; color: #10B981; }
.ev-tag.fun { background: #F5F3FF; color: #8B5CF6; }
.ev-info { flex: 1; }
.ev-name { font-size: 13px; font-weight: 700; color: #0F172A; }
.ev-meta { font-size: 11px; color: #94A3B8; margin-top: 2px; display: inline-flex; align-items: center; gap: 3px; }
.ev-quota { text-align: center; }
.ev-num { font-size: 18px; font-weight: 800; color: #F97316; }
.ev-l { font-size: 10px; color: #94A3B8; }

.notice-row { display: flex; gap: 10px; padding: 11px 0; border-bottom: 1px dashed #F1F5F9; cursor: pointer; }
.notice-row:last-child { border-bottom: none; }
.notice-row:hover { background: #F8FAFC; margin: 0 -20px; padding: 11px 20px; }
.nt-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex: 0 0 auto; }
.nt-dot.level-info { background: #3B82F6; }
.nt-dot.level-success { background: #10B981; }
.nt-dot.level-warning { background: #F59E0B; }
.nt-dot.level-danger { background: #EF4444; }
.nt-title { font-size: 13px; color: #334155; font-weight: 600; line-height: 1.4; }
.nt-time { font-size: 11px; color: #94A3B8; margin-top: 3px; }

@media (max-width: 1000px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .dual-grid { grid-template-columns: 1fr; }
  .hero-emoji { display: none; }
}
</style>
