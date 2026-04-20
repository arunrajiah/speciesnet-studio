import { useEffect, useState } from 'react'
import { openJobSocket } from '../api/inference'
import type { JobState } from '../types/job'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Progress } from '@/components/ui/progress'

interface Props {
  jobId: string
  open: boolean
  onClose: () => void
}

export function InferenceProgressDialog({ jobId, open, onClose }: Props) {
  const [job, setJob] = useState<JobState | null>(null)

  useEffect(() => {
    if (!open || !jobId) return
    const ws = openJobSocket(jobId)

    ws.onmessage = (evt: MessageEvent) => {
      const data = JSON.parse(evt.data as string) as JobState
      setJob(data)
    }

    ws.onerror = () => {
      setJob((prev) => prev ? { ...prev, status: 'failed', error: 'WebSocket error' } : null)
    }

    return () => ws.close()
  }, [jobId, open])

  const pct =
    job && job.total > 0 ? Math.round((job.current / job.total) * 100) : undefined

  const isDone = job?.status === 'completed' || job?.status === 'failed'

  return (
    <Dialog open={open} onOpenChange={(v) => !v && isDone && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Running inference…</DialogTitle>
        </DialogHeader>

        <div className="space-y-3 py-2">
          <p className="text-sm text-muted-foreground capitalize">
            {job?.stage ?? 'starting'}
            {job && job.total > 0 ? ` — ${job.current} / ${job.total}` : ''}
          </p>

          {pct !== undefined ? (
            <Progress value={pct} aria-label={`Inference progress ${pct}%`} />
          ) : (
            <Progress aria-label="Inference running" className="animate-pulse" />
          )}

          {job?.status === 'failed' && (
            <p className="text-sm text-destructive">{job.error ?? 'Unknown error'}</p>
          )}

          {job?.status === 'completed' && (
            <p className="text-sm text-green-600">Inference complete.</p>
          )}
        </div>

        <DialogFooter>
          <Button
            variant={isDone ? 'default' : 'outline'}
            disabled={!isDone}
            onClick={onClose}
          >
            {isDone ? 'Close' : 'Running…'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
