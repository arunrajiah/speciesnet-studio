import { UserCircle } from 'lucide-react'
import { useState } from 'react'
import { useReviewerName } from '../hooks/useReviewerName'
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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

/**
 * Compact button + dialog for setting / changing the reviewer name.
 * Shows in the app header so it is always accessible.
 */
export function ReviewerNameDialog() {
  const [reviewerName, setReviewerName] = useReviewerName()
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState(reviewerName)

  const handleOpen = (next: boolean) => {
    if (next) setDraft(reviewerName)
    setOpen(next)
  }

  const handleSave = () => {
    setReviewerName(draft)
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpen}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="gap-1.5 text-muted-foreground hover:text-foreground"
          aria-label={reviewerName ? `Reviewer: ${reviewerName}` : 'Set your reviewer name'}
        >
          <UserCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span className="max-w-[120px] truncate text-xs">
            {reviewerName || 'Set name'}
          </span>
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Your reviewer name</DialogTitle>
          <DialogDescription>
            Your name will be recorded on every review action. Helps teams track who reviewed what.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-1.5 py-2">
          <Label htmlFor="reviewer-name-input">Name</Label>
          <Input
            id="reviewer-name-input"
            placeholder="e.g. Jane Smith"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSave()}
            autoFocus
          />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSave} disabled={!draft.trim()}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
