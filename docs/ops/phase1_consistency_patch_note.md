# Phase 1 Consistency Patch Note

## What Was Fixed
- `intake_recordings.py` no longer uses `time_bucket=unknown`; it now falls back to the valid Phase 1 value `morning`.
- `import_app_log.py` now keeps import provenance in `note` and uses `observed_outcome=no_clear_outcome` instead of an import-specific placeholder.
- `import_app_log.py` now validates fixed structured fields more consistently:
  - `time_bucket`
  - `meal_context`
  - `owner_context`
  - `environment_trigger`
  - `activity_context`
  - `location_context`
  - `observed_outcome`
- `exportAppLog.mjs` now uses the same valid fixed value for `observed_outcome`.
- `exportAppLog.mjs` now derives `time_bucket` from the event’s local wall-clock hour in the timestamp string instead of UTC bucketing.

## Why It Mattered
These were small alignment issues, but they could quietly create drift between:

- the fixed Phase 1 template values
- exported app-log data
- imported SQLite rows
- draft rows created from recording intake

The patch keeps Phase 1 data more consistent without changing the schema or current workflow.

## What Was Intentionally Left Unchanged
- schema
- labels
- current local analysis logic
- current SQLite review/report flow
- app architecture
- import/export file structure

This patch is only for value alignment and safer defaults.
