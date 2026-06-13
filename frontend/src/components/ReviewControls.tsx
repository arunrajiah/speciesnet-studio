import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, ChevronDown, Flag, Loader2, Pencil, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { listLabels, submitReview } from '../api/items'
import { useInatSearch } from '../hooks/useInatSearch'
import { useReviewerName } from '../hooks/useReviewerName'
import type { ReviewDetail } from '../types/item'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Textarea } from '@/components/ui/textarea'

interface ReviewControlsProps {
  itemId: number
  collectionId: number
  currentReview: ReviewDetail | null
  topLabel: string | null
  onReviewed: () => void
  onNext: () => void
  onPrev: () => void
}

type Action = 'confirmed' | 'overridden' | 'flagged' | 'unreviewed'

export function ReviewControls({
  itemId,
  collectionId,
  currentReview,
  topLabel,
  onReviewed,
  onNext,
  onPrev,
}: ReviewControlsProps) {
  const queryClient = useQueryClient()
  const [reviewerName] = useReviewerName()
  const [overrideLabel, setOverrideLabel] = useState(currentReview?.override_label ?? '')
  const [note, setNote] = useState(currentReview?.reviewer_note ?? '')
  const [comboOpen, setComboOpen] = useState(false)
  const [search, setSearch] = useState('')

  const { data: labels = [] } = useQuery({
    queryKey: ['labels', collectionId],
    queryFn: () => listLabels(collectionId),
  })

  const { taxa, isLoading: inatLoading } = useInatSearch(search)

  const reviewMutation = useMutation({
    mutationFn: (action: Action) =>
      submitReview(itemId, {
        status: action,
        override_label: action === 'overridden' ? overrideLabel || undefined : undefined,
        reviewer_note: note || undefined,
        reviewer_name: reviewerName || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items', collectionId] })
      queryClient.invalidateQueries({ queryKey: ['item', itemId] })
      onReviewed()
    },
  })

  // keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
      switch (e.key) {
        case 'a':
        case 'A':
          reviewMutation.mutate('confirmed')
          break
        case 'r':
        case 'R':
          reviewMutation.mutate('flagged')
          break
        case 'o':
        case 'O':
          reviewMutation.mutate('overridden')
          break
        case 'b':
        case 'B':
          reviewMutation.mutate('unreviewed')
          break
        case 'ArrowRight':
          onNext()
          break
        case 'ArrowLeft':
          onPrev()
          break
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [reviewMutation, onNext, onPrev])

  const status = currentReview?.status ?? 'unreviewed'

  const selectLabel = (value: string) => {
    setOverrideLabel(value)
    setSearch('')
    setComboOpen(false)
  }

  // Existing collection labels filtered by search term
  const filteredLabels = search
    ? labels.filter((l) => l.toLowerCase().includes(search.toLowerCase()))
    : labels

  return (
    <div className="space-y-3">
      {/* status indicator */}
      <p className="text-xs text-muted-foreground">
        Current:{' '}
        <span className="font-medium capitalize text-foreground">{status}</span>
        {currentReview?.reviewer_name && (
          <span className="ml-1 text-muted-foreground">· by {currentReview.reviewer_name}</span>
        )}
      </p>

      {/* action buttons */}
      <div className="grid grid-cols-2 gap-2">
        <Button
          size="sm"
          variant={status === 'confirmed' ? 'default' : 'outline'}
          onClick={() => reviewMutation.mutate('confirmed')}
          title="Approve (A)"
        >
          <Check className="mr-1 h-3 w-3" />
          Approve
        </Button>
        <Button
          size="sm"
          variant={status === 'flagged' ? 'destructive' : 'outline'}
          onClick={() => reviewMutation.mutate('flagged')}
          title="Flag (R)"
        >
          <Flag className="mr-1 h-3 w-3" />
          Flag
        </Button>
        <Button
          size="sm"
          variant={status === 'overridden' ? 'secondary' : 'outline'}
          onClick={() => reviewMutation.mutate('overridden')}
          title="Override (O)"
        >
          <Pencil className="mr-1 h-3 w-3" />
          Override
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => reviewMutation.mutate('unreviewed')}
          title="Clear (B)"
        >
          <X className="mr-1 h-3 w-3" />
          Clear
        </Button>
      </div>

      {/* override label picker — collection labels + live iNaturalist suggestions */}
      <Popover open={comboOpen} onOpenChange={(o) => { setComboOpen(o); if (!o) setSearch('') }}>
        <PopoverTrigger asChild>
          <Button variant="outline" size="sm" className="w-full justify-between text-sm">
            {overrideLabel || topLabel || 'Select override label…'}
            <ChevronDown className="ml-1 h-3 w-3 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-72 p-0">
          <Command shouldFilter={false}>
            <CommandInput
              placeholder="Search labels or species…"
              value={search}
              onValueChange={setSearch}
            />
            <CommandList>
              {filteredLabels.length === 0 && taxa.length === 0 && !inatLoading && (
                <CommandEmpty>No results.</CommandEmpty>
              )}

              {filteredLabels.length > 0 && (
                <CommandGroup heading="Collection labels">
                  {filteredLabels.map((l) => (
                    <CommandItem key={l} value={l} onSelect={selectLabel}>
                      {l}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}

              {(taxa.length > 0 || inatLoading) && (
                <>
                  {filteredLabels.length > 0 && <CommandSeparator />}
                  <CommandGroup
                    heading={
                      inatLoading ? (
                        <span className="flex items-center gap-1">
                          <Loader2 className="h-3 w-3 animate-spin" />
                          iNaturalist…
                        </span>
                      ) : (
                        'iNaturalist species'
                      )
                    }
                  >
                    {taxa.map((t) => {
                      const display = t.commonName
                        ? `${t.commonName} (${t.scientificName})`
                        : t.scientificName
                      return (
                        <CommandItem
                          key={t.id}
                          value={display}
                          onSelect={() => selectLabel(t.commonName ?? t.scientificName)}
                        >
                          <span className="font-medium">{t.commonName ?? t.scientificName}</span>
                          {t.commonName && (
                            <span className="ml-1.5 text-xs italic text-muted-foreground">
                              {t.scientificName}
                            </span>
                          )}
                        </CommandItem>
                      )
                    })}
                  </CommandGroup>
                </>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {/* note */}
      <Textarea
        placeholder="Reviewer note…"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        rows={2}
        className="text-sm"
      />

      {/* keyboard hint */}
      <p className="text-[10px] text-muted-foreground">
        A approve · R flag · O override · B clear · ←→ navigate
      </p>
    </div>
  )
}
