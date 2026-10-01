<script setup lang="ts"></script>

<template>
  <wa-page>
    <div slot="header" class="om-header">
      <RouterLink :to="{ name: 'start' }" class="om-site-name">Ostbevern Money</RouterLink>
      <nav aria-label="Hauptnavigation" class="om-nav">
        <ul>
          <li><RouterLink :to="{ name: 'start' }">Start</RouterLink></li>
        </ul>
      </nav>
    </div>

    <div class="om-content">
      <RouterView />
    </div>

    <div slot="footer" class="om-footer">
      <p>
        Inspiriert von
        <a
          href="https://github.com/codeformuenster/haushalt-muenster-2026"
          target="_blank"
          rel="noopener"
          >Münster Money (Code for Münster)</a
        >
      </p>
    </div>
  </wa-page>
</template>

<style scoped>
.om-header,
.om-footer {
  background: var(--wa-color-surface-lowered);
  padding: var(--wa-space-m) var(--wa-space-l);
  display: flex;
  align-items: center;
  gap: var(--wa-space-l);
  flex-wrap: wrap;
}

.om-site-name {
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  text-decoration: none;
}

.om-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--wa-space-m);
}

.om-nav a {
  text-decoration: none;
}

.om-nav a.router-link-exact-active {
  color: var(--wa-color-brand-40);
  font-weight: var(--wa-font-weight-bold);
}

.om-content {
  padding: var(--wa-space-l);
}

.om-footer {
  justify-content: center;
}

.om-footer p {
  margin: 0;
}
</style>
