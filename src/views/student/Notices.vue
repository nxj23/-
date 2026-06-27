<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Megaphone, Bell, Clock, CheckCheck, Trash2, Inbox,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useNoticeStore } from '@/stores/notice'
import type { NoticeType } from '@/types'
import EmptyState from '@/components/common/EmptyState.vue'

const auth = useAuthStore()
const store = useNoticeStore()

const filterType = ref<NoticeType | 'all'>('all')
const onlyUnread = ref(false)

const myNotices = computed(() => {
  let list = store.listForUser(auth.user?.id || '', 'student')
  if (filterType.value !== 'all') list = list.filter((n) => n.type === filterType.value)
  if (onlyUnread.value) list = list.filter((n) => !n.read)
  return list
})

const levelMeta = {
  info: { label: '通知', color: '#3B82F6' },
  success: { label: '喜讯', color: '#10B981' },
  warning: { label: '提醒', color: '#F59E0B' },
  danger: { label: '紧急', color: '#EF4444' },
}

const unread = computed(() => store.listForUser(auth.user?.id || '', 'student').filter((n) => !n.read).length)

async function openNotice(id: string): Promise<void> {
  await store.markRead(id)
}

async function markAllRead(): Promise<void> {
  await store.markAllRead(auth.user?.id)
  ElMessage.success('已全部标为已读')
}
</script>

<template>
  <div class="notices-page">
    <div class="page-head">
      <div>
        <h1>公告通知</h1>
        <p>系统公告与个人消息 · {{ unread }} 条未读</p>
      </div>
      <button class="ghost-btn" :disabled="unread === 0" @click="markAllRead">
        <CheckCheck :size="15" /> 全部已读
      </button>
    </div>

    <div class="filter-bar">
      <div class="tabs">
        <button :class="{ active: filterType === 'all' }" @click="filterType = 'all'">全部</button>
        <button :class="{ active: filterType === 'system' }" @click="filterType = 'system'"><Megaphone :size="13" /> 系统公告</button>
        <button :class="{ active: filterType === 'personal' }" @click="filterType = 'personal'"><Bell :size="13" /> 个人消息</button>
      </div>
      <label class="unread-toggle">
        <input type="checkbox" v-model="onlyUnread" />
        <span>仅看未读</span>
      </label>
    </div>

    <div v-if="myNotices.length === 0" class="empty-card">
      <EmptyState :icon="Inbox" text="暂无消息" sub="有新公告或报名进展时会显示在此处" />
    </div>

    <div v-else class="notice-list">
      <article
        v-for="(n, i) in myNotices"
        :key="n.id"
        class="notice-card animate-slide-fade"
        :style="{ animationDelay: i * 0.04 + 's' }"
        :class="{ unread: !n.read }"
        @click="openNotice(n.id)"
      >
        <div class="card-side" :style="{ background: levelMeta[n.level].color }">
          <component :is="n.type === 'system' ? Megaphone : Bell" :size="18" color="#fff" />
        </div>
        <div class="card-main">
          <div class="card-top">
            <div class="title-row">
              <span v-if="!n.read" class="unread-dot" />
              <h3>{{ n.title }}</h3>
              <span class="type-tag" :class="`t-${n.type}`">{{ n.type === 'system' ? '系统' : '个人' }}</span>
              <span class="level-tag" :style="{ background: levelMeta[n.level].color + '1A', color: levelMeta[n.level].color }">{{ levelMeta[n.level].label }}</span>
            </div>
          </div>
          <p class="card-content">{{ n.content }}</p>
          <div class="card-foot">
            <span class="meta-item"><Clock :size="12" /> {{ n.createdAt }}</span>
            <span class="meta-item" :class="n.read ? 'read' : 'unread'">{{ n.read ? '已读' : '未读' }}</span>
          </div>
        </div>
        <div class="unread-bar" v-if="!n.read" />
      </article>
    </div>
  </div>
</template>

<style scoped lang="scss">
.notices-page { display: flex; flex-direction: column; gap: 18px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
.page-head h1 { font-size: 22px; font-weight: 800; color: #0F172A; margin: 0 0 4px; }
.page-head p { font-size: 13px; color: #64748B; margin: 0; }
.ghost-btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 16px; border-radius: 10px; border: 1px solid #E2E8F0; background: #fff; color: #475569; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.22s; }
.ghost-btn:hover:not(:disabled) { border-color: #F97316; color: #F97316; background: #FFF7ED; }
.ghost-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.filter-bar { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.tabs { display: flex; gap: 4px; background: #fff; padding: 6px; border-radius: 12px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }
.tabs button { display: inline-flex; align-items: center; gap: 5px; padding: 8px 16px; border: none; background: transparent; border-radius: 8px; font-size: 13px; font-weight: 600; color: #64748B; cursor: pointer; transition: all 0.2s; }
.tabs button.active { background: linear-gradient(135deg, #F97316, #FB923C); color: #fff; box-shadow: 0 4px 10px rgba(249,115,22,0.3); }
.unread-toggle { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #475569; font-weight: 600; cursor: pointer; }
.unread-toggle input { width: 16px; height: 16px; accent-color: #F97316; cursor: pointer; }

.empty-card { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(37,99,235,0.06); }

.notice-list { display: flex; flex-direction: column; gap: 12px; }
.notice-card { position: relative; display: flex; background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 20px rgba(37,99,235,0.06); cursor: pointer; transition: all 0.22s ease; }
.notice-card:hover { transform: translateX(4px); box-shadow: 0 10px 26px rgba(37,99,235,0.12); }
.card-side { flex: 0 0 56px; display: flex; align-items: center; justify-content: center; }
.card-main { flex: 1; padding: 16px 20px; min-width: 0; }
.card-top { display: flex; justify-content: space-between; align-items: flex-start; }
.title-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.unread-dot { width: 8px; height: 8px; border-radius: 50%; background: #F97316; flex: 0 0 auto; animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse { 0%,100%{ opacity:1 } 50%{ opacity:0.4 } }
.title-row h3 { font-size: 15px; font-weight: 800; color: #0F172A; margin: 0; }
.type-tag { font-size: 10px; padding: 2px 7px; border-radius: 5px; font-weight: 700; }
.type-tag.t-system { background: #EFF6FF; color: #2563EB; }
.type-tag.t-personal { background: #FFF7ED; color: #F97316; }
.level-tag { font-size: 10px; padding: 2px 7px; border-radius: 5px; font-weight: 700; }
.card-content { font-size: 13px; color: #475569; line-height: 1.7; margin: 8px 0 10px; }
.card-foot { display: flex; gap: 16px; font-size: 12px; color: #94A3B8; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
.meta-item.read { color: #94A3B8; }
.meta-item.unread { color: #F97316; font-weight: 700; }
.unread-bar { position: absolute; right: 0; top: 0; bottom: 0; width: 3px; background: #F97316; }
</style>
