import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).parent.parent.parent
JSON_PATH = ROOT / "data" / "sample_vocalizations.json"


def build_entry():
    now = datetime.now().astimezone().replace(microsecond=0)
    stamp = now.strftime("%Y_%m_%d_%H%M%S")
    recording_id = f"rec_{stamp}"

    return {
        "recording_id": recording_id,
        "cat_id": "momo",
        "created_at": now.isoformat(),
        "recording_uri": f"local://recordings/{recording_id}.m4a",
        "duration_ms": 0,
        "clip_quality": "clean",
        "time_bucket": "afternoon",
        "meal_context": "no_food_context",
        "owner_context": "owner_near",
        "environment_trigger": "quiet",
        "activity_context": "resting",
        "location_context": "unknown",
        "primary_tendency": "unknown",
        "secondary_tendency": None,
        "observed_outcome": "no_clear_outcome",
        "labeler_confidence": "low",
        "note": "template test entry",
    }


def main():
    with open(JSON_PATH, encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("sample_vocalizations.json must contain a JSON array at the root.")

    entry = build_entry()
    data.append(entry)

    with open(JSON_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")

    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()
