import { Download } from 'lucide-react'
import { useState } from 'react'
import type { ExportFormat } from '../api/export'
import { triggerDownload } from '../api/export'
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

  const handleExport = async () => {
    setLoading(true)
    setError(null)
    try {
      await triggerDownload(collectionId, format)
      setOpen(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Export failed')
    } finally {
      setLoading(false)
    }
  }

  const ext = format === 'json' ? 'json' : 'csv'

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
        </Tabs>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <DialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={loading}>
            <Download className="mr-2 h-4 w-4" aria-hidden="true" />
            {loading ? 'Downloading…' : `Download .${ext}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
