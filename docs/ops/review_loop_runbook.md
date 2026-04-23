# Review Loop Runbook

## Purpose
This runbook explains how to review Phase 1 collection using the current local SQLite workflow.

This step is for review only. It is not for schema changes, architecture changes, or model work.

## Explicit Constraints
- no schema changes
- no architecture changes
- no backend work
- no model training work
- no Flask / YAMNet direction for this step

## When To Run Review

### Weekly summary
Run `weekly_summary.py` at least once per week.

Also run it sooner if:

- you logged a concentrated burst of new rows
- you want a quick check on quality mix, unknown rate, and label spread

### Disagreement report
Run `disagreement_report.py` once you have enough rows for review to be meaningful.

Practical threshold:

- useful by about `10` recordings
- more useful by `20+`

### Intent bias report
Run `intent_bias_report.py` once you want to compare labeled vs inferred distribution.

Practical threshold:

- worth checking around `20` recordings
- more useful by `30+`

## What To Do At 10 Recordings
Inspect:

- whether logging is staying fast
- whether `unknown` is being used honestly
- whether clip quality is being marked consistently
- whether the set is too meal-heavy

Likely outcome at `10`:

- `no action` or `collect more data first`

Trigger `no action` when:

- rows are coming in consistently
- at least a few different labels appear
- no obvious collection bias is dominating

Trigger `collect more data first` when:

- most rows come from one repeated routine
- there are too few non-meal contexts
- review signals are still too thin to interpret

## What To Do At 20 Recordings
Inspect:

- whether disagreement seems quality-driven or logic-driven
- whether flagged rows repeat the same reason or context
- whether one tendency seems too easy to assign

Use:

- `weekly_summary.py`
- `disagreement_report.py`
- `review_queue.py`

Trigger `collect more data first` when:

- most flagged rows are noisy, unusable, or low-confidence
- disagreement is still sparse
- context coverage is still thin

Trigger `small scoring adjustment` when:

- repeated clean clips show the same label-vs-analysis mismatch
- the same reason cluster keeps appearing in flagged rows
- the same context cluster keeps appearing in flagged rows

Keep any scoring change small and narrow.

## What To Do At 30 Recordings
Inspect:

- whether inferred vs labeled distributions still look aligned
- whether disagreement clusters are repeating
- whether intent bias is starting to show a lean
- whether quality issues are masking logic issues

Use:

- `weekly_summary.py`
- `disagreement_report.py`
- `intent_bias_report.py`

Trigger `no action` when:

- distributions still look broadly aligned
- flagged rows are mostly explained by weak clip quality
- context coverage is broad enough to support another collection cycle

Trigger `collect more data first` when:

- the dataset is still too narrow by context
- the same collection bias keeps showing up
- the review outputs are still mostly describing sample imbalance

Trigger `small scoring adjustment` when:

- the same clean mismatch repeats
- one context or reason cluster seems to be over-supporting a tendency
- intent bias suggests one inferred tendency may be leaning high or low in a repeated way

## Practical Decision Rule
Use the smallest valid next move:

- if nothing repeats clearly: `no action`
- if quality problems dominate: `collect more data first`
- if one clean mismatch pattern repeats: `small scoring adjustment`

## Current Local Review Flow
The current Phase 1 flow is:

1. collect rows into `vocalizations.db`
2. run `weekly_summary.py`
3. inspect `review_queue.py` output when needed
4. run `disagreement_report.py` when enough data exists
5. run `intent_bias_report.py` when distribution comparison becomes useful

That is enough for Phase 1 review.
