"""Move finished months of docs/DECISIONS.md "Implementation decisions" into docs/decisions/<YYYY-MM>.md.

    python tools/archive_decisions.py            # archive every month before the current one
    python tools/archive_decisions.py --dry-run

Keeps in DECISIONS.md: the header, "Locked design decisions", the current month's entries, "Open
questions for the designer" (a test reads that section) and everything after it. An archive file
gets the moved `### ` entries verbatim, newest first, under a one-line header. An "## Archives"
index at the top of "Implementation decisions" links every archive. Nothing is deleted: a ruling
is found with `grep -rn "<topic>" docs/DECISIONS.md docs/decisions/`.

Entries are moved whole, cut only at `### ` headings; an entry whose heading carries no
`YYYY-MM-DD` date is dated by the dated entry above it (the section is newest first).

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "DECISIONS.md"
OUT = ROOT / "docs" / "decisions"
DATE_RE = re.compile(r"^### (\d{4}-\d{2})-\d{2}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep-month", default=dt.date.today().strftime("%Y-%m"), help="month kept in DECISIONS.md (default: this month)")
    args = ap.parse_args()

    lines = SRC.read_text(encoding="utf-8").splitlines()
    try:
        impl = next(i for i, l in enumerate(lines) if l.startswith("## Implementation decisions"))
        open_q = next(i for i, l in enumerate(lines) if l.startswith("## Open questions for the designer"))
    except StopIteration:
        print("archive_decisions: sections not found")
        return 2

    # Split the implementation section into entries at ### headings.
    body = lines[impl + 1:open_q]
    entries: list[list[str]] = []
    cur: list[str] = []
    for l in body:
        if l.startswith("### ") and cur:
            entries.append(cur)
            cur = []
        cur.append(l)
    if cur:
        entries.append(cur)
    preamble: list[str] = []
    if entries and not entries[0][0].startswith("### "):
        preamble = entries.pop(0)
    preamble = [l for l in preamble if not l.startswith("## Archives") and not l.startswith("- Archive ")]

    month = None
    keep: list[list[str]] = []
    moved: dict[str, list[list[str]]] = {}
    for e in entries:
        m = DATE_RE.match(e[0])
        if m:
            month = m.group(1)
        if month is None or month >= args.keep_month:
            keep.append(e)
        else:
            moved.setdefault(month, []).append(e)

    if not moved:
        print("archive_decisions: nothing older than", args.keep_month)
        return 0
    for mth, es in moved.items():
        print(f"archive_decisions: {mth}: {len(es)} entries, {sum(len(x) for x in es)} lines -> docs/decisions/{mth}.md")
    if args.dry_run:
        return 0

    OUT.mkdir(exist_ok=True)
    for mth, es in moved.items():
        target = OUT / f"{mth}.md"
        existing = target.read_text(encoding="utf-8").splitlines() if target.exists() else []
        header = [f"# Decision log archive — {mth}", "", f"Moved from `docs/DECISIONS.md` \"Implementation decisions\" (newest first; entries verbatim). Never delete; mark superseded. Search all rulings with `grep -rn \"<topic>\" docs/DECISIONS.md docs/decisions/`.", ""]
        old_entries = existing[len(header):] if existing[:1] == header[:1] else existing
        new_text = header + [l for e in es for l in e] + ([""] + old_entries if old_entries else [])
        target.write_text("\n".join(new_text).rstrip("\n") + "\n", encoding="utf-8", newline="\n")

    archives = sorted(p.stem for p in OUT.glob("*.md"))
    index = ["## Archives", "Finished months live in `docs/decisions/` (moved verbatim by `tools/archive_decisions.py`; grep both places):"] + [f"- Archive {a}: `docs/decisions/{a}.md`" for a in archives] + [""]
    new_lines = lines[:impl + 1] + preamble + index + [l for e in keep for l in e] + lines[open_q:]
    SRC.write_text("\n".join(new_lines).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
    print(f"archive_decisions: DECISIONS.md {len(lines)} -> {len(new_lines)} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
