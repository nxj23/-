<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Trophy, Zap, ChevronRight } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const form = reactive({ account: '', password: '' })
const loading = ref(false)

const demos = [
  { label: '教师·王建国', account: 'T001', password: '123456', role: 'teacher' },
  { label: '学生·张明', account: 'S001', password: '123456', role: 'student' },
  { label: '学生·李华', account: 'S002', password: '123456', role: 'student' },
]

async function handleLogin(): Promise<void> {
  if (!form.account || !form.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    const ok = await auth.login(form.account, form.password)
    if (!ok) {
      ElMessage.error('账号或密码错误')
      return
    }
    ElMessage.success(`欢迎回来，${auth.user?.name}`)
    const redirect = (route.query.redirect as string) || (auth.isTeacher ? '/teacher/dashboard' : '/student/home')
    router.push(redirect)
  } finally {
    loading.value = false
  }
}

function quickFill(account: string, password: string): void {
  form.account = account
  form.password = password
}
</script>

<template>
  <div class="login-page">
    <div class="bg-decor">
      <div class="blob blob-1" />
      <div class="blob blob-2" />
      <div class="blob blob-3" />
      <div class="track-line" />
    </div>

    <div class="login-container">
      <!-- 左侧品牌区 -->
      <div class="brand-panel">
        <div class="brand-head">
          <div class="brand-logo">
            <Trophy :size="28" color="#fff" :stroke-width="2.4" />
          </div>
          <div class="brand-name">校园运动会</div>
        </div>
        <div class="brand-hero">
          <h1 class="hero-title">燃动青春<br/>逐梦赛场</h1>
          <p class="hero-sub">2026 校园运动会数字管理平台 — 让每一份汗水都被记录，让每一次突破都被喝彩。</p>
        </div>
        <div class="brand-stats">
          <div class="bstat">
            <div class="bstat-num tnum">10+</div>
            <div class="bstat-label">比赛项目</div>
          </div>
          <div class="bstat-sep" />
          <div class="bstat">
            <div class="bstat-num tnum">8</div>
            <div class="bstat-label">参赛班级</div>
          </div>
          <div class="bstat-sep" />
          <div class="bstat">
            <div class="bstat-num tnum">200+</div>
            <div class="bstat-label">参赛选手</div>
          </div>
        </div>
        <div class="brand-foot">
          <Zap :size="14" /> 实时成绩 · 智能排名 · 破纪录追踪
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="form-panel">
        <div class="form-head">
          <h2>欢迎登录</h2>
          <p>请使用学号 / 工号登录系统</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="field">
            <label>账号</label>
            <div class="input-wrap">
              <User :size="18" class="input-icon" />
              <input v-model="form.account" type="text" placeholder="请输入学号或工号" autocomplete="username" />
            </div>
          </div>
          <div class="field">
            <label>密码</label>
            <div class="input-wrap">
              <Lock :size="18" class="input-icon" />
              <input v-model="form.password" type="password" placeholder="请输入密码" autocomplete="current-password" @keyup.enter="handleLogin" />
            </div>
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="!loading">登录系统</span>
            <span v-else class="loading-dot" />
            <ChevronRight :size="18" v-if="!loading" />
          </button>
        </form>

        <div class="demo-area">
          <div class="demo-title">演示账号 · 一键填充</div>
          <div class="demo-list">
            <button
              v-for="d in demos"
              :key="d.account"
              class="demo-chip"
              :class="`role-${d.role}`"
              @click="quickFill(d.account, d.password)"
            >
              {{ d.label }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #1E40AF 100%);
  overflow: hidden;
}
.bg-decor { position: absolute; inset: 0; pointer-events: none; }
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
}
.blob-1 { width: 420px; height: 420px; background: #F97316; top: -120px; right: -80px; animation: float 12s ease-in-out infinite; }
.blob-2 { width: 360px; height: 360px; background: #3B82F6; bottom: -100px; left: -60px; animation: float 14s ease-in-out infinite reverse; }
.blob-3 { width: 280px; height: 280px; background: #FBBF24; top: 40%; left: 40%; opacity: 0.3; animation: float 16s ease-in-out infinite; }
@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -40px); }
}
.track-line {
  position: absolute;
  bottom: 10%;
  left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
}

.login-container {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 980px;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  background: #fff;
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.4);
  animation: pop-in 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* 品牌区 */
.brand-panel {
  background: linear-gradient(150deg, #1E3A8A 0%, #2563EB 55%, #F97316 130%);
  padding: 44px 40px;
  color: #fff;
  display: flex;
  flex-direction: column;
  position: relative;
}
.brand-head { display: flex; align-items: center; gap: 12px; }
.brand-logo {
  width: 46px; height: 46px;
  border-radius: 12px;
  background: rgba(255,255,255,0.18);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(255,255,255,0.25);
}
.brand-name { font-size: 18px; font-weight: 800; letter-spacing: 0.04em; }

.brand-hero { margin-top: 56px; }
.hero-title {
  font-size: 42px;
  font-weight: 900;
  line-height: 1.15;
  margin: 0 0 18px;
  letter-spacing: 0.02em;
}
.hero-sub {
  font-size: 13px;
  line-height: 1.7;
  color: rgba(255,255,255,0.82);
  margin: 0;
  max-width: 340px;
}

.brand-stats {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px 0;
}
.bstat-num { font-size: 26px; font-weight: 800; }
.bstat-label { font-size: 11px; color: rgba(255,255,255,0.75); margin-top: 2px; }
.bstat-sep { width: 1px; height: 30px; background: rgba(255,255,255,0.25); }

.brand-foot {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  padding-top: 14px;
  border-top: 1px solid rgba(255,255,255,0.15);
}

/* 表单区 */
.form-panel {
  padding: 48px 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.form-head h2 {
  font-size: 26px; font-weight: 800; color: #0F172A; margin: 0 0 6px;
}
.form-head p { font-size: 13px; color: #64748B; margin: 0 0 30px; }

.login-form { display: flex; flex-direction: column; gap: 18px; }
.field label {
  display: block;
  font-size: 12px; font-weight: 600; color: #475569;
  margin-bottom: 8px;
  letter-spacing: 0.04em;
}
.input-wrap {
  position: relative;
  display: flex; align-items: center;
  border: 1.5px solid #E2E8F0;
  border-radius: 12px;
  background: #F8FAFC;
  transition: all 0.2s ease;
}
.input-wrap:focus-within {
  border-color: #2563EB;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}
.input-icon { position: absolute; left: 14px; color: #94A3B8; }
.input-wrap input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 13px 14px 13px 44px;
  font-size: 14px;
  color: #0F172A;
  outline: none;
  border-radius: 12px;
}

.submit-btn {
  margin-top: 6px;
  height: 48px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  transition: all 0.25s ease;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.32);
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.4);
}
.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; }
.loading-dot {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.demo-area { margin-top: 28px; padding-top: 22px; border-top: 1px dashed #E2E8F0; }
.demo-title { font-size: 12px; color: #94A3B8; margin-bottom: 10px; }
.demo-list { display: flex; flex-wrap: wrap; gap: 8px; }
.demo-chip {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #E2E8F0;
  background: #fff;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}
.demo-chip:hover { transform: translateY(-1px); }
.demo-chip.role-teacher:hover { border-color: #2563EB; color: #2563EB; background: #EFF6FF; }
.demo-chip.role-student:hover { border-color: #F97316; color: #F97316; background: #FFF7ED; }

@media (max-width: 820px) {
  .login-container { grid-template-columns: 1fr; max-width: 460px; }
  .brand-panel { padding: 32px; }
  .brand-hero { margin-top: 24px; }
  .hero-title { font-size: 30px; }
  .form-panel { padding: 32px; }
}
</style>
