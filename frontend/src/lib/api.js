/*
  One place for talking to the backend.
  Every page calls api('/something') instead of writing fetch() by hand,
  so errors are handled the same way everywhere.
*/

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

export async function api(path, { method = 'GET', body } = {}) {
  // FormData = file uploads (like audio). The browser sets the right headers itself.
  // Anything else is sent as JSON.
  const isUpload = body instanceof FormData

  let response
  try {
    response = await fetch(`/api${path}`, {
      method,
      headers: body && !isUpload ? { 'Content-Type': 'application/json' } : undefined,
      body: isUpload ? body : body ? JSON.stringify(body) : undefined,
    })
  } catch {
    // fetch only throws when the request never reached the server
    throw new ApiError("Can't reach the server. Make sure the backend is running on port 8000.", 0)
  }

  if (response.status === 204) return null // 204 = success with no body (e.g. logout)

  let data = null
  try {
    data = await response.json()
  } catch {
    // body wasn't JSON; keep data as null
  }

  if (!response.ok) throw new ApiError(readableError(data, response.status), response.status)
  return data
}

// Turns FastAPI's error responses into one readable sentence.
function readableError(data, status) {
  const detail = data?.detail

  // Our own errors, e.g. raise HTTPException(401, "Invalid email or password")
  if (typeof detail === 'string') return detail

  // Pydantic validation errors (422) arrive as a list
  if (Array.isArray(detail) && detail.length > 0) {
    const field = detail[0].loc?.at(-1)
    const message = detail[0].msg.replace(/^Value error, /, '')
    return field ? `${capitalize(String(field))}: ${message}` : message
  }

  if (status >= 500) return 'The server ran into a problem. Try again in a moment.'
  return 'Something went wrong. Try again.'
}

function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.slice(1)
}
