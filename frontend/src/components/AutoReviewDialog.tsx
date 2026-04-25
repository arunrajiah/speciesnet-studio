import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Wand2 } from 'lucide-react'
import { useState } from 'react'
import { autoReviewPreview, runAutoReview } from '../api/items'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'

// Labels SpeciesNet assigns to non-wildlife frames
const BLANK_LABELS = ['blank', 'human', 'vehicle', 'no_cv_result']

interface Props {
  collectionId: number
}

export function AutoReviewDialog({ collectionId }: Props) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)

  // Confidence threshold slider — stored as 0–100 integer for display
  const [threshold, setThreshold] = useState(90)
  const [includeBlanks, setIncludeBlanks] = useState(true)
  const [result, setResult] = useState<{ reviewed: number } | null>(null)

  // Live count preview — refetches whenever threshold or includeBlanks changes
  const minConf = threshold / 100
  const labels = includeBlanks ? BLANK_LABELS : undefined

  const { data: preview } = useQuery({
    queryKey: ['auto-review-preview', collectionId, threshold, includeBlanks],
    queryFn: () =>
      autoReviewPreview(collectionId, {
        min_confidence: minConf,
        labels: includeBlanks ? BLANK_LABELS : undefined,
        only_unreviewed: true,
      }),
    enabled: open && !result,
  })

  const mutation = useMutation({
    mutationFn: () =>
      runAutoReview(collectionId, {
        status: 'confirmed',
        min_confidence: minConf,
        labels,
        only_unreviewed: true,
      }),
    onSuccess: (data) => {
      setResult(data)
      queryClient.invalidateQueries({ queryKey: ['items', collectionId] })
      queryClient.invalidateQueries({ queryKey: ['stats', collectionId] })
    },
  })

  const handleOpenChange = (next: boolean) => {
    setOpen(next)
    if (!next) {
      setThreshold(90)
      setIncludeBlanks(true)
      setResult(null)
      mutation.reset()
    }
  }

  const count = preview?.count ?? 0

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" aria-label="Auto-approve by confidence">
          <Wand2 className="mr-2 h-4 w-4" aria-hidden="true" />
          Auto-approve
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Auto-approve by confidence</DialogTitle>
          <DialogDescription>
            Bulk-confirm all unreviewed images whose top prediction meets the threshold. Saves time
            on high-confidence sweeps.
          </DialogDescription>
        </DialogHeader>

        {!result ? (
          <div className="space-y-6 py-2">
            {/* Confidence threshold */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Minimum confidence</Label>
                <span className="text-sm font-semibold tabular-nums">{threshold}%</span>
              </div>
              <Slider
                min={50}
                max={99}
                step={1}
                value={[threshold]}
                onValueChange={([v]) => setThreshold(v)}
                aria-label="Confidence threshold"
              />
              <p className="text-xs text-muted-foreground">
                Only images with top-prediction confidence ≥ {threshold}% will be approved.
              </p>
            </div>

            {/* Blanks toggle */}
            <div className="flex items-start gap-3">
              <input
                id="include-blanks"
                type="checkbox"
                className="mt-0.5 h-4 w-4 rounded border-input accent-primary"
                checked={includeBlanks}
                onChange={(e) => setIncludeBlanks(e.target.checked)}
              />
              <div className="space-y-0.5">
                <Label htmlFor="include-blanks" className="cursor-pointer">
                  Also approve blanks, humans &amp; vehicles
                </Label>
                <p className="text-xs text-muted-foreground">
                  Images labelled <em>blank</em>, <em>human</em>, or <em>vehicle</em> will be
                  confirmed regardless of the threshold above.
                </p>
              </div>
            </div>

            {/* Live count */}
            <div className="rounded-md border bg-muted/40 px-4 py-3 text-sm">
              {preview === undefined ? (
                <span className="text-muted-foreground">Calculating…</span>
              ) : (
                <>
                  <span className="font-semibold">{count}</span> unreviewed image
                  {count !== 1 ? 's' : ''} will be approved.
                </>
              )}
            </div>

            {mutation.isError && (
              <Alert variant="destructive" className="text-sm">
                {mutation.error instanceof Error
                  ? mutation.error.message
                  : 'Auto-review failed. Please try again.'}
              </Alert>
            )}
          </div>
        ) : (
          <div className="py-4">
            <Alert className="text-sm">
              <p className="font-medium">
                Done — {result.reviewed} image{result.reviewed !== 1 ? 's' : ''} approved.
              </p>
            </Alert>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            {result ? 'Close' : 'Cancel'}
          </Button>
          {!result && (
            <Button
              onClick={() => mutation.mutate()}
              disabled={count === 0 || mutation.isPending}
            >
              {mutation.isPending
                ? 'Approving…'
                : `Approve ${count > 0 ? count : ''} image${count !== 1 ? 's' : ''}`}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
