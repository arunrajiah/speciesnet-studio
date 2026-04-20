import { useEffect, useRef } from 'react'

interface BBox {
  x1: number
  y1: number
  x2: number
  y2: number
}

interface BoundingBoxOverlayProps {
  bboxJson: string | null
  imageWidth: number | null
  imageHeight: number | null
  label: string | null
  confidence: number | null
  className?: string
}

function parseBbox(raw: string | null): BBox | null {
  if (!raw) return null
  try {
    const v = JSON.parse(raw) as unknown
    if (Array.isArray(v) && v.length === 4) {
      const [y1, x1, y2, x2] = v as number[]
      return { x1, y1, x2, y2 }
    }
    const obj = v as Record<string, number>
    if ('x1' in obj) return obj as unknown as BBox
  } catch {
    // ignore
  }
  return null
}

export function BoundingBoxOverlay({
  bboxJson,
  imageWidth,
  imageHeight,
  label,
  confidence,
  className = '',
}: BoundingBoxOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    const bbox = parseBbox(bboxJson)
    if (!bbox || !imageWidth || !imageHeight) return

    const scaleX = canvas.width / imageWidth
    const scaleY = canvas.height / imageHeight

    const x = bbox.x1 * scaleX
    const y = bbox.y1 * scaleY
    const w = (bbox.x2 - bbox.x1) * scaleX
    const h = (bbox.y2 - bbox.y1) * scaleY

    ctx.strokeStyle = 'rgba(34,197,94,0.9)'
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, w, h)

    if (label) {
      const confStr = confidence !== null ? ` ${Math.round(confidence * 100)}%` : ''
      const text = `${label}${confStr}`
      ctx.font = '13px sans-serif'
      const metrics = ctx.measureText(text)
      const tw = metrics.width + 8
      const th = 18
      ctx.fillStyle = 'rgba(34,197,94,0.85)'
      ctx.fillRect(x, y - th, tw, th)
      ctx.fillStyle = 'white'
      ctx.fillText(text, x + 4, y - 4)
    }
  }, [bboxJson, imageWidth, imageHeight, label, confidence])

  return (
    <canvas
      ref={canvasRef}
      className={`pointer-events-none absolute inset-0 h-full w-full ${className}`}
    />
  )
}
