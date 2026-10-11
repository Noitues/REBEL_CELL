"""Prefill a Human Playtest Task List for a User-Ready Gate (docs/process/04_PLAYTEST_PROTOCOL.md).

    python tools/playtest/make_playtest.py --since gate/PT-012 --id PT-013 --title "Group 3 city"
    python tools/playtest/make_playtest.py --since 3fa2c989 --id PT-013 --title "B5 pages" --out docs/playtest

Reads the template, fills the header (sha, date), lists the changed screens (paths under
scripts/ui, scenes, scripts/city3d grouped by folder), changed settings/config files, new content
ids, changed strings and the DECISIONS headings added since the ref. The steps table is left for
the orchestrator to write: the tool cannot know what to look for.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE = ROOT / "docs" / "process" / "templates" / "PLAYTEST.md"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False).stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", required=True, help="tag or sha of the previous gate")
    ap.add_argument("--id", required=True, help="PT-<nnn>")
    ap.add_argument("--title", required=True)
    ap.add_argument("--out", default="docs/playtest")
    args = ap.parse_args()

    sha = git("rev-parse", "--short", "HEAD").strip()
    files = [f for f in git("diff", "--name-only", f"{args.since}..HEAD").splitlines() if f and not f.endswith(".uid")]
    groups: dict[str, list[str]] = defaultdict(list)
    for f in files:
        parts = f.split("/")
        if f.startswith(("scripts/ui/", "scenes/", "scripts/city3d/")):
            groups["/".join(parts[:3]) if len(parts) > 3 else "/".join(parts[:2])].append(f)
        elif f.startswith("content/config/"):
            groups["settings / config"].append(f)
        elif f.startswith("content/"):
            groups["content"].append(f)
        elif f.endswith("strings.csv"):
            groups["text"].append(f)
    decisions = re.findall(r"^\+### (.+)$", git("diff", f"{args.since}..HEAD", "--", "docs/DECISIONS.md"), re.M)

    scope = []
    for g in sorted(groups):
        scope.append(f"- {g}: <what changed, user-visible> ({len(groups[g])} files: " + ", ".join(Path(x).name for x in groups[g][:4]) + (", ..." if len(groups[g]) > 4 else "") + ")")
    if decisions:
        scope.append("- Rulings since the last gate: " + "; ".join(decisions[:8]) + (" ..." if len(decisions) > 8 else ""))
    if not scope:
        scope.append("- <nothing user-visible changed since the ref; check --since>")

    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("PT-<nnn>", args.id).replace("<title>", args.title).replace("<sha>", sha)
    text = text.replace("<date>", dt.date.today().isoformat()).replace("gate/<tag>", f"since {args.since}")
    text = re.sub(r"- <screen or system>: <one line, user-visible> \(<ART-n / H-n / DECISIONS anchor>\)\n- \.\.\.", "\n".join(scope), text)
    settings = groups.get("settings / config", [])
    text = text.replace("Settings touched: <text scale / pad / reduce effects / high contrast / skin | none>", "Settings touched: " + (", ".join(Path(s).stem for s in settings) if settings else "none"))

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")
    out = out_dir / f"{args.id}_{slug}.md"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"make_playtest: {out} ({len(files)} changed files, {len(groups)} groups, {len(decisions)} rulings); now write the steps and `git tag gate/{args.id}` at the gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
