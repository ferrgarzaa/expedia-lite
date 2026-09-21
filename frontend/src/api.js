/**
 * The only place the View talks to the backend.
 *
 * Every call goes to FastAPI over HTTP; the frontend has no knowledge
 * of SQLite, the CSV seed files, or how records are joined.
 */

const API_BASE = 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new Error('Could not reach the booking service. Is the backend running?')
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status}).`
    try {
      const body = await response.json()
      if (body?.detail) {
        detail = typeof body.detail === 'string' ? body.detail : detail
      }
    } catch {
      // Keep the generic message.
    }
    throw new Error(detail)
  }

  return response.json()
}

export function searchStays(hotelName) {
  return request(`/api/search?hotel=${encodeURIComponent(hotelName)}`)
}

export function listUsers() {
  return request('/api/users')
}

export function listBookings() {
  return request('/api/bookings')
}

export function createBooking(userId, tripId) {
  return request('/api/bookings', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, trip_id: tripId }),
  })
}

export function cancelBooking(bookingId) {
  return request(`/api/bookings/${bookingId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status: 'cancelled' }),
  })
}

export function deleteBooking(bookingId) {
  return request(`/api/bookings/${bookingId}`, { method: 'DELETE' })
}
