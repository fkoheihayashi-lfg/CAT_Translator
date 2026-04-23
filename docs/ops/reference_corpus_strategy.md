# Reference Corpus Strategy

## Purpose
The reference corpus exists to keep external material useful without polluting the operational Phase 1 SQLite workflow.

The operational `vocalizations.db` table remains the working table for:

- local day-to-day logging
- manual labeling
- weekly summary
- disagreement review
- intent bias review

The reference corpus is separate and lighter-weight.

## What Belongs In The Operational DB
Operational `vocalizations.db` should continue to hold:

- real logged operational clips
- manual labels
- structured context fields
- local analysis comparison data

It is the active Phase 1 logging table and should stay usable for manual/operational review.

## What Belongs In The Reference Corpus
The reference corpus should hold:

- external audio clips with explicit provenance
- licensing notes
- age-group notes
- interaction-type notes
- context certainty notes
- evidence-only references such as papers or source notes

This keeps outside material available without mixing it into operational logging.

The working reference manifest should now be:

- `reference_corpus/manifest.json`

The template should remain:

- `reference_corpus/manifest_template.json`

Use `manifest_template.json` as a clean example only. Day-to-day tracking should go into `reference_corpus/manifest.json`.

## What Belongs In The Eval Set
The eval set should be a small subset of the reference corpus containing only items that are safe for current heuristic checking.

Good current eval candidates are:

- adult domestic cat clips
- locally stored audio
- clear enough license posture
- moderate or high context certainty
- useful for testing current adult Phase 1 tendencies

They should also be marked clearly in the manifest as:

- `decision=eval_ready`
- `reference_role=heuristic_eval_candidate`
- `verification_status` that honestly reflects whether the item is verified or still provisional

## Source-Type Posture

| Source type | Posture | Why |
| --- | --- | --- |
| Official datasets | Hold | May be useful, but license and age/context fit still need review |
| Freesound CC0 clips | Hold | Potentially usable if provenance and context are good enough |
| Freesound non-CC0 or unclear | Exclude | Too much license ambiguity for current safe use |
| YouTube / social video | Reference Only | Useful for observation, not clean eval input |
| Mother-cat / kitten audio | Exclude | Not aligned with current adult Phase 1 tendency evaluation |
| Research-paper evidence without reusable audio | Reference Only | Helpful context, but not eval audio |

## Why Mother / Kitten Audio Stays Out
Current Phase 1 logging and heuristic review are centered on adult domestic cat tendency interpretation.

Mother/kitten interaction clips may differ in:

- vocal pattern
- interaction motive
- context meaning
- practical interpretation target

Because of that, they should not be mixed into the current adult eval subset.

## Practical Use Of Licensed Adult Clips
Use a small number of licensed adult clips to:

- spot-check current heuristic tendencies
- compare whether the heuristic behaves sensibly outside the local logged sample
- test whether uncertainty handling still looks appropriate

Do not use external clips to replace operational logging. Use them only as a separate evaluation layer.
