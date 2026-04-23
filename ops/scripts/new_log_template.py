import json
from datetime import datetime


def build_template():
    now = datetime.now().astimezone().replace(microsecond=0)
    stamp = now.strftime("%Y_%m_%d_%H%M%S")

    return {
        "recording_id": f"rec_{stamp}",
        "cat_id": "",
        "created_at": now.isoformat(),
        "recording_uri": "",
        "duration_ms": "",
        "clip_quality": "",
        "time_bucket": "",
        "meal_context": "",
        "owner_context": "",
        "environment_trigger": "",
        "activity_context": "",
        "location_context": "",
        "primary_tendency": "",
        "secondary_tendency": "",
        "observed_outcome": "",
        "labeler_confidence": "",
        "note": "",
    }


def main():
    print(json.dumps(build_template(), indent=2))


if __name__ == "__main__":
    main()
