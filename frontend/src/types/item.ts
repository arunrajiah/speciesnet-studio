export type ReviewStatus = 'unreviewed' | 'confirmed' | 'overridden' | 'flagged'

export interface ItemRead {
  id: number
  filename: string
  thumbnail_url: string | null
  top_label: string | null
  top_confidence: number | null
  review_status: ReviewStatus
  latitude: number | null
  longitude: number | null
}

export interface PredictionDetail {
  label: string
  confidence: number
  bbox_json: string | null
  model_version: string | null
}

export interface ReviewDetail {
  status: ReviewStatus
  override_label: string | null
  reviewer_note: string | null
  reviewer_name: string | null
}

export interface ItemDetail {
  id: number
  filename: string
  full_image_url: string
  thumbnail_url: string | null
  captured_at: string | null
  latitude: number | null
  longitude: number | null
  width: number | null
  height: number | null
  predictions: PredictionDetail[]
  review: ReviewDetail | null
}

export interface ReviewRecord {
  id: number
  item_id: number
  status: ReviewStatus
  override_label: string | null
  reviewer_note: string | null
  updated_at: string
}

export interface ItemFilters {
  label?: string
  min_conf?: number
  max_conf?: number
  status?: ReviewStatus
  q?: string
}

export interface AutoReviewPreview {
  count: number
}

export interface GeoItem {
  id: number
  filename: string
  latitude: number
  longitude: number
  top_label: string | null
  top_confidence: number | null
  review_status: ReviewStatus
  thumbnail_url: string | null
}

export interface CollectionStats {
  total: number
  reviewed: number
  unreviewed: number
  confirmed: number
  overridden: number
  flagged: number
  avg_confidence: number | null
  top_labels: { label: string; count: number }[]
  reviewers: { name: string; count: number }[]
}
