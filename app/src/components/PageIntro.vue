<script setup lang="ts">
defineProps<{
  titel: string
  beschreibung: string
}>()
</script>

<template>
  <header class="om-page-intro">
    <h1 tabindex="-1">{{ titel }}</h1>
    <p>{{ beschreibung }}</p>
    <slot />
  </header>
</template>

<style scoped>
.om-page-intro {
  margin-bottom: var(--wa-space-3xl);
}

.om-page-intro h1 {
  margin: 0;
  font-size: var(--wa-font-size-2xl);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-page-intro p {
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-normal);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}
</style>
