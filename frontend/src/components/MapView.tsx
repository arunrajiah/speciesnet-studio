import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { MapPin } from 'lucide-react'
import { useMemo } from 'react'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import { Link } from 'react-router-dom'
import type { ItemRead, ReviewStatus } from '../types/item'

// Fix Leaflet's default icon paths broken by bundlers
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

// Status → marker colour matching the confidence badge palette
const STATUS_COLOUR: Record<ReviewStatus, string> = {
  confirmed: '#22c55e',   // green-500
  flagged: '#f59e0b',     // amber-500
  overridden: '#3b82f6',  // blue-500
  unreviewed: '#94a3b8',  // slate-400
}

function makeIcon(status: ReviewStatus) {
  const colour = STATUS_COLOUR[status]
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="36" viewBox="0 0 24 36">
      <path d="M12 0C5.4 0 0 5.4 0 12c0 9 12 24 12 24S24 21 24 12C24 5.4 18.6 0 12 0z"
            fill="${colour}" stroke="white" stroke-width="1.5"/>
      <circle cx="12" cy="12" r="5" fill="white" fill-opacity="0.85"/>
    </svg>`
  return L.divIcon({
    html: svg,
    className: '',
    iconSize: [24, 36],
    iconAnchor: [12, 36],
    popupAnchor: [0, -36],
  })
}

// Pre-build one icon per status to avoid re-creating on every render
const ICONS: Record<ReviewStatus, L.DivIcon> = {
  confirmed: makeIcon('confirmed'),
  flagged: makeIcon('flagged'),
  overridden: makeIcon('overridden'),
  unreviewed: makeIcon('unreviewed'),
}

interface FitBoundsProps {
  positions: [number, number][]
}

function FitBounds({ positions }: FitBoundsProps) {
  const map = useMap()
  useMemo(() => {
    if (positions.length === 0) return
    if (positions.length === 1) {
      map.setView(positions[0], 12)
      return
    }
    map.fitBounds(positions, { padding: [40, 40] })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [positions.length])
  return null
}

interface Props {
  collectionId: number
  items: ItemRead[]
}

export function MapView({ collectionId, items }: Props) {
  const gpsItems = useMemo(
    () => items.filter((it) => it.latitude != null && it.longitude != null),
    [items],
  )

  const positions = useMemo(
    () => gpsItems.map((it) => [it.latitude!, it.longitude!] as [number, number]),
    [gpsItems],
  )

  const noGpsCount = items.length - gpsItems.length

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 text-muted-foreground">
        <MapPin className="h-10 w-10" aria-hidden="true" />
        <p>No images match the current filters.</p>
      </div>
    )
  }

  if (gpsItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3 text-muted-foreground">
        <MapPin className="h-10 w-10" aria-hidden="true" />
        <p className="text-sm">None of the {items.length} matching images have GPS coordinates.</p>
        <p className="text-xs">GPS data is read from image EXIF at import time.</p>
      </div>
    )
  }

  return (
    <div className="relative flex flex-col h-full">
      {/* GPS coverage banner */}
      <div className="flex items-center justify-between px-4 py-1.5 text-xs text-muted-foreground border-b bg-muted/30 shrink-0">
        <span>
          Showing <strong className="text-foreground">{gpsItems.length}</strong> of{' '}
          <strong className="text-foreground">{items.length}</strong> images with GPS coordinates
          {noGpsCount > 0 && (
            <span className="ml-1">· {noGpsCount} without GPS hidden</span>
          )}
        </span>
        {/* Legend */}
        <div className="flex items-center gap-3">
          {(
            [
              ['confirmed', 'Confirmed'],
              ['overridden', 'Overridden'],
              ['flagged', 'Flagged'],
              ['unreviewed', 'Unreviewed'],
            ] as [ReviewStatus, string][]
          ).map(([status, label]) => (
            <span key={status} className="flex items-center gap-1">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full ring-1 ring-white/60"
                style={{ background: STATUS_COLOUR[status] }}
                aria-hidden="true"
              />
              {label}
            </span>
          ))}
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 min-h-0">
        <MapContainer
          center={[0, 0]}
          zoom={2}
          style={{ height: '100%', width: '100%' }}
          attributionControl
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <FitBounds positions={positions} />

          {gpsItems.map((item) => (
            <Marker
              key={item.id}
              position={[item.latitude!, item.longitude!]}
              icon={ICONS[item.review_status]}
            >
              <Popup maxWidth={220} className="leaflet-popup-studio">
                <div className="space-y-2 text-sm">
                  {item.thumbnail_url && (
                    <img
                      src={item.thumbnail_url}
                      alt={item.filename}
                      className="w-full rounded object-cover"
                      style={{ maxHeight: 120 }}
                    />
                  )}
                  <p className="font-medium truncate text-foreground">{item.filename}</p>
                  {item.top_label && (
                    <p className="text-muted-foreground">
                      {item.top_label}
                      {item.top_confidence != null && (
                        <span className="ml-1 font-semibold">
                          {Math.round(item.top_confidence * 100)}%
                        </span>
                      )}
                    </p>
                  )}
                  <p className="capitalize" style={{ color: STATUS_COLOUR[item.review_status] }}>
                    ● {item.review_status}
                  </p>
                  <Link
                    to={`/collections/${collectionId}/items/${item.id}`}
                    className="block text-center rounded bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:opacity-90"
                  >
                    View image →
                  </Link>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  )
}
