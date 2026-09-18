<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

interface EntityRecord {
  id: string
  kind: string
  title: string
  status?: string | null
  summary?: string
}

interface Edge {
  source: string
  target: string
  relation: string
}

interface ViewModel {
  entities: EntityRecord[]
  edges: Edge[]
}

const props = defineProps<{ dataUrl: string }>()

const model = ref<ViewModel>({ entities: [], edges: [] })
const query = ref('')
const kind = ref('all')
const status = ref('all')
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

const kinds = computed(() =>
  [...new Set(model.value.entities.map((entity) => entity.kind))].sort()
)

const statuses = computed(() =>
  [...new Set(
    model.value.entities
      .map((entity) => entity.status)
      .filter((value): value is string => Boolean(value))
  )].sort()
)

const filtered = computed(() => {
  const needle = query.value.trim().toLowerCase()
  return model.value.entities.filter((entity) => {
    if (kind.value !== 'all' && entity.kind !== kind.value) return false
    if (status.value !== 'all' && entity.status !== status.value) return false
    if (!needle) return true
    return [entity.id, entity.title, entity.summary ?? '']
      .join(' ')
      .toLowerCase()
      .includes(needle)
  })
})

function relations(entityId: string) {
  return model.value.edges.filter(
    (edge) => edge.source === entityId || edge.target === entityId
  )
}
</script>

<template>
  <section class="ers-explorer">
    <div class="ers-toolbar">
      <label>
        <span>Search</span>
        <input v-model="query" type="search" placeholder="ID, title, content…" />
      </label>
      <label>
        <span>Type</span>
        <select v-model="kind">
          <option value="all">All</option>
          <option v-for="value in kinds" :key="value" :value="value">{{ value }}</option>
        </select>
      </label>
      <label>
        <span>Status</span>
        <select v-model="status">
          <option value="all">All</option>
          <option v-for="value in statuses" :key="value" :value="value">{{ value }}</option>
        </select>
      </label>
    </div>

    <div v-if="error" class="ers-error">Unable to load entities: {{ error }}</div>
    <div v-else class="ers-explorer__meta">
      Showing {{ filtered.length }} / {{ model.entities.length }} entities
    </div>

    <div class="ers-entity-list">
      <article v-for="entity in filtered" :key="entity.id" class="ers-entity">
        <header>
          <div>
            <div class="ers-eyebrow">{{ entity.kind }}</div>
            <strong>{{ entity.id }} — {{ entity.title }}</strong>
          </div>
          <StatusBadge :status="entity.status" />
        </header>
        <p v-if="entity.summary">{{ entity.summary }}</p>
        <div v-if="relations(entity.id).length" class="ers-relations">
          <span
            v-for="edge in relations(entity.id)"
            :key="`${edge.source}:${edge.relation}:${edge.target}`"
          >
            {{ edge.source === entity.id ? '→' : '←' }}
            {{ edge.relation }}
            {{ edge.source === entity.id ? edge.target : edge.source }}
          </span>
        </div>
      </article>
    </div>
  </section>
</template>
