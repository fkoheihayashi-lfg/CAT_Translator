# Reference Corpus

## Purpose
This directory is a separate holding area for external reference materials used to support heuristic evaluation.

It is not part of the operational `vocalizations.db` workflow.

Use it for:

- licensed external adult domestic cat clips kept for heuristic spot-checking
- paper or evidence references that inform interpretation
- source tracking, provenance notes, and license posture

Do not use it to:

- replace the operational SQLite logging table
- insert external clips directly into `vocalizations.db`
- mix mother/kitten audio into current adult Phase 1 tendency evaluation

## Basic Structure
- `manifest.json`: real working manifest
- `manifest_template.json`: starter manifest shape
- `sources.md`: quick policy and source notes
- local clip files can be stored in subfolders if needed

Suggested future subfolders:

- `audio/adult_domestic/`
- `audio/hold/`
- `papers/`

Keep names simple and provenance explicit.

## Reference Item Fields
Recommended fields for each manifest entry:

- `source_id`
- `title`
- `source_type`
- `source_url`
- `local_path`
- `license_status`
- `provenance_confidence`
- `age_group`
- `interaction_type`
- `context_certainty`
- `audio_reuse_ok`
- `phase1_relevance`
- `reference_role`
- `candidate_tendency`
- `decision`
- `verification_status`
- `notes`

## Working File Rule
- `manifest_template.json` stays as an example/template
- `manifest.json` is the real working file

The helper script should read `manifest.json` first and only fall back to the template if the working file is missing.

## Operational Rule
If a clip is meant for current Phase 1 adult heuristic evaluation, it should:

- have a clear license posture
- have a local file path if it is audio
- be adult domestic cat material
- have enough context certainty to support cautious interpretation

If it fails those checks, keep it as hold/reference-only material.
