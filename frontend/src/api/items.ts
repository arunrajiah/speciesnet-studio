import { apiFetch } from './client'
import type {
  AutoReviewPreview,
  CollectionStats,
  GeoItem,
  ItemDetail,
  ItemFilters,
  ItemRead,
  ReviewRecord,
  ReviewStatus,
} from '../types/item'

export function listItems(collectionId: number, filters?: ItemFilters): Promise<ItemRead[]> {
  const params = new URLSearchParams()
  if (filters?.label) params.set('label', filters.label)
  if (filters?.min_conf !== undefined) params.set('min_conf', String(filters.min_conf))
  if (filters?.max_conf !== undefined) params.set('max_conf', String(filters.max_conf))
  if (filters?.status) params.set('status', filters.status)
  if (filters?.q) params.set('q', filters.q)
  const qs = params.toString()
  return apiFetch<ItemRead[]>(`/collections/${collectionId}/items${qs ? `?${qs}` : ''}`)
}

export function getItem(itemId: number): Promise<ItemDetail> {
  return apiFetch<ItemDetail>(`/items/${itemId}`)
}

export function listLabels(collectionId: number): Promise<string[]> {
  return apiFetch<string[]>(`/collections/${collectionId}/labels`)
}

export function submitReview(
  itemId: number,
  data: { status: string; override_label?: string; reviewer_note?: string; reviewer_name?: string },
): Promise<ReviewRecord> {
  return apiFetch<ReviewRecord>(`/items/${itemId}/review`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function getCollectionStats(collectionId: number): Promise<CollectionStats> {
  return apiFetch<CollectionStats>(`/collections/${collectionId}/stats`)
}

export function batchReview(
  itemIds: number[],
  data: {
    status: ReviewStatus
    override_label?: string
    reviewer_note?: string
    reviewer_name?: string
  },
): Promise<{ updated: number }> {
  return apiFetch<{ updated: number }>('/items/batch-review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item_ids: itemIds, ...data }),
  })
}

export function listGeoItems(collectionId: number): Promise<GeoItem[]> {
  return apiFetch<GeoItem[]>(`/collections/${collectionId}/geo-items`)
}

export function importPredictions(
  collectionId: number,
  predictionsPath: string,
): Promise<{ imported: number; warnings: string[] }> {
  return apiFetch<{ imported: number; warnings: string[] }>(
    `/collections/${collectionId}/import-predictions`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ predictions_path: predictionsPath }),
    },
  )
}

export function autoReviewPreview(
  collectionId: number,
  params: { min_confidence?: number; labels?: string[]; only_unreviewed?: boolean },
): Promise<AutoReviewPreview> {
  const qs = new URLSearchParams()
  if (params.min_confidence !== undefined) qs.set('min_confidence', String(params.min_confidence))
  if (params.labels?.length) qs.set('labels', params.labels.join(','))
  if (params.only_unreviewed !== undefined) qs.set('only_unreviewed', String(params.only_unreviewed))
  return apiFetch<AutoReviewPreview>(
    `/collections/${collectionId}/auto-review/preview?${qs.toString()}`,
  )
}

export function runAutoReview(
  collectionId: number,
  body: {
    status: ReviewStatus
    min_confidence?: number
    labels?: string[]
    only_unreviewed?: boolean
  },
): Promise<{ reviewed: number }> {
  return apiFetch<{ reviewed: number }>(`/collections/${collectionId}/auto-review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
