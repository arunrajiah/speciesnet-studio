# Reddit post drafts

**Note:** Post these at least one week apart so they don't read as coordinated spam. Post r/wildlifebiology first (it's the closer audience), then r/ecology a week later.

---

## Post 1: r/wildlifebiology

**Title:**  
Built an open source review tool for SpeciesNet camera trap predictions — looking for feedback from people who actually do this

**Body:**

I've been building a self-hosted review UI for SpeciesNet output and just shipped the first public version. Figured this community would have more useful feedback than anyone.

**The problem it solves:** SpeciesNet gives you a JSON blob of predictions. Reviewing that efficiently — especially at tens of thousands of images — requires tooling that hasn't existed until now. Most people I've talked to are doing this in spreadsheets, which doesn't scale and wastes ecologist time.

**What it does:** ingest a folder of images → run SpeciesNet in the background → review predictions in a gallery UI with keyboard shortcuts (A approve, arrow keys to navigate) → export to CSV. Everything runs locally, nothing goes to a server.

**Try it in 2 minutes:**
```
docker compose up
```
Then http://localhost:5173 → "Try with sample data" (uses CC-licensed images from LILA BC so you don't need to load your own data first).

GitHub: https://github.com/arunrajiah/speciesnet-studio  
Apache 2.0, free, no catch.

I'm especially interested in: what's slow about your current review process? What would make this actually useful for your workflow?

---

## Post 2: r/ecology

**Title:**  
Open source: self-hosted review UI for camera-based species identification

**Body:**

If you use camera traps and run an ML classifier on the images, this might be useful.

I built SpeciesNet Studio — a self-hosted web interface for reviewing the output of Google's SpeciesNet wildlife classifier (though the adapter is pluggable, so other models can work too). The idea: ML classifiers produce prediction files that are hard to review efficiently at scale. Studio gives you a gallery interface with confidence filtering, keyboard-driven review, and CSV/JSON export when you're done.

It runs entirely on your own hardware. No cloud account, no data leaving your machine.

**Quickstart:**
```bash
git clone https://github.com/arunrajiah/speciesnet-studio
cd speciesnet-studio
docker compose up
```
http://localhost:5173 → "Try with sample data" (Creative Commons images, no setup needed).

If you use camera traps as part of your research and have thoughts on the review workflow — or on export formats that would actually be useful to ecologists — I'd genuinely welcome the feedback.

Apache 2.0 / GitHub: https://github.com/arunrajiah/speciesnet-studio
