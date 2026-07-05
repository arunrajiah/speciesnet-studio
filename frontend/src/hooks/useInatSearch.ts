import { useEffect, useState } from 'react'

export interface InatTaxon {
  id: number
  scientificName: string
  commonName: string | null
  rank: string
}

const INAT_API = 'https://api.inaturalist.org/v1/taxa/autocomplete'
const MIN_CHARS = 2
const DEBOUNCE_MS = 350

export function useInatSearch(query: string): { taxa: InatTaxon[]; isLoading: boolean } {
  const [taxa, setTaxa] = useState<InatTaxon[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const trimmed = query.trim()
  const canSearch = trimmed.length >= MIN_CHARS

  useEffect(() => {
    if (!canSearch) {
      return
    }

    const controller = new AbortController()
    const timer = setTimeout(async () => {
      setIsLoading(true)
      try {
        const url = `${INAT_API}?q=${encodeURIComponent(trimmed)}&per_page=6&rank=species,genus,family`
        const res = await fetch(url, { signal: controller.signal })
        if (!res.ok) return
        const data = (await res.json()) as {
          results: {
            id: number
            name: string
            preferred_common_name?: string
            rank: string
          }[]
        }
        setTaxa(
          data.results.map((t) => ({
            id: t.id,
            scientificName: t.name,
            commonName: t.preferred_common_name ?? null,
            rank: t.rank,
          })),
        )
      } catch {
        // AbortError or network error — silently swallow
      } finally {
        setIsLoading(false)
      }
    }, DEBOUNCE_MS)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [canSearch, trimmed])

  return { taxa: canSearch ? taxa : [], isLoading: canSearch ? isLoading : false }
}
