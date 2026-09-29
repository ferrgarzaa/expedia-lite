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
    const error = new Error('Could not reach the Expedia Lite server. Is the backend running?')
    error.code = 'network'
    throw error
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status}).`
    let code = 'request_failed'
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') {
        detail = body.detail
      } else if (body?.detail?.message) {
        detail = body.detail.message
        code = body.detail.code ?? code
      }
    } catch {
      // Keep the generic message.
    }
    const error = new Error(detail)
    error.code = code
    error.status = response.status
    throw error
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

/**
 * Assignment 2 — live hotels within 5 km of a U.S. ZIP code.
 * The browser only calls FastAPI; FastAPI holds the Geoapify key.
 */
export function searchHotelsNearZip(zip) {
  return request(`/api/hotels/nearby?zip=${encodeURIComponent(zip)}`)
}
