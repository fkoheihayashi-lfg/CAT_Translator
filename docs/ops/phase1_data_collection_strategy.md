# Phase 1 Data Collection Strategy

## Purpose
Phase 1 collection is for building a practical local dataset of short cat vocalization logs that can be reviewed consistently in SQLite. The goal is not to prove a cat's true emotion. The goal is to capture a repeatable combination of:

- the clip
- the immediate context
- the best practical tendency label
- confidence and quality notes

That gives the local heuristic something useful to compare against and gives the review scripts enough structure to surface patterns.

## Why We Are Collecting Context + Tendency
Phase 1 should stay interpretive, not diagnostic. A single clip rarely gives enough information to claim a certain internal state. Context is what makes the label useful.

The working question is:

`Given this recording and this immediate situation, what tendency does this clip seem most like?`

That is more practical than trying to log a true emotion with certainty.

## Daily Capture Recommendation
For solo development, use a small daily target that is easy to repeat:

- Aim for `3` logs per day
- If the day is unusually active, `4-5` is fine
- If the day is quiet, even `1-2` is still useful if the context is different from recent clips

The important thing is repeatability, not volume spikes.

## What To Prioritize First
Prioritize clips that are:

1. easy to capture
2. easy to label quickly
3. spread across different contexts

If two clips happen close together, prefer the one with clearer context over the one that is merely louder or longer.

## Diversity Rule
Do not let early logging collapse into meal-only clips.

Use this practical rule:

- Never log more than `2` food-like or meal-adjacent clips in a row if another context is available that day
- After a meal-related clip, look next for one of:
  - owner-related attention
  - play
  - door/window curiosity
  - noise/environment reaction
  - bedtime or low-energy

If the day only produces meal-related clips, that is still usable, but the next day should intentionally look for non-meal contexts first.

## Policy For Unknown / Noisy / Unusable
Use `unknown` when context or signal is not strong enough to support a cleaner label.

Use `clip_quality=noisy` when the clip is still usable but background sound may be affecting interpretation.

Use `clip_quality=unusable` when the recording is too weak or contaminated to support real interpretation.

Practical rule:

- `unknown` is acceptable
- `noisy` is acceptable
- `unusable` should be logged sparingly, but it is still worth tracking if it reveals a recording problem

When in doubt:

- choose `unknown`
- keep `labeler_confidence=low`
- add a short note

## What To Do Immediately After Recording
Keep the per-row workflow short:

1. save the clip locally
2. create the row as soon as possible
3. fill only the minimum fields needed for Week 1
4. add a short note only if it helps explain why the label was chosen

The row should stay fillable in under about `30` seconds.

## Week 1 Behavior
Week 1 should optimize for speed and consistency, not completeness.

Minimum operating behavior:

- log quickly
- use the fixed Phase 1 labels only
- fill minimum fields first
- do not overthink secondary labels
- use `unknown` freely when needed

Recommended Week 1 minimum fields:

- `recording_id`
- `created_at`
- `primary_tendency`
- `clip_quality`
- `time_bucket`
- one strongest context field if obvious
  - usually `meal_context`, `owner_context`, `environment_trigger`, `activity_context`, or `location_context`
- `labeler_confidence`

If more than one context field is obvious, fill them. If not, move on.

## Week 2 Behavior
Week 2 should stay small but become slightly more deliberate.

Add effort in these places:

- improve spread across contexts
- reduce repeated easy labels only
- review `unknown` and noisy clips
- notice where the same reasons or contexts keep appearing

Do not slow the logging flow too much. Collection still matters more than polishing single rows.

## SQLite Logging Workflow
The local SQLite project is the operational center for Phase 1.

Practical flow:

1. capture a clip into `data/recordings/` if needed
2. use `intake_recordings.py` to create safe draft rows when helpful
3. use `add_log.py` or `import_app_log.py` to get rows into `vocalizations.db`
4. use `review_queue.py` to find clips worth relabeling or double-checking
5. use `weekly_summary.py` for a compact weekly readout
6. use `disagreement_report.py` and `intent_bias_report.py` to decide whether the heuristic needs a small adjustment or whether more data is the better next move

## Practical Collection Standard
Phase 1 is working if:

- logging happens daily or near-daily
- rows are quick to enter
- labels stay within the fixed set
- early data is not dominated by one context only
- review scripts can surface useful patterns without schema changes

That is enough to support immediate local collection.
