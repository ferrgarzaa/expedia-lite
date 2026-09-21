<script setup>
import { inject, onMounted, ref } from 'vue'
import { createBooking, listUsers, searchStays } from '../api.js'

const refreshHistory = inject('refreshHistory', () => {})
const goToHistory = inject('goToHistory', () => {})

const hotelName = ref('')
const submittedQuery = ref('')
const results = ref([])
const hasSearched = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const travelers = ref([])
const selectedTraveler = ref('')
const openBookingFor = ref('')
const bookingInFlight = ref('')
const successMessage = ref('')

onMounted(async () => {
  try {
    const data = await listUsers()
    travelers.value = data.results
    selectedTraveler.value = data.results[0]?.user_id ?? ''
  } catch (error) {
    errorMessage.value = error.message
  }
})

async function runSearch() {
  errorMessage.value = ''
  successMessage.value = ''
  openBookingFor.value = ''

  const query = hotelName.value.trim()
  if (!query) {
    errorMessage.value = 'Enter a hotel name to search.'
    return
  }

  isLoading.value = true
  try {
    const data = await searchStays(query)
    results.value = data.results
    submittedQuery.value = data.query
    hasSearched.value = true
  } catch (error) {
    errorMessage.value = error.message
    results.value = []
    hasSearched.value = false
  } finally {
    isLoading.value = false
  }
}

function toggleBookingForm(tripId) {
  successMessage.value = ''
  errorMessage.value = ''
  openBookingFor.value = openBookingFor.value === tripId ? '' : tripId
}

async function confirmBooking(trip) {
  errorMessage.value = ''
  successMessage.value = ''

  if (!selectedTraveler.value) {
    errorMessage.value = 'Choose a traveler before booking.'
    return
  }

  bookingInFlight.value = trip.trip_id
  try {
    const booking = await createBooking(selectedTraveler.value, trip.trip_id)
    successMessage.value =
      `Booked! Confirmation ${booking.booking_id} for ${booking.traveler} ` +
      `at ${booking.hotel_name}.`
    openBookingFor.value = ''
    refreshHistory()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    bookingInFlight.value = ''
  }
}

function money(value) {
  return `$${Number(value).toFixed(2)}`
}
</script>

<template>
  <section class="panel" aria-labelledby="search-heading">
    <h2 id="search-heading">Search hotel stays</h2>
    <p class="panel-hint">
      Type all or part of a hotel name, for example
      <code>Harbor Lantern Hotel</code>.
    </p>

    <form class="search-form" @submit.prevent="runSearch">
      <div class="field">
        <label for="hotel-input">Hotel name</label>
        <input
          id="hotel-input"
          v-model="hotelName"
          type="search"
          placeholder="e.g. Harbor Lantern Hotel"
          autocomplete="off"
        />
      </div>

      <div class="field">
        <label for="traveler-select">Traveler</label>
        <select id="traveler-select" v-model="selectedTraveler">
          <option v-for="person in travelers" :key="person.user_id" :value="person.user_id">
            {{ person.display_name }}
          </option>
        </select>
      </div>

      <button type="submit" class="btn btn--primary" :disabled="isLoading">
        {{ isLoading ? 'Searching…' : 'Search' }}
      </button>
    </form>

    <p v-if="errorMessage" class="banner banner--error" role="alert">
      {{ errorMessage }}
    </p>
    <p v-if="successMessage" class="banner banner--success" role="status">
      {{ successMessage }}
      <button type="button" class="link-button" @click="goToHistory()">
        View booking history
      </button>
    </p>

    <p v-if="isLoading" class="state-message">Searching hotels…</p>

    <p
      v-else-if="hasSearched && results.length === 0"
      class="state-message state-message--empty"
    >
      No hotel stays found for “{{ submittedQuery }}”. Check the spelling or
      try part of the name.
    </p>

    <div v-else-if="results.length > 0" class="results">
      <p class="results-count">
        {{ results.length }} stay{{ results.length === 1 ? '' : 's' }} found for
        “{{ submittedQuery }}”.
      </p>

      <div class="table-wrap">
        <table class="data-table">
          <caption class="visually-hidden">
            Hotel stays matching {{ submittedQuery }}
          </caption>
          <thead>
            <tr>
              <th scope="col">Trip</th>
              <th scope="col">Hotel</th>
              <th scope="col">Location</th>
              <th scope="col">Check-in</th>
              <th scope="col">Check-out</th>
              <th scope="col" class="num">Nights</th>
              <th scope="col" class="num">Nightly rate</th>
              <th scope="col" class="num">Stay price</th>
              <th scope="col"><span class="visually-hidden">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="trip in results" :key="trip.trip_id">
              <tr>
                <td>{{ trip.trip_name }}</td>
                <td>{{ trip.hotel_name }}</td>
                <td class="nowrap">{{ trip.city }}, {{ trip.state }}</td>
                <td class="nowrap">{{ trip.check_in }}</td>
                <td class="nowrap">{{ trip.check_out }}</td>
                <td class="num">{{ trip.nights }}</td>
                <td class="num">{{ money(trip.nightly_rate_usd) }}</td>
                <td class="num strong">{{ money(trip.stay_price_usd) }}</td>
                <td>
                  <button
                    type="button"
                    class="btn btn--primary btn--small"
                    :aria-expanded="openBookingFor === trip.trip_id"
                    @click="toggleBookingForm(trip.trip_id)"
                  >
                    {{ openBookingFor === trip.trip_id ? 'Close' : 'Book' }}
                  </button>
                </td>
              </tr>

              <tr v-if="openBookingFor === trip.trip_id" class="booking-row">
                <td colspan="9">
                  <div class="booking-form">
                    <p>
                      Book <strong>{{ trip.trip_name }}</strong> at
                      <strong>{{ trip.hotel_name }}</strong> for
                      <strong>{{ money(trip.stay_price_usd) }}</strong>
                      ({{ trip.nights }} nights).
                    </p>
                    <label :for="`booking-traveler-${trip.trip_id}`">Traveler</label>
                    <select
                      :id="`booking-traveler-${trip.trip_id}`"
                      v-model="selectedTraveler"
                    >
                      <option
                        v-for="person in travelers"
                        :key="person.user_id"
                        :value="person.user_id"
                      >
                        {{ person.display_name }}
                      </option>
                    </select>
                    <button
                      type="button"
                      class="btn btn--primary"
                      :disabled="bookingInFlight === trip.trip_id"
                      @click="confirmBooking(trip)"
                    >
                      {{ bookingInFlight === trip.trip_id ? 'Booking…' : 'Confirm booking' }}
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <p v-else class="state-message state-message--idle">
      Your results will appear here.
    </p>
  </section>
</template>

<style scoped>
.search-form {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  flex-wrap: wrap;
  margin: 1.25rem 0 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.field label {
  font-weight: 600;
  font-size: 0.9rem;
}

.field input {
  min-width: 18rem;
}

.results-count {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin: 0 0 0.6rem;
}

.booking-row td {
  background: var(--surface-muted);
}

.booking-form {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.35rem 0;
}

.booking-form p {
  margin: 0;
  flex: 1 1 20rem;
}

.booking-form label {
  font-weight: 600;
  font-size: 0.9rem;
}
</style>
