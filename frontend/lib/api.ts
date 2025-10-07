import type { RecommendationRequest, RecommendationResponse, ChatRequest, ChatResponse } from './types'

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'APIError'
  }
}

export async function fetchRecipes(
  request: RecommendationRequest,
  timeoutMs = 120000
): Promise<RecommendationResponse> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch('http://localhost:8000/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: controller.signal
    })

    clearTimeout(timeout)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new APIError(response.status, errorData.detail || `HTTP ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    clearTimeout(timeout)

    if (error instanceof APIError) throw error
    if (error.name === 'AbortError') {
      throw new APIError(408, 'Request timeout - please try again')
    }
    throw new APIError(500, 'Network error - check your connection')
  }
}

export async function sendChatMessage(
  request: ChatRequest,
  timeoutMs = 120000
): Promise<ChatResponse> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: controller.signal
    })

    clearTimeout(timeout)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new APIError(response.status, errorData.detail || `HTTP ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    clearTimeout(timeout)

    if (error instanceof APIError) throw error
    if (error.name === 'AbortError') {
      throw new APIError(408, 'Request timeout - please try again')
    }
    throw new APIError(500, 'Network error - check your connection')
  }
}
