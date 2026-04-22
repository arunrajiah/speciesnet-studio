import { apiFetch } from './client'
import type { CollectionStats, ItemDetail, ItemFilters, ItemRead, ReviewRecord, ReviewStatus } from '../types/item'

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
  data: { status: string; override_label?: string; reviewer_note?: string },
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
  data: { status: ReviewStatus; override_label?: string; reviewer_note?: string },
): Promise<{ updated: number }> {
  return apiFetch<{ updated: number }>('/items/batch-review', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item_ids: itemIds, ...data }),
  })
}
