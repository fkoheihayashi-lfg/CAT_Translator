# Reference Corpus Next Actions

Use this page to turn the reference corpus into a small working layer without touching the operational SQLite workflow.

## Add A New Item

1. Open `reference_corpus/manifest.json`.
2. Copy the shape of an existing item.
3. Fill in all standard fields:
   - `source_id`
   - `title`
   - `source_type`
   - `source_url`
   - `local_path`
   - `license_status`
   - `provenance_confidence`
   - `age_group`
   - `interaction_type`
   - `context_certainty`
   - `audio_reuse_ok`
   - `phase1_relevance`
   - `reference_role`
   - `candidate_tendency`
   - `decision`
   - `verification_status`
   - `notes`
4. If anything is still uncertain, say that directly in `verification_status` and `notes`.

## Decision Meanings

| Decision | Use when |
| --- | --- |
| `eval_ready` | Adult domestic audio is locally stored, reuse posture is clear, and context is at least moderately interpretable |
| `reference_only` | Useful for comparison, boundary checking, or paper evidence, but not for current Phase 1 audio eval |
| `hold` | Might become usable later, but license, provenance, or context is not clear enough yet |
| `exclude` | Should stay out of the current eval path |

## Exact Gate For Phase 1 Heuristic-Eval Ready

An adult clip should only be marked `eval_ready` if all of the following are true:

- `age_group` is `adult`
- `interaction_type` is `adult_domestic`
- `license_status` is clearly reusable for local evaluation work
- `audio_reuse_ok` is `true`
- `local_path` points to a local audio file
- `context_certainty` is at least `medium`
- `decision` is `eval_ready`
- `verification_status` does not hide unresolved licensing or provenance questions

If any of those fail, keep the item as `hold`, `reference_only`, or `exclude`.

## What Must Not Enter The Operational DB

Do not insert any external reference item into `data/vocalizations.db`.

Keep these out of the operational SQLite flow:
- external licensed clips
- dataset examples
- social or web video clips
- mother-cat or kitten references
- paper-evidence references
- any provisional or placeholder item

The operational DB stays for real Phase 1 logging, manual labeling, and comparison against inferred local analysis.

## First-Pass Workflow For 3 To 5 Real Candidates

1. Find 3 to 5 adult domestic clip candidates with a reviewable source page.
2. Download or store only the items whose reuse posture appears acceptable.
3. Add each one to `reference_corpus/manifest.json`.
4. Mark uncertain items as `hold`, not `eval_ready`.
5. Run `python3 ops/scripts/eval_reference_manifest.py`.
6. Keep only the clearly adult, locally stored, moderate-context items in the first eval-ready subset.

## Caution

Do not treat online clips as ground truth.

Even when a clip is useful for heuristic checking, the source context may still be thin, staged, incomplete, or mislabeled. Use the reference corpus as a cautious comparison layer, not as a source of certainty.
