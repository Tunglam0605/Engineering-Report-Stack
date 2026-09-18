<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

interface ViewModel {
  report: {
    id: string
    name: string
    version: string
    status?: string
  }
  summary: Record<string, number>
  entities: Array<{ status?: string | null }>
}

const props = defineProps<{ dataUrl: string }>()
const model = ref<ViewModel | null>(null)
const error = ref('')

onMounted(async () => {
  try {
    const response = await fetch(props.dataUrl)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    model.value = await response.json()
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : String(reason)
  }
})

const total = computed(() =>
  model.value ? Object.values(model.value.summary).reduce((a, b) => a + b, 0) : 0
)

const statusCounts = computed(() => {
  const counts = new Map<string, number>()
  for (const entity of model.value?.entities ?? []) {
    const status = entity.status || 'n/a'
    counts.set(status, (counts.get(status) ?? 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => a[0].localeCompare(b[0]))
})
</script>

<template>
  <div v-if="error" class="ers-error">Unable to load report model: {{ error }}</div>
  <div v-else-if="!model" class="ers-loading">Loading canonical view model…</div>
  <section v-else class="ers-summary">
    <div class="ers-summary__header">
      <div>
        <div class="ers-eyebrow">{{ model.report.id }}</div>
        <strong>{{ model.report.name }}</strong>
      </div>
      <div class="ers-summary__meta">
        <span>v{{ model.report.version }}</span>
        <StatusBadge :status="model.report.status" />
      </div>
    </div>

    <div class="ers-metric-grid">
      <article v-for="(count, kind) in model.summary" :key="kind" class="ers-metric">
        <strong>{{ count }}</strong>
        <span>{{ kind }}</span>
      </article>
      <article class="ers-metric">
        <strong>{{ total }}</strong>
        <span>total entities</span>
      </article>
    </div>

    <div class="ers-status-row">
      <span v-for="[status, count] in statusCounts" :key="status">
        <StatusBadge :status="status" /> × {{ count }}
      </span>
    </div>
  </section>
</template>
