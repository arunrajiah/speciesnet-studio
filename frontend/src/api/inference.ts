import { apiFetch } from './client'
import type { JobState } from '../types/job'

export function startInference(collectionId: number): Promise<{ job_id: string }> {
  return apiFetch<{ job_id: string }>(`/collections/${collectionId}/inference`, {
    method: 'POST',
  })
}

export function getJob(jobId: string): Promise<JobState> {
  return apiFetch<JobState>(`/jobs/${jobId}`)
}

export function openJobSocket(jobId: string): WebSocket {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.host
  return new WebSocket(`${proto}://${host}/ws/jobs/${jobId}`)
}
