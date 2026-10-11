"""Consolidate a lint_report / text_audit batch's RC_NOTES into one digest, violations only.

    python tools/batch/lint_digest.py batches/lint_ui_out            # writes LINT_DIGEST.md there
    python tools/batch/lint_digest.py batches/lint_ui_out --min 2    # files with at least 2 findings

Drops lines the model wrote about things that pass ("-> none", "ok", "no action", "confirm",
"acceptable", "allowed", "fine"), counts the rest by rule id and by file, and lists them grouped
by rule so an auditor or a fix agent reads one file instead of 280.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

LINE_RE = re.compile(r"^- (?P<path>[^\s:]+):(?P<line>\d+)\s+(?P<rule>[RS]\d)\s+(?P<text>.*)$")
NOISE_RE = re.compile(
    r"(->\s*(none|ok|no action|no change|nothing|confirm|verify|acceptable|allowed|fine|keep)\b|"
    r"\b(none needed|no action|is fine|is allowed|are allowed|acceptable|not a violation|no violation|no finding|"
    r"not violated|not state mutation|not a state write|read-only view|passes|present; ok|: ok|; ok|\bok\b)\b|"
    r"\b(but |please |then )?(verify|confirm|check)\b[^-]*$)",
    re.I,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_dir")
    ap.add_argument("--min", type=int, default=1)
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    by_rule: dict[str, list[str]] = defaultdict(list)
    by_file: Counter = Counter()
    dropped = 0
    files = 0
    for notes in sorted(out_dir.glob("*.notes.md")):
        files += 1
        for raw in notes.read_text(encoding="utf-8").splitlines():
            m = LINE_RE.match(raw.strip())
            if not m:
                continue
            if NOISE_RE.search(m.group("text")):
                dropped += 1
                continue
            by_rule[m.group("rule")].append(f"- `{m.group('path')}:{m.group('line')}` {m.group('text')}")
            by_file[m.group("path")] += 1
    total = sum(len(v) for v in by_rule.values())
    names = {"R1": "core purity", "R2": "randomness", "R3": "resource mutation", "R4": "views changing state", "R5": "magic numbers", "R7": "nondeterministic tie-breaks", "S1": "missing static types", "S2": "naming", "S3": "missing ## docs", "S4": "player-facing literals"}
    lines = [f"# Lint digest: {out_dir.name}", "", f"- files reported: {files}; findings kept: {total}; pass/noise lines dropped: {dropped}", "", "## By rule", ""]
    for rule in sorted(by_rule, key=lambda r: -len(by_rule[r])):
        lines.append(f"- {rule} {names.get(rule, '')}: {len(by_rule[rule])}")
    lines += ["", "## Files with the most findings", ""]
    for path, n in by_file.most_common(25):
        if n >= args.min:
            lines.append(f"- {n:3d}  `{path}`")
    for rule in sorted(by_rule, key=lambda r: -len(by_rule[r])):
        lines += ["", f"## {rule} {names.get(rule, '')} ({len(by_rule[rule])})", ""] + by_rule[rule]
    (out_dir / "LINT_DIGEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"lint_digest: {total} findings from {files} files ({dropped} noise lines dropped) -> {out_dir / 'LINT_DIGEST.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
