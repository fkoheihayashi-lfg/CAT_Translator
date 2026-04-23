# Intent Bias Report - 2026-04-22

## Executive Snapshot
- Rows inspected: 11
- Flagged comparison rows: 3
- Suggested next step: collect more data first

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

## Intent Distribution Gaps
- attention_like: labeled=2 (18.2%), inferred=2 (18.2%), gap=0 (+0.0%)
- food_like: labeled=2 (18.2%), inferred=2 (18.2%), gap=0 (+0.0%)
- playful: labeled=2 (18.2%), inferred=2 (18.2%), gap=0 (+0.0%)
- curious: labeled=1 (9.1%), inferred=1 (9.1%), gap=0 (+0.0%)
- unsettled: labeled=1 (9.1%), inferred=1 (9.1%), gap=0 (+0.0%)
- sleepy: labeled=1 (9.1%), inferred=1 (9.1%), gap=0 (+0.0%)
- unknown: labeled=2 (18.2%), inferred=2 (18.2%), gap=0 (+0.0%)

## Overrepresented Inferred Intents
- No inferred intent currently looks overrepresented against the labeled distribution.

## Underrepresented Inferred Intents
- No inferred intent currently looks underrepresented against the labeled distribution.

## Top Recurring Reasons In Flagged Rows
- clip unusable: 1
- short clip duration: 1
- unusual trigger: 1
- owner left room: 1
- clip too short to read: 1
- noisy clip with weak context: 1
- after loud noise: 1
- on the bed: 1

## Top Recurring Contexts In Flagged Rows
- meal_context=no_food_context: 3
- owner_context=owner_near: 2
- activity_context=resting: 2
- time_bucket=afternoon: 1
- environment_trigger=quiet: 1
- activity_context=during_pet_or_brush: 1
- location_context=sofa: 1
- time_bucket=early_morning: 1

## Cautious Observations
- Sleepy may be receiving repeated support from bed (1), bedtime_or_just_woke (1) style contexts.
- Unknown rows may be driven more by clip quality than by label mismatch, with 2 of 2 flagged unknown rows landing in noisy or unusable audio.
- Flagged rows seem to repeat around a small set of contexts, especially meal_context=no_food_context (3), owner_context=owner_near (2).
- A few heuristic reasons appear repeatedly in flagged rows, including clip unusable (1), short clip duration (1).

## Recommendation
- collect more data first
