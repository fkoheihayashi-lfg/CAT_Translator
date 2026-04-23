import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "vocalizations.db"
JSON_PATH = Path(__file__).parent.parent.parent / "data" / "sample_vocalizations.json"

REQUIRED = {"recording_id", "cat_id", "created_at", "primary_tendency", "clip_quality", "labeler_confidence"}
VALID_TENDENCY = {"attention_like", "food_like", "playful", "curious", "unsettled", "sleepy", "unknown"}
VALID_QUALITY = {"clean", "noisy", "unusable"}
VALID_CONFIDENCE = {"low", "medium", "high"}

COLUMNS = [
    "recording_id", "cat_id", "created_at", "recording_uri", "duration_ms",
    "clip_quality", "time_bucket", "meal_context", "owner_context",
    "environment_trigger", "activity_context", "location_context",
    "primary_tendency", "secondary_tendency", "observed_outcome",
    "labeler_confidence", "note",
]


def validate(row):
    missing = REQUIRED - row.keys()
    if missing:
        return f"missing fields: {', '.join(sorted(missing))}"
    if row["clip_quality"] not in VALID_QUALITY:
        return f"invalid clip_quality: {row['clip_quality']}"
    if row["primary_tendency"] not in VALID_TENDENCY:
        return f"invalid primary_tendency: {row['primary_tendency']}"
    if row["labeler_confidence"] not in VALID_CONFIDENCE:
        return f"invalid labeler_confidence: {row['labeler_confidence']}"
    return None


def normalize(row):
    row = dict(row)

    if row.get("clip_quality") == "unusable":
        row["primary_tendency"] = "unknown"

    if row.get("primary_tendency") == "unknown" and row.get("labeler_confidence") != "low":
        row["labeler_confidence"] = "low"

    if row.get("secondary_tendency") and row["secondary_tendency"] == row.get("primary_tendency"):
        row["secondary_tendency"] = None

    return row


def main():
    with open(JSON_PATH) as f:
        records = json.load(f)

    con = sqlite3.connect(DB_PATH)
    inserted = skipped = rejected = 0
    rejection_reasons = []

    for record in records:
        error = validate(record)
        if error:
            rejected += 1
            rejection_reasons.append(f"  {record.get('recording_id', '?')}: {error}")
            continue

        row = normalize(record)
        values = [row.get(col) for col in COLUMNS]

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
        for r in rejection_reasons:
            print(r)


if __name__ == "__main__":
    main()
