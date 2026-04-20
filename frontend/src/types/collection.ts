export interface CollectionRead {
  id: number
  name: string
  source_folder: string
  created_at: string
  item_count: number
}

export interface CollectionCreate {
  name: string
  source_folder: string
}

export interface IngestionStatus {
  processed: number
  total: number
  stage: 'idle' | 'scanning' | 'ingesting' | 'done'
}
