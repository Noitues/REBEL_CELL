"""Diff-based test selection for REBEL_CELL (docs/process/01_PROCESS_OPTIMIZATION_PLAN.md).

Maps the files changed since a git ref (default: main) to the test scripts that exercise
them, then runs only those scripts (plus the always-on guards) through tools/run_tests.py.
It never replaces the full suite at a gate; it replaces the full suite between gates.

    python tools/select_tests.py                 # changes vs main, run the selected scripts
    python tools/select_tests.py --base HEAD~3   # changes in the last three commits
    python tools/select_tests.py --staged        # only what is staged (pre-commit)
    python tools/select_tests.py --list          # print the selection, run nothing
    python tools/select_tests.py --full-if-core  # changed scripts/core => fast tier instead

Selection rules (union):
  1. A changed test script selects itself.
  2. A changed script selects every test whose text names its class_name, its basename
     (without .gd), or its res:// path.
  3. A changed .tres / .tscn selects tests naming its basename, plus the content tests.
  4. Changes under scripts/core/ or scripts/state/ add the rule guards (preview == result,
     rewind, replay, rng, wheel math, raid resolver, map generator, save) and the
     integrity check. tests/test_manifest.json changes add the integrity check.
  5. Nothing matched => the fast tier (never "no tests").

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tests" / "test_manifest.json"
TEST_DIRS = [ROOT / "tests" / "unit", ROOT / "tests" / "integration"]
# Rule guards that run whenever the deterministic core or runtime state changes
# (CLAUDE.md rule 6). Substrings of test script paths.
CORE_GUARDS = [
    "test_suite_integrity",
    "test_preview",
    "test_rewind",
    "test_replay",
    "test_rng",
    "test_wheel_math",
    "test_raid_resolver",
    "test_map_generator",
    "test_save",
    "test_determinism",
]
CONTENT_GUARDS = ["test_content", "test_cards", "test_suite_integrity"]
CORE_DIRS = ("scripts/core/", "scripts/state/", "scripts/autoload/")
CONTENT_DIRS = ("content/", "scripts/data/")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False).stdout


def changed_files(base: str, staged: bool) -> list[str]:
    if staged:
        out = git("diff", "--name-only", "--cached")
    else:
        out = git("diff", "--name-only", f"{base}...HEAD") + git("diff", "--name-only") + git(
            "ls-files", "--others", "--exclude-standard"
        )
    files = sorted({line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()})
    return [f for f in files if not f.endswith(".uid")]


def class_name_of(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = re.search(r"^class_name\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.M)
    return m.group(1) if m else ""


def all_tests() -> list[Path]:
    tests: list[Path] = []
    for d in TEST_DIRS:
        tests.extend(sorted(d.rglob("test_*.gd")))
    return tests


def select(files: list[str]) -> tuple[set[str], list[str]]:
    """Return (selected test substrings, reasons)."""
    tests = all_tests()
    texts = {t: t.read_text(encoding="utf-8", errors="replace") for t in tests}
    selected: set[str] = set()
    reasons: list[str] = []

    def add(t: Path, why: str) -> None:
        key = t.stem
        if key not in selected:
            selected.add(key)
            reasons.append(f"{key}  <- {why}")

    for f in files:
        p = ROOT / f
        if f.startswith("tests/") and f.endswith(".gd") and Path(f).name.startswith("test_"):
            add(p, "changed test")
            continue
        if f == "tests/test_manifest.json":
            for t in tests:
                if "test_suite_integrity" in t.stem:
                    add(t, "manifest changed")
            continue
        needles: set[str] = set()
        stem = Path(f).stem
        if f.endswith(".gd"):
            cn = class_name_of(p)
            if cn:
                needles.add(cn)
            needles.add(stem)
            needles.add("res://" + f)
        elif f.endswith((".tres", ".tscn", ".csv", ".json", ".gdshader")):
            needles.add(stem)
        else:
            continue
        for t in tests:
            body = texts[t]
            for n in needles:
                if re.search(r"\b" + re.escape(n) + r"\b", body):
                    add(t, f"{f} ({n})")
                    break
        if f.startswith(CORE_DIRS):
            for t in tests:
                if any(g in t.stem for g in CORE_GUARDS):
                    add(t, "core guard")
        if f.startswith(CONTENT_DIRS):
            for t in tests:
                if any(g in t.stem for g in CONTENT_GUARDS):
                    add(t, "content guard")
    return selected, reasons


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="main", help="git ref the change is measured against")
    ap.add_argument("--staged", action="store_true", help="select from staged files only (pre-commit)")
    ap.add_argument("--list", action="store_true", help="print the selection and exit")
    ap.add_argument("--full-if-core", action="store_true", help="run the fast tier instead when scripts/core changed")
    ap.add_argument("--hub-ratio", type=float, default=0.5, help="when the selection exceeds this share of all scripts (a hub class changed), run the fast tier instead")
    ap.add_argument("-j", "--jobs", type=int, default=2)
    ap.add_argument("--out", default="", help="log folder for run_tests.py")
    args = ap.parse_args()

    files = changed_files(args.base, args.staged)
    if not files:
        print("select_tests: no changed files")
        return 0
    selected, reasons = select(files)
    core_touched = any(f.startswith(CORE_DIRS) for f in files)
    print(f"select_tests: {len(files)} changed files -> {len(selected)} test scripts")
    for r in reasons:
        print("  " + r)

    cmd = [sys.executable, str(ROOT / "tools" / "run_tests.py"), "-j", str(args.jobs)]
    if args.out:
        cmd += ["--out", args.out]
    hub = len(selected) > args.hub_ratio * len(all_tests())
    if not selected or hub or (args.full_if_core and core_touched):
        print("select_tests: running the fast tier" + (" (hub change: selection too wide; the full suite runs at the gate)" if hub else ""))
        cmd += ["--tier", "fast"]
    else:
        for s in sorted(selected):
            cmd += ["--select", s]
    if args.list:
        print(" ".join(cmd))
        return 0
    print("select_tests: " + " ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
