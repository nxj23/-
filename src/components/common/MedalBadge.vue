<script setup lang="ts">
import { Medal } from 'lucide-vue-next'
import type { Medal as MedalType } from '@/types'

const props = defineProps<{ medal?: MedalType; rank?: number; size?: number }>()

const colorMap: Record<MedalType, { bg: string; ring: string; label: string }> = {
  gold: { bg: 'linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%)', ring: '#F59E0B', label: '金' },
  silver: { bg: 'linear-gradient(135deg, #E5E7EB 0%, #9CA3AF 100%)', ring: '#9CA3AF', label: '银' },
  bronze: { bg: 'linear-gradient(135deg, #D97706 0%, #B45309 100%)', ring: '#B45309', label: '铜' },
}

const size = props.size ?? 36
</script>

<template>
  <div v-if="medal && colorMap[medal]" class="medal-badge" :style="{ width: size + 'px', height: size + 'px', background: colorMap[medal].bg, boxShadow: `0 6px 14px ${colorMap[medal].ring}66` }">
    <Medal :size="size * 0.5" color="#fff" :stroke-width="2.4" />
    <span class="medal-rank">{{ rank ?? '' }}</span>
  </div>
  <div v-else-if="rank" class="rank-plain" :style="{ width: size + 'px', height: size + 'px' }">
    {{ rank }}
  </div>
</template>

<style scoped lang="scss">
.medal-badge {
  position: relative;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: medal-bounce 1.8s ease-in-out infinite;
}
.medal-rank {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: #0F172A;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
}
.rank-plain {
  border-radius: 50%;
  background: #F1F5F9;
  color: #64748B;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}
</style>
