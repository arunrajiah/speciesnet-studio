import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, ArrowRight, MapPin } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { getItem, listItems } from '../api/items'
import { BoundingBoxOverlay } from '../components/BoundingBoxOverlay'
import { ReviewControls } from '../components/ReviewControls'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export default function ItemDetail() {
  const { collectionId, itemId } = useParams<{ collectionId: string; itemId: string }>()
  const colId = Number(collectionId)
  const itmId = Number(itemId)
  const navigate = useNavigate()

  const { data: item, isLoading, isError, refetch } = useQuery({
    queryKey: ['item', itmId],
    queryFn: () => getItem(itmId),
    enabled: !isNaN(itmId),
  })

  const { data: siblings = [] } = useQuery({
    queryKey: ['items', colId],
    queryFn: () => listItems(colId),
    enabled: !isNaN(colId),
  })

  const siblingIds = siblings.map((s) => s.id)
  const currentIdx = siblingIds.indexOf(itmId)
  const prevId = currentIdx > 0 ? siblingIds[currentIdx - 1] : null
  const nextId = currentIdx < siblingIds.length - 1 ? siblingIds[currentIdx + 1] : null

  const goTo = (id: number) => navigate(`/collections/${colId}/items/${id}`)

  const topPred = item?.predictions[0] ?? null

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading…</p>
      </div>
    )
  }

  if (isError || !item) {
    return (
      <div className="container py-10 space-y-4">
        <Button variant="ghost" asChild>
          <Link to={`/collections/${colId}`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Link>
        </Button>
        <p className="text-destructive">Item not found.</p>
      </div>
    )
  }

  return (
    <div className="flex h-screen flex-col">
      {/* top bar */}
      <div className="flex items-center gap-3 border-b px-4 py-2">
        <Button variant="ghost" size="icon" asChild aria-label="Back to collection">
          <Link to={`/collections/${colId}`}>
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="flex-1 truncate text-sm text-muted-foreground">{item.filename}</span>
        <Button
          variant="ghost"
          size="icon"
          disabled={!prevId}
          onClick={() => prevId && goTo(prevId)}
          aria-label="Previous image"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <span className="text-xs text-muted-foreground">
          {currentIdx + 1} / {siblingIds.length}
        </span>
        <Button
          variant="ghost"
          size="icon"
          disabled={!nextId}
          onClick={() => nextId && goTo(nextId)}
          aria-label="Next image"
        >
          <ArrowRight className="h-4 w-4" />
        </Button>
      </div>

      {/* body */}
      <div className="flex flex-1 overflow-hidden">
        {/* image pane */}
        <div className="relative flex flex-[2] items-center justify-center bg-black overflow-hidden">
          <img
            src={item.full_image_url}
            alt={item.filename}
            className="max-h-full max-w-full object-contain"
          />
          <BoundingBoxOverlay
            bboxJson={topPred?.bbox_json ?? null}
            imageWidth={item.width}
            imageHeight={item.height}
            label={topPred?.label ?? null}
            confidence={topPred?.confidence ?? null}
          />
        </div>

        {/* sidebar */}
        <div className="flex w-80 shrink-0 flex-col gap-4 overflow-y-auto border-l p-4">
          {/* predictions */}
          <section>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Predictions
            </h2>
            {item.predictions.length === 0 ? (
              <p className="text-xs text-muted-foreground">No predictions</p>
            ) : (
              <ul className="space-y-1">
                {item.predictions.map((p, i) => (
                  <li key={i} className="flex items-center justify-between text-sm">
                    <span className="truncate">{p.label}</span>
                    <Badge variant="secondary">{Math.round(p.confidence * 100)}%</Badge>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* metadata */}
          <section>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Metadata
            </h2>
            <dl className="space-y-1 text-sm">
              {item.captured_at && (
                <>
                  <dt className="text-muted-foreground">Captured</dt>
                  <dd>{new Date(item.captured_at).toLocaleString()}</dd>
                </>
              )}
              {item.width && item.height && (
                <>
                  <dt className="text-muted-foreground">Dimensions</dt>
                  <dd>
                    {item.width} × {item.height}
                  </dd>
                </>
              )}
              {item.latitude != null && item.longitude != null && (
                <>
                  <dt className="text-muted-foreground flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    Location
                  </dt>
                  <dd>
                    {item.latitude.toFixed(5)}, {item.longitude.toFixed(5)}
                  </dd>
                </>
              )}
            </dl>
          </section>

          {/* review */}
          <section>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Review
            </h2>
            <ReviewControls
              itemId={item.id}
              collectionId={colId}
              currentReview={item.review}
              topLabel={topPred?.label ?? null}
              onReviewed={() => refetch()}
              onNext={() => nextId && goTo(nextId)}
              onPrev={() => prevId && goTo(prevId)}
            />
          </section>
        </div>
      </div>
    </div>
  )
}
