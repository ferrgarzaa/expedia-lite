<script setup>
import { provide, ref } from 'vue'
import TripSearch from './components/TripSearch.vue'
import BookingHistory from './components/BookingHistory.vue'

const TABS = [
  { id: 'search', label: 'Search stays' },
  { id: 'history', label: 'Booking history' },
]

const activeTab = ref('search')
const historyVersion = ref(0)

/**
 * A booking created in the search tab has to show up in history.
 * Bumping this counter tells BookingHistory to reload.
 */
function refreshHistory() {
  historyVersion.value += 1
}

function goToHistory() {
  activeTab.value = 'history'
}

provide('refreshHistory', refreshHistory)
provide('goToHistory', goToHistory)
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">EL</span>
        <div>
          <h1>Expedia Lite</h1>
          <p class="tagline">Find a hotel, book a stay, manage your trips.</p>
        </div>
      </div>

      <nav class="tabs" aria-label="Sections">
        <button
          v-for="tab in TABS"
          :key="tab.id"
          type="button"
          class="tab"
          :class="{ 'tab--active': activeTab === tab.id }"
          :aria-current="activeTab === tab.id ? 'page' : undefined"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </nav>
    </header>

    <main class="app-main">
      <TripSearch v-show="activeTab === 'search'" />
      <BookingHistory
        v-if="activeTab === 'history'"
        :reload-key="historyVersion"
      />
    </main>

    <footer class="app-footer">
      <p>Demo application — bookings are simulated and stored locally in SQLite.</p>
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  padding: 1.25rem clamp(1rem, 4vw, 2.5rem) 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  max-width: var(--page-width);
  margin: 0 auto;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.75rem;
  background: var(--accent);
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.brand h1 {
  margin: 0;
  font-size: 1.5rem;
  line-height: 1.2;
}

.tagline {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.tabs {
  display: flex;
  gap: 0.25rem;
  max-width: var(--page-width);
  margin: 1rem auto 0;
}

.tab {
  appearance: none;
  border: none;
  background: none;
  padding: 0.7rem 1rem;
  font: inherit;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  border-radius: 0.35rem 0.35rem 0 0;
}

.tab:hover {
  color: var(--text);
  background: var(--surface-muted);
}

.tab--active {
  color: var(--accent-dark);
  border-bottom-color: var(--accent);
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: var(--page-width);
  margin: 0 auto;
  padding: clamp(1.25rem, 3vw, 2rem) clamp(1rem, 4vw, 2.5rem);
}

.app-footer {
  border-top: 1px solid var(--line);
  padding: 1rem clamp(1rem, 4vw, 2.5rem);
  color: var(--text-muted);
  font-size: 0.85rem;
}

.app-footer p {
  max-width: var(--page-width);
  margin: 0 auto;
}
</style>
