export type ReviewStatus = 'unreviewed' | 'confirmed' | 'overridden' | 'flagged'

export interface ItemRead {
  id: number
  filename: string
  thumbnail_url: string | null
  top_label: string | null
  top_confidence: number | null
  review_status: ReviewStatus
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
