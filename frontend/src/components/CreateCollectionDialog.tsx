import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { createCollection } from '../api/collections'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CreateCollectionDialog({ open, onOpenChange }: Props) {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [folder, setFolder] = useState('')

  const mutation = useMutation({
    mutationFn: createCollection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      setName('')
      setFolder('')
      onOpenChange(false)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !folder.trim()) return
    mutation.mutate({ name: name.trim(), source_folder: folder.trim() })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New collection</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <Label htmlFor="col-name">Name</Label>
            <Input
              id="col-name"
              placeholder="August fieldwork"
              value={name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="col-folder">Folder path</Label>
            <Input
              id="col-folder"
              placeholder="/data/images/august"
              value={folder}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFolder(e.target.value)}
              required
            />
          </div>
          {mutation.isError && (
            <p className="text-sm text-destructive">
              {mutation.error instanceof Error ? mutation.error.message : 'Something went wrong'}
            </p>
          )}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Creating…' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
