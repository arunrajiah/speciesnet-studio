export function exportUrl(collectionId: number, format: 'csv' | 'json'): string {
  return `/api/collections/${collectionId}/export?format=${format}`
}

export async function triggerDownload(collectionId: number, format: 'csv' | 'json'): Promise<void> {
  const url = exportUrl(collectionId, format)
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Export failed: ${res.statusText}`)
  const blob = await res.blob()
  const objectUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objectUrl
  a.download = `collection_${collectionId}.${format}`
  a.click()
  URL.revokeObjectURL(objectUrl)
}
