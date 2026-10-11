"""Slice docs/DECISIONS.md into date-range files for the decisions_digest batch kind.

    python tools/batch/split_decisions.py                 # writes batches/decisions_slices/NN_<first-heading>.md
    python tools/batch/split_decisions.py --max-lines 700

Cuts only at `### ` headings (an entry never splits), keeps the `## ` section each entry belongs
to as the first line of every slice, and writes an index (slices.json) mapping slice -> line range,
so a digest can cite `DECISIONS.md:<line>`.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "docs" / "DECISIONS.md"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-lines", type=int, default=700)
    ap.add_argument("--out", default="batches/decisions_slices")
    args = ap.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.md"):
        old.unlink()

    lines = SRC.read_text(encoding="utf-8").splitlines()
    section = ""
    slices: list[tuple[int, int, str, list[str]]] = []
    cur: list[str] = []
    cur_start = 1
    cur_title = ""
    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = line
        if line.startswith("### ") and len(cur) >= args.max_lines:
            slices.append((cur_start, i - 1, cur_title, cur))
            cur, cur_start, cur_title = [], i, ""
        if line.startswith("### ") and not cur_title:
            cur_title = line[4:]
        if not cur and section and not line.startswith("## "):
            cur.append(section + "  (section; slice starts at DECISIONS.md line %d)" % i)
        cur.append(line)
    if cur:
        slices.append((cur_start, len(lines), cur_title, cur))

    index = {}
    for n, (a, b, title, body) in enumerate(slices, 1):
        slug = re.sub(r"[^A-Za-z0-9]+", "-", title)[:40].strip("-") or "head"
        name = f"{n:02d}_{slug}.md"
        (out / name).write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")
        index[name] = {"lines": [a, b], "first_heading": title}
    (out / "slices.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
    print(f"split_decisions: {len(slices)} slices from {len(lines)} lines -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
