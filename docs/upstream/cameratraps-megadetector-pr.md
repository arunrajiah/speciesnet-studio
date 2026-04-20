# PR draft: microsoft/CameraTraps — add SpeciesNet Studio to ecosystem listing

## Context

microsoft/CameraTraps maintains a long-standing list of downstream tools and ecosystem projects. A listing there is high-value — it's one of the first places camera trap researchers look when evaluating tooling.

**Before opening this PR:**
1. Check the current state of the repo at https://github.com/microsoft/CameraTraps
2. Find their tools/ecosystem index file — it may be in `README.md`, `docs/`, or a dedicated `ECOSYSTEM.md`. Search for "tools" or "community" in the repo.
3. Drop the snippet below in the right spot (alphabetical within its section, or wherever their convention dictates).
4. If there's no existing tools section, the PR description below asks where the best place would be — let the maintainers guide it.

---

## Markdown snippet

```markdown
- **[SpeciesNet Studio](https://github.com/arunrajiah/speciesnet-studio)** — Self-hosted web UI for reviewing wildlife classifier predictions. Currently wraps SpeciesNet; a MegaDetector adapter is planned for v0.2 via a pluggable InferenceAdapter protocol. Apache 2.0.
```

---

## PR title

```
docs: add SpeciesNet Studio to ecosystem / community tools
```

---

## PR description

SpeciesNet Studio is a self-hosted web UI for reviewing wildlife ML predictions: https://github.com/arunrajiah/speciesnet-studio

It currently wraps SpeciesNet, but the architecture uses a pluggable `InferenceAdapter` protocol — a MegaDetector adapter is on the roadmap for v0.2. I wanted to flag its existence before building the adapter, in case the team has preferences about how downstream tools should invoke MegaDetector or represent its outputs.

The tool is aimed at field researchers who want a human-in-the-loop review step: ingest images, run a classifier, review predictions in a gallery UI, export results. Apache 2.0.

I wasn't sure which file is your current tools index — if this PR targets the wrong place, I'm happy to move the snippet wherever fits best. And if you'd prefer I hold off until the MegaDetector adapter actually exists, just say so and I'll close this and reopen when it's ready.

This is the start of a conversation, not a one-shot PR. I'd value any feedback on the adapter interface design before I build it.
