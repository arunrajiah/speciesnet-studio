import { useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { ItemFilters } from '../types/item'

export function useFilterParams(): [ItemFilters, (f: Partial<ItemFilters>) => void] {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters: ItemFilters = {
    label: searchParams.get('label') ?? undefined,
    min_conf: searchParams.has('min_conf') ? Number(searchParams.get('min_conf')) : undefined,
    max_conf: searchParams.has('max_conf') ? Number(searchParams.get('max_conf')) : undefined,
    status: (searchParams.get('status') as ItemFilters['status']) ?? undefined,
    q: searchParams.get('q') ?? undefined,
  }

  const setFilters = useCallback(
    (patch: Partial<ItemFilters>) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev)
          const merged: ItemFilters = { ...filters, ...patch }

          if (merged.label) next.set('label', merged.label)
          else next.delete('label')

          if (merged.min_conf !== undefined) next.set('min_conf', String(merged.min_conf))
          else next.delete('min_conf')

          if (merged.max_conf !== undefined) next.set('max_conf', String(merged.max_conf))
          else next.delete('max_conf')

          if (merged.status) next.set('status', merged.status)
          else next.delete('status')

          if (merged.q) next.set('q', merged.q)
          else next.delete('q')

          return next
        },
        { replace: true },
      )
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [searchParams, setSearchParams],
  )

  return [filters, setFilters]
}
