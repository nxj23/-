<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Trophy, Medal, Award, Download, Clock, TrendingUp, Inbox,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useScoreStore } from '@/stores/score'
import MedalBadge from '@/components/common/MedalBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const auth = useAuthStore()
const scoreStore = useScoreStore()

const myScores = computed(() =>
  scoreStore.scores.filter((s) => s.studentId === auth.user?.id),
)

const myMedals = computed(() => myScores.value.filter((s) => s.medal))
const myRecords = computed(() => myScores.value.filter((s) => s.isRecordBroken))
const bestRank = computed(() => {
  if (myScores.value.length === 0) return 0
  return Math.min(...myScores.value.map((s) => s.rank))
})

const sortKey = ref<'time' | 'rank'>('rank')
const sorted = computed(() => {
  const list = [...myScores.value]
  if (sortKey.value === 'rank') return list.sort((a, b) => a.rank - b.rank)
  return list.sort((a, b) => (a.publishedAt || '').localeCompare(b.publishedAt || ''))
})

function medalText(m?: 'gold' | 'silver' | 'bronze'): string {
  return m === 'gold' ? '金牌' : m === 'silver' ? '银牌' : m === 'bronze' ? '铜牌' : ''
}

function downloadCert(score: typeof myScores.value[number]): void {
  const win = window.open('', '_blank', 'width=820,height=580')
  if (!win) { ElMessage.warning('请允许弹窗以下载证书'); return }
  const medalLine = score.medal ? `<div class="cert-medal">${medalText(score.medal)}</div>` : ''
  const recordLine = score.isRecordBroken ? `<div class="cert-record">破校纪录</div>` : ''
  win.document.write(`
    <!doctype html><html><head><meta charset="utf-8"><title>成绩证书 - ${score.eventName}</title>
    <style>
      * { margin:0; padding:0; box-sizing:border-box; }
      body { font-family: 'Noto Sans SC', sans-serif; background:#F4F7FB; padding:30px; }
      .cert { width:760px; margin:0 auto; background:#fff; border-radius:24px; overflow:hidden; box-shadow:0 20px 60px rgba(15,23,42,0.18); border:8px solid transparent; background-image: linear-gradient(#fff,#fff), linear-gradient(135deg,#2563EB,#F97316); background-origin:border-box; background-clip:content-box,border-box; }
      .cert-head { background: linear-gradient(120deg,#1E3A8A,#2563EB,#F97316); color:#fff; padding:32px 40px; text-align:center; }
      .cert-school { font-size:13px; letter-spacing:0.3em; opacity:0.85; }
      .cert-title { font-size:30px; font-weight:900; margin-top:8px; letter-spacing:0.1em; }
      .cert-body { padding:44px 50px; text-align:center; }
      .cert-name { font-size:32px; font-weight:800; color:#0F172A; margin-bottom:6px; }
      .cert-class { font-size:14px; color:#64748B; }
      .cert-line { font-size:15px; color:#334155; margin:24px 0 8px; }
      .cert-event { font-size:24px; font-weight:800; color:#2563EB; }
      .cert-result { font-size:48px; font-weight:900; color:#F97316; margin:18px 0; }
      .cert-result span { font-size:18px; color:#94A3B8; }
      .cert-rank { font-size:16px; color:#475569; }
      .cert-medal { display:inline-block; margin-top:14px; padding:8px 24px; background:linear-gradient(135deg,#FBBF24,#F59E0B); color:#fff; border-radius:24px; font-weight:700; }
      .cert-record { display:inline-block; margin-left:10px; padding:8px 18px; background:#FEF3C7; color:#B45309; border-radius:24px; font-weight:700; }
      .cert-foot { padding:20px 50px 36px; display:flex; justify-content:space-between; align-items:center; border-top:1px dashed #E2E8F0; margin-top:20px; }
      .cert-date { font-size:13px; color:#94A3B8; }
      .cert-seal { width:90px; height:90px; border-radius:50%; border:3px solid #EF4444; color:#EF4444; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:14px; transform:rotate(-12deg); opacity:0.85; }
    </style></head>
    <body><div class="cert">
      <div class="cert-head">
        <div class="cert-school">校 园 运 动 会 管 理 系 统</div>
        <div class="cert-title">成 绩 证 书</div>
      </div>
      <div class="cert-body">
        <div class="cert-name">${auth.user?.name}</div>
        <div class="cert-class">${auth.user?.class} · ${auth.user?.grade}</div>
        <div class="cert-line">在 2026 校园运动会</div>
        <div class="cert-event">${score.eventName}</div>
        <div class="cert-line">项目中取得成绩</div>
        <div class="cert-result">${score.result}<span>${score.unit}</span></div>
        <div class="cert-rank">排名第 ${score.rank} 名</div>
        ${medalLine}${recordLine}
      </div>
      <div class="cert-foot">
        <div class="cert-date">颁发日期：${score.publishedAt || new Date().toISOString().slice(0,10)}</div>
        <div class="cert-seal">校园<br/>运动会</div>
      </div>
    </div>
    <script>window.onload=function(){setTimeout(function(){window.print()},300)}<\/script>
    </body></html>
  `)
  win.document.close()
}
</script>

<template>
  <div class="scores-page">
    <div class="page-head">
      <div>
        <h1>我的成绩</h1>
        <p>查看个人参赛成绩与奖牌 · 支持下载成绩证书</p>
      </div>
    </div>

    <!-- 概览卡片 -->
    <div class="overview-grid">
      <div class="ov-card">
        <div class="ov-icon" style="background:linear-gradient(135deg,#2563EB,#3B82F6)"><Trophy :size="22" color="#fff" /></div>
        <div class="ov-body"><div class="ov-n tnum">{{ myScores.length }}</div><div class="ov-l">参赛项目</div></div>
      </div>
      <div class="ov-card">
        <div class="ov-icon" style="background:linear-gradient(135deg,#FBBF24,#F59E0B)"><Medal :size="22" color="#fff" /></div>
        <div class="ov-body"><div class="ov-n tnum">{{ myMedals.length }}</div><div class="ov-l">获得奖牌</div></div>
      </div>
      <div class="ov-card">
        <div class="ov-icon" style="background:linear-gradient(135deg,#F97316,#FB923C)"><TrendingUp :size="22" color="#fff" /></div>
        <div class="ov-body"><div class="ov-n tnum">{{ myRecords.length }}</div><div class="ov-l">破纪录</div></div>
      </div>
      <div class="ov-card">
        <div class="ov-icon" style="background:linear-gradient(135deg,#10B981,#34D399)"><Award :size="22" color="#fff" /></div>
        <div class="ov-body"><div class="ov-n tnum">{{ bestRank > 0 ? '第' + bestRank : '—' }}</div><div class="ov-l">最佳排名</div></div>
      </div>
    </div>

    <!-- 排序 -->
    <div v-if="myScores.length > 0" class="sort-bar">
      <span class="sort-label">排序：</span>
      <button :class="{ active: sortKey === 'rank' }" @click="sortKey = 'rank'">按排名</button>
      <button :class="{ active: sortKey === 'time' }" @click="sortKey = 'time'">按时间</button>
    </div>

    <!-- 成绩列表 -->
    <div v-if="myScores.length === 0" class="empty-card">
      <EmptyState :icon="Inbox" text="暂无参赛成绩" sub="比赛结束后教师将录入并发布成绩" />
    </div>
    <div v-else class="score-grid">
      <article
        v-for="(s, i) in sorted"
        :key="s.id"
        class="score-card animate-slide-fade"
        :style="{ animationDelay: i * 0.05 + 's' }"
        :class="{ record: s.isRecordBroken, medaled: !!s.medal }"
      >
        <div class="card-glow" v-if="s.medal" :class="`m-${s.medal}`" />
        <div class="card-head">
          <div class="head-left">
            <MedalBadge v-if="s.rank <= 3" :medal="s.medal" :rank="s.rank" :size="44" />
            <div v-else class="rank-circle tnum">{{ s.rank }}</div>
          </div>
          <div class="head-right">
            <div class="ev-name">{{ s.eventName }}</div>
            <div class="ev-meta"><Clock :size="11" /> {{ s.publishedAt || '—' }}</div>
          </div>
        </div>
        <div class="card-result">
          <div class="result-num tnum">{{ s.result }}<span class="result-unit">{{ s.unit }}</span></div>
          <div class="result-rank">排名第 {{ s.rank }} 名</div>
        </div>
        <div class="card-tags">
          <span v-if="s.medal" class="tag medal" :class="`m-${s.medal}`">{{ medalText(s.medal) }}</span>
          <span v-if="s.isRecordBroken" class="tag record animate-record">破校纪录</span>
          <span class="tag class-tag">{{ s.class }}</span>
        </div>
        <button class="cert-btn" @click="downloadCert(s)">
          <Download :size="14" /> 下载证书
        </button>
      </article>
    </div>
  </div>
</template>

<style scoped lang="scss">
.scores-page { display: flex; flex-direction: column; gap: 18px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }

.overview-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.ov-card { display: flex; align-items: center; gap: 14px; padding: 18px 20px; background: #fff; border-radius: 14px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }
.ov-icon { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 14px rgba(37,99,235,0.2); }
.ov-n { font-size: 24px; font-weight: 800; color: #0F172A; }
.ov-l { font-size: 12px; color: #64748B; margin-top: 2px; }

.sort-bar { display: flex; align-items: center; gap: 8px; }
.sort-label { font-size: 13px; color: #64748B; font-weight: 600; }
.sort-bar button { padding: 6px 14px; border: 1px solid #E2E8F0; border-radius: 8px; background: #fff; font-size: 12px; font-weight: 600; color: #475569; cursor: pointer; transition: all 0.2s; }
.sort-bar button.active { border-color: #F97316; color: #F97316; background: #FFF7ED; }

.empty-card { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }

.score-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.score-card { position: relative; background: #fff; border-radius: 16px; padding: 22px; box-shadow: 0 4px 20px rgba(37,99,235,0.07); overflow: hidden; transition: transform 0.28s cubic-bezier(0.22,1,0.36,1), box-shadow 0.28s; }
.score-card:hover { transform: translateY(-4px); box-shadow: 0 14px 32px rgba(37,99,235,0.16); }
.score-card.medaled { border: 1px solid #FDE68A; }
.score-card.record { border: 2px solid #FBBF24; }
.card-glow { position: absolute; top: -40px; right: -40px; width: 120px; height: 120px; border-radius: 50%; opacity: 0.12; filter: blur(20px); }
.card-glow.m-gold { background: #FBBF24; }
.card-glow.m-silver { background: #9CA3AF; }
.card-glow.m-bronze { background: #B45309; }

.card-head { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.rank-circle { width: 44px; height: 44px; border-radius: 50%; background: #F1F5F9; color: #64748B; font-weight: 800; font-size: 16px; display: flex; align-items: center; justify-content: center; }
.head-right { flex: 1; }
.ev-name { font-size: 16px; font-weight: 800; color: #0F172A; }
.ev-meta { font-size: 11px; color: #94A3B8; margin-top: 3px; display: inline-flex; align-items: center; gap: 3px; }

.card-result { padding: 14px 0; border-top: 1px dashed #F1F5F9; border-bottom: 1px dashed #F1F5F9; text-align: center; }
.result-num { font-size: 36px; font-weight: 900; color: #2563EB; line-height: 1; }
.result-unit { font-size: 14px; color: #94A3B8; margin-left: 4px; }
.result-rank { font-size: 13px; color: #64748B; margin-top: 6px; }

.card-tags { display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; }
.tag { font-size: 11px; padding: 3px 9px; border-radius: 6px; font-weight: 700; }
.tag.medal.m-gold { background: #FEF3C7; color: #B45309; }
.tag.medal.m-silver { background: #F1F5F9; color: #475569; }
.tag.medal.m-bronze { background: #FED7AA; color: #9A3412; }
.tag.record { background: linear-gradient(90deg, #FBBF24, #F59E0B); color: #fff; }
.tag.class-tag { background: #EFF6FF; color: #2563EB; }

.cert-btn { width: 100%; margin-top: 14px; padding: 10px 0; border: 1px solid #E2E8F0; border-radius: 10px; background: #fff; color: #475569; font-size: 13px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s; }
.cert-btn:hover { border-color: #2563EB; color: #2563EB; background: #EFF6FF; }

@media (max-width: 900px) {
  .overview-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
