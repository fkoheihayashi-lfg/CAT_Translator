# Reference Candidate Verification Sheet

Use this sheet when verifying one candidate by hand.

## Candidate Fields

- `source_id`:
- `title`:
- `source_url`:
- `local_path`:
- `source_type`:
- `license_status`:
- `provenance_confidence`:
- `age_group`:
- `interaction_type`:
- `context_certainty`:
- `audio_reuse_ok`:
- `decision`:
- `verification_status`:
- `notes`:

## Minimum Evidence Needed To Mark `verified`

Only mark a candidate `verified` when you have enough evidence to state all of these clearly:

- where the item came from
- what the current reuse posture is
- that the local file matches the source you reviewed
- that the clip is adult domestic rather than kitten or mother/kitten
- that the context is specific enough to support cautious interpretation

## Promotion Guardrail

Do not promote a candidate to `eval_ready` unless all current gates are satisfied.

That means:
- `verification_status=verified`
- `decision=eval_ready`
- `audio_reuse_ok=true`
- `local_path` is present
- `age_group=adult`
- interaction is adult domestic, not mother/kitten
- `context_certainty` is not low

## Common Reasons To Stay `hold` Or `reference_only`

- license posture is still unclear
- local audio file is missing
- age group is still uncertain
- context is too thin or too staged
- the item is kitten or mother/kitten material
- the item is useful as evidence or a boundary example, but not as direct Phase 1 eval audio
