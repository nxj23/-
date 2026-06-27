<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Bell, LogOut, ChevronDown, Menu as MenuIcon } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useNoticeStore } from '@/stores/notice'

const props = defineProps<{ toggleSidebar?: () => void }>()

const auth = useAuthStore()
const notice = useNoticeStore()
const router = useRouter()

const showNotices = ref(false)

const displayName = computed(() => auth.user?.name ?? '用户')
const displayRole = computed(() => (auth.isTeacher ? '教师' : '学生'))
const initials = computed(() => displayName.value.charAt(0))

const recentNotices = computed(() => notice.notices.slice(0, 5))
const unread = computed(() => notice.unreadCount)

async function handleLogout(): Promise<void> {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await auth.logout()
    notice.notices = []
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // user cancelled
  }
}

async function viewNotice(id: string): Promise<void> {
  await notice.markRead(id)
  showNotices.value = false
  if (auth.isTeacher) router.push('/teacher/notices')
  else router.push('/student/notices')
}
</script>

<template>
  <header class="topbar">
    <div class="topbar-left">
      <button v-if="toggleSidebar" class="icon-btn mobile-only" @click="toggleSidebar">
        <MenuIcon :size="20" />
      </button>
      <div class="page-greeting">
        <span class="hello">Hi, {{ displayName }}</span>
        <span class="role-tag">{{ displayRole }}</span>
      </div>
    </div>

    <div class="topbar-right">
      <el-popover :visible="showNotices" placement="bottom-end" :width="340" trigger="manual">
        <template #reference>
          <button class="icon-btn notice-btn" @click="showNotices = !showNotices">
            <Bell :size="19" />
            <span v-if="unread > 0" class="badge">{{ unread > 99 ? '99+' : unread }}</span>
          </button>
        </template>
        <div class="notice-pop">
          <div class="pop-header">
            <span>通知消息</span>
            <span class="pop-count">{{ unread }} 条未读</span>
          </div>
          <div class="pop-list">
            <div v-for="n in recentNotices" :key="n.id" class="pop-item" :class="{ unread: !n.read }" @click="viewNotice(n.id)">
              <div class="pop-dot" :class="`level-${n.level}`" />
              <div class="pop-content">
                <div class="pop-title">{{ n.title }}</div>
                <div class="pop-time">{{ n.createdAt }}</div>
              </div>
            </div>
            <div v-if="recentNotices.length === 0" class="pop-empty">暂无消息</div>
          </div>
        </div>
      </el-popover>

      <el-dropdown trigger="click" @command="(c: string) => c === 'logout' && handleLogout()">
        <div class="user-chip">
          <div class="avatar">{{ initials }}</div>
          <div class="user-meta">
            <div class="user-name">{{ displayName }}</div>
            <div class="user-id">{{ auth.user?.id }}</div>
          </div>
          <ChevronDown :size="16" />
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">
              <LogOut :size="15" style="margin-right: 6px" /> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<style scoped lang="scss">
.topbar {
  height: 64px;
  flex: 0 0 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #E2E8F0;
  position: sticky;
  top: 0;
  z-index: 15;
}
.topbar-left { display: flex; align-items: center; gap: 14px; }
.page-greeting { display: flex; align-items: center; gap: 10px; }
.hello { font-size: 16px; font-weight: 700; color: #0F172A; }
.role-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(37, 99, 235, 0.1);
  color: #2563EB;
  font-weight: 600;
}
.topbar-right { display: flex; align-items: center; gap: 14px; }

.icon-btn {
  position: relative;
  width: 38px; height: 38px;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
  background: #fff;
  color: #475569;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}
.icon-btn:hover { background: #F1F5F9; color: #2563EB; border-color: #BFDBFE; }
.badge {
  position: absolute;
  top: -4px; right: -4px;
  min-width: 18px; height: 18px;
  padding: 0 4px;
  border-radius: 9px;
  background: #EF4444;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid #fff;
}

.user-chip {
  display: flex; align-items: center; gap: 10px;
  padding: 5px 10px 5px 5px;
  border-radius: 30px;
  border: 1px solid #E2E8F0;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}
.user-chip:hover { border-color: #BFDBFE; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1); }
.avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563EB, #F97316);
  color: #fff;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
}
.user-meta { line-height: 1.2; }
.user-name { font-size: 13px; font-weight: 700; color: #0F172A; }
.user-id { font-size: 11px; color: #94A3B8; }

.notice-pop { margin: -8px; }
.pop-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px 10px;
  font-weight: 700; color: #0F172A; font-size: 14px;
  border-bottom: 1px solid #F1F5F9;
}
.pop-count { font-size: 12px; font-weight: 600; color: #F97316; }
.pop-list { max-height: 320px; overflow-y: auto; padding: 6px 0; }
.pop-item {
  display: flex; gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
}
.pop-item:hover { background: #F8FAFC; }
.pop-item.unread { background: #EFF6FF; }
.pop-item.unread:hover { background: #DBEAFE; }
.pop-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex: 0 0 auto; }
.pop-dot.level-info { background: #3B82F6; }
.pop-dot.level-success { background: #10B981; }
.pop-dot.level-warning { background: #F59E0B; }
.pop-dot.level-danger { background: #EF4444; }
.pop-title { font-size: 13px; color: #334155; font-weight: 600; line-height: 1.4; }
.pop-time { font-size: 11px; color: #94A3B8; margin-top: 3px; }
.pop-empty { text-align: center; padding: 30px; color: #94A3B8; font-size: 13px; }

.mobile-only { display: none; }

@media (max-width: 900px) {
  .mobile-only { display: flex; }
  .user-meta { display: none; }
  .topbar { padding: 0 16px; }
}
</style>
