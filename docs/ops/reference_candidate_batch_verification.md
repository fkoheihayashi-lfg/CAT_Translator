# Reference Candidate Batch Verification

Use this runbook when reviewing 2 to 3 candidates in one sitting.

## Batch Flow

1. Prepare candidate info.
   Gather source URL, local file path, license posture, age-group notes, interaction notes, and any context notes.

2. Update `reference_corpus/manifest.json`.
   Add or edit the 2 to 3 candidates and keep unresolved items as `candidate`, `hold`, or `reference_only`.

3. Run the audit.
   Use `python3 ops/scripts/reference_manifest_audit.py` to catch missing fields and unsafe promotions.

4. Run the eval subset builder.
   Use `python3 ops/scripts/build_eval_subset.py` to see what actually clears the strict gate.

5. Run the corpus report.
   Use `python3 ops/scripts/reference_corpus_report.py` to get the current weekly posture.

6. Check whether the strict eval subset is still empty.
   If it is still empty, read the blocker reasons before changing more items.

7. Decide what stays blocked.
   If a candidate remains blocked, keep it where it belongs and write the unresolved reason into `notes`.

## If A Candidate Remains Blocked

Do not force promotion.

Leave it as:
- `hold` if it may still become usable
- `reference_only` if it is still useful but not for direct eval
- `exclude` if it should stay out of the current Phase 1 path
