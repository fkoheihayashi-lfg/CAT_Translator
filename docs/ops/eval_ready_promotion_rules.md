# Eval-Ready Promotion Rules

Use this note when deciding whether a reference item can move into `eval_ready`.

## Exact Gate

A candidate should only move to `eval_ready` when all of the following are true:

- `decision=eval_ready`
- `verification_status=verified`
- `audio_reuse_ok=true`
- `local_path` is present and points to the local clip
- `age_group=adult`
- the interaction is adult domestic, not mother/kitten
- `context_certainty` is not low
- the source is not view-only
- license posture is clear enough for local heuristic evaluation

## What Is Still Not Enough

These are not enough on their own:

- a good guess about the source
- a local file without license clarity
- an adult-looking clip with weak context
- a promising placeholder entry
- a manifest item already labeled `eval_ready` but still unverified

## Why The Gates Work Together

Verified plus reusable plus adult plus local plus decent context matters because current Phase 1 eval should stay small and cautious.

If one of those pieces is missing, the item may still be useful, but not as strict eval material.

## Important Boundary

`eval_ready` does not mean operational DB ingestion.

It only means the item is safe enough to appear in the strict Phase 1 heuristic-eval subset while staying outside `vocalizations.db`.
