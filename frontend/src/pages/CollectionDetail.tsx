import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, CheckSquare, ImageIcon, Play } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { getCollection } from '../api/collections'
import { startInference } from '../api/inference'
import { batchReview, listItems, listLabels } from '../api/items'
import { AutoReviewDialog } from '../components/AutoReviewDialog'
import { ExportDialog } from '../components/ExportDialog'
import { FilterSidebar } from '../components/FilterSidebar'
import { Gallery } from '../components/Gallery'
import { ImportPredictionsDialog } from '../components/ImportPredictionsDialog'
import { InferenceProgressDialog } from '../components/InferenceProgressDialog'
import { StatsBar } from '../components/StatsBar'
import { useFilterParams } from '../hooks/useFilterParams'
import type { ItemRead } from '../types/item'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

export default function CollectionDetail() {
  const { id } = useParams<{ id: string }>()
  const collectionId = Number(id)
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [jobId, setJobId] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [filters, setFilters] = useFilterParams()
  const [selectionMode, setSelectionMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())

  const { data: collection, isLoading, isError } = useQuery({
    queryKey: ['collections', collectionId],
    queryFn: () => getCollection(collectionId),
    enabled: !isNaN(collectionId),
  })

  const { data: items = [] } = useQuery({
    queryKey: ['items', collectionId, filters],
    queryFn: () => listItems(collectionId, filters),
    enabled: !isNaN(collectionId) && !!collection && collection.item_count > 0,
  })

  const { data: labels = [] } = useQuery({
    queryKey: ['labels', collectionId],
    queryFn: () => listLabels(collectionId),
    enabled: !isNaN(collectionId),
  })

  const inferenceMutation = useMutation({
    mutationFn: () => startInference(collectionId),
    onSuccess: (data) => {
      setJobId(data.job_id)
      setDialogOpen(true)
    },
  })

  const batchMutation = useMutation({
    mutationFn: (vars: { status: 'confirmed' | 'flagged' }) =>
      batchReview(Array.from(selectedIds), vars),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items', collectionId] })
      queryClient.invalidateQueries({ queryKey: ['stats', collectionId] })
      setSelectedIds(new Set())
    },
  })

  const handleDialogClose = () => {
    setDialogOpen(false)
    queryClient.invalidateQueries({ queryKey: ['collections', collectionId] })
    queryClient.invalidateQueries({ queryKey: ['items', collectionId] })
  }

  const handleItemClick = (item: ItemRead) => {
    navigate(`/collections/${collectionId}/items/${item.id}`)
  }

  const handleToggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const handleToggleSelectionMode = () => {
    setSelectionMode((prev) => {
      if (prev) {
        setSelectedIds(new Set())
      }
      return !prev
    })
  }

  if (isLoading) {
    return (
      <div className="flex h-screen flex-col">
        <div className="flex items-center gap-4 border-b px-6 py-4">
          <Skeleton className="h-8 w-8 rounded-md" />
          <Skeleton className="h-6 w-64" />
          <Skeleton className="ml-auto h-8 w-24" />
          <Skeleton className="h-8 w-32" />
        </div>
        <div className="flex flex-1 overflow-hidden">
          <Skeleton className="w-56 border-r" />
          <div className="flex-1 p-4">
            <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(220px,1fr))]">
              {Array.from({ length: 16 }).map((_, i) => (
                <Skeleton key={i} className="aspect-square rounded-md" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (isError || !collection) {
    return (
      <div className="container py-10 space-y-4">
        <Button variant="ghost" asChild>
          <Link to="/collections">
            <ArrowLeft className="mr-2 h-4 w-4" aria-hidden="true" />
            Back
          </Link>
        </Button>
        <p className="text-destructive">Collection not found.</p>
      </div>
    )
  }

  return (
    <div className="flex h-screen flex-col">
      {/* header */}
      <div className="flex items-center gap-4 border-b px-6 py-4">
        <Button variant="ghost" size="icon" asChild aria-label="Back to collections">
          <Link to="/collections">
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          </Link>
        </Button>
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold tracking-tight truncate">{collection.name}</h1>
          <p className="text-xs text-muted-foreground truncate">{collection.source_folder}</p>
        </div>
        <Badge variant="secondary">{collection.item_count} images</Badge>
        <ImportPredictionsDialog collectionId={collectionId} />
        <AutoReviewDialog collectionId={collectionId} />
        <ExportDialog collectionId={collectionId} collectionName={collection.name} />
        <Button
          variant={selectionMode ? 'secondary' : 'outline'}
          onClick={handleToggleSelectionMode}
          aria-pressed={selectionMode}
          aria-label={selectionMode ? 'Cancel selection mode' : 'Enter selection mode'}
        >
          <CheckSquare className="mr-2 h-4 w-4" aria-hidden="true" />
          {selectionMode ? 'Cancel' : 'Select'}
        </Button>
        <Button
          onClick={() => inferenceMutation.mutate()}
          disabled={inferenceMutation.isPending || collection.item_count === 0}
          aria-label="Run inference on this collection"
        >
          <Play className="mr-2 h-4 w-4" aria-hidden="true" />
          Run inference
        </Button>
      </div>

      {/* stats bar */}
      {collection.item_count > 0 && <StatsBar collectionId={collectionId} />}

      {/* body */}
      <div className="flex flex-1 overflow-hidden">
        <FilterSidebar labels={labels} filters={filters} onChange={setFilters} />

        <div className="flex flex-col flex-1 overflow-hidden">
          {/* bulk action toolbar */}
          {selectionMode && (
            <div className="flex items-center gap-3 border-b bg-background px-4 py-2 sticky top-0 z-10">
              <span className="text-sm font-medium">
                {selectedIds.size} selected
              </span>
              <Button
                size="sm"
                variant="secondary"
                disabled={selectedIds.size === 0 || batchMutation.isPending}
                onClick={() => batchMutation.mutate({ status: 'confirmed' })}
              >
                Approve all
              </Button>
              <Button
                size="sm"
                variant="secondary"
                disabled={selectedIds.size === 0 || batchMutation.isPending}
                onClick={() => batchMutation.mutate({ status: 'flagged' })}
              >
                Flag all
              </Button>
              <button
                type="button"
                className="text-sm text-muted-foreground underline underline-offset-2 hover:text-foreground"
                onClick={() => setSelectedIds(new Set())}
              >
                Clear selection
              </button>
            </div>
          )}

          <div className="flex-1 overflow-hidden p-4">
            {collection.item_count === 0 ? (
              <div className="flex flex-col items-center justify-center h-full space-y-3 text-center">
                <ImageIcon className="h-12 w-12 text-muted-foreground" aria-hidden="true" />
                <p className="text-muted-foreground">
                  Ingestion is running in the background. Images will appear here shortly.
                </p>
              </div>
            ) : (
              <Gallery
                items={items}
                onItemClick={handleItemClick}
                selectionMode={selectionMode}
                selectedIds={selectedIds}
                onToggleSelect={handleToggleSelect}
              />
            )}
          </div>
        </div>
      </div>

      {jobId && (
        <InferenceProgressDialog
          jobId={jobId}
          open={dialogOpen}
          onClose={handleDialogClose}
        />
      )}
    </div>
  )
}
