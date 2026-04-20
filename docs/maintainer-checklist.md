# Maintainer checklist — one-time setup

Work through these on github.com and the listed platforms. None of this is code.

---

## GitHub repository settings

- [ ] **Enable GitHub Sponsors** — go to github.com/arunrajiah → Settings → GitHub Sponsors. Requires a verified account and payout method.
- [ ] **Enable "Sponsor" button on repo** — repo Settings → General → Sponsorships → check "Enable Sponsorships button." Link to `.github/FUNDING.yml` (create if missing: `github: arunrajiah`).
- [ ] **Enable GitHub Discussions** — repo Settings → General → Features → Discussions. Categories to create:
  - Announcements (moderator-only posting)
  - Q&A (mark answers)
  - Show and tell (users sharing their results)
  - Adapter requests (feature requests for new model adapters)
  - Export format requests (feature requests for new export schemas)
- [ ] **Pin a welcome Discussion** — write a short post: who this is for, what v0.1 can do, the v0.2 roadmap items, how to get help. Pin it.
- [ ] **Turn on vulnerability reporting** — repo Settings → Code security → Private vulnerability reporting → Enable.
- [ ] **Set repository topics** — repo main page → gear icon next to "About":
  `speciesnet`, `camera-trap`, `wildlife`, `conservation-tech`, `self-hosted`, `fastapi`, `react`, `docker`, `apache-2`
- [ ] **Set repo description** — "Self-hosted review UI for SpeciesNet wildlife classifier predictions"
- [ ] **Set repo website** — your project page URL once it exists

---

## Community presence

- [ ] **Register on WILDLABS** — wildlabs.net → Create account. Complete your profile; mention SpeciesNet Studio in the bio. Join the Camera Traps and AI/ML groups.
- [ ] **Subscribe to LILA BC mailing list** — check lila.science for signup link.
- [ ] **Join AI for Conservation Slack** — if accessible (check via WILDLABS or direct search). Introduce yourself in #tools or #camera-traps.
- [ ] **Create project page** — a simple page at `arunrajiah.github.io/speciesnet-studio` with the demo video embedded. A single HTML file or GitHub Pages site is sufficient.

---

## Funding platforms

- [ ] **GitHub Sponsors** — primary (see above)
- [ ] **Open Collective** — secondary for institutional funders (see docs/open-collective-setup.md). Not urgent — revisit after the first foundation conversation.

---

## Housekeeping

- [ ] Verify `.github/FUNDING.yml` exists: `github: arunrajiah`
- [ ] Verify `.github/SPONSOR_TIERS.md` is committed and correct
- [ ] Verify `docs/supporters.md` is committed
- [ ] Verify `docs/media/` contains at least hero.png before publishing the README
