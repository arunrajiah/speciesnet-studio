# Contributing to SpeciesNet Studio

Thank you for your interest in contributing. SpeciesNet Studio is maintained by [Arun Rajiah](https://github.com/arunrajiah) and the community. All contributions — bug reports, feature requests, code, documentation, and adapter integrations — are welcome.

---

## For users: reporting bugs and requesting features

### Filing a bug

Please include the following in your issue:

- **OS and version** (e.g. macOS 14, Ubuntu 22.04, Windows 11)
- **Docker version** (`docker --version`) or Python version if running without Docker
- **SpeciesNet version** (`python -c "import speciesnet; print(speciesnet.__version__)"`)
- **Browser** (Chrome, Firefox, Safari — and version)
- **Steps to reproduce** — the exact sequence of clicks/actions that triggers the issue
- **A minimal predictions JSON snippet** — if the bug is in parsing or displaying results, paste a small (2–5 item) excerpt of the JSON that SpeciesNet produced. Redact any sensitive paths or personal identifiers.

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Requesting a feature

Open an issue with a description of your workflow: what you're trying to accomplish, what data you have, and why the current tool falls short. Feature requests grounded in a real research use case are prioritised over abstract functionality.

Use the [workflow question template](.github/ISSUE_TEMPLATE/workflow_question.md) if your request is "how do I make this work with my data" rather than a code change.

---

## For developers: running and contributing code

### Running locally

**With Docker (recommended)**

```bash
docker compose up
# backend at :8000, frontend at :5173 with hot reload
```

**Without Docker**

```bash
# Backend
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
pnpm install
pnpm dev
```

### Code style

| Layer | Linter / formatter | Run with |
|-------|--------------------|---------|
| Python | ruff (lint + format) + mypy (strict) | `just lint-backend` |
| TypeScript | ESLint + Prettier (via Vite) | `just lint-frontend` |

Run everything at once: `just lint`

All lints must pass before a PR is merged. CI enforces this.

### Commit format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add MegaDetector adapter
fix: handle missing bbox_json in overlay render
docs: add Wildlife Insights export schema reference
chore: update speciesnet to 5.0.3
```

Types: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `perf`.

**Do not add `Co-Authored-By:` trailer lines to commits.** Commit as yourself.

### Pull request checklist

- [ ] `just lint` passes
- [ ] `just test` passes (backend: 19+ tests green; frontend: `tsc --noEmit` clean)
- [ ] If you added a new endpoint, there is a corresponding test in `backend/tests/`
- [ ] If you changed the UI, you've visually tested the golden path and dark mode

---

## For scientists: adapters, export formats, and taxonomy

We actively welcome contributions that extend Studio's scientific usefulness. These don't require deep software engineering skills — the patterns are straightforward.

### Adding a new model adapter

SpeciesNet Studio uses a pluggable `InferenceAdapter` protocol. Any class with a `run(folder, output_json, on_progress)` method qualifies.

A good adapter PR:

1. Implements the protocol in `backend/src/app/adapters/your_adapter.py`
2. Includes a test in `backend/tests/test_your_adapter.py` with a fixture JSON (a small synthetic predictions file is fine)
3. Updates `config/inference.yaml` with a commented-out example configuration block
4. Adds a brief description of the model and its output format to `docs/adapters.md` (create if it doesn't exist)

See [`backend/src/app/adapters/speciesnet_adapter.py`](backend/src/app/adapters/speciesnet_adapter.py) as a reference.

### Adding a new export format

Export functions live in `backend/src/app/services/exporters.py`. Add a function `export_yourformat(session, collection_id) -> str` and wire it into the export router.

Formats we'd particularly value:
- Wildlife Insights bulk upload CSV schema
- iNaturalist observation CSV
- Zooniverse subject set format
- Movebank (for GPS-tagged deployments)
- Lab-specific schemas (open an issue first to discuss)

### Taxonomy and species handling

If you notice taxonomic errors, inconsistencies in how SpeciesNet labels map to accepted species names, or missing handling for regional species, please open an issue with a citation to the relevant taxonomy authority (GBIF, iNaturalist, MSW, etc.). We'll work through it together.
