<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { cancelBooking, deleteBooking, listBookings } from '../api.js'

const props = defineProps({
  reloadKey: { type: Number, default: 0 },
})

const bookings = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const statusMessage = ref('')
const busyBooking = ref('')
const pendingDelete = ref('')

const confirmedCount = computed(
  () => bookings.value.filter((b) => b.status === 'confirmed').length,
)

async function load() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const data = await listBookings()
    bookings.value = data.results
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

onMounted(load)
watch(() => props.reloadKey, load)

async function onCancel(booking) {
  errorMessage.value = ''
  statusMessage.value = ''
  busyBooking.value = booking.booking_id
  try {
    await cancelBooking(booking.booking_id)
    statusMessage.value =
      `Booking ${booking.booking_id} cancelled. The record stays in your history.`
    await load()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    busyBooking.value = ''
  }
}

function askDelete(bookingId) {
  statusMessage.value = ''
  errorMessage.value = ''
  pendingDelete.value = pendingDelete.value === bookingId ? '' : bookingId
}

async function onDelete(booking) {
  errorMessage.value = ''
  statusMessage.value = ''
  busyBooking.value = booking.booking_id
  try {
    await deleteBooking(booking.booking_id)
    statusMessage.value = `Booking ${booking.booking_id} deleted permanently.`
    pendingDelete.value = ''
    await load()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    busyBooking.value = ''
  }
}

function money(value) {
  return `$${Number(value).toFixed(2)}`
}
</script>

<template>
  <section class="panel" aria-labelledby="history-heading">
    <div class="panel-head">
      <div>
        <h2 id="history-heading">Booking history</h2>
        <p class="panel-hint">
          Cancel keeps the record and marks it cancelled. Delete removes it for good.
        </p>
      </div>
      <button type="button" class="btn btn--ghost" :disabled="isLoading" @click="load">
        {{ isLoading ? 'Refreshing…' : 'Refresh' }}
      </button>
    </div>

    <p v-if="errorMessage" class="banner banner--error" role="alert">
      {{ errorMessage }}
    </p>
    <p v-if="statusMessage" class="banner banner--success" role="status">
      {{ statusMessage }}
    </p>

    <p v-if="isLoading && bookings.length === 0" class="state-message">
      Loading your bookings…
    </p>

    <p
      v-else-if="bookings.length === 0"
      class="state-message state-message--empty"
    >
      No bookings yet. Search for a hotel and book a stay to see it here.
    </p>

    <div v-else class="results">
      <p class="results-count">
        {{ bookings.length }} booking{{ bookings.length === 1 ? '' : 's' }},
        {{ confirmedCount }} confirmed.
      </p>

      <div class="table-wrap">
        <table class="data-table">
          <caption class="visually-hidden">Your bookings</caption>
          <thead>
            <tr>
              <th scope="col">Booking</th>
              <th scope="col">Traveler</th>
              <th scope="col">Stay</th>
              <th scope="col">Dates</th>
              <th scope="col" class="num">Total</th>
              <th scope="col">Booked on</th>
              <th scope="col">Status</th>
              <th scope="col"><span class="visually-hidden">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="booking in bookings" :key="booking.booking_id">
              <tr>
                <th scope="row" class="id-cell">{{ booking.booking_id }}</th>
                <td class="nowrap">{{ booking.traveler }}</td>
                <td>
                  {{ booking.hotel_name }}<br />
                  <small>{{ booking.trip_name }} · {{ booking.city }}, {{ booking.state }}</small>
                </td>
                <td class="nowrap">{{ booking.check_in }}<br />→ {{ booking.check_out }}</td>
                <td class="num strong">{{ money(booking.stay_price_usd) }}</td>
                <td class="nowrap">{{ booking.booked_on }}</td>
                <td>
                  <span class="badge" :class="`badge--${booking.status}`">
                    {{ booking.status === 'confirmed' ? 'Confirmed' : 'Cancelled' }}
                  </span>
                </td>
                <td>
                  <div class="actions">
                    <button
                      type="button"
                      class="btn btn--ghost btn--small"
                      :disabled="booking.status === 'cancelled' || busyBooking === booking.booking_id"
                      @click="onCancel(booking)"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      class="btn btn--danger btn--small"
                      :disabled="busyBooking === booking.booking_id"
                      @click="askDelete(booking.booking_id)"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="pendingDelete === booking.booking_id" class="confirm-row">
                <td colspan="8">
                  <div class="confirm">
                    <span>
                      Delete booking <strong>{{ booking.booking_id }}</strong>
                      permanently? This cannot be undone.
                    </span>
                    <button
                      type="button"
                      class="btn btn--danger btn--small"
                      :disabled="busyBooking === booking.booking_id"
                      @click="onDelete(booking)"
                    >
                      {{ busyBooking === booking.booking_id ? 'Deleting…' : 'Yes, delete' }}
                    </button>
                    <button
                      type="button"
                      class="btn btn--ghost btn--small"
                      @click="pendingDelete = ''"
                    >
                      Keep it
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.results-count {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin: 1rem 0 0.6rem;
}

.id-cell {
  text-align: left;
  font-variant-numeric: tabular-nums;
}

.actions {
  display: flex;
  gap: 0.4rem;
  white-space: nowrap;
}

.confirm-row td {
  background: var(--danger-soft);
}

.confirm {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.25rem 0;
}

small {
  color: var(--text-muted);
}
</style>
