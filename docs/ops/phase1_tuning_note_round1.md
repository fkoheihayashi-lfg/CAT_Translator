# Phase 1 Tuning Note Round 1

## What Was Tuned
Round 1 kept the heuristic structure intact and changed only two small behaviors:

- noisy clips with very weak context now fall back to `unknown` a little earlier
- `high` confidence on clean clips now requires slightly stronger evidence than before

## Why It Was Tuned
The current review outputs show very little true label-vs-analysis divergence, so this round was less about forcing new agreements and more about making uncertainty safer.

The main signals behind the change were:

- noisy weak-context clips looked like they could still lean into a content label too easily
- some clean clips could still receive `high` confidence with a fairly narrow evidence margin

The goal was to reduce optimism, not to make the heuristic more aggressive.

## What Was Intentionally Not Tuned
These areas were left alone on purpose:

- label set
- schema
- overall heuristic structure
- major score families
- interpretive summary text
- app flow or logging flow

No tuning was added just to manufacture disagreement reduction.

## What Should Wait For More Logs
These should only be revisited after more real collection:

- whether `owner_left_room` is weighted too strongly toward `unsettled`
- whether `resting` gives slightly too much sleepy support in mixed contexts
- whether any one tendency is truly over-favored in clean clips
- whether additional near-tie handling is actually needed

At the current dataset size, those questions still look a little thin.

## Caution Against Overfitting
This round should stay small because the dataset is still limited.

A useful rule for future passes:

- tune only repeated clean-pattern issues
- do not tune around one-off clips
- if uncertainty is mostly quality-driven, collect more data first
