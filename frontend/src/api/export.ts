export type ExportFormat = 'csv' | 'json' | 'wi-csv'

export function exportUrl(collectionId: number, format: ExportFormat): string {
  return `/api/collections/${collectionId}/export?format=${format}`
}

export async function triggerDownload(collectionId: number, format: ExportFormat): Promise<void> {
  const url = exportUrl(collectionId, format)
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`)
  const blob = await res.blob()
  const objectUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objectUrl
  const ext = format === 'json' ? 'json' : 'csv'
  a.download = `collection_${collectionId}${format === 'wi-csv' ? '_wildlife_insights' : ''}.${ext}`
  a.click()
  URL.revokeObjectURL(objectUrl)
}
