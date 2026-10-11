"""Minimal context slices for sub-agents and batch requests (docs/process/02_MULTI_AGENT_BATCH_ARCHITECTURE.md).

Prints only what another agent needs to work on a file without reading the tree:
signatures (class_name, extends, signals, consts, exports, vars at class level, func
lines with their ## doc comment), optionally the git diff, optionally the full text of
the named files. Everything else stays out of the context.

    python tools/batch/context_slice.py scripts/core/wheel_math.gd                # signatures
    python tools/batch/context_slice.py --diff main scripts/core/wheel_math.gd    # + its diff vs main
    python tools/batch/context_slice.py --full scripts/core/wheel_math.gd         # the whole file
    python tools/batch/context_slice.py --deps scripts/ui/combat/hud.gd           # + signatures of the
                                                                                  #   class_names it references
    python tools/batch/context_slice.py --json ...                                # machine-readable

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SIG_RE = re.compile(
    r"^(class_name\s+\S+.*|extends\s+\S+.*|signal\s+.*|const\s+.*|@export.*|enum\s+.*|"
    r"(static\s+)?func\s+.*|(static\s+)?var\s+[A-Za-z_][A-Za-z0-9_]*\s*(:[^=]*)?(=.*)?)$"
)


def signatures(path: Path) -> list[str]:
    out: list[str] = []
    doc: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        return [f"# unreadable: {e}"]
    for ln in lines:
        s = ln.rstrip()
        if s.startswith("##"):
            doc.append(s)
            continue
        if s and not s.startswith((" ", "\t")) and SIG_RE.match(s):
            out.extend(doc)
            out.append(s.rstrip(":") if s.startswith(("func", "static func")) else s)
        elif s.startswith(("\t", "    ")) and SIG_RE.match(s.strip()) and s.strip().startswith(("func", "static func", "signal")):
            # inner-class members: keep indented
            out.extend(doc)
            out.append(s.rstrip(":"))
        doc = []
    return out


def class_index() -> dict[str, Path]:
    idx: dict[str, Path] = {}
    for p in (ROOT / "scripts").rglob("*.gd"):
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            continue
        m = re.search(r"^class_name\s+([A-Za-z_][A-Za-z0-9_]*)", head, re.M)
        if m:
            idx[m.group(1)] = p
    return idx


def referenced_classes(path: Path, idx: dict[str, Path]) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    own = re.search(r"^class_name\s+(\S+)", text, re.M)
    names = {n for n in idx if re.search(r"\b" + re.escape(n) + r"\b", text)}
    if own:
        names.discard(own.group(1))
    return sorted(names)


def git_diff(base: str, rel: str) -> str:
    r = subprocess.run(["git", "diff", f"{base}...HEAD", "--", rel], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    wt = subprocess.run(["git", "diff", "--", rel], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    return (r.stdout + wt.stdout).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--diff", metavar="BASE", help="append the git diff vs BASE for each file")
    ap.add_argument("--full", action="store_true", help="print the full text instead of signatures")
    ap.add_argument("--deps", action="store_true", help="also print signatures of referenced class_names")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    idx = class_index() if args.deps else {}
    result: dict[str, dict] = {}
    for f in args.files:
        p = ROOT / f
        entry: dict = {"path": f}
        if args.full:
            entry["text"] = p.read_text(encoding="utf-8", errors="replace")
        else:
            entry["signatures"] = signatures(p)
        if args.diff:
            entry["diff"] = git_diff(args.diff, f)
        if args.deps:
            entry["deps"] = {n: signatures(idx[n]) for n in referenced_classes(p, idx)}
        result[f] = entry

    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
        return 0
    for f, e in result.items():
        print(f"=== {f}")
        if "text" in e:
            print(e["text"])
        else:
            print("\n".join(e["signatures"]))
        if e.get("diff"):
            print(f"--- diff vs {args.diff}")
            print(e["diff"])
        for n, sigs in e.get("deps", {}).items():
            print(f"--- dep {n} ({idx[n].relative_to(ROOT).as_posix()})")
            print("\n".join(sigs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
