<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Megaphone, Trash2, Bell, Send, Clock } from 'lucide-vue-next'
import { useNoticeStore } from '@/stores/notice'
import type { NoticeType } from '@/types'
import EmptyState from '@/components/common/EmptyState.vue'

const store = useNoticeStore()

const filterType = ref<NoticeType | 'all'>('all')
const filtered = computed(() => {
  if (filterType.value === 'all') return store.notices
  return store.notices.filter((n) => n.type === filterType.value)
})

const dialogVisible = ref(false)
const form = reactive({
  title: '',
  content: '',
  type: 'system' as NoticeType,
  level: 'info' as 'info' | 'success' | 'warning' | 'danger',
})

const levelMeta = {
  info: { label: '通知', color: '#3B82F6' },
  success: { label: '喜讯', color: '#10B981' },
  warning: { label: '提醒', color: '#F59E0B' },
  danger: { label: '紧急', color: '#EF4444' },
}

function openCreate(): void {
  Object.assign(form, { title: '', content: '', type: 'system', level: 'info' })
  dialogVisible.value = true
}

async function handleSubmit(): Promise<void> {
  if (!form.title.trim()) { ElMessage.warning('请输入公告标题'); return }
  if (!form.content.trim()) { ElMessage.warning('请输入公告内容'); return }
  await store.create({
    title: form.title.trim(),
    content: form.content.trim(),
    type: form.type,
    level: form.level,
  })
  ElMessage.success('公告已发布')
  dialogVisible.value = false
}

async function handleDelete(id: string): Promise<void> {
  try {
    await ElMessageBox.confirm('确定删除该公告吗？', '删除确认', {
      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
    })
    await store.remove(id)
    ElMessage.success('已删除')
  } catch { /* cancelled */ }
}

async function markAllRead(): Promise<void> {
  await store.markAllRead()
  ElMessage.success('已全部标为已读')
}
</script>

<template>
  <div class="notices-page">
    <div class="page-head">
      <div>
        <h1>公告管理</h1>
        <p>发布系统公告与个人消息 · 共 {{ store.notices.length }} 条</p>
      </div>
      <div class="head-actions">
        <button class="ghost-btn" @click="markAllRead"><Bell :size="15" /> 全部已读</button>
        <button class="primary-btn" @click="openCreate"><Plus :size="15" /> 发布公告</button>
      </div>
    </div>

    <div class="filter-tabs">
      <button :class="{ active: filterType === 'all' }" @click="filterType = 'all'">全部</button>
      <button :class="{ active: filterType === 'system' }" @click="filterType = 'system'">系统公告</button>
      <button :class="{ active: filterType === 'personal' }" @click="filterType = 'personal'">个人消息</button>
    </div>

    <div v-if="filtered.length === 0" class="empty-card">
      <EmptyState :icon="Megaphone" text="暂无公告" sub="点击右上角发布第一条公告" />
    </div>

    <div v-else class="notice-list">
      <article
        v-for="(n, i) in filtered"
        :key="n.id"
        class="notice-card animate-slide-fade"
        :style="{ animationDelay: i * 0.04 + 's' }"
        :class="{ unread: !n.read }"
      >
        <div class="card-side" :style="{ background: levelMeta[n.level].color }">
          <Megaphone :size="18" color="#fff" />
        </div>
        <div class="card-main">
          <div class="card-top">
            <div class="title-row">
              <span v-if="!n.read" class="unread-dot" />
              <h3>{{ n.title }}</h3>
              <span class="type-tag" :class="`t-${n.type}`">{{ n.type === 'system' ? '系统' : '个人' }}</span>
              <span class="level-tag" :style="{ background: levelMeta[n.level].color + '1A', color: levelMeta[n.level].color }">{{ levelMeta[n.level].label }}</span>
            </div>
            <button class="del-btn" @click="handleDelete(n.id)"><Trash2 :size="14" /></button>
          </div>
          <p class="card-content">{{ n.content }}</p>
          <div class="card-foot">
            <span class="meta-item"><Clock :size="12" /> {{ n.createdAt }}</span>
            <span v-if="n.targetName" class="meta-item">接收人：{{ n.targetName }}</span>
            <span class="meta-item" :class="n.read ? 'read' : 'unread'">{{ n.read ? '已读' : '未读' }}</span>
          </div>
        </div>
      </article>
    </div>

    <!-- 发布弹窗 -->
    <el-dialog v-model="dialogVisible" title="发布公告" width="540px" :close-on-click-modal="false">
      <el-form label-width="78px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="如：运动会开幕通知" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.type">
            <el-radio value="system">系统公告</el-radio>
            <el-radio value="personal">个人消息</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="级别">
          <el-radio-group v-model="form.level">
            <el-radio value="info">通知</el-radio>
            <el-radio value="success">喜讯</el-radio>
            <el-radio value="warning">提醒</el-radio>
            <el-radio value="danger">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="5" placeholder="请输入公告正文" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit"><Send :size="14" style="margin-right:4px" /> 发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.notices-page { display: flex; flex-direction: column; gap: 18px; }

.page-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }
.head-actions { display: flex; gap: 10px; }
.primary-btn, .ghost-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 16px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer;
  transition: all 0.22s ease;
}
.primary-btn { border: none; background: linear-gradient(135deg, #2563EB, #3B82F6); color: #fff; box-shadow: 0 8px 18px rgba(37,99,235,0.3); }
.primary-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(37,99,235,0.38); }
.ghost-btn { border: 1px solid #E2E8F0; background: #fff; color: #475569; }
.ghost-btn:hover { border-color: #2563EB; color: #2563EB; background: #EFF6FF; }

.filter-tabs { display: flex; gap: 4px; background: #fff; padding: 6px; border-radius: 12px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); width: fit-content; }
.filter-tabs button {
  padding: 8px 18px; border: none; background: transparent; border-radius: 8px;
  font-size: 13px; font-weight: 600; color: #64748B; cursor: pointer; transition: all 0.2s;
}
.filter-tabs button.active { background: linear-gradient(135deg, #2563EB, #3B82F6); color: #fff; box-shadow: 0 4px 10px rgba(37,99,235,0.3); }

.empty-card { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }

.notice-list { display: flex; flex-direction: column; gap: 12px; }
.notice-card {
  display: flex; background: #fff; border-radius: 14px; overflow: hidden;
  box-shadow: 0 4px 20px rgba(37,99,235,0.06);
  transition: all 0.22s ease;
}
.notice-card:hover { transform: translateX(4px); box-shadow: 0 10px 26px rgba(37,99,235,0.12); }
.notice-card.unread { border-left: 3px solid #2563EB; }
.card-side {
  flex: 0 0 60px;
  display: flex; align-items: center; justify-content: center;
}
.card-main { flex: 1; padding: 16px 20px; min-width: 0; }
.card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.title-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.unread-dot { width: 8px; height: 8px; border-radius: 50%; background: #EF4444; flex: 0 0 auto; }
.title-row h3 { font-size: 15px; font-weight: 800; color: #0F172A; margin: 0; }
.type-tag {
  font-size: 10px; padding: 2px 7px; border-radius: 5px; font-weight: 700;
}
.type-tag.t-system { background: #EFF6FF; color: #2563EB; }
.type-tag.t-personal { background: #FFF7ED; color: #F97316; }
.level-tag { font-size: 10px; padding: 2px 7px; border-radius: 5px; font-weight: 700; }
.del-btn {
  width: 28px; height: 28px; border-radius: 7px; border: 1px solid #E2E8F0; background: #fff;
  color: #94A3B8; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.del-btn:hover { border-color: #EF4444; color: #EF4444; background: #FEF2F2; }
.card-content { font-size: 13px; color: #475569; line-height: 1.7; margin: 8px 0 10px; }
.card-foot { display: flex; gap: 16px; font-size: 12px; color: #94A3B8; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
.meta-item.read { color: #94A3B8; }
.meta-item.unread { color: #EF4444; font-weight: 700; }
</style>
