# Changelog

All notable changes to SpeciesNet Studio are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-04-20

### Added

**Ingest**
- Collections — create named collections pointing at local image folders; delete cascades items and predictions
- Recursive folder walk for JPG, JPEG, PNG, TIF/TIFF
- EXIF extraction: capture datetime and GPS latitude/longitude via Pillow
- 300 px thumbnail generation at import time
- Background ingestion with in-memory progress tracking

**Infer**
- Pluggable `InferenceAdapter` protocol — any callable that accepts `(folder, output_json, on_progress)` can be wired in
- `SubprocessAdapter` — runs any CLI tool, parses `X/Y` and JSON progress lines from stdout
- `SpeciesNetAdapter` — calls the SpeciesNet Python API directly; activate with `adapter: speciesnet` in `config/inference.yaml`
- In-memory job registry with `pending → running → completed/failed` state machine
- WebSocket endpoint (`/ws/jobs/{id}`) streaming job state every second until terminal
- Predictions parser for SpeciesNet JSON output schema; persists label, confidence, bbox, model version per detection

**Review**
- Items API: list with filters (species label, confidence range, review status, filename search), single-item detail, distinct labels
- Virtualized thumbnail gallery via `@tanstack/react-virtual` — smooth rendering at 10 000+ images
- Confidence badge overlay: green ≥ 80 %, amber 50–79 %, red < 50 %, grey for blank/human/vehicle
- Review status dot overlay per thumbnail (confirmed, overridden, flagged)
- Full-res detail view with bounding box canvas overlay (`<canvas>` over `<img>`)
- Predictions sidebar ranked by confidence with model version
- Review controls: Approve / Override / Flag / Clear with label combobox and reviewer note textarea
- Keyboard shortcuts: **A** approve · **O** override · **R** flag · **B** clear · **← →** navigate
- Review status upserted per image (one record per item, update-in-place)
- Filter sidebar: species chips, confidence range slider, review status select, filename search
- Filter state synced to URL query params (bookmarkable, shareable)
- Dark mode with system default, toggleable; powered by `next-themes`

**Export**
- `GET /api/collections/{id}/export?format=csv` — CSV with filename, top label, confidence, review status, override label, reviewer note
- `GET /api/collections/{id}/export?format=json` — same fields as JSON array
- Frontend Export dialog with format tabs and one-click download

**Platform**
- FastAPI backend with SQLite persistence via SQLModel; SQLite file at `./data/app.db`
- Static file serving for thumbnails (`/thumbs`) and full-res images (`/images`)
- React 18 + TypeScript + Vite + Tailwind CSS v3 + shadcn/ui (slate base)
- Docker Compose: one-command startup; Vite dev server proxies `/api` to FastAPI
- `ghcr.io/arunrajiah/speciesnet-studio-{backend,frontend}` images published on each tag push
- GitHub Actions CI: backend (ruff, mypy, pytest) + frontend (eslint, tsc, vite build)
- GitHub Actions release: tag-triggered GitHub Release + multi-arch Docker image build
- `justfile` with `dev`, `build`, `test`, `lint`, `format` targets
- Apache 2.0 license; third-party attributions in NOTICE

### Changed

- Project name updated throughout from `studio-backend` → `speciesnet-studio-backend`

### Fixed

- `StaticFiles` mount uses `check_dir=False` so tests pass before data directories are created

[Unreleased]: https://github.com/arunrajiah/speciesnet-studio/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/arunrajiah/speciesnet-studio/releases/tag/v0.1.0
