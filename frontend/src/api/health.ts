import { apiFetch } from './client'

export interface HealthResponse {
  status: string
}

export function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health')
}
