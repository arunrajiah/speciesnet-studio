export interface HealthResponse {
  status: string
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch('/health')
  if (!res.ok) throw new Error('Backend unreachable')
  return res.json() as Promise<HealthResponse>
}
