# Review Checkpoints: 10 / 20 / 30 Recordings

## Purpose
These checkpoints are for deciding whether the next step should be:

- no action
- a small scoring adjustment
- collection bias correction

They should stay inside the current local Phase 1 workflow. No schema changes are needed.

## At 10 Recordings
Inspect:

- whether logging is actually happening quickly
- whether labels are spread beyond the easiest context
- whether `unknown` is being used honestly
- whether `clip_quality` is being marked consistently

Use:

- `weekly_summary.py` for a simple top-level readout
- `review_queue.py` to find weak or unclear rows

### Likely decision at 10
Usually `no action` or `collection bias correction`.

Trigger `no action` when:

- rows are being logged consistently
- at least a few different labels appear
- no obvious over-collection pattern dominates

Trigger `collection bias correction` when:

- most rows are meal-adjacent
- most rows come from one time of day
- nearly all rows use the same few context values

Do not tune heuristic rules yet unless something looks clearly broken.

## At 20 Recordings
Inspect:

- whether disagreement is driven more by clip quality or by logic
- whether certain contexts are showing up repeatedly in flagged rows
- whether one tendency seems too easy to assign
- whether `unknown` is mostly a quality issue or a context issue

Use:

- `weekly_summary.py`
- `disagreement_report.py`
- `review_queue.py`

### Trigger `no action`
- most flagged rows are noisy or unusable
- disagreement is still small
- current labeling seems internally consistent

### Trigger `small scoring adjustment`
- repeated clean clips show the same label-vs-analysis mismatch
- the same mismatch pair appears multiple times
- one reason or context seems to be pushing the heuristic too hard

Keep any scoring change small and narrow. One rule adjustment is enough for a pass.

### Trigger `collection bias correction`
- food-related or owner-related contexts dominate the set
- one label appears often only because the same situation is being captured repeatedly
- key contexts like play, door/window curiosity, or low-energy clips are still thin

## At 30 Recordings
Inspect:

- whether intent balance still looks reasonable
- whether disagreement clusters are repeating
- whether intent bias review shows over- or under-representation
- whether quality issues are masking logic issues

Use:

- `weekly_summary.py`
- `disagreement_report.py`
- `intent_bias_report.py`

### Trigger `no action`
- inferred and labeled distributions still look broadly aligned
- flagged rows are mostly explained by noise, unusable clips, or low confidence
- context coverage is broad enough to support another week of collection

### Trigger `small scoring adjustment`
- a repeated clean mismatch keeps appearing
- the same context or reason cluster shows up in flagged rows
- the intent bias report suggests one inferred intent may be leaning high or low in a repeated way

The adjustment should stay minimal and easy to explain.

### Trigger `collection bias correction`
- the dataset still leans heavily toward one routine context
- there are too few non-food or non-owner clips
- review scripts cannot separate heuristic issues from sample imbalance

## Practical Reading Of The Current Workflow

### Weekly summary
Use this for:

- overall label mix
- unknown rate
- clip quality mix
- broad patterns worth watching next week

### Disagreement review
Use this for:

- whether review pressure is coming from clean logic mismatches or weak recordings
- repeated flagged reasons
- repeated flagged contexts

### Intent bias review
Use this for:

- whether inferred tendencies seem to run above or below labeled tendencies
- whether the dataset is still too small or too narrow to justify tuning

## Practical Decision Rule

If the same clean mismatch repeats:

- consider a small scoring adjustment

If flagged rows are mostly noisy, unusable, or low-confidence:

- collect more data first

If one context family dominates the sample:

- correct collection bias before tuning

If nothing repeats clearly:

- no action yet
