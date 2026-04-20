# Media assets — capture checklist

All assets here use Creative Commons–licensed sample images from LILA BC. Do not include images from your own camera deployments in anything published publicly.

---

## Required before launch

### hero.png
- **What:** Gallery view showing a mix of confidence badge colours (green, amber, red), a few flagged items, dark theme
- **Dimensions:** ~1600 × 1000 px
- **Where used:** README.md hero image

### screenshot-gallery.png
- **What:** Full gallery view with filter sidebar open, label chips selected
- **Dimensions:** ~1400 × 900 px
- **Where used:** README.md screenshots table

### screenshot-review.png
- **What:** Item detail view — full-res image with bounding box overlay, top-5 predictions sidebar, Review controls panel showing override label combobox
- **Dimensions:** ~1400 × 900 px
- **Where used:** README.md screenshots table

### screenshot-export.png
- **What:** Export dialog open, CSV tab selected, collection name visible
- **Dimensions:** ~800 × 600 px (dialog-focused)
- **Where used:** README.md screenshots table

---

## Nice-to-have before launch

### demo.mp4
- **Length:** ~90 seconds
- **Script:**
  1. App loads at `/collections` — empty state
  2. Click "Try with sample data" → ingestion progress visible
  3. Collection opens → gallery populates
  4. Run inference → WebSocket progress bar counts up
  5. Gallery refreshes with confidence badges
  6. Click an image → detail view, bounding box visible
  7. Press **A** to approve, **→** to next, **O** to override with label combobox
  8. Open filter sidebar → filter by "confirmed"
  9. Click Export → download CSV
- **Recommended tool:** QuickTime Screen Recording → Handbrake (H.264, ~5 MB)

### keyboard-review.gif
- **Length:** ~15 seconds, looped
- **What:** Close-up of the review controls area while pressing A / O / R / ← → in sequence — shows badge colour update and auto-advance
- **Why this matters:** Camera trap researchers value review speed above almost everything else. This GIF is the single asset most likely to convert a viewer into a user.
- **Recommended tools:** LICEcap (Windows/Mac) or Gifski (Mac, higher quality)
- **Target size:** < 3 MB for fast README load

---

## Notes

- Use LILA BC Creative Commons sample images for all public assets. Verify the license of the specific dataset before publishing.
- Dark theme is preferred for screenshots — it photographs better and matches many researchers' setups.
- Capture at 2× resolution if on a Retina display; scale down to the listed dimensions in export.
