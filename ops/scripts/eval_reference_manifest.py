import argparse
import json
from collections import Counter
from pathlib import Path

DEFAULT_MANIFEST = Path("reference_corpus") / "manifest.json"
FALLBACK_MANIFEST = Path("reference_corpus") / "manifest_template.json"
AUDIO_SOURCE_TYPES = {
    "licensed_audio_clip",
    "licensed_audio_library_clip",
    "dataset_audio",
    "freesound_clip",
    "youtube_audio",
    "official_dataset",
}
VIEW_ONLY_SOURCE_TYPES = {"social_video", "youtube_video", "web_video", "youtube_audio"}


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize a reference corpus manifest for Phase 1 heuristic eval.")
    parser.add_argument(
        "manifest_path",
        nargs="?",
        default=None,
        help="Path to a reference corpus manifest JSON file.",
    )
    return parser.parse_args()


def resolve_manifest_path(path_arg):
    if path_arg:
        return Path(path_arg), None
    if DEFAULT_MANIFEST.exists():
        return DEFAULT_MANIFEST, None
    if FALLBACK_MANIFEST.exists():
        return FALLBACK_MANIFEST, f"Working manifest not found, falling back to template: {FALLBACK_MANIFEST}"
    return DEFAULT_MANIFEST, "No manifest.json or manifest_template.json found."


def load_items(path):
    with open(path, encoding="utf-8") as handle:
        parsed = json.load(handle)

    if not isinstance(parsed, dict) or not isinstance(parsed.get("items"), list):
        raise ValueError("Manifest must be an object containing an 'items' list.")

    return parsed["items"]


def group_summary(items, field):
    counts = Counter(str(item.get(field, "missing")) for item in items)
    return counts.most_common()


def flag_reasons(item):
    reasons = []
    if item.get("license_status") in (None, "", "unclear", "unknown", "needs_review"):
        reasons.append("unclear_license")
    if item.get("age_group") in {"kitten", "mother_kitten"}:
        reasons.append(item.get("age_group"))
    if item.get("interaction_type") == "mother_kitten":
        reasons.append("mother_kitten")
    if item.get("source_type") in AUDIO_SOURCE_TYPES:
        if not item.get("local_path"):
            reasons.append("no_local_path")
    if item.get("context_certainty") in {"low", None, ""}:
        reasons.append("low_context_certainty")
    if item.get("audio_reuse_ok") is False:
        reasons.append("audio_reuse_not_ok")
    if item.get("source_type") in VIEW_ONLY_SOURCE_TYPES or item.get("license_status") == "view_only":
        reasons.append("view_only_source")
    if item.get("decision") == "hold":
        reasons.append("hold")
    if item.get("decision") == "exclude":
        reasons.append("exclude")
    if item.get("decision") == "reference_only":
        reasons.append("reference_only")
    return reasons


def print_group(items, field):
    print(f"\n-- {field} --")
    for value, count in group_summary(items, field):
        print(f"  {value}: {count}")


def eval_ready(item):
    return (
        item.get("decision") == "eval_ready"
        and item.get("license_status") == "clear_reuse"
        and item.get("age_group") == "adult"
        and item.get("interaction_type") == "adult_domestic"
        and item.get("context_certainty") in {"medium", "high"}
        and item.get("audio_reuse_ok") is True
        and bool(item.get("local_path"))
    )


def main():
    args = parse_args()
    manifest_path, note = resolve_manifest_path(args.manifest_path)
    if note and not manifest_path.exists():
        raise FileNotFoundError(note)

    items = load_items(manifest_path)

    print("=" * 55)
    print("  Reference Manifest Summary")
    print("=" * 55)
    print(f"Manifest: {manifest_path}")
    if note:
        print(note)
    print(f"Items: {len(items)}")

    for field in ("decision", "source_type", "license_status", "age_group", "interaction_type", "reference_role"):
        print_group(items, field)

    ready_items = [item for item in items if eval_ready(item)]
    blocked = []
    for item in items:
        reasons = flag_reasons(item)
        if reasons:
            blocked.append((item, reasons))
        elif item.get("decision") != "eval_ready":
            blocked.append((item, ["not_marked_eval_ready"]))

    print("\n-- Phase 1 Heuristic-Eval Ready --")
    if not ready_items:
        print("  none")
    else:
        for item in ready_items:
            print(
                f"  {item.get('source_id', '?')}: {item.get('title', 'untitled')} "
                f"[{item.get('candidate_tendency', 'unknown')}] "
                f"(local_path={item.get('local_path', '')})"
            )

    print("\n-- Do Not Use For Current Phase 1 Eval --")
    if not blocked:
        print("  none")
    else:
        for item, reasons in blocked:
            deduped = list(dict.fromkeys(reasons))
            print(f"  {item.get('source_id', '?')}: {', '.join(deduped)}")


if __name__ == "__main__":
    main()
