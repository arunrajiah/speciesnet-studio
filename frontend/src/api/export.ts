export type ExportFormat = 'csv' | 'json' | 'wi-csv' | 'wdx'

export interface WdxParams {
  latitude?: number
  longitude?: number
  utcOffset?: string
  reviewedOnly: boolean
}

function wdxQuery(p: WdxParams): string {
  const q = new URLSearchParams({ reviewed_only: String(p.reviewedOnly) })
  if (p.latitude !== undefined) q.set('latitude', String(p.latitude))
  if (p.longitude !== undefined) q.set('longitude', String(p.longitude))
  if (p.utcOffset) q.set('utc_offset', p.utcOffset)
  return `&${q}`
}

export function exportUrl(collectionId: number, format: ExportFormat, wdx?: WdxParams): string {
  return `/api/collections/${collectionId}/export?format=${format}${format === 'wdx' && wdx ? wdxQuery(wdx) : ''}`
}

export async function triggerDownload(collectionId: number, format: ExportFormat, wdx?: WdxParams): Promise<void> {
  const url = exportUrl(collectionId, format, wdx)
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`)
  const blob = await res.blob()
  const objectUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objectUrl
  const name =
    format === 'wdx'
      ? `collection_${collectionId}.wdx.ndjson`
      : `collection_${collectionId}${format === 'wi-csv' ? '_wildlife_insights' : ''}.${format === 'json' ? 'json' : 'csv'}`
  a.download = name
  a.click()
  URL.revokeObjectURL(objectUrl)
}

export interface SendResult {
  sent: number
  skipped: Record<string, number>
  result: { received: number; inserted: number; updated: number; rejected: number } | null
}

/** Sends the collection to WildNetwork as WDX. The key is used for this request only; Studio never stores it. */
export async function sendToWildNetwork(collectionId: number, apiKey: string, wdx: WdxParams): Promise<SendResult> {
  const res = await fetch(`/api/collections/${collectionId}/send-wdx`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      api_key: apiKey,
      latitude: wdx.latitude,
      longitude: wdx.longitude,
      utc_offset: wdx.utcOffset || undefined,
      reviewed_only: wdx.reviewedOnly,
    }),
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.detail ?? `Send failed: ${res.statusText}`)
  return body as SendResult
}
