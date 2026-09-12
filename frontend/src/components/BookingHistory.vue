<script setup>
import { onMounted, ref } from 'vue'

const API_BASE = 'http://127.0.0.1:8000'

const bookings = ref([])
const errorMessage = ref('')
const actionMessage = ref('')
const isLoading = ref(false)

async function loadBookings() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(`${API_BASE}/api/bookings`)
    if (!response.ok) {
      throw new Error('Failed to load bookings')
    }
    bookings.value = await response.json()
  } catch {
    errorMessage.value = 'Could not load booking history. Please try again.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadBookings)

async function cancelBooking(bookingId) {
  actionMessage.value = ''
  try {
    const response = await fetch(`${API_BASE}/api/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'cancelled' }),
    })
    if (!response.ok) {
      throw new Error('Cancel failed')
    }
    actionMessage.value = `Booking ${bookingId} cancelled.`
    await loadBookings()
  } catch {
    actionMessage.value = `Could not cancel booking ${bookingId}.`
  }
}

async function deleteBooking(bookingId) {
  actionMessage.value = ''
  try {
    const response = await fetch(`${API_BASE}/api/bookings/${bookingId}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      throw new Error('Delete failed')
    }
    actionMessage.value = `Booking ${bookingId} deleted.`
    await loadBookings()
  } catch {
    actionMessage.value = `Could not delete booking ${bookingId}.`
  }
}
</script>

<template>
  <section class="booking-history">
    <h1>Booking History</h1>
    <p class="tagline">All simulated reservations, oldest to newest.</p>

    <button type="button" class="refresh-button" @click="loadBookings" :disabled="isLoading">
      {{ isLoading ? 'Refreshing…' : 'Refresh' }}
    </button>

    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <p v-if="actionMessage" class="action-message" role="status">{{ actionMessage }}</p>

    <p v-if="!isLoading && bookings.length === 0" class="no-results">
      No bookings yet.
    </p>

    <table v-else-if="bookings.length > 0" class="history-table">
      <caption class="visually-hidden">Booking history</caption>
      <thead>
        <tr>
          <th scope="col">Booking</th>
          <th scope="col">Traveler</th>
          <th scope="col">Trip</th>
          <th scope="col">Hotel</th>
          <th scope="col">Dates</th>
          <th scope="col">Booked on</th>
          <th scope="col">Status</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in bookings" :key="b.booking_id">
          <td>{{ b.booking_id }}</td>
          <td>{{ b.display_name }}</td>
          <td>{{ b.trip_name }}</td>
          <td>{{ b.hotel_name }} ({{ b.city }}, {{ b.state }})</td>
          <td>{{ b.check_in }} → {{ b.check_out }}</td>
          <td>{{ b.booked_on }}</td>
          <td>
            <span class="status" :class="b.status">{{ b.status }}</span>
          </td>
          <td class="actions">
            <button
              v-if="b.status !== 'cancelled'"
              type="button"
              class="cancel-button"
              @click="cancelBooking(b.booking_id)"
            >
              Cancel
            </button>
            <button
              type="button"
              class="delete-button"
              @click="deleteBooking(b.booking_id)"
            >
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<style scoped>
.booking-history {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
  font-family: system-ui, sans-serif;
}

.tagline {
  color: #555;
  margin-bottom: 1rem;
}

.refresh-button {
  padding: 0.45rem 1rem;
  font-size: 0.95rem;
  background: #eee;
  color: #333;
  border: 1px solid #999;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
}

.refresh-button:hover:not(:disabled) {
  background: #ddd;
}

.refresh-button:focus-visible,
.cancel-button:focus-visible,
.delete-button:focus-visible {
  outline: 3px solid #1f7a4d;
  outline-offset: 2px;
}

.error {
  color: #9b1c1c;
  font-weight: 600;
}

.action-message {
  color: #1f7a4d;
  font-weight: 600;
}

.no-results {
  color: #444;
  font-style: italic;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  text-align: left;
  padding: 0.5rem 0.6rem;
  border-bottom: 1px solid #ddd;
  vertical-align: top;
}

.history-table th {
  background: #f2f2f2;
}

.status {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.85rem;
  text-transform: capitalize;
}

.status.confirmed {
  background: #e3f3ea;
  color: #1f7a4d;
}

.status.cancelled {
  background: #f3e3e3;
  color: #9b1c1c;
}

.actions {
  white-space: nowrap;
}

.cancel-button,
.delete-button {
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.4rem;
}

.cancel-button {
  background: #eee;
  color: #333;
  border: 1px solid #999;
}

.cancel-button:hover {
  background: #ddd;
}

.delete-button {
  background: #fff;
  color: #9b1c1c;
  border: 1px solid #9b1c1c;
}

.delete-button:hover {
  background: #fbe9e9;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}
</style>
