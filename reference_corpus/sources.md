# Reference Corpus Sources

## Purpose
This note keeps source posture explicit before anything is used for heuristic evaluation.

## Source-Type Policy

| Source type | Default decision | Can store locally? | Can be Phase 1 eval-ready? | Can enter operational DB? | Why |
| --- | --- | --- | --- | --- | --- |
| Official datasets | Hold | Sometimes, after review | Not by default | No | License, provenance, and age/context fit often need review first |
| Licensed audio library clips | Hold | Yes, if license allows | Sometimes, after review | No | May become usable if adult/domestic and context is clear enough |
| Unclear-license audio | Hold | No, unless cleared later | No | No | License posture is too uncertain for current safe use |
| YouTube / social / general web video | Exclude | No | No | No | Usually view-only and too weak for direct eval use |
| Mother-cat audio | Reference Only | Sometimes, if license allows | No | No | Useful for boundary notes, not aligned with current adult heuristic eval |
| Kitten audio | Reference Only | Sometimes, if license allows | No | No | Should stay separate from adult Phase 1 evaluation |
| Paper / evidence-only source | Reference Only | Optional local note or PDF only | No | No | Useful as evidence context, not as eval audio |

## Practical Rules
- Keep adult domestic cat audio separate from mother/kitten material.
- Keep audio items separate from paper/evidence-only references.
- If license status is unclear, do not use the clip for Phase 1 heuristic eval.
- If an audio item has no local copy, do not treat it as an eval-ready item.
- Do not ingest external reference items into `vocalizations.db`.
- Use `manifest.json` as the working file and keep `manifest_template.json` as a clean example.

## Current Eval Standard
An item is only a good current Phase 1 heuristic eval candidate if it is:

- adult
- domestic interaction context
- locally available
- clearly reusable
- not mixed with mother/kitten behavior
- specific enough to support cautious interpretation
