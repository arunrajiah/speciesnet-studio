# Good-neighbor PR checklist

Small, unsolicited PRs against upstream repos before making the listing asks. The goal is to show up as a contributor, not just a beneficiary. Keep each PR under 50 LOC and very low-risk.

Complete these before (or alongside) the listing PRs in the other docs/upstream files.

---

## google/cameratrapai

- [ ] Check the open issues at https://github.com/google/cameratrapai/issues — look for anything labelled `documentation`, `good first issue`, or `help wanted`
- [ ] Review the README and docs for broken links, outdated example commands, or typos
- [ ] Check example scripts for any obvious Python 3.11+ compatibility issues
- [ ] If the test suite has gaps on edge-case JSON inputs (empty predictions, missing bbox, etc.), add a small test

**Candidate PR:** docs fix or example script update. Open the issue first to confirm it's wanted before sending the PR.

---

## microsoft/CameraTraps (MegaDetector)

- [ ] Check https://github.com/microsoft/CameraTraps/labels/good%20first%20issue
- [ ] Browse `README.md` and any `docs/` pages for stale links or outdated version numbers
- [ ] Check example notebooks for any dependencies that have changed APIs
- [ ] If there's a FAQ or troubleshooting page, look for common GitHub issue themes that aren't documented there

**Candidate PR:** docs improvement or notebook update. This repo is large and active; a small documentation fix is very likely to be merged.

---

## LILA BC (if they maintain a tools/code repo)

- [ ] Check https://github.com/agentmorris/lila for any open issues
- [ ] If they have any helper scripts for downloading data, check for outdated dependencies or Python version issues
- [ ] If they have a datasets index page with broken links, fix one

**Candidate PR:** dependency fix or dead link correction.

---

## Notes

- Don't open a PR and the listing ask at the same time — it looks transactional. Land the small PR first, wait for it to merge, then open the listing ask.
- If a maintainer declines the small PR (it happens), that's fine — still make the listing ask. The good-neighbor effort is genuine, not a precondition.
- Keep a note here of what you opened and its status:

| Repo | PR title | Status | Date |
|------|----------|--------|------|
| google/cameratrapai | | | |
| microsoft/CameraTraps | | | |
| lila (agentmorris) | | | |
