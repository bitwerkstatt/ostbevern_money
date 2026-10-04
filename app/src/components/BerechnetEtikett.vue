<script setup lang="ts">
import { useId } from 'vue'

const id = useId()
</script>

<template>
  <span class="om-berechnet">
    <wa-tag :id="id" size="small" variant="neutral" tabindex="0">berechnet</wa-tag>
    <wa-tooltip :for="id">
      Dieser Wert steht nicht im PDF. Er wird aus den Planwerten berechnet.
    </wa-tooltip>
  </span>
</template>

<style scoped>
.om-berechnet {
  display: inline-block;
  margin-inline-start: var(--wa-space-2xs);
}
</style>
