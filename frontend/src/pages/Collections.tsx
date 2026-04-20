import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FlaskConical, FolderOpen, Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { deleteCollection, listCollections } from '../api/collections'
import { loadSampleData } from '../api/sample'
import { CreateCollectionDialog } from '@/components/CreateCollectionDialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export default function Collections() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)

  const { data: collections = [], isLoading, isError } = useQuery({
    queryKey: ['collections'],
    queryFn: listCollections,
  })

  const deleteMutation = useMutation({
    mutationFn: deleteCollection,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['collections'] }),
  })

  const sampleMutation = useMutation({
    mutationFn: loadSampleData,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['collections'] })
      navigate(`/collections/${data.collection_id}`)
    },
  })

  if (isLoading) {
    return (
      <div className="container py-10 space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-9 w-48" />
          <Skeleton className="h-9 w-36" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-40 rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-destructive">Failed to load collections. Is the backend running?</p>
      </div>
    )
  }

  return (
    <div className="container py-10 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">SpeciesNet Studio</h1>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" aria-hidden="true" />
          Add collection
        </Button>
      </div>

      {collections.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 space-y-4 text-center">
          <FolderOpen className="h-12 w-12 text-muted-foreground" aria-hidden="true" />
          <p className="text-lg font-medium">No collections yet</p>
          <p className="text-sm text-muted-foreground max-w-sm">
            Point Studio at a folder of camera trap images, or try the sample data to explore the
            review workflow first.
          </p>
          <div className="flex gap-3 flex-wrap justify-center">
            <Button
              onClick={() => sampleMutation.mutate()}
              disabled={sampleMutation.isPending}
            >
              <FlaskConical className="mr-2 h-4 w-4" aria-hidden="true" />
              {sampleMutation.isPending ? 'Downloading…' : 'Try with sample data'}
            </Button>
            <Button variant="outline" onClick={() => setDialogOpen(true)}>
              Add your own collection
            </Button>
          </div>
          {sampleMutation.isError && (
            <p className="text-sm text-destructive">
              Could not download sample images. Check your internet connection and try again.
            </p>
          )}
          <p className="text-xs text-muted-foreground">
            Sample images are CC-licensed wildlife photos from Wikimedia Commons.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {collections.map((col) => (
            <Card
              key={col.id}
              className="cursor-pointer hover:border-primary transition-colors"
              onClick={() => navigate(`/collections/${col.id}`)}
            >
              <CardHeader>
                <CardTitle className="truncate">{col.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground truncate">{col.source_folder}</p>
              </CardContent>
              <CardFooter className="flex items-center justify-between">
                <Badge variant="secondary">{col.item_count} images</Badge>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Delete ${col.name}`}
                  onClick={(e: React.MouseEvent) => {
                    e.stopPropagation()
                    deleteMutation.mutate(col.id)
                  }}
                >
                  <Trash2 className="h-4 w-4 text-destructive" aria-hidden="true" />
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      <CreateCollectionDialog open={dialogOpen} onOpenChange={setDialogOpen} />
    </div>
  )
}
