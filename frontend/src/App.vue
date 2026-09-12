<script setup>
import { ref } from 'vue'
import TripSearch from './components/TripSearch.vue'
import BookingHistory from './components/BookingHistory.vue'

const activeTab = ref('search')
</script>

<template>
  <div class="app-shell">
    <nav class="tabs" role="tablist" aria-label="Expedia Lite sections">
      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'search'"
        :class="{ active: activeTab === 'search' }"
        @click="activeTab = 'search'"
      >
        Search &amp; Book
      </button>
      <button
        type="button"
        role="tab"
        :aria-selected="activeTab === 'history'"
        :class="{ active: activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        Booking History
      </button>
    </nav>

    <TripSearch v-if="activeTab === 'search'" />
    <BookingHistory v-else />
  </div>
</template>

<style>
.app-shell {
  max-width: 900px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1rem 0;
  max-width: 720px;
  margin: 0 auto;
}

.tabs button {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-bottom: none;
  background: #f2f2f2;
  border-radius: 6px 6px 0 0;
  cursor: pointer;
  font-size: 0.95rem;
  font-family: inherit;
}

.tabs button.active {
  background: white;
  border-color: #1f7a4d;
  color: #1f7a4d;
  font-weight: 600;
}

.tabs button:focus-visible {
  outline: 3px solid #1f7a4d;
  outline-offset: 2px;
}
</style>
