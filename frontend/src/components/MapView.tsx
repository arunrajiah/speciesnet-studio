import { useQuery } from '@tanstack/react-query'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MapPin } from 'lucide-react'
import { useEffect, useMemo, useRef } from 'react'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import { useNavigate } from 'react-router-dom'
import { listGeoItems } from '../api/items'
import type { GeoItem, ReviewStatus } from '../types/item'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

// Fix Leaflet default icon paths broken by Vite bundler
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const STATUS_COLOR: Record<ReviewStatus, string> = {
  confirmed: '#22c55e',
  overridden: '#3b82f6',
  flagged: '#f59e0b',
  unreviewed: '#94a3b8',
}

function makeIcon(status: ReviewStatus): L.DivIcon {
  const color = STATUS_COLOR[status]
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="24" height="36">
    <path d="M12 0C5.373 0 0 5.373 0 12c0 9 12 24 12 24s12-15 12-24C24 5.373 18.627 0 12 0z"
      fill="${color}" stroke="white" stroke-width="1.5"/>
    <circle cx="12" cy="12" r="5" fill="white"/>
  </svg>`
  return L.divIcon({
    className: '',
    html: svg,
    iconSize: [24, 36],
    iconAnchor: [12, 36],
    popupAnchor: [0, -36],
  })
}

function BoundsController({ items }: { items: GeoItem[] }) {
  const map = useMap()
  const fitted = useRef(false)

  useEffect(() => {
    if (fitted.current || items.length === 0) return
    const bounds = L.latLngBounds(items.map((i) => [i.latitude, i.longitude]))
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 })
    fitted.current = true
  }, [map, items])

  return null
}

interface MapViewProps {
  collectionId: number
}

export function MapView({ collectionId }: MapViewProps) {
  const navigate = useNavigate()

  const { data: items = [], isLoading } = useQuery({
    queryKey: ['geo-items', collectionId],
    queryFn: () => listGeoItems(collectionId),
  })

  const icons = useMemo(
    () => ({
      confirmed: makeIcon('confirmed'),
      overridden: makeIcon('overridden'),
      flagged: makeIcon('flagged'),
      unreviewed: makeIcon('unreviewed'),
    }),
    [],
  )

  if (isLoading) {
    return <Skeleton className="h-full w-full rounded-none" />
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 text-center px-4">
        <MapPin className="h-10 w-10 text-muted-foreground" aria-hidden="true" />
        <p className="text-muted-foreground text-sm max-w-xs">
          No GPS data found. Images with EXIF geotags will appear here as map markers.
        </p>
      </div>
    )
  }

  const center: [number, number] = [items[0].latitude, items[0].longitude]

  return (
    <div className="relative h-full w-full">
      {/* Legend */}
      <div className="absolute bottom-6 right-3 z-[1000] flex flex-col gap-1.5 rounded-lg border bg-background/95 px-3 py-2.5 text-xs shadow-md backdrop-blur">
        {(Object.entries(STATUS_COLOR) as [ReviewStatus, string][]).map(([status, color]) => (
          <div key={status} className="flex items-center gap-2">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ background: color }}
            />
            <span className="capitalize">{status}</span>
          </div>
        ))}
      </div>

      {/* Count badge */}
      <div className="absolute top-3 right-3 z-[1000]">
        <Badge variant="secondary" className="shadow-sm">
          {items.length} geotagged image{items.length !== 1 ? 's' : ''}
        </Badge>
      </div>

      <MapContainer center={center} zoom={10} className="h-full w-full" zoomControl>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <BoundsController items={items} />
        {items.map((item) => (
          <Marker
            key={item.id}
            position={[item.latitude, item.longitude]}
            icon={icons[item.review_status]}
          >
            <Popup minWidth={200} maxWidth={260}>
              <div className="space-y-2 py-1 text-sm">
                {item.thumbnail_url && (
                  <img
                    src={item.thumbnail_url}
                    alt={item.filename}
                    className="w-full rounded object-cover"
                    style={{ maxHeight: 120 }}
                  />
                )}
                <p className="font-medium truncate leading-snug" title={item.filename}>
                  {item.filename}
                </p>
                {item.top_label && (
                  <p className="text-muted-foreground">
                    {item.top_label}
                    {item.top_confidence !== null && (
                      <span className="ml-1 text-xs opacity-70">
                        {Math.round(item.top_confidence * 100)}%
                      </span>
                    )}
                  </p>
                )}
                <p
                  className="text-xs capitalize font-medium"
                  style={{ color: STATUS_COLOR[item.review_status] }}
                >
                  {item.review_status}
                </p>
                <Button
                  size="sm"
                  className="w-full"
                  onClick={() => navigate(`/collections/${collectionId}/items/${item.id}`)}
                >
                  Review image
                </Button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}
