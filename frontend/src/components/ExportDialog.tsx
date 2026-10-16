import { Download, Send } from 'lucide-react'
import { useState } from 'react'
import type { ExportFormat, SendResult } from '../api/export'
import { sendToWildNetwork, triggerDownload } from '../api/export'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface ExportDialogProps {
  collectionId: number
  collectionName: string
}

export function ExportDialog({ collectionId, collectionName }: ExportDialogProps) {
  const [open, setOpen] = useState(false)
  const [format, setFormat] = useState<ExportFormat>('csv')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // WildNetwork (WDX) options. The API key lives only in this dialog's state.
  const [lat, setLat] = useState('')
  const [lon, setLon] = useState('')
  const [utcOffset, setUtcOffset] = useState('')
  const [reviewedOnly, setReviewedOnly] = useState(true)
  const [apiKey, setApiKey] = useState('')
  const [sent, setSent] = useState<SendResult | null>(null)

  const wdxParams = () => ({
    latitude: lat.trim() ? Number(lat) : undefined,
    longitude: lon.trim() ? Number(lon) : undefined,
    utcOffset: utcOffset.trim() || undefined,
    reviewedOnly,
  })

  const handleSend = async () => {
    setLoading(true)
    setError(null)
    setSent(null)
    try {
      setSent(await sendToWildNetwork(collectionId, apiKey.trim(), wdxParams()))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Send failed')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setLoading(true)
    setError(null)
    try {
      await triggerDownload(collectionId, format, format === 'wdx' ? wdxParams() : undefined)
      setOpen(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Export failed')
    } finally {
      setLoading(false)
    }
  }

  const ext = format === 'json' ? 'json' : format === 'wdx' ? 'ndjson' : 'csv'

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Download className="mr-2 h-4 w-4" aria-hidden="true" />
          Export
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export "{collectionName}"</DialogTitle>
        </DialogHeader>

        <Tabs value={format} onValueChange={(v) => setFormat(v as ExportFormat)}>
          <TabsList className="w-full">
            <TabsTrigger value="csv" className="flex-1">CSV</TabsTrigger>
            <TabsTrigger value="json" className="flex-1">JSON</TabsTrigger>
            <TabsTrigger value="wi-csv" className="flex-1">Wildlife Insights</TabsTrigger>
            <TabsTrigger value="wdx" className="flex-1">WildNetwork</TabsTrigger>
          </TabsList>
          <TabsContent value="csv">
            <p className="text-sm text-muted-foreground mt-2">
              Spreadsheet-compatible. Includes one row per image with filename, top label,
              confidence, review status, override label, reviewer note, and reviewer name.
            </p>
          </TabsContent>
          <TabsContent value="json">
            <p className="text-sm text-muted-foreground mt-2">
              Machine-readable JSON array. Same fields as CSV, suitable for downstream
              pipelines and further analysis.
            </p>
          </TabsContent>
          <TabsContent value="wi-csv">
            <p className="text-sm text-muted-foreground mt-2">
              CSV formatted for{' '}
              <a
                href="https://www.wildlifeinsights.org"
                target="_blank"
                rel="noopener noreferrer"
                className="underline underline-offset-2"
              >
                Wildlife Insights
              </a>{' '}
              data submission. Includes deployment ID, timestamp, blank/human/vehicle flags,
              species label, GPS coordinates, and reviewer attribution. Optional annotation
              columns (age, sex, individual ID) are left blank for manual completion.
            </p>
          </TabsContent>
          <TabsContent value="wdx">
            <p className="text-sm text-muted-foreground mt-2">
              Shares your reviewed results with the open{' '}
              <a href="https://wildnetwork.arunrajiah.com" target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">
                WildNetwork
              </a>{' '}
              map in the{' '}
              <a href="https://github.com/arunrajiah/wildlife-detection-exchange" target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">
                WDX
              </a>{' '}
              format: species, time, location rounded to about 1 km, confidence, the box, and your review decision. Blank,
              human and vehicle images are never included.
            </p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
              <label className="flex flex-col gap-1">
                Latitude (images without GPS)
                <input value={lat} onChange={(e) => setLat(e.target.value)} inputMode="decimal" placeholder="11.58" className="rounded-md border px-2 py-1" />
              </label>
              <label className="flex flex-col gap-1">
                Longitude
                <input value={lon} onChange={(e) => setLon(e.target.value)} inputMode="decimal" placeholder="76.54" className="rounded-md border px-2 py-1" />
              </label>
              <label className="flex flex-col gap-1">
                Camera clock offset from UTC
                <input value={utcOffset} onChange={(e) => setUtcOffset(e.target.value)} placeholder="+05:30" className="rounded-md border px-2 py-1" />
              </label>
              <label className="flex items-center gap-2 self-end pb-1">
                <input type="checkbox" checked={reviewedOnly} onChange={(e) => setReviewedOnly(e.target.checked)} />
                Reviewed images only
              </label>
              <label className="col-span-2 flex flex-col gap-1">
                WildNetwork API key (to send directly; not stored)
                <input value={apiKey} onChange={(e) => setApiKey(e.target.value)} type="password" autoComplete="off" placeholder="wn_..." className="rounded-md border px-2 py-1" />
              </label>
              <p className="col-span-2 text-xs text-muted-foreground">
                Get a key by registering this camera at wildnetwork.arunrajiah.com/contribute (source: speciesnet-studio). Sending
                again updates the same records, so later review decisions replace earlier ones.
              </p>
            </div>
            {sent && (
              <p className="mt-2 text-sm">
                Sent {sent.sent} records{sent.result ? `: ${sent.result.inserted} new, ${sent.result.updated} updated, ${sent.result.rejected} rejected` : ''}.
                {Object.entries(sent.skipped).filter(([, n]) => n > 0).length > 0 &&
                  ` Skipped: ${Object.entries(sent.skipped).filter(([, n]) => n > 0).map(([k, n]) => `${n} ${k.replaceAll('_', ' ')}`).join(', ')}.`}
              </p>
            )}
          </TabsContent>
        </Tabs>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <DialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          {format === 'wdx' && (
            <Button variant="secondary" onClick={handleSend} disabled={loading || !apiKey.trim()}>
              <Send className="mr-2 h-4 w-4" aria-hidden="true" />
              {loading ? 'Sending…' : 'Send to WildNetwork'}
            </Button>
          )}
          <Button onClick={handleExport} disabled={loading}>
            <Download className="mr-2 h-4 w-4" aria-hidden="true" />
            {loading ? 'Downloading…' : `Download .${ext}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
