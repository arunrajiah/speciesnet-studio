export type JobStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface JobState {
  status: JobStatus
  stage: string
  current: number
  total: number
  started_at: string
  finished_at: string | null
  error: string | null
}
