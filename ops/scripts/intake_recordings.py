import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "data" / "vocalizations.db"
RECORDINGS_DIR = ROOT / "data" / "recordings"

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
    "note": "auto-intake draft from recordings scan",
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

AUDIO_EXTENSIONS = {".m4a", ".wav", ".mp3", ".aac", ".flac", ".ogg"}


def iso_from_mtime(path):
    return datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds")


def local_recording_uri(path):
    rel_path = path.relative_to(RECORDINGS_DIR).as_posix()
    return f"local://recordings/{rel_path}"


def recording_id_for(path):
    return path.stem


def iter_recordings():
    if not RECORDINGS_DIR.exists():
        return []

    return sorted(
        path for path in RECORDINGS_DIR.rglob("*") if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )


def build_row(path):
    row = dict(DEFAULTS)
    row["recording_id"] = recording_id_for(path)
    row["created_at"] = iso_from_mtime(path)
    row["recording_uri"] = local_recording_uri(path)
    return row


def main():
    recordings = iter_recordings()

    if not recordings:
        print(f"No recordings found in {RECORDINGS_DIR}")
        return

    con = sqlite3.connect(DB_PATH)
    inserted = 0
    skipped = 0

    for path in recordings:
        row = build_row(path)
        cur = con.execute(
            f"INSERT OR IGNORE INTO vocalizations ({', '.join(COLUMNS)}) VALUES ({', '.join(['?'] * len(COLUMNS))})",
            [row[column] for column in COLUMNS],
        )
        if cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    con.commit()
    con.close()

    print(f"Scanned {len(recordings)} recording file(s)")
    print(f"Inserted draft rows: {inserted}")
    print(f"Skipped existing rows: {skipped}")


if __name__ == "__main__":
    main()
