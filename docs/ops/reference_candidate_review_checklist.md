# Reference Candidate Review Checklist

Use this checklist when reviewing one reference item by hand.

## Candidate Review

- `source_id` is present and unique enough to track
- title is specific enough to recognize later
- source URL is present
- provenance is described clearly enough to explain where the item came from
- license posture is clear enough for local evaluation use
- local audio file exists if this is an audio item
- `audio_reuse_ok` is actually true for the intended use
- age group is identified clearly enough
- interaction type is identified clearly enough
- context certainty is not low if the item might become eval-ready
- the item is adult domestic enough for current Phase 1 heuristic eval
- the item is not mother/kitten or kitten-only
- the item is not only a view-only web/social example

## Decision Check

Choose one:

- `eval_ready`
  Use only if the item is verified, locally available, clearly reusable, adult, and contextually usable.

- `hold`
  Use if the item may still become useful, but something important is still unresolved.

- `reference_only`
  Use if the item is still useful for notes, boundaries, or evidence context, but not for audio eval.

- `exclude`
  Use if the item should stay out of the current Phase 1 path.

## Quick Stop Rules

If any of these are true, do not mark the item `eval_ready`:

- unclear license
- no local audio file
- `verification_status` is not `verified`
- kitten or mother/kitten material
- low context certainty
- view-only source
