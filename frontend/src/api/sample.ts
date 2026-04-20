import { apiFetch } from './client'

export function loadSampleData(): Promise<{ collection_id: number; created: boolean }> {
  return apiFetch('/sample', { method: 'POST' })
}
