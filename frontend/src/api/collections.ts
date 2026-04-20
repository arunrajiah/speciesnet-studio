import { apiFetch } from './client'
import type { CollectionCreate, CollectionRead, IngestionStatus } from '../types/collection'

export function listCollections(): Promise<CollectionRead[]> {
  return apiFetch<CollectionRead[]>('/collections')
}

export function createCollection(data: CollectionCreate): Promise<CollectionRead> {
  return apiFetch<CollectionRead>('/collections', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function getCollection(id: number): Promise<CollectionRead> {
  return apiFetch<CollectionRead>(`/collections/${id}`)
}

export function deleteCollection(id: number): Promise<void> {
  return apiFetch<void>(`/collections/${id}`, { method: 'DELETE' })
}

export function getIngestionStatus(id: number): Promise<IngestionStatus> {
  return apiFetch<IngestionStatus>(`/collections/${id}/ingestion-status`)
}
