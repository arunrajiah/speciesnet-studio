import { useCallback, useEffect, useState } from 'react'

const STORAGE_KEY = 'speciesnet-studio:reviewer-name'

/**
 * Persists the current reviewer's name in localStorage.
 * Returns [name, setName, isSet] where isSet is true once a non-empty name has been saved.
 */
export function useReviewerName(): [string, (name: string) => void, boolean] {
  const [name, setNameState] = useState<string>(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) ?? ''
    } catch {
      return ''
    }
  })

  useEffect(() => {
    try {
      if (name) {
        localStorage.setItem(STORAGE_KEY, name)
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
    } catch {
      // localStorage unavailable — silently continue
    }
  }, [name])

  const setName = useCallback((next: string) => {
    setNameState(next.trim())
  }, [])

  return [name, setName, name.length > 0]
}
