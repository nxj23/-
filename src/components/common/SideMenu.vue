<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Component } from 'vue'

interface MenuItem {
  path: string
  label: string
  icon: Component
}

const props = defineProps<{
  items: MenuItem[]
  brand: string
  brandIcon?: Component
  accent?: string
}>()

const route = useRoute()
const router = useRouter()

const activePath = computed(() => route.path)

function go(path: string): void {
  router.push(path)
}
</script>

<template>
  <aside class="side-menu" :style="{ '--accent': accent || '#2563EB' }">
    <div class="brand">
      <div class="brand-icon">
        <component :is="brandIcon" v-if="brandIcon" :size="22" color="#fff" :stroke-width="2.4" />
      </div>
      <div class="brand-text">
        <div class="brand-title">{{ brand }}</div>
        <div class="brand-sub">校园运动会</div>
      </div>
    </div>

    <nav class="nav">
      <button
        v-for="item in items"
        :key="item.path"
        class="nav-item"
        :class="{ active: activePath === item.path }"
        @click="go(item.path)"
      >
        <span class="nav-bar" />
        <component :is="item.icon" :size="19" :stroke-width="2" />
        <span class="nav-label">{{ item.label }}</span>
      </button>
    </nav>

    <div class="side-footer">
      <div class="footer-line" />
      <div class="footer-text">2026 春季运动会</div>
    </div>
  </aside>
</template>

<style scoped lang="scss">
.side-menu {
  width: 244px;
  flex: 0 0 244px;
  height: 100vh;
  position: sticky;
  top: 0;
  background: #fff;
  border-right: 1px solid #E2E8F0;
  display: flex;
  flex-direction: column;
  padding: 22px 16px;
  z-index: 20;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 10px 22px;
  border-bottom: 1px solid #F1F5F9;
  margin-bottom: 14px;
}
.brand-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--accent);
  background-image: linear-gradient(135deg, var(--accent) 0%, #F97316 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.28);
}
.brand-title { font-size: 16px; font-weight: 800; color: #0F172A; line-height: 1.2; }
.brand-sub { font-size: 11px; color: #94A3B8; letter-spacing: 0.08em; margin-top: 2px; }

.nav { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border: none;
  background: transparent;
  border-radius: 10px;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.22s ease;
  width: 100%;
  text-align: left;
}
.nav-item:hover { background: #F1F5F9; color: #0F172A; }
.nav-item.active {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(249, 115, 22, 0.08));
  color: var(--accent);
}
.nav-bar {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) scaleY(0);
  width: 3px;
  height: 22px;
  border-radius: 0 3px 3px 0;
  background: var(--accent);
  transition: transform 0.25s ease;
}
.nav-item.active .nav-bar { transform: translateY(-50%) scaleY(1); }
.nav-label { flex: 1; }

.side-footer { margin-top: auto; padding-top: 14px; }
.footer-line { height: 1px; background: #F1F5F9; margin-bottom: 10px; }
.footer-text { font-size: 11px; color: #94A3B8; text-align: center; letter-spacing: 0.04em; }
</style>
