import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = ROOT / "ops" / "scripts"

SCRIPT_ORDER = [
    "weekly_summary.py",
    "disagreement_report.py",
    "intent_bias_report.py",
]


def run_script(script_name):
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Skip: {script_name} not found")
        return 0

    print(f"\n== Running {script_name} ==")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        print(f"Warning: {script_name} exited with code {result.returncode}")
    return result.returncode


def main():
    print("Phase 1 review loop")
    exit_codes = []
    for script_name in SCRIPT_ORDER:
        exit_codes.append(run_script(script_name))

    if any(code != 0 for code in exit_codes):
        print("\nPhase 1 review completed with warnings.")
    else:
        print("\nPhase 1 review completed.")


if __name__ == "__main__":
    main()
