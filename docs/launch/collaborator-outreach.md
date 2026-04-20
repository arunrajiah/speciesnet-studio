# Collaborator outreach emails

Send these individually, not as a batch. Space them at least a week apart to give each team time to respond before the next one arrives.

---

## 1. Wildlife Insights team

**To:** wildlifeinsights@google.org (or use the contact form at wildlifeinsights.org)  
**Subject:** Open-source self-hosted review tool that sits upstream of Wildlife Insights — interested in collaborating?

Hi,

I'm Arun Rajiah, an independent developer. I've just shipped the first version of SpeciesNet Studio (https://github.com/arunrajiah/speciesnet-studio) — an open-source, self-hosted web UI for reviewing Google SpeciesNet predictions on a researcher's own camera data before they decide what to do with the results.

I think Studio sits naturally upstream of Wildlife Insights: researchers who run SpeciesNet locally, do their own human review, then want to upload a clean, reviewed dataset to Wildlife Insights for the collaborative features. The gap right now is that there's no good tool for the review step.

I'm open to building an export format that lines up with your bulk upload CSV schema, so Studio could be a first-class on-ramp for researchers who want to use Wildlife Insights downstream. Would the team be interested in collaborating on that, or in listing Studio somewhere in your docs as a self-hosted complement to the platform?

Happy to share more or demo — just let me know.

Arun Rajiah  
https://github.com/arunrajiah/speciesnet-studio

---

## 2. Microsoft AI for Good / MegaDetector team

**To:** cameratraps@microsoft.com or maintainer(s) via GitHub (microsoft/CameraTraps)  
**Subject:** MegaDetector adapter for SpeciesNet Studio — looking for guidance

Hi,

I'm Arun Rajiah. I've just released SpeciesNet Studio (https://github.com/arunrajiah/speciesnet-studio), an open-source review UI for wildlife classifier predictions. It currently wraps SpeciesNet but uses a pluggable InferenceAdapter protocol so other models can be added.

I'd like to add a MegaDetector adapter as a first-class option in v0.2. Before I build it, I wanted to ask: are there any guidelines or preferences from your side about how downstream tools should invoke MegaDetector? Any output format specifics, citation requirements, or things previous integrators have got wrong that I should know about?

I want to build the adapter in a way that's correct and that you'd be comfortable pointing users toward if they ask about review tooling. If there's a better person to ask on the team, I'm happy to be redirected.

Thanks for everything the MegaDetector project has contributed to this field.

Arun Rajiah  
https://github.com/arunrajiah/speciesnet-studio

---

## 3. Google SpeciesNet / cameratrapai team

**To:** Via GitHub issue or discussion on google/cameratrapai  
**Subject / issue title:** Heads-up: SpeciesNet Studio — a review UI built on SpeciesNet

Hi,

I wanted to flag the existence of SpeciesNet Studio (https://github.com/arunrajiah/speciesnet-studio) in case it's useful to link from your docs.

Studio is a self-hosted web UI that wraps SpeciesNet's documented CLI (`python -m speciesnet.scripts.run_model`) unchanged — it doesn't modify the model or its output format, just adds a review interface on top. Apache 2.0, same as SpeciesNet itself.

I'm not asking for endorsement or a formal partnership — just wanted to be transparent about the tool's existence. If the team has any feedback about how Studio invokes SpeciesNet, or concerns about how it's described relative to SpeciesNet's own capabilities, I'd genuinely want to know.

And if it's useful to mention in your ecosystem docs, I'd be honoured.

Thanks for building SpeciesNet and making it open-source.

Arun Rajiah  
https://github.com/arunrajiah/speciesnet-studio
