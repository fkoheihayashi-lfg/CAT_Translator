# First 30 Recordings Plan

## Goal
The first `30` recordings should create a usable spread across common daily contexts without making logging slow or complicated.

The target is not perfect balance. The target is good enough diversity to make weekly and disagreement review meaningful.

## Staged Plan

### Recordings 1-10
Focus on making the workflow real and repeatable.

Priorities:

- at least one meal-related clip
- at least one owner-related clip
- at least one play-related clip
- at least one door or window curiosity clip
- at least one low-energy or bedtime clip
- at least one `unknown` or noisy clip if it happens naturally

Good enough diversity by `10`:

- at least `4` different primary labels seen
- at least `4` different context fields used meaningfully
- no more than about half the set dominated by meal-related logging

### Recordings 11-20
Focus on spreading across situations, not just easy captures.

Priorities:

- add at least one environment-triggered clip
- add more owner-related variation
- add a second play-related clip if possible
- add at least one non-meal morning or evening clip
- capture a second curiosity clip near `door` or `window` if naturally available

Good enough diversity by `20`:

- at least `5-6` different labels seen, including `unknown` if needed
- at least `5` distinct values across `owner_context`, `activity_context`, `location_context`, and `environment_trigger`
- no single label obviously overwhelming the rest unless that truly reflects the week

### Recordings 21-30
Focus on correcting collection bias and filling gaps.

Priorities:

- check which label or context is missing or under-sampled
- intentionally look for one calmer clip and one more reactive clip
- add at least one clip with clearer owner context
- add at least one clip with clearer environment trigger if possible
- reduce repetition of the easiest capture pattern

Good enough diversity by `30`:

- all major daily context families represented
- enough variation for weekly summary and disagreement review to say something useful
- early bias visible if it exists

## Suggested Balance

| Category | Suggested target by 30 |
| --- | --- |
| Meal-related | 5-7 |
| Owner-related | 5-7 |
| Play-related | 4-6 |
| Environment-triggered | 3-5 |
| Bedtime / low-energy | 3-5 |
| Door / window curiosity | 3-5 |
| Unknown / unclear | 2-4 |

This is a practical guide, not a hard quota. Some clips may fit more than one category through context fields.

## Context Spread To Intentionally Seek

Use the fixed schema values already in the repo.

### Meal-related
- `meal_context=before_meal_window`
- `meal_context=after_meal_recent`
- `meal_context=food_visible`
- `meal_context=owner_preparing_food`

### Owner-related
- `owner_context=owner_near`
- `owner_context=owner_not_looking`
- `owner_context=owner_interacting`
- `owner_context=owner_left_room`
- `owner_context=owner_returned_home`

### Play-related
- `activity_context=before_play`
- `activity_context=during_play`

### Environment-triggered
- `environment_trigger=after_noise`
- `environment_trigger=door_or_barrier_present`
- `environment_trigger=unfamiliar_person`
- `environment_trigger=unfamiliar_animal`
- `environment_trigger=other`

### Bedtime / low-energy
- `activity_context=bedtime_or_just_woke`
- `activity_context=resting`
- `time_bucket=late_night`
- `location_context=bed`

### Door / window curiosity
- `location_context=door`
- `location_context=window`

## Simple Checklist

| Recording range | Checkpoint | Done when... |
| --- | --- | --- |
| 1-10 | Workflow works | You can log a row quickly without friction |
| 1-10 | Basic spread exists | At least 4 labels and multiple context families appear |
| 11-20 | Bias check starts | Meal-only collection is no longer dominating |
| 11-20 | Review becomes useful | `weekly_summary.py` and `disagreement_report.py` surface real patterns |
| 21-30 | Gaps are intentional | You are collecting to fill missing contexts, not just easy clips |
| 21-30 | Tuning decision becomes possible | You can tell whether issues seem data-driven or rule-driven |

## Good Enough Diversity Rules

### By 10 recordings
- `4+` labels seen
- `4+` context values across the core fields
- at least one non-meal clip logged on purpose

### By 20 recordings
- `5+` labels seen
- clear spread across meal, owner, play, curiosity, and low-energy situations
- at least one noisy or uncertain case handled consistently

### By 30 recordings
- enough variation to spot repeated patterns
- enough `unknown` handling to see whether uncertainty is mostly quality-related
- enough non-food clips to avoid tuning around a meal-only sample

## Logging Rule During This Plan
If a clip is hard to interpret:

- use `primary_tendency=unknown`
- keep `labeler_confidence=low`
- set `clip_quality` honestly

It is better to have a clean uncertain row than a forced label.
