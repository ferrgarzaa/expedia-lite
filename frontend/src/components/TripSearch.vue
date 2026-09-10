<script setup>
import { ref } from 'vue'

const API_BASE = 'http://127.0.0.1:8000'

const city = ref('')
const results = ref([])
const hasSearched = ref(false)
const errorMessage = ref('')
const isLoading = ref(false)

async function runSearch() {
  errorMessage.value = ''
  if (!city.value.trim()) {
    errorMessage.value = 'Enter a city to search.'
    return
  }

  isLoading.value = true
  try {
    const url = `${API_BASE}/api/search?city=${encodeURIComponent(city.value.trim())}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`Search failed with status ${response.status}`)
    }
    const data = await response.json()
    results.value = data.results
    hasSearched.value = true
  } catch {
    errorMessage.value = 'Could not reach the search service. Please try again.'
    results.value = []
    hasSearched.value = false
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <section class="trip-search">
    <h1>Expedia Lite</h1>
    <p class="tagline">Search hotel stays by city.</p>

    <form class="search-form" @submit.prevent="runSearch">
      <label for="city-input">City</label>
      <input
        id="city-input"
        v-model="city"
        type="text"
        placeholder="e.g. Boston"
        autocomplete="off"
      />
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Searching…' : 'Search' }}
      </button>
    </form>

    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>

    <p v-else-if="hasSearched && results.length === 0" class="no-results">
      No hotel stays found for "{{ city }}".
    </p>

    <table v-else-if="results.length > 0" class="results-table">
      <caption class="visually-hidden">Hotel stays matching {{ city }}</caption>
      <thead>
        <tr>
          <th scope="col">Trip</th>
          <th scope="col">Hotel</th>
          <th scope="col">City</th>
          <th scope="col">Check-in</th>
          <th scope="col">Check-out</th>
          <th scope="col">Nights</th>
          <th scope="col">Nightly rate</th>
          <th scope="col">Stay price</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="trip in results" :key="trip.trip_id">
          <td>{{ trip.trip_name }}</td>
          <td>{{ trip.hotel_name }}</td>
          <td>{{ trip.city }}, {{ trip.state }}</td>
          <td>{{ trip.check_in }}</td>
          <td>{{ trip.check_out }}</td>
          <td>{{ trip.nights }}</td>
          <td>${{ trip.nightly_rate_usd.toFixed(2) }}</td>
          <td>${{ trip.stay_price_usd.toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.trip-search {
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1rem;
  font-family: system-ui, sans-serif;
}

.tagline {
  color: #555;
  margin-bottom: 1.5rem;
}

.search-form {
  display: flex;
  gap: 0.5rem;
  align-items: end;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.search-form label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.search-form input {
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #999;
  border-radius: 4px;
  min-width: 220px;
}

.search-form button {
  padding: 0.55rem 1.25rem;
  font-size: 1rem;
  background: #1f7a4d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-form button:hover:not(:disabled) {
  background: #17603c;
}

.search-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-form button:focus-visible,
.search-form input:focus-visible {
  outline: 3px solid #1f7a4d;
  outline-offset: 2px;
}

.error {
  color: #9b1c1c;
  font-weight: 600;
}

.no-results {
  color: #444;
  font-style: italic;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th,
.results-table td {
  text-align: left;
  padding: 0.5rem 0.6rem;
  border-bottom: 1px solid #ddd;
}

.results-table th {
  background: #f2f2f2;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}
</style>
