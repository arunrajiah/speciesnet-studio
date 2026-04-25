import { useMutation, useQueryClient } from '@tanstack/react-query'
import { FolderOpen } from 'lucide-react'
import { useState } from 'react'
import { importPredictions } from '../api/items'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface Props {
  collectionId: number
}

export function ImportPredictionsDialog({ collectionId }: Props) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [path, setPath] = useState('')
  const [result, setResult] = useState<{ imported: number; warnings: string[] } | null>(null)

  const mutation = useMutation({
    mutationFn: () => importPredictions(collectionId, path.trim()),
    onSuccess: (data) => {
      setResult(data)
      queryClient.invalidateQueries({ queryKey: ['items', collectionId] })
      queryClient.invalidateQueries({ queryKey: ['stats', collectionId] })
      queryClient.invalidateQueries({ queryKey: ['labels', collectionId] })
    },
  })

  const handleOpenChange = (next: boolean) => {
    setOpen(next)
    if (!next) {
      setPath('')
      setResult(null)
      mutation.reset()
    }
  }

  const handleImport = () => {
    setResult(null)
    mutation.mutate()
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" aria-label="Import existing predictions JSON">
          <FolderOpen className="mr-2 h-4 w-4" aria-hidden="true" />
          Import predictions
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Import predictions</DialogTitle>
          <DialogDescription>
            Load an existing SpeciesNet <code>predictions.json</code> file. Predictions will be
            matched to images by filename — no re-running the model required.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="predictions-path">Absolute path to predictions JSON</Label>
            <Input
              id="predictions-path"
              placeholder="/home/user/data/predictions.json"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              disabled={mutation.isPending}
              aria-describedby={mutation.isError ? 'import-error' : undefined}
            />
          </div>

          {mutation.isError && (
            <Alert id="import-error" variant="destructive" className="text-sm">
              {mutation.error instanceof Error
                ? mutation.error.message
                : 'Import failed — check the file path and format.'}
            </Alert>
          )}

          {result && (
            <Alert className="text-sm space-y-1">
              <p className="font-medium">
                Imported {result.imported} prediction{result.imported !== 1 ? 's' : ''}.
              </p>
              {result.warnings.map((w, i) => (
                <p key={i} className="text-muted-foreground">
                  ⚠ {w}
                </p>
              ))}
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            {result ? 'Close' : 'Cancel'}
          </Button>
          {!result && (
            <Button
              onClick={handleImport}
              disabled={!path.trim() || mutation.isPending}
            >
              {mutation.isPending ? 'Importing…' : 'Import'}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
