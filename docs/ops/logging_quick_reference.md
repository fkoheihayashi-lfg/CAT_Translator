# Logging Quick Reference

## Week 1 Minimum Fields
- `recording_id`
- `created_at`
- `primary_tendency`
- `clip_quality`
- `time_bucket`
- `labeler_confidence`
- one strongest context field if obvious

## Allowed Phase 1 Labels
- `attention_like`
- `food_like`
- `playful`
- `curious`
- `unsettled`
- `sleepy`
- `unknown`

## Allowed Quality Values
- `clean`
- `noisy`
- `unusable`

## Fast Logging Rule
- Fill one row in under about `30` seconds
- Use the clearest label, not the most confident-sounding one
- If context is weak, do not force it

## Common Mistakes To Avoid
- logging too many meal clips in a row
- forcing a label when `unknown` is more honest
- marking noisy clips as clean
- spending too long on notes
- treating one clip like proof of a true emotion

## When In Doubt
- use `unknown`
- use `labeler_confidence=low`
- keep `clip_quality` honest

## Daily Target
- aim for `3` logs per day
