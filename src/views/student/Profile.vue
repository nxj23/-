<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  User, IdCard, GraduationCap, Mail, Phone, Trophy, Medal, Award,
  ClipboardList, Calendar, Download, Pencil,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useRegistrationStore } from '@/stores/registration'
import { useScoreStore } from '@/stores/score'
import { ElMessage } from 'element-plus'
import MedalBadge from '@/components/common/MedalBadge.vue'

const auth = useAuthStore()
const regStore = useRegistrationStore()
const scoreStore = useScoreStore()

const editing = ref(false)
const form = ref({
  name: auth.user?.name || '',
  email: 'zhangming@school.edu.cn',
  phone: '138****6688',
})

const myRegs = computed(() => regStore.registrations.filter((r) => r.studentId === auth.user?.id))
const myScores = computed(() => scoreStore.scores.filter((s) => s.studentId === auth.user?.id))
const myMedals = computed(() => myScores.value.filter((s) => s.medal))
const myRecords = computed(() => myScores.value.filter((s) => s.isRecordBroken))

const medalBreakdown = computed(() => {
  const m = { gold: 0, silver: 0, bronze: 0 }
  myMedals.value.forEach((s) => { if (s.medal) m[s.medal] += 1 })
  return m
})

const regHistory = computed(() =>
  [...myRegs.value].sort((a, b) => b.createdAt.localeCompare(a.createdAt)),
)

function saveProfile(): void {
  if (auth.user) auth.user.name = form.value.name
  editing.value = false
  ElMessage.success('资料已保存（演示）')
}

function medalText(m?: 'gold' | 'silver' | 'bronze'): string {
  return m === 'gold' ? '金牌' : m === 'silver' ? '银牌' : m === 'bronze' ? '铜牌' : ''
}
</script>

<template>
  <div class="profile-page">
    <!-- 个人卡片 -->
    <section class="profile-card animate-slide-fade">
      <div class="cover" />
      <div class="profile-body">
        <div class="avatar">{{ auth.user?.name?.charAt(0) }}</div>
        <div class="profile-info">
          <div class="name-row">
            <h2>{{ auth.user?.name }}</h2>
            <span class="role-tag">学生</span>
          </div>
          <div class="id-row">
            <span class="id-item"><IdCard :size="13" /> {{ auth.user?.id }}</span>
            <span class="id-item"><GraduationCap :size="13" /> {{ auth.user?.class }}</span>
          </div>
        </div>
        <button class="edit-btn" @click="editing = !editing">
          <Pencil :size="14" /> {{ editing ? '取消' : '编辑资料' }}
        </button>
      </div>
    </section>

    <!-- 资料编辑 + 数据概览 -->
    <div class="dual-grid">
      <!-- 个人资料 -->
      <section class="panel">
        <div class="panel-head"><div class="panel-title"><User :size="18" /> 个人资料</div></div>
        <div class="panel-body">
          <div class="info-list">
            <div class="info-item">
              <div class="info-label"><User :size="13" /> 姓名</div>
              <input v-if="editing" v-model="form.name" class="info-input" />
              <div v-else class="info-value">{{ auth.user?.name }}</div>
            </div>
            <div class="info-item">
              <div class="info-label"><IdCard :size="13" /> 学号</div>
              <div class="info-value muted">{{ auth.user?.id }}</div>
            </div>
            <div class="info-item">
              <div class="info-label"><GraduationCap :size="13" /> 班级</div>
              <div class="info-value">{{ auth.user?.class }}</div>
            </div>
            <div class="info-item">
              <div class="info-label"><Calendar :size="13" /> 年级</div>
              <div class="info-value">{{ auth.user?.grade }}</div>
            </div>
            <div class="info-item">
              <div class="info-label"><Mail :size="13" /> 邮箱</div>
              <input v-if="editing" v-model="form.email" class="info-input" />
              <div v-else class="info-value">{{ form.email }}</div>
            </div>
            <div class="info-item">
              <div class="info-label"><Phone :size="13" /> 电话</div>
              <input v-if="editing" v-model="form.phone" class="info-input" />
              <div v-else class="info-value">{{ form.phone }}</div>
            </div>
          </div>
          <button v-if="editing" class="save-btn" @click="saveProfile">保存修改</button>
        </div>
      </section>

      <!-- 奖牌成就 -->
      <section class="panel">
        <div class="panel-head"><div class="panel-title"><Trophy :size="18" /> 我的成就</div></div>
        <div class="panel-body">
          <div class="medal-showcase">
            <div class="medal-slot gold">
              <div class="medal-circle"><MedalBadge medal="gold" :size="50" /></div>
              <div class="medal-count tnum">{{ medalBreakdown.gold }}</div>
              <div class="medal-label">金牌</div>
            </div>
            <div class="medal-slot silver">
              <div class="medal-circle"><MedalBadge medal="silver" :size="50" /></div>
              <div class="medal-count tnum">{{ medalBreakdown.silver }}</div>
              <div class="medal-label">银牌</div>
            </div>
            <div class="medal-slot bronze">
              <div class="medal-circle"><MedalBadge medal="bronze" :size="50" /></div>
              <div class="medal-count tnum">{{ medalBreakdown.bronze }}</div>
              <div class="medal-label">铜牌</div>
            </div>
          </div>
          <div class="achv-stats">
            <div class="achv-row"><span><Award :size="14" /> 参赛项目</span><span class="achv-num tnum">{{ myScores.length }}</span></div>
            <div class="achv-row"><span><Trophy :size="14" /> 获奖牌数</span><span class="achv-num tnum">{{ myMedals.length }}</span></div>
            <div class="achv-row"><span><Medal :size="14" /> 破纪录</span><span class="achv-num tnum">{{ myRecords.length }}</span></div>
            <div class="achv-row"><span><ClipboardList :size="14" /> 报名总数</span><span class="achv-num tnum">{{ myRegs.length }}</span></div>
          </div>
        </div>
      </section>
    </div>

    <!-- 报名历史 -->
    <section class="panel">
      <div class="panel-head"><div class="panel-title"><ClipboardList :size="18" /> 报名历史</div></div>
      <div v-if="regHistory.length === 0" class="empty-row">暂无报名记录</div>
      <div v-else class="table-scroll">
        <table class="data-table">
          <thead>
            <tr><th>项目</th><th>比赛时间</th><th>场地</th><th>提交时间</th><th>状态</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in regHistory" :key="r.id">
              <td class="name-cell">{{ r.eventName }}</td>
              <td class="tnum">{{ r.scheduledTime }}</td>
              <td>{{ r.venue }}</td>
              <td class="tnum muted">{{ r.createdAt }}</td>
              <td><span class="status-pill" :class="r.status">{{ r.status === 'pending' ? '审核中' : r.status === 'approved' ? '已通过' : '已驳回' }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.profile-page { display: flex; flex-direction: column; gap: 18px; }

.profile-card {
  background: #fff; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 20px rgba(37,99,235,0.07);
}
.cover { height: 110px; background: linear-gradient(120deg, #F97316 0%, #EA580C 45%, #1E3A8A 130%); }
.profile-body { position: relative; padding: 0 28px 24px; display: flex; align-items: flex-end; gap: 22px; }
.avatar {
  width: 92px; height: 92px; border-radius: 24px;
  background: linear-gradient(135deg, #2563EB, #F97316);
  color: #fff; font-size: 38px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  margin-top: -46px; border: 4px solid #fff;
  box-shadow: 0 12px 28px rgba(37,99,235,0.28);
}
.profile-info { flex: 1; padding-bottom: 8px; }
.name-row { display: flex; align-items: center; gap: 10px; }
.name-row h2 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0; }
.role-tag { font-size: 11px; padding: 3px 10px; border-radius: 6px; background: #FFF7ED; color: #F97316; font-weight: 700; }
.id-row { display: flex; gap: 16px; margin-top: 8px; }
.id-item { font-size: 13px; color: #64748B; display: inline-flex; align-items: center; gap: 5px; }
.edit-btn { display: inline-flex; align-items: center; gap: 5px; padding: 8px 14px; border-radius: 8px; border: 1px solid #E2E8F0; background: #fff; color: #475569; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; margin-bottom: 8px; }
.edit-btn:hover { border-color: #F97316; color: #F97316; background: #FFF7ED; }

.dual-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.panel { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); overflow: hidden; }
.panel-head { display: flex; align-items: center; gap: 8px; padding: 16px 22px; border-bottom: 1px solid #F1F5F9; font-size: 15px; font-weight: 700; color: #0F172A; }
.panel-body { padding: 20px 22px; }

.info-list { display: flex; flex-direction: column; gap: 16px; }
.info-item { display: flex; align-items: center; gap: 16px; }
.info-label { width: 72px; font-size: 12px; color: #94A3B8; font-weight: 600; display: inline-flex; align-items: center; gap: 5px; flex: 0 0 auto; }
.info-value { font-size: 14px; color: #0F172A; font-weight: 600; }
.info-value.muted { color: #94A3B8; }
.info-input { flex: 1; padding: 8px 12px; border: 1px solid #E2E8F0; border-radius: 8px; font-size: 14px; color: #0F172A; outline: none; }
.info-input:focus { border-color: #F97316; box-shadow: 0 0 0 3px rgba(249,115,22,0.1); }
.save-btn { margin-top: 18px; width: 100%; padding: 11px 0; border: none; border-radius: 10px; background: linear-gradient(135deg, #F97316, #FB923C); color: #fff; font-size: 14px; font-weight: 700; cursor: pointer; box-shadow: 0 8px 18px rgba(249,115,22,0.3); }
.save-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(249,115,22,0.4); }

.medal-showcase { display: flex; justify-content: space-around; padding: 10px 0 20px; }
.medal-slot { text-align: center; }
.medal-circle { display: flex; justify-content: center; margin-bottom: 8px; }
.medal-count { font-size: 26px; font-weight: 800; color: #0F172A; }
.medal-slot.gold .medal-count { color: #F59E0B; }
.medal-slot.silver .medal-count { color: #64748B; }
.medal-slot.bronze .medal-count { color: #B45309; }
.medal-label { font-size: 12px; color: #64748B; margin-top: 2px; }

.achv-stats { border-top: 1px dashed #F1F5F9; padding-top: 14px; }
.achv-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; font-size: 13px; color: #475569; }
.achv-row span { display: inline-flex; align-items: center; gap: 6px; }
.achv-num { font-size: 16px; font-weight: 800; color: #F97316; }

.empty-row { text-align: center; color: #94A3B8; padding: 30px; font-size: 13px; }
.table-scroll { overflow-x: auto; padding: 8px 22px 18px; }
.data-table { width: 100%; border-collapse: collapse; min-width: 560px; }
.data-table thead th { background: #F8FAFC; color: #475569; font-size: 12px; font-weight: 700; padding: 10px 14px; border-bottom: 1px solid #E2E8F0; text-align: left; }
.data-table tbody td { padding: 11px 14px; border-bottom: 1px solid #F1F5F9; font-size: 13px; color: #334155; }
.data-table tbody tr:hover { background: #F8FAFC; }
.name-cell { font-weight: 700; color: #0F172A; }
.muted { color: #94A3B8; }
.status-pill { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; }
.status-pill.pending { background: #FFF7ED; color: #F97316; }
.status-pill.approved { background: #ECFDF5; color: #10B981; }
.status-pill.rejected { background: #FEF2F2; color: #EF4444; }

@media (max-width: 900px) {
  .dual-grid { grid-template-columns: 1fr; }
  .profile-body { flex-direction: column; align-items: flex-start; gap: 14px; }
}
</style>
