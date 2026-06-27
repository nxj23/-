<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Home } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function goHome(): void {
  if (auth.isLoggedIn) {
    router.push(auth.isTeacher ? '/teacher/dashboard' : '/student/home')
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <div class="not-found">
    <div class="nf-inner">
      <div class="nf-code">
        <span>4</span>
        <span class="nf-ball">0</span>
        <span>4</span>
      </div>
      <div class="nf-text">跑偏了！这条赛道不存在</div>
      <div class="nf-sub">你访问的页面可能已被移动或从未开赛</div>
      <button class="nf-btn" @click="goHome">
        <Home :size="16" /> 返回主场
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #EFF6FF 0%, #FFF7ED 100%);
  padding: 24px;
}
.nf-inner { text-align: center; animation: slide-fade-in 0.5s ease both; }
.nf-code {
  font-size: 120px;
  font-weight: 900;
  line-height: 1;
  color: #2563EB;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.nf-ball {
  width: 96px; height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, #F97316, #FBBF24);
  color: #fff;
  display: inline-flex; align-items: center; justify-content: center;
  box-shadow: 0 12px 30px rgba(249, 115, 22, 0.4);
  animation: medal-bounce 1.8s ease-in-out infinite;
}
.nf-text { font-size: 22px; font-weight: 800; color: #0F172A; margin-top: 18px; }
.nf-sub { font-size: 14px; color: #64748B; margin-top: 8px; }
.nf-btn {
  margin-top: 26px;
  padding: 12px 26px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563EB, #3B82F6);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex; align-items: center; gap: 8px;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.3);
  transition: all 0.2s ease;
}
.nf-btn:hover { transform: translateY(-2px); box-shadow: 0 14px 28px rgba(37, 99, 235, 0.4); }
</style>
