# Reference Corpus Weekly Workflow

Use this workflow to keep the reference corpus small, reviewable, and honest.

## When Adding 1 New Candidate

1. Add the item to `reference_corpus/manifest.json`.
2. Start it as `candidate` or `hold` unless it is already fully verified.
3. Run `python3 ops/scripts/eval_reference_manifest.py`.
4. Run `python3 ops/scripts/reference_manifest_audit.py`.
5. Only move it to `eval_ready` if it clears the current Phase 1 gate.

## When Adding 5 Candidates In A Batch

1. Add all five to `manifest.json`.
2. Keep unresolved items as `candidate` or `hold`.
3. Run the audit script first to catch missing fields and bad promotions.
4. Run the eval helper to review quick screening posture.
5. Run the subset builder only after the manifest looks clean.
6. Generate the weekly corpus report to see whether the batch actually improved the usable eval pool.

## When To Run Each Script

- `eval_reference_manifest.py`
  Run after adding or editing items when you want a quick screen of ready vs blocked items.

- `reference_manifest_audit.py`
  Run after any manifest editing session and before a weekly review.

- `build_eval_subset.py`
  Run only when you want the current strict eval-ready subset generated.

- `reference_corpus_report.py`
  Run once per weekly review pass or after a meaningful curation batch.

## Keep Collecting Or Start Spot-Checking

Keep collecting when:
- most items are still `candidate`, `hold`, or provisional
- the strict eval subset is empty
- the corpus is still dominated by blocked reasons like unclear license or missing local files

Start heuristic spot-checking when:
- there is a small verified adult-only subset
- the eval subset is no longer empty
- the blocked reasons are no longer doing most of the work

## Placeholder Separation Rule

Keep placeholders and examples visibly separate from verified items.

Do that by:
- leaving `verification_status` as non-verified
- keeping notes explicit about placeholder status
- never treating a placeholder as automatic eval material
