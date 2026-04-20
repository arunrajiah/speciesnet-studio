# LILA BC data attribution checklist

Work through this before publishing any screenshots, demo videos, or releasing the sample-data downloader script publicly.

---

## Datasets used in Studio's sample-data flow

`scripts/download_sample.py` currently downloads a small set of CC0/CC-BY images from Wikimedia Commons as a fallback. If you switch to actual LILA BC datasets, verify each one below.

| Dataset | License | Redistribution allowed? | Attribution required? | License page |
|---------|---------|------------------------|----------------------|--------------|
| Snapshot Serengeti v2 | CC BY 4.0 | Yes | Yes — cite Swanson et al. | https://lila.science/datasets/snapshot-serengeti |
| Caltech Camera Traps | CC BY 4.0 | Yes | Yes — cite Beery et al. | https://lila.science/datasets/caltech-camera-traps |
| ENA24 | CC BY 4.0 | Yes | Yes | https://lila.science/datasets/ena24detection |
| *(add others as used)* | | | | |

**Action items:**

- [ ] Confirm which specific dataset(s) and image files end up in the `FALLBACK_IMAGES` list in `scripts/download_sample.py`
- [ ] Verify each dataset's license at the links above (licenses can change)
- [ ] For CC BY datasets: confirm the attribution string in the UI and NOTICE file matches the dataset's preferred citation
- [ ] For screenshots used publicly: confirm the images in the screenshot come from a CC-licensed dataset, not from private camera data

---

## Attribution in NOTICE

NOTICE currently contains general third-party attributions. Add a section like:

```
Sample Data
-----------
The "Try with sample data" feature downloads images from the following
Creative Commons–licensed datasets:

  Snapshot Serengeti v2
  Swanson et al. (2015). Snapshot Serengeti, high-frequency annotated
  camera trap images of 40 mammalian species in an African savanna.
  Scientific Data 2, 150026. https://doi.org/10.1038/sdata.2015.26
  License: CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/

  [Add others here]
```

---

## Attribution in the UI

The sample-data flow (once it uses actual LILA datasets) should show a small attribution line:

> Sample images from [Snapshot Serengeti](https://lila.science/datasets/snapshot-serengeti), CC BY 4.0

This can go in the loading screen or as a footer note on the sample collection page.

---

## LILA BC contact

If you're unsure about a dataset's terms, email contact@lila.science or check the LILA BC GitHub at https://github.com/agentmorris/lila before using images publicly.
