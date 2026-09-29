<script setup>
/**
 * Leaflet map for live hotel results (View only).
 *
 * Props in, events out: the parent owns the selected hotel. Each hotel is
 * a numbered, keyboard-focusable marker whose number matches the list.
 * Tiles come from OpenStreetMap (no key needed in the browser); the
 * attribution control stays visible.
 */
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  center: { type: Object, default: null },
  radiusM: { type: Number, default: 5000 },
  hotels: { type: Array, default: () => [] },
  selectedId: { type: String, default: '' },
})
const emit = defineEmits(['select'])

const mapEl = ref(null)
let map = null
let layer = null
const markers = new Map()

function displayName(hotel) {
  return hotel.name ?? 'Name not provided by source'
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

function hotelIcon(index, selected) {
  return L.divIcon({
    className: '',
    html: `<span class="pin${selected ? ' pin--selected' : ''}">${index + 1}</span>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -14],
  })
}

/** Enter/Space on a focused marker selects it (keyboard parity with the list). */
function bindKeyboard(marker, id) {
  const el = marker.getElement()
  if (!el || el.dataset.kbd) return
  el.dataset.kbd = '1'
  el.setAttribute('role', 'button')
  el.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      emit('select', id)
    }
  })
}

function render() {
  if (!map) return
  layer.clearLayers()
  markers.clear()
  if (!props.center) {
    map.setView([39.5, -98.35], 4)
    return
  }
  const c = [props.center.lat, props.center.lon]
  // Set the view first: Leaflet only creates marker elements once the map has a view.
  map.fitBounds(L.latLng(c).toBounds(props.radiusM * 2), { padding: [10, 10] })
  L.circle(c, {
    radius: props.radiusM,
    color: '#be185d',
    weight: 1.5,
    fillOpacity: 0.05,
    interactive: false,
  }).addTo(layer)
  L.marker(c, {
    icon: L.divIcon({ className: '', html: '<span class="zip-pin">ZIP</span>', iconSize: [38, 22], iconAnchor: [19, 11] }),
    title: `Search center for ZIP ${props.center.zip}`,
    alt: `Search center for ZIP ${props.center.zip}`,
    keyboard: false,
  })
    .bindTooltip(`ZIP ${props.center.zip} center (from Geoapify)`)
    .addTo(layer)

  props.hotels.forEach((hotel, index) => {
    const name = displayName(hotel)
    const marker = L.marker([hotel.lat, hotel.lon], {
      icon: hotelIcon(index, hotel.place_id === props.selectedId),
      title: `${index + 1}. ${name}`,
      alt: `${index + 1}. ${name}`,
      riseOnHover: true,
    })
      .bindPopup(`<strong>${index + 1}. ${escapeHtml(name)}</strong>`)
      .on('click', () => emit('select', hotel.place_id))
      .on('add', (event) => bindKeyboard(event.target, hotel.place_id))
      .addTo(layer)
    markers.set(hotel.place_id, { marker, index })
  })
}

function highlight(id, previous) {
  const prev = markers.get(previous)
  if (prev) {
    prev.marker.setIcon(hotelIcon(prev.index, false))
    bindKeyboard(prev.marker, previous)
    prev.marker.setZIndexOffset(0)
  }
  const current = markers.get(id)
  if (current && map) {
    current.marker.setIcon(hotelIcon(current.index, true))
    bindKeyboard(current.marker, id)
    current.marker.setZIndexOffset(1000)
    map.panTo(current.marker.getLatLng())
    current.marker.openPopup()
  }
}

onMounted(() => {
  map = L.map(mapEl.value, { scrollWheelZoom: false })
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Hotel data &copy; <a href="https://www.geoapify.com/">Geoapify</a>',
  }).addTo(map)
  layer = L.layerGroup().addTo(map)
  render()
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})

watch(() => [props.center, props.hotels], render)
watch(() => props.selectedId, (id, previous) => highlight(id, previous))
</script>

<template>
  <div
    ref="mapEl"
    class="hotel-map"
    role="region"
    aria-label="Map of hotel results. Use Tab to move between numbered hotel markers and Enter to select one."
  ></div>
</template>

<style scoped>
.hotel-map {
  width: 100%;
  height: 100%;
  min-height: 26rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  z-index: 0;
}

.hotel-map :deep(.pin) {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #fff;
  color: var(--accent-dark);
  border: 2px solid var(--accent);
  font: 700 0.8rem/1 system-ui, sans-serif;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.hotel-map :deep(.pin--selected) {
  background: #7e1d6b;
  border-color: #4a0d3f;
  color: #fff;
  transform: scale(1.25);
}

.hotel-map :deep(.leaflet-marker-icon:focus-visible) {
  outline: 3px solid #7e1d6b;
  outline-offset: 2px;
  border-radius: 50%;
}

.hotel-map :deep(.zip-pin) {
  display: grid;
  place-items: center;
  width: 38px;
  height: 22px;
  border-radius: 4px;
  background: var(--text);
  color: #fff;
  font: 700 0.7rem/1 system-ui, sans-serif;
}
</style>
