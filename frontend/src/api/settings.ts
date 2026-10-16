export interface WildNetworkSettings {
  has_api_key: boolean
  endpoint: string
  latitude: number | null
  longitude: number | null
  utc_offset: string | null
  round_coords: number
  auto_send: boolean
  last_send_at: string | null
  last_send_result: string | null
}

export type WildNetworkUpdate = Partial<Omit<WildNetworkSettings, 'has_api_key' | 'last_send_at' | 'last_send_result'>> & {
  api_key?: string
}

export async function getWildNetworkSettings(): Promise<WildNetworkSettings> {
  const res = await fetch('/api/settings/wildnetwork')
  if (!res.ok) throw new Error(`Could not load settings: ${res.statusText}`)
  return res.json()
}

export async function saveWildNetworkSettings(update: WildNetworkUpdate): Promise<WildNetworkSettings> {
  const res = await fetch('/api/settings/wildnetwork', {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(update),
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.detail ?? `Could not save settings: ${res.statusText}`)
  return body as WildNetworkSettings
}
