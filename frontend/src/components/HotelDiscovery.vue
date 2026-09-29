<script setup>
/**
 * Live hotel search by U.S. ZIP code (Assignment 2, Part 1) — View.
 *
 * Owns the ZIP form, the result list, and the shared ``selectedId`` that
 * keeps the list and the Leaflet map in sync. Every state is explicit:
 * idle, loading, results, invalid input, unresolved ZIP, no nearby
 * results, and failed request. A failure is never shown as "0 hotels".
 */
import { computed, nextTick, ref } from 'vue'
import { searchHotelsNearZip } from '../api.js'
import HotelMap from './HotelMap.vue'

const zipInput = ref('')
const status = ref('idle') // idle | loading | results | empty | invalid | not_found | error
const message = ref('')
const center = ref(null)
const hotels = ref([])
const radiusM = ref(5000)
const retrievedAt = ref('')
const selectedId = ref('')
const listEl = ref(null)

const ZIP_RE = /^\d{5}$/

const selectedHotel = computed(() =>
  hotels.value.find((h) => h.place_id === selectedId.value) ?? null,
)

function displayName(hotel) {
  return hotel.name ?? 'Name not provided by source'
}

function formatKm(meters) {
  if (meters == null) return ''
  const text = meters < 1000 ? `${Math.round(meters / 10) * 10} m` : `${(meters / 1000).toFixed(1)} km`
  return `≈ ${text} from ZIP center (straight line)`
}

function resetResults() {
  center.value = null
  hotels.value = []
  selectedId.value = ''
}

async function runSearch() {
  const zip = zipInput.value.trim()
  message.value = ''
  if (!ZIP_RE.test(zip)) {
    resetResults()
    status.value = 'invalid'
    message.value = 'Enter exactly five digits, for example 16802 or 02134 (keep leading zeros).'
    return
  }

  status.value = 'loading'
  resetResults()
  try {
    const data = await searchHotelsNearZip(zip)
    center.value = data.center
    hotels.value = data.results
    radiusM.value = data.radius_m
    retrievedAt.value = data.retrieved_at
    status.value = data.count > 0 ? 'results' : 'empty'
  } catch (error) {
    if (error.code === 'invalid_zip') {
      status.value = 'invalid'
    } else if (error.code === 'zip_not_found') {
      status.value = 'not_found'
    } else {
      status.value = 'error'
    }
    message.value = error.message
  }
}

async function select(id) {
  selectedId.value = id
  await nextTick()
  const item = listEl.value?.querySelector(`[data-id="${CSS.escape(id)}"]`)
  item?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
}
</script>

<template>
  <section class="discovery" aria-labelledby="discovery-title">
    <div class="panel">
      <h2 id="discovery-title">Hotels near a U.S. ZIP code</h2>
      <p class="hint">
        Live search: hotels within 5 km of the point Geoapify returns for the ZIP code.
        Location data only — no prices, ratings, or room availability.
      </p>
      <form class="zip-form" novalidate @submit.prevent="runSearch">
        <label for="zip">ZIP code</label>
        <input
          id="zip"
          v-model="zipInput"
          type="text"
          inputmode="numeric"
          autocomplete="postal-code"
          maxlength="10"
          placeholder="e.g. 16802"
          :aria-invalid="status === 'invalid'"
          aria-describedby="search-status"
        />
        <button type="submit" class="btn-primary" :disabled="status === 'loading'">
          {{ status === 'loading' ? 'Searching…' : 'Search hotels' }}
        </button>
      </form>

      <div id="search-status" class="status" role="status" aria-live="polite">
        <p v-if="status === 'loading'" class="note">Looking up ZIP {{ zipInput.trim() }} and nearby hotels…</p>
        <p v-else-if="status === 'invalid'" class="note note--warn"><strong>Invalid ZIP code.</strong> {{ message }}</p>
        <p v-else-if="status === 'not_found'" class="note note--warn"><strong>ZIP code not found.</strong> {{ message }}</p>
        <p v-else-if="status === 'error'" class="note note--error">
          <strong>Search failed — this is not an empty result.</strong> {{ message }}
        </p>
        <p v-else-if="status === 'empty'" class="note">
          <strong>No hotels found</strong> within 5 km of the ZIP {{ center?.zip }} center in Geoapify's data.
          This does not mean no lodging exists nearby.
        </p>
        <p v-else-if="status === 'results'" class="note note--ok">
          {{ hotels.length }} hotel{{ hotels.length === 1 ? '' : 's' }} within 5 km of ZIP {{ center?.zip }}
          <span class="muted">(up to 50 shown, nearest first; source: Geoapify; retrieved {{ retrievedAt }})</span>
        </p>
      </div>
    </div>

    <div v-if="center" class="results-layout">
      <div class="list-wrap">
        <p class="center-label muted">
          Search center: {{ center.label ?? `ZIP ${center.zip}` }}
          ({{ center.lat.toFixed(4) }}, {{ center.lon.toFixed(4) }})
        </p>
        <ol v-if="hotels.length" ref="listEl" class="hotel-list" aria-label="Hotel results">
          <li v-for="(hotel, index) in hotels" :key="hotel.place_id">
            <button
              type="button"
              class="hotel-item"
              :class="{ 'hotel-item--selected': hotel.place_id === selectedId }"
              :data-id="hotel.place_id"
              :aria-pressed="hotel.place_id === selectedId"
              @click="select(hotel.place_id)"
            >
              <span class="num" aria-hidden="true">{{ index + 1 }}</span>
              <span class="body">
                <span class="name" :class="{ missing: !hotel.name }">{{ displayName(hotel) }}</span>
                <span class="line">{{ hotel.address ?? 'Address not provided by source' }}</span>
                <span class="line muted">
                  {{ formatKm(hotel.distance_m) }} · {{ hotel.lat.toFixed(5) }}, {{ hotel.lon.toFixed(5) }}
                </span>
              </span>
            </button>
          </li>
        </ol>
      </div>

      <div class="map-wrap">
        <HotelMap
          :center="center"
          :radius-m="radiusM"
          :hotels="hotels"
          :selected-id="selectedId"
          @select="select"
        />
        <p class="selected-label" aria-live="polite">
          <template v-if="selectedHotel">
            Selected: <strong>{{ hotels.indexOf(selectedHotel) + 1 }}. {{ displayName(selectedHotel) }}</strong>
            <a v-if="selectedHotel.website" :href="selectedHotel.website" target="_blank" rel="noopener">website</a>
          </template>
          <template v-else-if="hotels.length">Select a hotel in the list or on the map.</template>
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.panel {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.25rem 1.5rem;
}
.panel h2 { margin: 0 0 0.25rem; }
.hint, .muted { color: var(--text-muted); }
.hint { margin: 0 0 1rem; font-size: 0.95rem; }
.zip-form { display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; }
.zip-form label { font-weight: 600; }
.zip-form input {
  font: inherit; padding: 0.55rem 0.75rem; width: 9rem;
  border: 1px solid var(--line); border-radius: var(--radius);
}
.zip-form input[aria-invalid='true'] { border-color: #7e1d6b; }
.btn-primary {
  font: inherit; font-weight: 600; padding: 0.55rem 1.1rem; border: none;
  border-radius: var(--radius); background: var(--accent); color: #fff; cursor: pointer;
}
.btn-primary:hover { background: var(--accent-dark); }
.btn-primary:disabled { opacity: 0.7; cursor: progress; }
input:focus-visible, button:focus-visible, a:focus-visible {
  outline: 3px solid #7e1d6b; outline-offset: 2px;
}
.status { min-height: 1.5rem; margin-top: 0.75rem; }
.note { margin: 0; padding: 0.6rem 0.8rem; border-radius: var(--radius); background: var(--surface-muted); }
.note--ok { background: var(--accent-soft); }
.note--warn { background: #fff4e5; border-left: 4px solid #7e1d6b; }
.note--error { background: var(--danger-soft); border-left: 4px solid var(--danger); }
.results-layout {
  display: grid; grid-template-columns: minmax(18rem, 2fr) 3fr; gap: 1rem; margin-top: 1rem;
}
@media (max-width: 800px) { .results-layout { grid-template-columns: 1fr; } }
.center-label { margin: 0 0 0.5rem; font-size: 0.9rem; }
.hotel-list { list-style: none; margin: 0; padding: 0; max-height: 32rem; overflow-y: auto; display: grid; gap: 0.4rem; }
.hotel-item {
  display: flex; gap: 0.7rem; width: 100%; text-align: left; font: inherit; color: inherit;
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 0.6rem 0.75rem; cursor: pointer;
}
.hotel-item:hover { background: var(--surface-muted); }
.hotel-item--selected { border: 2px solid #7e1d6b; background: #fdf0fa; }
.num {
  flex: none; display: grid; place-items: center; width: 1.8rem; height: 1.8rem; border-radius: 50%;
  border: 2px solid var(--accent); color: var(--accent-dark); font-weight: 700; font-size: 0.8rem;
}
.hotel-item--selected .num { background: #7e1d6b; border-color: #4a0d3f; color: #fff; }
.body { display: grid; gap: 0.1rem; }
.name { font-weight: 600; }
.name.missing { font-style: italic; color: var(--text-muted); }
.line { font-size: 0.88rem; }
.map-wrap { display: flex; flex-direction: column; gap: 0.5rem; min-height: 28rem; }
.selected-label { margin: 0; font-size: 0.95rem; }
.selected-label a { margin-left: 0.5rem; }
</style>
