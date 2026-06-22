"""
scripts/migrate_to_central_openai_client.py

ONE-TIME migration: updates all service files to use the centralized
OpenAI client from backend/services/_openai_client.py instead of each
file creating its own client and hardcoding model names.

Run once from project root:
    python scripts/migrate_to_central_openai_client.py

Idempotent — safe to re-run. If a file is already migrated, no changes
are made to it.

What it does to each target file:
  1. Replaces  model="gpt-4o-mini"  →  model=MODEL_CHEAP
  2. Replaces  model="gpt-4o"       →  model=MODEL_SMART
  3. Replaces  OpenAI(api_key=...)  →  get_client()    (multiple patterns)
  4. Adds the import statement at the top if it was changed

It does NOT remove the now-unused `from openai import OpenAI` import,
because that's a one-line cleanup that's harmless and easier for you
to do by hand if you care about it.
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TARGET_FILES = [
    "backend/services/ai_forecast_service.py",
    "backend/services/ai_recruiter_service.py",
    "backend/services/ai_salary_engine.py",
    "backend/services/blind_spot_service.py",
    "backend/services/career_time_machine_service.py",
    "backend/services/cover_letter_service.py",
    "backend/services/interview_service.py",
    "backend/services/job_match_engine.py",
    "backend/services/market_intelligence_service.py",
    "backend/services/offer_predictor_service.py",
    "backend/services/resume_ai_service.py",
    "backend/routes/interview_routes.py",
]

IMPORT_LINE = "from backend.services._openai_client import get_client, MODEL_CHEAP, MODEL_SMART"

REPLACEMENTS = [
    # Model name replacements — order matters, gpt-4o-mini before gpt-4o
    (re.compile(r'model="gpt-4o-mini"'), 'model=MODEL_CHEAP'),
    (re.compile(r"model='gpt-4o-mini'"), 'model=MODEL_CHEAP'),
    (re.compile(r'model="gpt-4o"'),      'model=MODEL_SMART'),
    (re.compile(r"model='gpt-4o'"),      'model=MODEL_SMART'),

    # OpenAI() instantiation patterns
    (re.compile(r'OpenAI\(api_key=os\.getenv\(["\']OPENAI_API_KEY["\']\)\)'), 'get_client()'),
    (re.compile(r'OpenAI\(api_key=os\.environ\.get\(["\']OPENAI_API_KEY["\']\)\)'), 'get_client()'),
    (re.compile(r'OpenAI\(api_key=current_app\.config\[["\']OPENAI_API_KEY["\']\]\)'), 'get_client()'),
    (re.compile(r'OpenAI\(api_key=Config\.OPENAI_API_KEY\)'), 'get_client()'),
    (re.compile(r'OpenAI\(api_key=api_key\)'), 'get_client()'),
    (re.compile(r'OpenAI\(api_key=key\)'), 'get_client()'),
]


def migrate_file(filepath: Path) -> dict:
    if not filepath.exists():
        return {"error": "file not found"}

    content = filepath.read_text(encoding="utf-8")
    original = content

    total_changes = 0
    for pattern, replacement in REPLACEMENTS:
        new_content, n = pattern.subn(replacement, content)
        total_changes += n
        content = new_content

    added_import = False
    if total_changes > 0 and IMPORT_LINE not in content:
        # Insert after the last 'import' or 'from' line in the first 50 lines
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines[:50]):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                insert_idx = i + 1
        lines.insert(insert_idx, IMPORT_LINE)
        content = "\n".join(lines)
        added_import = True

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return {"changes": total_changes, "added_import": added_import}

    return {"changes": 0, "added_import": False}


def main():
    print("Migrating files to centralized OpenAI client...\n")

    for relpath in TARGET_FILES:
        filepath = PROJECT_ROOT / relpath
        result = migrate_file(filepath)

        if "error" in result:
            print(f"  SKIP: {relpath} — {result['error']}")
            continue

        if result["changes"] == 0:
            print(f"  OK (no changes needed): {relpath}")
        else:
            import_note = "  + added import" if result["added_import"] else ""
            print(f"  CHANGED: {relpath} — {result['changes']} replacements{import_note}")

    print("\nDone.\n")
    print("Verify with:")
    print('   grep -rn \'"gpt-4o\' backend/ | grep -v _openai_client.py')
    print("(should print nothing — the only remaining hardcoded model strings")
    print(" should be inside _openai_client.py)")


if __name__ == "__main__":
    main()