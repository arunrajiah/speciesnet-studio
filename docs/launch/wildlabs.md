# WILDLABS post draft

**Platform:** wildlabs.net — Conservation Technology community discussion  
**Category:** Tools & Tech (or Camera Traps, whichever fits best)

---

## Title

SpeciesNet Studio — an open source review UI for SpeciesNet predictions

---

## Body

Hi everyone,

I'm Arun, a software developer who's been working alongside researchers doing camera trap fieldwork. I built a tool I'd like to share with this community because you're the people most likely to have useful feedback on it.

**The problem, as you probably already know:**

If you've run SpeciesNet on a few seasons of data, you know the JSON output is the easy part — the hard part is getting a human reviewer through it efficiently. The raw prediction file doesn't tell you which images your team should spend the most time on, doesn't let you correct a misidentified species and track that correction, and doesn't give you a clean export when you're ready to hand off results. Most programs I've seen end up with some combination of spreadsheets, scripts, and a lot of manual clicking. That process doesn't scale, and it's a poor use of researcher time.

**What Studio does:**

SpeciesNet Studio is a self-hosted web UI that wraps your existing SpeciesNet workflow. You point it at a folder of images, it ingests everything (thumbnails, EXIF, GPS), runs SpeciesNet in the background, and opens a review interface: a virtualized thumbnail gallery with confidence badges, a detail view with bounding box overlays, keyboard-driven review (A approve, O override, R flag, arrow keys to navigate), species and confidence filters, and a one-click CSV or JSON export when you're done. All of it runs on your own machine — nothing goes to a server.

![Gallery view showing confidence badges and filter sidebar](https://github.com/arunrajiah/speciesnet-studio/raw/main/docs/media/hero.png)

**What it doesn't do:**

No cloud. No training. No detection algorithm of its own. Studio is scaffolding around your existing SpeciesNet workflow — it doesn't change how SpeciesNet classifies images, it just makes the human review step faster and less painful.

**How to try it:**

```bash
git clone https://github.com/arunrajiah/speciesnet-studio
cd speciesnet-studio
docker compose up
```

Then open http://localhost:5173 and click "Try with sample data" — it loads a small set of Creative Commons images from LILA BC so you can see the workflow without having to point it at your own data first.

**What I'm looking for from this community:**

1. **Feedback on the review workflow** from people who actually review thousands of images for a living. What's slow? What's missing? What would make A-approve/R-flag feel more natural?

2. **Export format requests** — who needs Wildlife Insights bulk upload? iNaturalist CSV? Zooniverse? A lab-specific schema? Let me know what you'd actually use. I'll build the ones that show up most.

3. **People willing to test it with their own data** — especially atypical setups (unusual folder structures, very large datasets, specific camera brands). If you try it and something breaks, please file an issue with your OS, Docker version, and a snippet of the predictions JSON.

None of this is commercial. Apache 2.0, source on GitHub, no cloud dependency.

Thank you to the Google SpeciesNet/CameraTrapAI team, the Microsoft AI for Good / MegaDetector team, and the LILA BC team — this project wouldn't exist without the foundation they've built. This community reads the same papers and cares about the same things; I'm hoping Studio can be a useful piece of infrastructure for it.

Happy to answer questions in the comments — what would you want to see next?

Arun  
https://github.com/arunrajiah/speciesnet-studio

---

*Notes for posting: attach hero.png as the post image. Post in the morning (UK time) on a Tuesday–Thursday for maximum reach. Respond to every comment within 24 hours in the first week — the WILDLABS community values responsiveness highly.*
