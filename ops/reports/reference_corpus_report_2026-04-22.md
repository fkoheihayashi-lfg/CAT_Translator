# Reference Corpus Report - 2026-04-22

## Executive Snapshot
- Total candidate count: 8
- Eval-ready count in manifest: 2
- Verified eval subset count: 0
- Blocked-for-now count: 8

## Decision Distribution
- reference_only: 3
- eval_ready: 2
- hold: 2
- exclude: 1

## Verification Status Distribution
- placeholder_for_verification: 4
- example: 4

## Block Reasons
- Top block reasons reflect the current strict Phase 1 gate and may still be provisional rather than final quality judgments.
- verification_not_verified: 8
- decision_not_eval_ready: 6
- audio_reuse_not_ok: 4
- not_adult: 3
- low_context_certainty: 2
- missing_local_path: 2

## Age Group / Interaction Type Split
- age_group=adult: 5
- age_group=mother_kitten: 1
- age_group=kitten: 1
- age_group=mixed_or_unspecified: 1
- interaction_type=adult_domestic: 5
- interaction_type=mother_kitten: 1
- interaction_type=juvenile_only: 1
- interaction_type=paper_summary: 1

## Current Phase 1 Eval Posture
- Likely usable for current Phase 1 eval: 2
- Strict generated eval subset available: 0
- No item has cleared the strict verified gate yet, so the corpus still seems partly provisional.

## Next-Step Recommendations
- 8 item(s) are still provisional, so verification work may matter more than adding another batch immediately.
- The strict eval subset is still empty, so it may be better to verify a few adult clips before doing broader heuristic spot-checking.
- Verification status is still blocking several items, so a small source-review pass may unlock more value than collecting loosely.
