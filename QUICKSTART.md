# SpeciesNet Studio — Quick Start

Five minutes from zero to reviewing predictions in your browser.

---

## Prerequisites

- Docker (recommended) **or** Python 3.11+ and Node 20+
- Your images in a folder somewhere on disk
- SpeciesNet installed and able to produce a predictions JSON (optional for the review-only workflow)

---

## Option A — Docker (recommended)

### 1. Clone and configure inference

```bash
git clone https://github.com/arunrajiah/speciesnet-studio.git
cd speciesnet-studio
```

Edit `config/inference.yaml`. The default is a placeholder — pick one of the two options below and uncomment it:

**Option A1 — Native Python adapter (fastest)**
```yaml
adapter: speciesnet
speciesnet_model: null        # null = default model
speciesnet_country: KEN       # ISO-3166 code, or null to disable geofencing
speciesnet_geofence: true
```
Then install SpeciesNet into the backend image (add to `backend/pyproject.toml` optional deps or install separately).

**Option A2 — Subprocess adapter (works with any SpeciesNet installation)**
```yaml
adapter: subprocess
adapter_command:
  - python
  - -m
  - speciesnet.scripts.run_model
  - --folders
  - "{folder}"
  - --predictions_json
  - "{output_json}"
```

### 2. Start the production container

```bash
docker compose -f docker-compose.prod.yml up -d
```

Open **http://localhost:8000** in your browser.

---

## Option B — Local development (no Docker)

```bash
# 1. Backend
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload
# → http://localhost:8000

# 2. Frontend (separate terminal)
cd frontend
pnpm install
pnpm dev
# → http://localhost:5173
```

---

## First steps in the UI

### Load your images

1. Click **New collection** on the home screen.
2. Enter a name and paste the **absolute path** to your image folder.
3. Studio walks the folder, generates thumbnails, and shows the gallery. No images need to be copied — Studio reads them in place.

### Already ran SpeciesNet? Import predictions directly

If you have an existing `predictions.json` from SpeciesNet, you can skip the "Run inference" step.  
Paste your predictions file path into the collection form (feature roadmap — see issue tracker).  
For now: use **Run inference** with the subprocess adapter pointing at your existing JSON.

### Run inference

Click **Run inference** in the collection header. A progress dialog streams live updates. When complete, confidence badges and species labels appear on every thumbnail.

> **If inference fails immediately:** check `config/inference.yaml`. The error message in the dialog tells you exactly what's misconfigured.

### Review predictions

- Click any image to open the detail view — full image, predictions panel, bbox overlay.
- **Approve**: confirms the top prediction is correct.
- **Flag**: marks the image for follow-up (e.g. ambiguous ID, poor image quality).
- **Override**: lets you select a different species label and add a reviewer note.
- Keyboard shortcuts: `A` approve · `R` flag · `O` override · `B` clear · `←→` navigate.

### Batch review

Click **Select** in the gallery header to enter selection mode. Click thumbnails to select them (checkboxes appear), then **Approve all** or **Flag all** from the toolbar. Useful for bulk-confirming a high-confidence species sweep.

### Export results

Click **Export** → choose **CSV** (one row per image, spreadsheet-compatible) or **JSON** (full prediction + review detail). The downloaded file includes filename, top label, confidence, review status, override label, reviewer note, and reviewer name.

---

## Multi-user deployment with PostgreSQL

The default SQLite setup is ideal for a single reviewer on one machine. For team use — multiple reviewers on separate machines, or a shared server — switch to PostgreSQL.

### 1. Add a Postgres service to your compose file

```yaml
# docker-compose.prod.yml  (add alongside the existing services)
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: speciesnet
      POSTGRES_USER: speciesnet
      POSTGRES_PASSWORD: changeme          # ← change this
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U speciesnet"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

### 2. Point the backend at Postgres

Add `DATABASE_URL` to the `backend` service environment:

```yaml
  backend:
    environment:
      DATABASE_URL: postgresql+psycopg2://speciesnet:changeme@db:5432/speciesnet
    depends_on:
      db:
        condition: service_healthy
```

### 3. Install the Postgres driver

Add `psycopg2-binary` to `backend/pyproject.toml` under `[project] dependencies`:

```toml
dependencies = [
  ...
  "psycopg2-binary>=2.9",
]
```

Then rebuild: `docker compose -f docker-compose.prod.yml up -d --build`

Alembic runs `upgrade head` on startup — the schema is created automatically in Postgres exactly as it is in SQLite.

> **Migrating from SQLite:** there is no automated migration path from an existing SQLite database. Export your reviews to CSV/JSON first, stand up the Postgres instance, then re-import your images and predictions.

---

## Upgrading from a previous version

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

The database is migrated automatically on startup (alembic runs `upgrade head`). Your existing reviews and predictions are preserved.

If you were running Studio before v0.1 (before alembic was introduced), the first startup will detect the pre-alembic database and stamp it at the baseline revision automatically — no data is lost.

---

## Configuring inference for your setup

See `config/inference.yaml` for full documentation of all options, including:
- Country-based geofencing (`speciesnet_country`)
- Custom model paths (`speciesnet_model`)
- Subprocess adapter for any CLI tool that writes SpeciesNet-compatible JSON

---

## Getting help

- **Bug?** → [File an issue](https://github.com/arunrajiah/speciesnet-studio/issues/new?template=bug_report.md)
- **Feature request?** → [Open a discussion](https://github.com/arunrajiah/speciesnet-studio/issues/new?template=feature_request.md)
- **Contributing?** → See [CONTRIBUTING.md](CONTRIBUTING.md)
