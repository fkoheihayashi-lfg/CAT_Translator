# Reference Corpus Lifecycle

Use this lifecycle to keep reference items practical, separate, and easy to review.

## States

| State | Meaning |
| --- | --- |
| `candidate` | Newly added item that still needs a real review pass |
| `hold` | Potentially useful later, but not clear enough yet on license, provenance, or context |
| `reference_only` | Useful for awareness, boundary checking, or evidence notes, but not for current Phase 1 audio eval |
| `exclude` | Should stay out of the current eval path |
| `eval_ready` | Cleared for the current adult Phase 1 heuristic-eval subset |

## What Each State Means In Practice

`candidate` is the intake state. Use it when an item has been added but not screened.

`hold` means the item might still become useful, but not yet. This is the right state for unclear licensing, thin context, missing local files, or incomplete provenance notes.

`reference_only` means the item can still be worth keeping around, but only as a note, boundary example, or evidence source.

`exclude` means the item should not be part of the current Phase 1 curation path.

`eval_ready` is reserved for a small set of adult clips that are safe enough for cautious heuristic spot-checking.

## What Is Required To Move Into `eval_ready`

An item should only move into `eval_ready` when all of the following are true:

- provenance is clear enough to describe honestly
- license posture is clear enough for local evaluation use
- the audio file exists locally
- `audio_reuse_ok` is true
- `age_group` is `adult`
- the interaction is adult domestic, not mother/kitten
- context certainty is at least moderate
- `verification_status` is `verified`

## What Should Never Move Into `eval_ready` For Current Phase 1

These should stay out of the current eval subset:

- kitten-only audio
- mother-cat / kitten interaction audio
- view-only web or social sources
- unclear-license items
- paper or evidence-only references without reusable audio
- placeholders that are still unverified

## How To Treat Placeholders And Examples

Placeholders and examples are useful for structure, but they are not approved items.

Keep them marked clearly in `verification_status` and `notes`. Do not silently promote them to `eval_ready`.

## Adult Domestic Audio vs Mother/Kitten vs Evidence-Only

Adult domestic audio is the only source class that can become current Phase 1 heuristic-eval material.

Mother/kitten audio can still be useful as a boundary reference, but it should stay separate because the interaction pattern may differ.

Evidence-only items such as papers or source notes may help interpretation, but they are not audio eval inputs.
