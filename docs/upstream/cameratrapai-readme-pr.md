# PR draft: google/cameratrapai — add SpeciesNet Studio to community tools

## Markdown snippet to add

Find or create a "Community Tools" or "Tools built on SpeciesNet" section in the google/cameratrapai README. Proposed placement: after the "Getting started" section, before "Citation."

```markdown
## Community Tools

Tools built by the community on top of SpeciesNet:

- **[SpeciesNet Studio](https://github.com/arunrajiah/speciesnet-studio)** — Self-hosted web UI for reviewing SpeciesNet predictions. Ingest a folder of images, run inference from the UI, review results in a virtualized gallery with keyboard shortcuts, and export to CSV or JSON. Apache 2.0.
```

If a community tools section already exists, insert the bullet in alphabetical order by tool name.

---

## PR title

```
docs: add SpeciesNet Studio to community tools
```

---

## PR description

SpeciesNet Studio is a self-hosted web UI for reviewing SpeciesNet predictions on a researcher's own camera data: https://github.com/arunrajiah/speciesnet-studio

It uses SpeciesNet's documented CLI interface (`python -m speciesnet.scripts.run_model`) without modification — Studio is purely scaffolding around the prediction workflow. The adapter also supports calling the Python API directly. Apache 2.0, same license as SpeciesNet itself.

The tool is aimed at field ecologists and camera trap practitioners who want a human-in-the-loop review step between running SpeciesNet and handing off results. It doesn't replace SpeciesNet, retrain the model, or require a cloud account.

I'm flagging this via PR so the team has a chance to review the description before it appears in the docs, and so the link is visible to users who search the SpeciesNet repo for review tooling.

Happy to move this section, revise the description, or split into a separate docs page — whatever fits your repo structure. If you'd prefer not to maintain a community tools list, I completely understand; just close the PR.

---

*Notes: check google/cameratrapai's CONTRIBUTING.md before opening the PR. Some Google repos require a CLA. Keep the PR small — just the one README edit. Reference this file in the PR description if helpful.*
