<script setup lang="ts">
import type { Component } from 'vue'

withDefaults(
  defineProps<{
    label: string
    value: number
    icon?: Component
    gradient?: string
    suffix?: string
    hint?: string
  }>(),
  { gradient: 'linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)', suffix: '' },
)
</script>

<template>
  <div class="stat-card group">
    <div class="stat-icon" :style="{ background: gradient }">
      <component :is="icon" v-if="icon" :size="24" color="#fff" :stroke-width="2.2" />
    </div>
    <div class="stat-body">
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value tnum">
        <span class="value-num">{{ value }}</span>
        <span v-if="suffix" class="value-suffix">{{ suffix }}</span>
      </div>
      <div v-if="hint" class="stat-hint">{{ hint }}</div>
    </div>
    <div class="stat-shine" />
  </div>
</template>

<style scoped lang="scss">
.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 22px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.08);
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.3s;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 32px rgba(37, 99, 235, 0.16);
}
.stat-icon {
  flex: 0 0 auto;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.28);
}
.stat-body { flex: 1; min-width: 0; }
.stat-label {
  font-size: 13px;
  color: #64748B;
  margin-bottom: 4px;
  letter-spacing: 0.02em;
}
.stat-value {
  font-size: 30px;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.1;
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.value-suffix { font-size: 14px; font-weight: 600; color: #64748B; }
.stat-hint { font-size: 12px; color: #94A3B8; margin-top: 4px; }
.stat-shine {
  position: absolute;
  top: -50%;
  right: -30%;
  width: 80%;
  height: 200%;
  background: linear-gradient(120deg, transparent, rgba(255, 255, 255, 0.45), transparent);
  transform: rotate(25deg) translateX(-120%);
  transition: transform 0.7s ease;
}
.stat-card:hover .stat-shine {
  transform: rotate(25deg) translateX(120%);
}
</style>
