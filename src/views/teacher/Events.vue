<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Trophy, Pencil, Trash2, MapPin, Clock, Users,
  Search, Zap, Target, Volleyball, PartyPopper,
} from 'lucide-vue-next'
import { useEventStore } from '@/stores/event'
import type { SportsEvent, EventCategory, Gender, EventStatus } from '@/types'
import EmptyState from '@/components/common/EmptyState.vue'

const store = useEventStore()

const filterCategory = ref<EventCategory | 'all'>('all')
const filterStatus = ref<EventStatus | 'all'>('all')
const keyword = ref('')

const filtered = computed(() =>
  store.events.filter((e) => {
    if (filterCategory.value !== 'all' && e.category !== filterCategory.value) return false
    if (filterStatus.value !== 'all' && e.status !== filterStatus.value) return false
    if (keyword.value && !e.name.includes(keyword.value)) return false
    return true
  }),
)

const categoryMeta: Record<EventCategory, { label: string; color: string; icon: typeof Zap }> = {
  track: { label: '田径', color: '#2563EB', icon: Zap },
  field: { label: '田赛', color: '#F97316', icon: Target },
  ball: { label: '球类', color: '#10B981', icon: Volleyball },
  fun: { label: '趣味', color: '#8B5CF6', icon: PartyPopper },
}
const genderLabel: Record<Gender, string> = { male: '男子', female: '女子', mixed: '混合' }
const statusMeta: Record<EventStatus, { label: string; cls: string }> = {
  open: { label: '报名中', cls: 'open' },
  closed: { label: '已截止', cls: 'closed' },
  finished: { label: '已完赛', cls: 'finished' },
}

const dialogVisible = ref(false)
const editing = ref(false)
const form = reactive({
  id: '',
  name: '',
  category: 'track' as EventCategory,
  gender: 'male' as Gender,
  quota: 8,
  venue: '',
  scheduledTime: '',
  record: '',
  unit: '秒',
  status: 'open' as EventStatus,
  group: '',
  description: '',
})

function resetForm(): void {
  Object.assign(form, {
    id: '', name: '', category: 'track', gender: 'male', quota: 8,
    venue: '', scheduledTime: '', record: '', unit: '秒',
    status: 'open', group: '', description: '',
  })
}

function openCreate(): void {
  resetForm()
  editing.value = false
  dialogVisible.value = true
}

function openEdit(e: SportsEvent): void {
  Object.assign(form, {
    id: e.id, name: e.name, category: e.category, gender: e.gender,
    quota: e.quota, venue: e.venue, scheduledTime: e.scheduledTime,
    record: e.record || '', unit: e.unit, status: e.status,
    group: e.group || '', description: e.description || '',
  })
  editing.value = true
  dialogVisible.value = true
}

async function handleSubmit(): Promise<void> {
  if (!form.name.trim()) { ElMessage.warning('请输入项目名称'); return }
  if (!form.venue.trim()) { ElMessage.warning('请输入比赛场地'); return }
  if (!form.scheduledTime) { ElMessage.warning('请选择比赛时间'); return }
  if (form.quota <= 0) { ElMessage.warning('名额必须大于 0'); return }

  const payload = {
    name: form.name.trim(),
    category: form.category,
    gender: form.gender,
    quota: Number(form.quota),
    venue: form.venue.trim(),
    scheduledTime: form.scheduledTime,
    record: form.record.trim() || undefined,
    unit: form.unit,
    status: form.status,
    group: form.group.trim() || undefined,
    description: form.description.trim() || undefined,
  }

  if (editing.value) {
    await store.update(form.id, payload)
    ElMessage.success('项目已更新')
  } else {
    await store.create(payload as Omit<SportsEvent, 'id' | 'registeredCount'>)
    ElMessage.success('项目已创建')
  }
  dialogVisible.value = false
}

async function handleDelete(e: SportsEvent): Promise<void> {
  try {
    await ElMessageBox.confirm(`确定删除项目「${e.name}」吗？相关报名记录将保留。`, '删除确认', {
      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
    })
    await store.remove(e.id)
    ElMessage.success('已删除')
  } catch { /* cancelled */ }
}

function quotaPercent(e: SportsEvent): number {
  return Math.min(100, Math.round((e.registeredCount / e.quota) * 100))
}
</script>

<template>
  <div class="events-page">
    <div class="page-head">
      <div>
        <h1>赛事管理</h1>
        <p>管理运动会全部比赛项目 · 共 {{ store.events.length }} 个项目</p>
      </div>
      <button class="primary-btn" @click="openCreate">
        <Plus :size="16" /> 新增项目
      </button>
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
      <el-select v-model="filterStatus" size="default" style="width: 130px">
        <el-option label="全部状态" value="all" />
        <el-option label="报名中" value="open" />
        <el-option label="已截止" value="closed" />
        <el-option label="已完赛" value="finished" />
      </el-select>
    </div>

    <!-- 项目卡片网格 -->
    <div v-if="filtered.length > 0" class="card-grid">
      <article
        v-for="(e, i) in filtered"
        :key="e.id"
        class="event-card animate-slide-fade"
        :style="{ animationDelay: i * 0.04 + 's' }"
      >
        <div class="card-top" :style="{ background: categoryMeta[e.category].color }">
          <div class="cat-icon">
            <component :is="categoryMeta[e.category].icon" :size="20" color="#fff" :stroke-width="2.2" />
          </div>
          <span class="status-tag" :class="statusMeta[e.status].cls">{{ statusMeta[e.status].label }}</span>
        </div>
        <div class="card-body">
          <div class="card-title-row">
            <h3>{{ e.name }}</h3>
            <span class="gender-tag">{{ genderLabel[e.gender] }}</span>
          </div>
          <div class="card-meta">
            <div class="meta-item"><MapPin :size="13" /> {{ e.venue }}</div>
            <div class="meta-item"><Clock :size="13" /> {{ e.scheduledTime }}</div>
          </div>
          <div v-if="e.record" class="record-line">
            <Trophy :size="12" /> 校纪录 <span class="tnum">{{ e.record }}{{ e.unit }}</span>
          </div>
          <div class="quota-block">
            <div class="quota-head">
              <span class="quota-label"><Users :size="12" /> 报名名额</span>
              <span class="quota-num tnum">{{ e.registeredCount }} / {{ e.quota }}</span>
            </div>
            <div class="quota-bar">
              <div class="quota-fill" :style="{ width: quotaPercent(e) + '%', background: categoryMeta[e.category].color }" />
            </div>
          </div>
        </div>
        <div class="card-actions">
          <button class="act-btn" @click="openEdit(e)"><Pencil :size="14" /> 编辑</button>
          <button class="act-btn danger" @click="handleDelete(e)"><Trash2 :size="14" /> 删除</button>
        </div>
      </article>
    </div>
    <div v-else class="empty-card">
      <EmptyState :icon="Trophy" text="暂无符合条件的项目" sub="试试调整筛选条件或新增项目" />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editing ? '编辑项目' : '新增项目'"
      width="540px"
      :close-on-click-modal="false"
    >
      <el-form label-width="86px" label-position="right">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" placeholder="如：男子100米" />
        </el-form-item>
        <el-form-item label="项目类别">
          <el-select v-model="form.category" style="width: 100%">
            <el-option label="田径" value="track" />
            <el-option label="田赛" value="field" />
            <el-option label="球类" value="ball" />
            <el-option label="趣味" value="fun" />
          </el-select>
        </el-form-item>
        <el-form-item label="性别组别">
          <el-radio-group v-model="form.gender">
            <el-radio value="male">男子</el-radio>
            <el-radio value="female">女子</el-radio>
            <el-radio value="mixed">混合</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="名额上限">
          <el-input-number v-model="form.quota" :min="1" :max="200" />
        </el-form-item>
        <el-form-item label="比赛场地">
          <el-input v-model="form.venue" placeholder="如：主田径场" />
        </el-form-item>
        <el-form-item label="比赛时间">
          <el-input v-model="form.scheduledTime" placeholder="如：2026-06-27 09:00" />
        </el-form-item>
        <el-form-item label="成绩单位">
          <el-input v-model="form.unit" placeholder="秒 / 米 / 分:秒" />
        </el-form-item>
        <el-form-item label="校纪录">
          <el-input v-model="form.record" placeholder="可选，如 11.20" />
        </el-form-item>
        <el-form-item label="分组">
          <el-input v-model="form.group" placeholder="可选，如 A 组" />
        </el-form-item>
        <el-form-item label="项目状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="报名中" value="open" />
            <el-option label="已截止" value="closed" />
            <el-option label="已完赛" value="finished" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ editing ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.events-page { display: flex; flex-direction: column; gap: 20px; }

.page-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }
.primary-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563EB, #3B82F6);
  color: #fff; font-size: 13px; font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.3);
  transition: all 0.22s ease;
}
.primary-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(37, 99, 235, 0.38); }

.filter-bar {
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
  padding: 14px 18px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.06);
}
.search-wrap {
  position: relative; flex: 1; min-width: 180px;
}
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94A3B8; }
.search-wrap input {
  width: 100%;
  padding: 9px 12px 9px 36px;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}
.search-wrap input:focus { border-color: #2563EB; }
.filter-group { display: flex; gap: 6px; flex-wrap: wrap; }
.cat-chip {
  padding: 7px 14px;
  border: 1px solid #E2E8F0;
  border-radius: 20px;
  background: #fff;
  font-size: 12px; font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}
.cat-chip:hover { border-color: #93C5FD; color: #2563EB; }
.cat-chip.active { color: #fff; }

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 18px;
}
.event-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.07);
  display: flex; flex-direction: column;
  transition: transform 0.28s cubic-bezier(0.22,1,0.36,1), box-shadow 0.28s;
}
.event-card:hover { transform: translateY(-5px); box-shadow: 0 16px 36px rgba(37, 99, 235, 0.16); }
.card-top {
  position: relative;
  padding: 14px 18px;
  display: flex; align-items: center; justify-content: space-between;
}
.cat-icon {
  width: 38px; height: 38px;
  border-radius: 10px;
  background: rgba(255,255,255,0.22);
  display: flex; align-items: center; justify-content: center;
}
.status-tag {
  padding: 4px 10px; border-radius: 12px;
  font-size: 11px; font-weight: 700;
  background: rgba(255,255,255,0.92);
}
.status-tag.open { color: #2563EB; }
.status-tag.closed { color: #64748B; }
.status-tag.finished { color: #10B981; }

.card-body { padding: 16px 18px; flex: 1; }
.card-title-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.card-title-row h3 { font-size: 17px; font-weight: 800; color: #0F172A; margin: 0; }
.gender-tag {
  font-size: 11px; padding: 2px 8px; border-radius: 6px;
  background: #FFF7ED; color: #F97316; font-weight: 600;
}
.card-meta { display: flex; flex-direction: column; gap: 4px; margin-top: 10px; }
.meta-item { font-size: 12px; color: #64748B; display: flex; align-items: center; gap: 5px; }
.record-line {
  margin-top: 10px; padding: 6px 10px;
  border-radius: 8px;
  background: linear-gradient(90deg, #FFFBEB, #FEF3C7);
  font-size: 12px; color: #B45309; font-weight: 600;
  display: inline-flex; align-items: center; gap: 5px;
}
.quota-block { margin-top: 14px; }
.quota-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.quota-label { font-size: 12px; color: #64748B; display: inline-flex; align-items: center; gap: 4px; }
.quota-num { font-size: 13px; font-weight: 700; color: #0F172A; }
.quota-bar { height: 6px; border-radius: 4px; background: #F1F5F9; overflow: hidden; }
.quota-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }

.card-actions { display: flex; gap: 8px; padding: 0 18px 16px; }
.act-btn {
  flex: 1;
  padding: 8px 0;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  background: #fff;
  color: #475569;
  font-size: 12px; font-weight: 600;
  cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center; gap: 5px;
  transition: all 0.2s ease;
}
.act-btn:hover { border-color: #2563EB; color: #2563EB; background: #EFF6FF; }
.act-btn.danger:hover { border-color: #EF4444; color: #EF4444; background: #FEF2F2; }

.empty-card {
  background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06);
}
</style>
