# Show HN draft

**Note:** HN body has a ~1500 character limit. Show HN posts perform best Tuesday–Thursday, 9–11 am Pacific. Don't post within 24 hours of a big news cycle.

---

## Title

Show HN: SpeciesNet Studio – self-hosted review UI for wildlife ML predictions

## Body

Camera trap programs routinely produce millions of images per field season. The ML classification half is largely solved — Google's SpeciesNet (Apache 2.0) classifies ~2,000 wildlife species with good accuracy. The human review half isn't: the output is a JSON blob, and there's no open-source UI for working through it efficiently.

SpeciesNet Studio is that UI. Point it at a folder of images, run SpeciesNet, and review predictions in a virtualized gallery with keyboard shortcuts (A approve, arrow keys to navigate), bounding box overlays, confidence filters, and CSV/JSON export. Everything runs on your own hardware via Docker Compose. Nothing leaves your machine.

Stack: FastAPI + SQLModel (SQLite) on the backend, React 18 + TypeScript + Tailwind on the frontend, @tanstack/react-virtual for the gallery. Apache 2.0.

This is not a model, not a cloud service, and not a competitor to Wildlife Insights (which is a cloud platform for a different audience). It's a review tool for field researchers who already have SpeciesNet running locally.

https://github.com/arunrajiah/speciesnet-studio

---

*Character count of body above (without this note): ~960 characters. Well within the limit.*
