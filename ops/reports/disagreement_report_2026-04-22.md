# Disagreement Report - 2026-04-22

## Executive Snapshot
- Rows inspected: 11
- Flagged review rows: 3
- Labeled vs inferred mismatches among flagged rows: 0
- High priority rows: 0
- Medium priority rows: 2
- Low priority rows: 1
- hard_mismatch: 0
- fragile_match: 1
- unknown_unusable: 1
- unknown_noisy: 1
- unknown_clean: 0
- overdominance_candidate: 0

## Dataset Health
- Total rows: 11
- Clean ratio: 8 (72.7%)
- Noisy ratio: 2 (18.2%)
- Unusable ratio: 1 (9.1%)
- Low confidence ratio: 2 (18.2%)
- Medium confidence ratio: 3 (27.3%)
- High confidence ratio: 6 (54.5%)
- Unknown ratio: 2 (18.2%)
- Distinct time_bucket values: 5
- Distinct meal_context values: 3
- Distinct owner_context values: 5
- Distinct environment_trigger values: 4
- Distinct activity_context values: 5
- Distinct location_context values: 5

## Top Mismatch Pairs
- No mismatch pairs stood out in this pass; most rows seem to line up with the current heuristic.

## High-Priority Review Rows
- No rows reached high priority in this pass; the current set may mostly need lighter monitoring.

## Context Clusters
- meal_context=no_food_context: 2
- time_bucket=afternoon: 1
- owner_context=owner_near: 1
- environment_trigger=quiet: 1
- activity_context=during_pet_or_brush: 1
- location_context=sofa: 1
- time_bucket=early_morning: 1
- owner_context=owner_left_room: 1

## Reason Clusters
- clip unusable: 1
- short clip duration: 1
- unusual trigger: 1
- owner left room: 1
- clip too short to read: 1
- noisy clip with weak context: 1

## Cautious Observations
- Unknown rows may be driven more by clip quality than by label mismatch in this pass.
- Flagged rows seem to cluster around a small set of contexts: meal_context=no_food_context (2), time_bucket=afternoon (1).
- A few reasons appear repeatedly in flagged rows: clip unusable (1), short clip duration (1).

## Tuning Suggestions
- The context cluster `meal_context=no_food_context` appears repeatedly in review rows (2 hits), so that context may be worth watching more closely.
- The reason `clip unusable` comes up often in flagged rows (1 times), which could mean that signal is doing more work than expected.
- Unknown rows may be driven more by clip quality than by label mismatch right now, with 2 flagged unknown row(s).
