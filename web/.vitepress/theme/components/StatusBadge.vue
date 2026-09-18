<script setup lang="ts">
defineProps<{
  status?: string | null
}>()
</script>

<template>
  <span v-if="status" class="ers-status" :data-status="status">
    {{ status }}
  </span>
  <span v-else class="ers-status ers-status--neutral">n/a</span>
</template>
