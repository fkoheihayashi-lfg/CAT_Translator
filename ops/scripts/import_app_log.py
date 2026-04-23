import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "data" / "vocalizations.db"

VALID_TENDENCY = {"attention_like", "food_like", "playful", "curious", "unsettled", "sleepy", "unknown"}
VALID_QUALITY = {"clean", "noisy", "unusable"}
VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_TIME_BUCKET = {"early_morning", "morning", "afternoon", "evening", "late_night"}
VALID_MEAL_CONTEXT = {"before_meal_window", "after_meal_recent", "food_visible", "owner_preparing_food", "no_food_context"}
VALID_OWNER_CONTEXT = {"owner_near", "owner_not_looking", "owner_interacting", "owner_left_room", "owner_returned_home"}
VALID_ENVIRONMENT_TRIGGER = {"quiet", "after_noise", "door_or_barrier_present", "unfamiliar_person", "unfamiliar_animal", "other"}
VALID_ACTIVITY_CONTEXT = {"resting", "before_play", "during_play", "during_pet_or_brush", "bedtime_or_just_woke"}
VALID_LOCATION_CONTEXT = {"kitchen", "sofa", "bed", "window", "door", "unknown"}
VALID_OBSERVED_OUTCOME = {"no_clear_outcome"}

DEFAULTS = {
    "cat_id": "momo",
    "duration_ms": 1000,
    "clip_quality": "noisy",
    "time_bucket": "morning",
    "meal_context": "no_food_context",
    "owner_context": "owner_near",
    "environment_trigger": "quiet",
    "activity_context": "resting",
    "location_context": "unknown",
    "primary_tendency": "unknown",
    "secondary_tendency": None,
    "observed_outcome": "no_clear_outcome",
    "labeler_confidence": "low",
    "note": "imported from app log export",
}

COLUMNS = [
    "recording_id",
    "cat_id",
    "created_at",
    "recording_uri",
    "duration_ms",
    "clip_quality",
    "time_bucket",
    "meal_context",
    "owner_context",
    "environment_trigger",
    "activity_context",
    "location_context",
    "primary_tendency",
    "secondary_tendency",
    "observed_outcome",
    "labeler_confidence",
    "note",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Import app log export JSON into vocalizations.db")
    parser.add_argument("json_path", help="Path to app_log_export.json")
    return parser.parse_args()


def load_records(path):
    with open(path, encoding="utf-8") as handle:
        parsed = json.load(handle)

    if isinstance(parsed, list):
        return parsed

    if isinstance(parsed, dict) and isinstance(parsed.get("entries"), list):
        return parsed["entries"]

    raise ValueError("Input JSON must be an array or an object containing an 'entries' array.")


def normalize(record):
    row = dict(DEFAULTS)
    row.update({key: record.get(key) for key in COLUMNS if key in record})

    if not row.get("recording_id"):
        fallback = record.get("source_log_id")
        row["recording_id"] = str(fallback) if fallback else ""

    if row.get("cat_id") is None or row.get("cat_id") == "":
        row["cat_id"] = DEFAULTS["cat_id"]

    duration = row.get("duration_ms")
    try:
        row["duration_ms"] = int(duration)
    except (TypeError, ValueError):
        row["duration_ms"] = DEFAULTS["duration_ms"]

    if row["duration_ms"] <= 0:
        row["duration_ms"] = DEFAULTS["duration_ms"]

    if row.get("clip_quality") not in VALID_QUALITY:
        row["clip_quality"] = DEFAULTS["clip_quality"]

    if row.get("time_bucket") not in VALID_TIME_BUCKET:
        row["time_bucket"] = DEFAULTS["time_bucket"]

    if row.get("meal_context") not in VALID_MEAL_CONTEXT:
        row["meal_context"] = DEFAULTS["meal_context"]

    if row.get("owner_context") not in VALID_OWNER_CONTEXT:
        row["owner_context"] = DEFAULTS["owner_context"]

    if row.get("environment_trigger") not in VALID_ENVIRONMENT_TRIGGER:
        row["environment_trigger"] = DEFAULTS["environment_trigger"]

    if row.get("activity_context") not in VALID_ACTIVITY_CONTEXT:
        row["activity_context"] = DEFAULTS["activity_context"]

    if row.get("location_context") not in VALID_LOCATION_CONTEXT:
        row["location_context"] = DEFAULTS["location_context"]

    if row.get("primary_tendency") not in VALID_TENDENCY:
        row["primary_tendency"] = DEFAULTS["primary_tendency"]

    if row.get("labeler_confidence") not in VALID_CONFIDENCE:
        row["labeler_confidence"] = DEFAULTS["labeler_confidence"]

    if row.get("observed_outcome") not in VALID_OBSERVED_OUTCOME:
        row["observed_outcome"] = DEFAULTS["observed_outcome"]

    if row.get("secondary_tendency") not in VALID_TENDENCY:
        row["secondary_tendency"] = None

    if row.get("clip_quality") == "unusable":
        row["primary_tendency"] = "unknown"
        row["labeler_confidence"] = "low"

    if row.get("primary_tendency") == "unknown":
        row["labeler_confidence"] = "low"

    if row.get("secondary_tendency") == row.get("primary_tendency"):
        row["secondary_tendency"] = None

    note_parts = []

    def append_note(part):
        text = str(part).strip()
        if text and text not in note_parts:
            note_parts.append(text)

    if row.get("note"):
        for part in str(row["note"]).split(" | "):
            append_note(part)
    if record.get("app_summary_text"):
        append_note(f"app summary: {record['app_summary_text']}")
    if record.get("source_log_id"):
        append_note(f"source_log_id={record['source_log_id']}")

    row["note"] = " | ".join(note_parts) or DEFAULTS["note"]
    return row


def validate(row):
    if not row.get("recording_id"):
        return "missing recording_id"
    if not row.get("created_at"):
        return "missing created_at"
    if not row.get("primary_tendency"):
        return "missing primary_tendency"
    if row.get("clip_quality") not in VALID_QUALITY:
        return f"invalid clip_quality: {row.get('clip_quality')}"
    if row.get("primary_tendency") not in VALID_TENDENCY:
        return f"invalid primary_tendency: {row.get('primary_tendency')}"
    if row.get("labeler_confidence") not in VALID_CONFIDENCE:
        return f"invalid labeler_confidence: {row.get('labeler_confidence')}"
    if row.get("time_bucket") not in VALID_TIME_BUCKET:
        return f"invalid time_bucket: {row.get('time_bucket')}"
    if row.get("meal_context") not in VALID_MEAL_CONTEXT:
        return f"invalid meal_context: {row.get('meal_context')}"
    if row.get("owner_context") not in VALID_OWNER_CONTEXT:
        return f"invalid owner_context: {row.get('owner_context')}"
    if row.get("environment_trigger") not in VALID_ENVIRONMENT_TRIGGER:
        return f"invalid environment_trigger: {row.get('environment_trigger')}"
    if row.get("activity_context") not in VALID_ACTIVITY_CONTEXT:
        return f"invalid activity_context: {row.get('activity_context')}"
    if row.get("location_context") not in VALID_LOCATION_CONTEXT:
        return f"invalid location_context: {row.get('location_context')}"
    if row.get("observed_outcome") not in VALID_OBSERVED_OUTCOME:
        return f"invalid observed_outcome: {row.get('observed_outcome')}"
    if row.get("duration_ms") is not None and row["duration_ms"] <= 0:
        return f"duration_ms must be > 0, got: {row['duration_ms']}"
    return None


def main():
    args = parse_args()
    records = load_records(args.json_path)

    con = sqlite3.connect(DB_PATH)
    inserted = skipped = rejected = 0
    rejection_reasons = []

    for record in records:
        row = normalize(record)
        error = validate(row)
        if error:
            rejected += 1
            rejection_reasons.append(f"  {record.get('recording_id') or record.get('source_log_id') or '?'}: {error}")
            continue

        values = [row.get(column) for column in COLUMNS]
        cur = con.execute(
            f"INSERT OR IGNORE INTO vocalizations ({', '.join(COLUMNS)}) VALUES ({', '.join(['?'] * len(COLUMNS))})",
            values,
        )

        if cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    con.commit()
    con.close()

    print(f"Inserted:  {inserted}")
    print(f"Skipped (duplicate): {skipped}")
    print(f"Rejected:  {rejected}")
    if rejection_reasons:
        print("\nRejection reasons:")
        for reason in rejection_reasons:
            print(reason)


if __name__ == "__main__":
    main()
