const BASE_URL = '/api'

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'NetworkError'
  }
}

const MAX_RETRIES = 3
const RETRY_BASE_MS = 300

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let lastError: Error | undefined

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    if (attempt > 0) {
      await sleep(RETRY_BASE_MS * 2 ** (attempt - 1))
    }

    let response: Response
    try {
      response = await fetch(`${BASE_URL}${path}`, init)
    } catch (err) {
      lastError = new NetworkError(err instanceof Error ? err.message : String(err))
      // Only retry on network-level failures, not on API errors
      continue
    }

    if (!response.ok) {
      const text = await response.text().catch(() => '')
      throw new ApiError(response.status, `API error ${response.status}: ${text}`)
    }

    return response.json() as Promise<T>
  }

  throw lastError ?? new NetworkError('Request failed after retries')
}
