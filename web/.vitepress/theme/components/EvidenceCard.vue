<script setup lang="ts">
defineProps<{
  title: string
  evidenceId: string
  type: string
  testId: string
  resultId?: string
  locator: string
}>()
</script>

<template>
  <article class="ers-evidence">
    <header>
      <div>
        <div class="ers-eyebrow">{{ evidenceId }} · {{ type }}</div>
        <strong>{{ title }}</strong>
      </div>
      <div class="ers-evidence__links">
        <code>{{ testId }}</code>
        <code v-if="resultId">{{ resultId }}</code>
      </div>
    </header>
    <div class="ers-evidence__body"><slot /></div>
    <footer><code>{{ locator }}</code></footer>
  </article>
</template>
