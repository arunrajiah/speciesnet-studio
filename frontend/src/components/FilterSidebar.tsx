import { X } from 'lucide-react'
import type { ItemFilters, ReviewStatus } from '../types/item'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'

const ALL_STATUSES = '__all__'

const STATUSES: { value: string; label: string }[] = [
  { value: ALL_STATUSES, label: 'All statuses' },
  { value: 'unreviewed', label: 'Unreviewed' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'overridden', label: 'Overridden' },
  { value: 'flagged', label: 'Flagged' },
]

interface FilterSidebarProps {
  labels: string[]
  filters: ItemFilters
  onChange: (patch: Partial<ItemFilters>) => void
}

export function FilterSidebar({ labels, filters, onChange }: FilterSidebarProps) {
  const hasActive =
    filters.label || filters.status || filters.q || filters.min_conf !== undefined || filters.max_conf !== undefined

  const clearAll = () =>
    onChange({ label: undefined, status: undefined, q: undefined, min_conf: undefined, max_conf: undefined })

  const confRange: [number, number] = [
    filters.min_conf !== undefined ? Math.round(filters.min_conf * 100) : 0,
    filters.max_conf !== undefined ? Math.round(filters.max_conf * 100) : 100,
  ]

  return (
    <aside className="flex w-56 shrink-0 flex-col gap-4 border-r p-4 overflow-y-auto">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold">Filters</span>
        {hasActive && (
          <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={clearAll}>
            <X className="mr-1 h-3 w-3" />
            Clear
          </Button>
        )}
      </div>

      {/* filename search */}
      <div className="space-y-1">
        <Label className="text-xs">Filename</Label>
        <Input
          placeholder="Search…"
          value={filters.q ?? ''}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            onChange({ q: e.target.value || undefined })
          }
          className="h-8 text-sm"
        />
      </div>

      {/* label chips */}
      <div className="space-y-1">
        <Label className="text-xs">Label</Label>
        <div className="flex flex-wrap gap-1">
          {labels.map((l) => (
            <Badge
              key={l}
              variant={filters.label === l ? 'default' : 'outline'}
              className="cursor-pointer text-xs"
              onClick={() => onChange({ label: filters.label === l ? undefined : l })}
            >
              {l}
            </Badge>
          ))}
          {labels.length === 0 && (
            <span className="text-xs text-muted-foreground">No labels yet</span>
          )}
        </div>
      </div>

      {/* confidence range */}
      <div className="space-y-2">
        <Label className="text-xs">
          Confidence: {confRange[0]}%–{confRange[1]}%
        </Label>
        <Slider
          min={0}
          max={100}
          step={1}
          value={confRange}
          onValueChange={([lo, hi]) => {
            onChange({
              min_conf: lo > 0 ? lo / 100 : undefined,
              max_conf: hi < 100 ? hi / 100 : undefined,
            })
          }}
        />
      </div>

      {/* review status */}
      <div className="space-y-1">
        <Label className="text-xs">Review status</Label>
        <Select
          value={filters.status ?? ALL_STATUSES}
          onValueChange={(v) => onChange({ status: v === ALL_STATUSES ? undefined : (v as ReviewStatus) })}
        >
          <SelectTrigger className="h-8 text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STATUSES.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </aside>
  )
}
