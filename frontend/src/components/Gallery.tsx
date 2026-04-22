import { useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import type { ItemRead } from '../types/item'
import { Checkbox } from '@/components/ui/checkbox'

interface GalleryProps {
  items: ItemRead[]
  onItemClick: (item: ItemRead) => void
  selectionMode: boolean
  selectedIds: Set<number>
  onToggleSelect: (id: number) => void
}

const CELL_SIZE = 220
const GAP = 8

function confidenceColor(label: string | null, conf: number | null): string {
  if (!label || label === 'blank' || label === 'human' || label === 'vehicle') return 'bg-gray-500'
  if (conf === null) return 'bg-gray-500'
  if (conf >= 0.8) return 'bg-green-600'
  if (conf >= 0.5) return 'bg-amber-500'
  return 'bg-red-500'
}

export function Gallery({ items, onItemClick, selectionMode, selectedIds, onToggleSelect }: GalleryProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  const columnCount = useColumnCount(containerRef)
  const rowCount = Math.ceil(items.length / columnCount)

  const rowVirtualizer = useVirtualizer({
    count: rowCount,
    getScrollElement: () => containerRef.current,
    estimateSize: () => CELL_SIZE + GAP,
    overscan: 3,
  })

  if (items.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-muted-foreground">
        No images match the current filters.
      </div>
    )
  }

  return (
    <div ref={containerRef} className="h-full overflow-auto">
      <div
        style={{
          height: rowVirtualizer.getTotalSize(),
          position: 'relative',
          width: '100%',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => {
          const startIdx = virtualRow.index * columnCount
          const rowItems = items.slice(startIdx, startIdx + columnCount)

          return (
            <div
              key={virtualRow.key}
              style={{
                position: 'absolute',
                top: virtualRow.start,
                left: 0,
                width: '100%',
                display: 'flex',
                gap: GAP,
                padding: `0 ${GAP}px`,
              }}
            >
              {rowItems.map((item) => (
                <GalleryCell
                  key={item.id}
                  item={item}
                  onClick={onItemClick}
                  selectionMode={selectionMode}
                  selected={selectedIds.has(item.id)}
                  onToggleSelect={onToggleSelect}
                />
              ))}
              {/* fill empty slots in last row */}
              {rowItems.length < columnCount &&
                Array.from({ length: columnCount - rowItems.length }).map((_, i) => (
                  <div key={`empty-${i}`} style={{ width: CELL_SIZE, flexShrink: 0 }} />
                ))}
            </div>
          )
        })}
      </div>
    </div>
  )
}

interface GalleryCellProps {
  item: ItemRead
  onClick: (item: ItemRead) => void
  selectionMode: boolean
  selected: boolean
  onToggleSelect: (id: number) => void
}

function GalleryCell({ item, onClick, selectionMode, selected, onToggleSelect }: GalleryCellProps) {
  const badgeColor = confidenceColor(item.top_label, item.top_confidence)
  const confText =
    item.top_confidence !== null ? `${Math.round(item.top_confidence * 100)}%` : '—'

  const handleClick = () => {
    if (selectionMode) {
      onToggleSelect(item.id)
    } else {
      onClick(item)
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`group relative overflow-hidden rounded-md bg-muted focus:outline-none focus:ring-2 focus:ring-ring ${
        selected ? 'ring-2 ring-primary' : ''
      }`}
      style={{ width: CELL_SIZE, height: CELL_SIZE, flexShrink: 0 }}
      aria-pressed={selectionMode ? selected : undefined}
    >
      {item.thumbnail_url ? (
        <img
          src={item.thumbnail_url}
          alt={item.filename}
          className="h-full w-full object-cover transition-transform group-hover:scale-105"
          loading="lazy"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-xs text-muted-foreground">
          No image
        </div>
      )}

      {/* selection checkbox */}
      {selectionMode && (
        <div className="absolute left-1.5 top-1.5 z-10">
          <Checkbox
            checked={selected}
            onCheckedChange={() => onToggleSelect(item.id)}
            onClick={(e) => e.stopPropagation()}
            aria-label={`Select ${item.filename}`}
            className="bg-white/90 shadow"
          />
        </div>
      )}

      {/* label / confidence badge */}
      <div
        className={`absolute bottom-1 left-1 right-1 flex items-center justify-between rounded px-1.5 py-0.5 text-xs font-medium text-white ${badgeColor} bg-opacity-90`}
      >
        <span className="truncate">{item.top_label ?? 'unknown'}</span>
        <span className="ml-1 shrink-0">{confText}</span>
      </div>

      {/* review status dot */}
      {item.review_status !== 'unreviewed' && (
        <div
          className={`absolute right-1 top-1 h-2.5 w-2.5 rounded-full border border-white ${
            item.review_status === 'confirmed'
              ? 'bg-green-500'
              : item.review_status === 'overridden'
                ? 'bg-blue-500'
                : 'bg-yellow-500'
          }`}
        />
      )}
    </button>
  )
}

function useColumnCount(ref: React.RefObject<HTMLDivElement | null>): number {
  // derive column count from container width; default 4 if not yet measured
  if (typeof window === 'undefined') return 4
  const width = ref.current?.clientWidth ?? 900
  return Math.max(1, Math.floor((width - GAP) / (CELL_SIZE + GAP)))
}
