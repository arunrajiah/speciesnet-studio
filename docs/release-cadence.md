# Release cadence playbook

Research users value stability over novelty. This cadence is intentionally slower than consumer OSS. Do not ship weekly churn.

---

## v0.1.0 launch (Week 0)

- [ ] Tag `v0.1.0`, push to GitHub
- [ ] Confirm CI passes and Docker images publish to ghcr.io
- [ ] Verify `docker compose -f docker-compose.release.yml up` works from scratch
- [ ] Capture and commit hero.png and screenshots to docs/media/
- [ ] Finalize README (screenshots populated, not placeholders)
- [ ] Record demo.mp4 and keyboard-review.gif (see docs/media/README.md)
- [ ] Open GitHub Discussions with welcome post (see docs/maintainer-checklist.md)

---

## Week 1 — WILDLABS (anchor post)

- [ ] Post on WILDLABS using docs/launch/wildlabs.md
- [ ] **Respond to every comment within 24 hours** for the first week — WILDLABS community values this
- [ ] Pin the WILDLABS thread URL in the GitHub Discussions welcome post

---

## Week 2 — Broader reach

- [ ] Post on r/wildlifebiology (docs/launch/reddit-research.md, post 1)
- [ ] Post in Camera Trappers Facebook group (docs/launch/camera-trappers-facebook.md)
- [ ] Send LILA BC outreach (docs/launch/lila-bc.md)
- [ ] Triage any issues opened from Week 1 posts

---

## Week 3 — Upstream outreach + good-neighbor PRs

- [ ] Land at least one good-neighbor PR against google/cameratrapai or microsoft/CameraTraps (docs/upstream/good-neighbor.md)
- [ ] Send MegaDetector team outreach (docs/launch/collaborator-outreach.md, email 2)
- [ ] Send SpeciesNet team heads-up (docs/launch/collaborator-outreach.md, email 3)
- [ ] Send Wildlife Insights outreach (docs/launch/collaborator-outreach.md, email 1)

---

## Week 4 — HN + patch release

- [ ] Post Show HN using docs/launch/hacker-news.md (Tue–Thu, 9–11 am Pacific)
- [ ] Post on r/ecology (docs/launch/reddit-research.md, post 2)
- [ ] Ship `v0.1.1` with the top 2–3 issues reported from launch week
- [ ] `v0.1.1` release note template (see below)

---

## Month 2 — Roadmap post + v0.2 start

- [ ] Post "one month in" retrospective on WILDLABS — what's working, what isn't, early usage patterns
- [ ] Post v0.2 roadmap on WILDLABS as a separate thread, listing planned items with explicit requests for input
- [ ] Begin MegaDetector adapter work
- [ ] Begin first partner export format (whichever was most requested in issues/comments)

---

## Month 3 — v0.2 release

- [ ] Ship `v0.2.0` with MegaDetector adapter and first partner export format
- [ ] Full release post on WILDLABS (not just a tag)
- [ ] Update the good-neighbor PRs section with any new upstream collaborations

---

## Month 4–6 — Steady cadence

- Release every **4–6 weeks**. Do not ship more frequently unless fixing a critical bug.
- Research users plan around their field seasons; a tool that changes every week is more disruptive than helpful.
- Each release: 1–3 features or fixes, full changelog entry, WILDLABS comment or update (not a new post every time — just a reply in an existing thread).

---

## Month 6 — Sustainability check

Evaluate:
- **> 1 foundation sponsor** — yes/no
- **> 300 GitHub stars** — yes/no
- **> 20 active installs** (inferred from GitHub Issues activity, not analytics) — yes/no

If 2 of 3: start planning v1.0 (stability guarantees, migration path, docs site).  
If 0 of 3: write a retrospective, post on WILDLABS asking what's blocking adoption, adjust.

---

## Release update template

Use this for every release post/comment:

> **[1 screenshot — new feature or fixed UI]**
>
> **What's new in vX.Y.Z:**
> - [Feature or fix 1]
> - [Feature or fix 2]
> - [Feature or fix 3 or "various small fixes"]
>
> **One ask:** [specific, actionable — "if you use Wildlife Insights, please try the new export and let me know if the format is correct"]
>
> **Thanks:** [named acknowledgment of anyone who contributed, filed a useful bug report, or tested a pre-release]
