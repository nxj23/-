<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = withDefaults(
  defineProps<{
    end: number
    duration?: number
    decimals?: number
    suffix?: string
    prefix?: string
  }>(),
  { duration: 900, decimals: 0, suffix: '', prefix: '' },
)

const display = ref(0)

function animate(from: number, to: number): void {
  const start = performance.now()
  const step = (now: number) => {
    const t = Math.min(1, (now - start) / props.duration)
    const eased = 1 - Math.pow(1 - t, 3)
    display.value = from + (to - from) * eased
    if (t < 1) requestAnimationFrame(step)
    else display.value = to
  }
  requestAnimationFrame(step)
}

onMounted(() => animate(0, props.end))

watch(
  () => props.end,
  (val, old) => animate(old ?? 0, val),
)

function format(n: number): string {
  return n.toLocaleString('zh-CN', {
    minimumFractionDigits: props.decimals,
    maximumFractionDigits: props.decimals,
  })
}
</script>

<template>
  <span class="tnum">{{ prefix }}{{ format(display) }}{{ suffix }}</span>
</template>
