import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ThemeProvider } from 'next-themes'
import { fetchHealth } from './api/health'
import { ThemeToggle } from './components/ThemeToggle'
import CollectionDetail from './pages/CollectionDetail'
import Collections from './pages/Collections'
import ItemDetail from './pages/ItemDetail'

type ApiStatus = 'loading' | 'ok' | 'unreachable'

function HealthBanner() {
  const [status, setStatus] = useState<ApiStatus>('loading')

  useEffect(() => {
    fetchHealth()
      .then((d) => setStatus(d.status === 'ok' ? 'ok' : 'unreachable'))
      .catch(() => setStatus('unreachable'))
  }, [])

  if (status === 'ok') return null

  const msg =
    status === 'loading' ? 'Connecting to backend…' : 'Backend unreachable — is it running?'
  const colour =
    status === 'loading' ? 'bg-yellow-500/10 text-yellow-600' : 'bg-destructive/10 text-destructive'

  return (
    <div className={`w-full px-4 py-2 text-center text-sm font-medium ${colour}`} role="alert">
      {msg}
    </div>
  )
}

function TopBar() {
  return (
    <div className="flex items-center justify-end border-b px-4 py-1">
      <ThemeToggle />
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <BrowserRouter>
        <HealthBanner />
        <TopBar />
        <Routes>
          <Route path="/" element={<Navigate to="/collections" replace />} />
          <Route path="/collections" element={<Collections />} />
          <Route path="/collections/:id" element={<CollectionDetail />} />
          <Route path="/collections/:collectionId/items/:itemId" element={<ItemDetail />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}
