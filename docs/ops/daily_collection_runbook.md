# Daily Collection Runbook

## Purpose
This is the daily-use page for Phase 1 collection. Keep the workflow fast, local, and repeatable.

The goal is not to capture every detail. The goal is to get a usable row into SQLite in under about `30` seconds.

## Week 1 Minimum Logging Flow
1. notice a usable vocalization moment
2. record the clip locally
3. decide whether the clip is worth logging
4. enter one row with minimum fields only
5. move on

If the row starts taking too long, simplify rather than adding more detail.

## Before Recording
Before pressing record:

- check that local recording is easy to save and find
- prefer clips with a clear immediate context
- if you already logged two meal-like clips in a row, look for a different context next if one is available

Do not wait for a perfect example. A practical clip with clear context is enough.

## What To Record Immediately After
Right after recording, capture the row while the situation is still fresh.

Fill:

- `recording_id`
- `created_at`
- `primary_tendency`
- `clip_quality`
- `time_bucket`
- `labeler_confidence`
- one strongest context field if obvious

Possible context fields:

- `meal_context`
- `owner_context`
- `environment_trigger`
- `activity_context`
- `location_context`

If a second context field is obvious, fill it. If not, skip it.

## Minimum Week 1 Fields
Week 1 should stay minimal:

- `recording_id`
- `created_at`
- `primary_tendency`
- `clip_quality`
- `time_bucket`
- `labeler_confidence`
- one strongest context field

`secondary_tendency` is optional. `note` is optional. Use them only if they help.

## Handling Unknown / Noisy / Unusable
Use `primary_tendency=unknown` when the clip does not support a cleaner label.

Use:

- `clip_quality=clean` when the clip is usable and the source is reasonably clear
- `clip_quality=noisy` when the clip is still usable but background sound may be affecting interpretation
- `clip_quality=unusable` when the clip is too weak or contaminated to support useful interpretation

Practical rule:

- if unsure, use `unknown`
- if unsure, use `labeler_confidence=low`
- keep quality honest

## When To Skip A Clip
Skip the clip if:

- it is mostly accidental handling noise
- the vocalization source is too ambiguous
- you missed the actual moment and only caught the tail end
- logging it would add no useful context beyond several nearly identical clips already captured that day

It is fine to skip weak clips. Collection quality matters more than forcing every recording into the dataset.

## How To Avoid Overusing `food_like`
Meal clips are easy to capture, so they can take over early logging.

Use this rule:

- do not log more than `2` meal-related clips in a row if another context is available that day
- after a meal-related clip, look next for one of:
  - owner-related attention
  - play
  - door/window curiosity
  - noise/environment reaction
  - bedtime or low-energy

## Realistic Solo-Dev Daily Target
- target `3` rows per day
- `1-2` still counts on a quiet day
- `4-5` is fine on an active day if rows stay quick

Consistency matters more than volume.

## Don't Overthink It
- choose the clearest tendency, not the fanciest one
- use only the fixed Phase 1 labels
- if context is weak, do not force certainty
- if the clip is unclear, use `unknown`
- if the row takes too long, simplify it

## Existing Local Workflow
Use the current local scripts as the routine:

- `add_log.py` for direct row entry
- `intake_recordings.py` if you want draft rows from `data/recordings/`
- `weekly_summary.py` for weekly review
- `disagreement_report.py` and `intent_bias_report.py` for review once the dataset grows
