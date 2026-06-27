<script setup lang="ts">
import type { Component } from 'vue'

withDefaults(
  defineProps<{ icon?: Component; text?: string; sub?: string }>(),
  { text: '暂无数据', sub: '' },
)
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">
      <component :is="icon" v-if="icon" :size="36" :stroke-width="1.6" color="#94A3B8" />
    </div>
    <div class="empty-text">{{ text }}</div>
    <div v-if="sub" class="empty-sub">{{ sub }}</div>
  </div>
</template>

<style scoped lang="scss">
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: #94A3B8;
}
.empty-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #F1F5F9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}
.empty-text { font-size: 14px; font-weight: 600; color: #64748B; }
.empty-sub { font-size: 12px; color: #94A3B8; margin-top: 4px; }
</style>
