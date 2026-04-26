import { useQuery } from '@tanstack/react-query'
import { getCollectionStats } from '../api/items'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'

interface StatsBarProps {
  collectionId: number
}

export function StatsBar({ collectionId }: StatsBarProps) {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats', collectionId],
    queryFn: () => getCollectionStats(collectionId),
  })

  if (isLoading) {
    return <Skeleton className="h-10 w-full rounded-none border-b" />
  }

  if (!stats || stats.total === 0) {
    return null
  }

  const reviewedPct = stats.total > 0 ? (stats.reviewed / stats.total) * 100 : 0

  return (
    <div className="flex items-center gap-4 border-b bg-muted/30 px-6 py-2">
      <div className="flex items-center gap-2 min-w-[140px]">
        <Progress value={reviewedPct} className="h-2 w-28" aria-label="Review progress" />
        <span className="text-xs text-muted-foreground whitespace-nowrap">
          {stats.reviewed}/{stats.total}
        </span>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <Pill className="bg-green-100 text-green-800">
          ✓ {stats.confirmed} confirmed
        </Pill>
        <Pill className="bg-blue-100 text-blue-800">
          ↩ {stats.overridden} overridden
        </Pill>
        <Pill className="bg-yellow-100 text-yellow-800">
          ⚑ {stats.flagged} flagged
        </Pill>
        <Pill className="bg-secondary text-secondary-foreground">
          · {stats.unreviewed} unreviewed
        </Pill>
      </div>

      {stats.reviewers && stats.reviewers.length > 0 && (
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-muted-foreground">Reviewed by:</span>
          {stats.reviewers.map(({ name, count }) => (
            <Pill key={name} className="bg-muted text-muted-foreground">
              {name} · {count}
            </Pill>
          ))}
        </div>
      )}

      {stats.avg_confidence !== null && (
        <span className="ml-auto text-xs text-muted-foreground whitespace-nowrap shrink-0">
          avg {Math.round(stats.avg_confidence * 100)}%
        </span>
      )}
    </div>
  )
}

interface PillProps {
  children: React.ReactNode
  className?: string
}

function Pill({ children, className = '' }: PillProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${className}`}
    >
      {children}
    </span>
  )
}
