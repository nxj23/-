<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, X, ShieldCheck, AlertTriangle, Inbox } from 'lucide-vue-next'
import { useRegistrationStore } from '@/stores/registration'
import type { Registration, RegistrationStatus } from '@/types'
import EmptyState from '@/components/common/EmptyState.vue'

const store = useRegistrationStore()

const filterStatus = ref<RegistrationStatus | 'all'>('all')
const keyword = ref('')
const selected = ref<string[]>([])

const statusMeta: Record<RegistrationStatus, { label: string; cls: string }> = {
  pending: { label: '待审批', cls: 'pending' },
  approved: { label: '已通过', cls: 'approved' },
  rejected: { label: '已驳回', cls: 'rejected' },
}

const filtered = computed(() => {
  let list = store.registrations
  if (filterStatus.value !== 'all') list = list.filter((r) => r.status === filterStatus.value)
  if (keyword.value) {
    const k = keyword.value
    list = list.filter(
      (r) => r.studentName.includes(k) || r.eventName.includes(k) || r.class.includes(k),
    )
  }
  return [...list].sort((a, b) => b.createdAt.localeCompare(a.createdAt))
})

const pendingList = computed(() => filtered.value.filter((r) => r.status === 'pending'))

const summary = computed(() => ({
  total: store.registrations.length,
  pending: store.registrations.filter((r) => r.status === 'pending').length,
  approved: store.registrations.filter((r) => r.status === 'approved').length,
  rejected: store.registrations.filter((r) => r.status === 'rejected').length,
}))

function toggleSelect(id: string): void {
  const idx = selected.value.indexOf(id)
  if (idx === -1) selected.value.push(id)
  else selected.value.splice(idx, 1)
}
const allChecked = computed(
  () => pendingList.value.length > 0 && selected.value.length === pendingList.value.length,
)
function toggleAll(): void {
  if (allChecked.value) selected.value = []
  else selected.value = pendingList.value.map((r) => r.id)
}

async function approve(id: string): Promise<void> {
  await store.updateStatus(id, 'approved')
  ElMessage.success('已通过报名')
}
async function reject(id: string): Promise<void> {
  await store.updateStatus(id, 'rejected')
  ElMessage.info('已驳回报名')
}

async function batchApprove(): Promise<void> {
  if (selected.value.length === 0) { ElMessage.warning('请先选择待审批记录'); return }
  try {
    await ElMessageBox.confirm(`确认批量通过 ${selected.value.length} 条报名？`, '批量审批', {
      confirmButtonText: '通过', cancelButtonText: '取消', type: 'success',
    })
    for (const id of [...selected.value]) {
      await store.updateStatus(id, 'approved')
    }
    selected.value = []
    ElMessage.success('批量审批完成')
  } catch { /* cancelled */ }
}

function isConflict(r: Registration): boolean {
  return !!r.conflict
}
</script>

<template>
  <div class="approvals-page">
    <div class="page-head">
      <div>
        <h1>报名审批</h1>
        <p>审核学生报名申请 · 共 {{ summary.total }} 条记录</p>
      </div>
      <button class="primary-btn" :disabled="selected.length === 0" @click="batchApprove">
        <Check :size="16" /> 批量通过 ({{ selected.length }})
      </button>
    </div>

    <!-- 汇总卡片 -->
    <div class="summary-grid">
      <div class="sum-card total"><div class="sum-num tnum">{{ summary.total }}</div><div class="sum-label">报名总数</div></div>
      <div class="sum-card pending"><div class="sum-num tnum">{{ summary.pending }}</div><div class="sum-label">待审批</div></div>
      <div class="sum-card approved"><div class="sum-num tnum">{{ summary.approved }}</div><div class="sum-label">已通过</div></div>
      <div class="sum-card rejected"><div class="sum-num tnum">{{ summary.rejected }}</div><div class="sum-label">已驳回</div></div>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <input v-model="keyword" class="search-input" placeholder="搜索学生 / 项目 / 班级" />
      <div class="status-tabs">
        <button :class="{ active: filterStatus === 'all' }" @click="filterStatus = 'all'">全部</button>
        <button :class="{ active: filterStatus === 'pending' }" @click="filterStatus = 'pending'">待审批</button>
        <button :class="{ active: filterStatus === 'approved' }" @click="filterStatus = 'approved'">已通过</button>
        <button :class="{ active: filterStatus === 'rejected' }" @click="filterStatus = 'rejected'">已驳回</button>
      </div>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <div v-if="filtered.length === 0" class="empty-wrap">
        <EmptyState :icon="Inbox" text="暂无报名记录" sub="学生提交报名后将显示在此处" />
      </div>
      <div v-else class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-check" v-if="filterStatus === 'pending' || filterStatus === 'all'">
                <input type="checkbox" :checked="allChecked" @change="toggleAll" :disabled="pendingList.length === 0" />
              </th>
              <th>学生</th>
              <th>班级</th>
              <th>项目</th>
              <th>比赛时间</th>
              <th>场地</th>
              <th>提交时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in filtered" :key="r.id" :class="{ 'row-conflict': isConflict(r) }">
              <td class="col-check" v-if="filterStatus === 'pending' || filterStatus === 'all'">
                <input
                  v-if="r.status === 'pending'"
                  type="checkbox"
                  :checked="selected.includes(r.id)"
                  @change="toggleSelect(r.id)"
                />
              </td>
              <td>
                <div class="stu-cell">
                  <div class="stu-avatar">{{ r.studentName.charAt(0) }}</div>
                  <span>{{ r.studentName }}</span>
                </div>
              </td>
              <td>{{ r.class }}</td>
              <td class="event-cell">{{ r.eventName }}</td>
              <td class="tnum">{{ r.scheduledTime }}</td>
              <td>{{ r.venue }}</td>
              <td class="tnum muted">{{ r.createdAt }}</td>
              <td>
                <span class="status-pill" :class="statusMeta[r.status].cls">
                  {{ statusMeta[r.status].label }}
                </span>
                <div v-if="r.conflict" class="conflict-tip">
                  <AlertTriangle :size="11" /> {{ r.conflict }}
                </div>
              </td>
              <td>
                <div v-if="r.status === 'pending'" class="row-actions">
                  <button class="op-btn ok" @click="approve(r.id)"><Check :size="13" /> 通过</button>
                  <button class="op-btn no" @click="reject(r.id)"><X :size="13" /> 驳回</button>
                </div>
                <span v-else class="done-text"><ShieldCheck :size="13" /> 已处理</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.approvals-page { display: flex; flex-direction: column; gap: 18px; }

.page-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }
.primary-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; border: none; border-radius: 10px;
  background: linear-gradient(135deg, #10B981, #34D399);
  color: #fff; font-size: 13px; font-weight: 700; cursor: pointer;
  box-shadow: 0 8px 18px rgba(16, 185, 129, 0.3);
  transition: all 0.22s ease;
}
.primary-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(16,185,129,0.38); }
.primary-btn:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }

.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.sum-card {
  padding: 18px 20px; border-radius: 14px; background: #fff;
  box-shadow: 0 4px 20px rgba(37,99,235,0.06);
  border-left: 4px solid #94A3B8;
}
.sum-card.total { border-left-color: #2563EB; }
.sum-card.pending { border-left-color: #F97316; }
.sum-card.approved { border-left-color: #10B981; }
.sum-card.rejected { border-left-color: #EF4444; }
.sum-num { font-size: 26px; font-weight: 800; color: #0F172A; }
.sum-card.pending .sum-num { color: #F97316; }
.sum-card.approved .sum-num { color: #10B981; }
.sum-card.rejected .sum-num { color: #EF4444; }
.sum-label { font-size: 12px; color: #64748B; margin-top: 2px; }

.filter-bar {
  display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
  padding: 12px 16px; background: #fff; border-radius: 12px;
  box-shadow: 0 4px 20px rgba(37,99,235,0.06);
}
.search-input {
  flex: 1; min-width: 200px;
  padding: 9px 14px; border: 1px solid #E2E8F0; border-radius: 10px;
  font-size: 13px; outline: none;
}
.search-input:focus { border-color: #2563EB; }
.status-tabs { display: flex; gap: 4px; background: #F1F5F9; padding: 4px; border-radius: 10px; }
.status-tabs button {
  padding: 7px 14px; border: none; background: transparent;
  border-radius: 7px; font-size: 12px; font-weight: 600; color: #64748B; cursor: pointer;
  transition: all 0.2s ease;
}
.status-tabs button.active { background: #fff; color: #2563EB; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }

.table-card {
  background: #fff; border-radius: 14px; box-shadow: 0 4px 20px rgba(37,99,235,0.06);
  overflow: hidden;
}
.empty-wrap { padding: 30px; }
.table-scroll { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; min-width: 920px; }
.data-table thead th {
  background: #F8FAFC; color: #475569;
  font-size: 12px; font-weight: 700; text-align: left;
  padding: 12px 14px; border-bottom: 1px solid #E2E8F0;
  white-space: nowrap;
}
.data-table tbody td {
  padding: 12px 14px; border-bottom: 1px solid #F1F5F9;
  font-size: 13px; color: #334155; vertical-align: middle;
}
.data-table tbody tr:hover { background: #F8FAFC; }
.data-table tbody tr.row-conflict { background: #FFFBEB; }
.data-table tbody tr.row-conflict:hover { background: #FEF3C7; }
.col-check { width: 40px; text-align: center; }
.col-check input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; accent-color: #2563EB; }

.stu-cell { display: flex; align-items: center; gap: 8px; font-weight: 600; color: #0F172A; }
.stu-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #2563EB, #F97316);
  color: #fff; font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.event-cell { font-weight: 600; color: #2563EB; }
.muted { color: #94A3B8; }

.status-pill {
  display: inline-block; padding: 3px 10px; border-radius: 12px;
  font-size: 11px; font-weight: 700;
}
.status-pill.pending { background: #FFF7ED; color: #F97316; }
.status-pill.approved { background: #ECFDF5; color: #10B981; }
.status-pill.rejected { background: #FEF2F2; color: #EF4444; }
.conflict-tip {
  font-size: 11px; color: #EF4444; margin-top: 4px; display: flex; align-items: center; gap: 3px;
}

.row-actions { display: flex; gap: 6px; }
.op-btn {
  padding: 5px 10px; border-radius: 7px; border: 1px solid #E2E8F0;
  background: #fff; font-size: 11px; font-weight: 600; color: #475569;
  cursor: pointer; display: inline-flex; align-items: center; gap: 3px;
  transition: all 0.2s ease;
}
.op-btn.ok:hover { border-color: #10B981; color: #10B981; background: #ECFDF5; }
.op-btn.no:hover { border-color: #EF4444; color: #EF4444; background: #FEF2F2; }
.done-text { font-size: 12px; color: #94A3B8; display: inline-flex; align-items: center; gap: 4px; }

@media (max-width: 800px) {
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
