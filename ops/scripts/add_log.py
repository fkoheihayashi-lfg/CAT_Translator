import sqlite3
import argparse
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "vocalizations.db"

VALID_TENDENCY = {"attention_like", "food_like", "playful", "curious", "unsettled", "sleepy", "unknown"}
VALID_QUALITY = {"clean", "noisy", "unusable"}
VALID_CONFIDENCE = {"low", "medium", "high"}

REQUIRED = {"recording_id", "cat_id", "created_at", "primary_tendency", "clip_quality", "labeler_confidence"}

DEFAULTS = {
    "cat_id": "momo",
    "created_at": "2026-04-22T07:00:00-07:00",
    "recording_uri": "local://recordings/sample.m4a",
    "duration_ms": 1000,
    "clip_quality": "clean",
    "time_bucket": "morning",
    "meal_context": "no_food_context",
    "owner_context": "owner_near",
    "environment_trigger": "quiet",
    "activity_context": "resting",
    "location_context": "sofa",
    "primary_tendency": "unknown",
    "secondary_tendency": None,
    "observed_outcome": "no_clear_outcome",
    "labeler_confidence": "low",
    "note": "",
}

COLUMNS = ["recording_id"] + list(DEFAULTS.keys())

parser = argparse.ArgumentParser(description="Insert one vocalization row into vocalizations.db")
parser.add_argument("--recording_id", required=True)
for key, val in DEFAULTS.items():
    parser.add_argument(f"--{key}", default=val, type=(int if isinstance(val, int) else str) if val is not None else str)

args = vars(parser.parse_args())
row = {k: args[k] for k in COLUMNS}

# --- validation ---
errors = []

for field in REQUIRED:
    if not row.get(field):
        errors.append(f"missing required field: {field}")

if row.get("clip_quality") and row["clip_quality"] not in VALID_QUALITY:
    errors.append(f"invalid clip_quality: {row['clip_quality']}")

if row.get("primary_tendency") and row["primary_tendency"] not in VALID_TENDENCY:
    errors.append(f"invalid primary_tendency: {row['primary_tendency']}")

if row.get("labeler_confidence") and row["labeler_confidence"] not in VALID_CONFIDENCE:
    errors.append(f"invalid labeler_confidence: {row['labeler_confidence']}")

if row.get("duration_ms") is not None and row["duration_ms"] <= 0:
    errors.append(f"duration_ms must be > 0, got: {row['duration_ms']}")

if errors:
    for e in errors:
        print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

# --- normalization ---
if row.get("clip_quality") == "unusable":
    row["primary_tendency"] = "unknown"
    row["labeler_confidence"] = "low"

if row.get("primary_tendency") == "unknown" and row.get("labeler_confidence") != "low":
    row["labeler_confidence"] = "low"

if row.get("secondary_tendency") and row["secondary_tendency"] == row.get("primary_tendency"):
    row["secondary_tendency"] = None

# --- insert ---
con = sqlite3.connect(DB_PATH)
cur = con.execute(
    f"INSERT OR IGNORE INTO vocalizations ({', '.join(COLUMNS)}) VALUES ({', '.join(['?'] * len(COLUMNS))})",
    [row[c] for c in COLUMNS],
)
con.commit()
con.close()

if cur.rowcount == 1:
    print(f"Inserted: {row['recording_id']}")
else:
    print(f"Skipped (duplicate): {row['recording_id']}")
