import argparse
import json
from collections import Counter
from pathlib import Path

DEFAULT_MANIFEST = Path("reference_corpus") / "manifest.json"
AUDIO_SOURCE_TYPES = {
    "licensed_audio_clip",
    "licensed_audio_library_clip",
    "dataset_audio",
    "freesound_clip",
    "youtube_audio",
    "official_dataset",
}
REQUIRED_FIELDS = [
    "source_id",
    "title",
    "source_type",
    "source_url",
    "license_status",
    "age_group",
    "interaction_type",
    "context_certainty",
    "reference_role",
    "decision",
    "verification_status",
]
VERIFIED_STATUSES = {"verified"}
UNCLEAR_LICENSES = {"unclear", "unknown", "needs_review", "view_only", "dataset_restricted"}


def parse_args():
    parser = argparse.ArgumentParser(description="Audit reference_corpus/manifest.json for basic Phase 1 consistency.")
    parser.add_argument("manifest_path", nargs="?", default=str(DEFAULT_MANIFEST), help="Path to manifest JSON.")
    return parser.parse_args()


def load_items(path):
    with open(path, encoding="utf-8") as handle:
        parsed = json.load(handle)

    if not isinstance(parsed, dict) or not isinstance(parsed.get("items"), list):
        raise ValueError("Manifest must be an object containing an 'items' list.")
    return parsed["items"]


def group_counts(items, field):
    return Counter(str(item.get(field) or "missing") for item in items)


def is_audio_item(item):
    return item.get("source_type") in AUDIO_SOURCE_TYPES


def find_duplicate_ids(items):
    seen = Counter(str(item.get("source_id") or "missing") for item in items)
    return [(source_id, count) for source_id, count in seen.items() if count > 1]


def missing_field_counts(items):
    counts = Counter()
    for item in items:
        for field in REQUIRED_FIELDS:
            if item.get(field) in (None, ""):
                counts[field] += 1
    return counts


def problem_reasons(item):
    reasons = []
    if not item.get("source_url"):
        reasons.append("missing_source_url")
    if not item.get("decision"):
        reasons.append("missing_decision")
    if not item.get("verification_status"):
        reasons.append("missing_verification_status")
    if is_audio_item(item) and not item.get("local_path"):
        reasons.append("audio_item_missing_local_path")

    if item.get("decision") == "eval_ready":
        if not item.get("local_path"):
            reasons.append("eval_ready_missing_local_path")
        if item.get("verification_status") not in VERIFIED_STATUSES:
            reasons.append("eval_ready_not_verified")
        if item.get("age_group") in {"kitten", "mother_kitten"}:
            reasons.append("eval_ready_invalid_age_group")
        if item.get("interaction_type") == "mother_kitten":
            reasons.append("eval_ready_mother_kitten")
        if item.get("license_status") in UNCLEAR_LICENSES:
            reasons.append("eval_ready_unclear_license")
    return reasons


def main():
    args = parse_args()
    manifest_path = Path(args.manifest_path)
    items = load_items(manifest_path)
    duplicates = find_duplicate_ids(items)
    missing_counts = missing_field_counts(items)

    print("=" * 60)
    print("  Reference Manifest Audit")
    print("=" * 60)
    print(f"Manifest: {manifest_path}")
    print(f"Total items: {len(items)}")
    print(f"Duplicate source_id values: {len(duplicates)}")

    print("\nMissing required field counts")
    if not missing_counts:
        print("  none")
    else:
        for field, count in missing_counts.most_common():
            print(f"  {field}: {count}")

    for field in (
        "decision",
        "verification_status",
        "source_type",
        "license_status",
        "age_group",
        "interaction_type",
        "reference_role",
    ):
        print(f"\nCounts by {field}")
        for value, count in group_counts(items, field).most_common():
            print(f"  {value}: {count}")

    print("\nDuplicate source_id details")
    if not duplicates:
        print("  none")
    else:
        for source_id, count in duplicates:
            print(f"  {source_id}: {count}")

    problems = []
    for item in items:
        reasons = problem_reasons(item)
        if reasons:
            problems.append((item.get("source_id") or "missing", reasons))

    print("\nManifest problems")
    if not problems:
        print("  none")
    else:
        for source_id, reasons in problems:
            print(f"  {source_id}: {', '.join(dict.fromkeys(reasons))}")


if __name__ == "__main__":
    main()
