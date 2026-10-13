"""Roll up a batch of Claude playtest reports (docs/process/05_CLAUDE_PLAYTESTER.md).

    python tools/playtest/aggregate.py --batch PB-001

Reads the SUMMARY block (section 8) of every docs/playtest/claude/<batch>/<handle>.md and writes
docs/playtest/claude/<batch>/_BATCH.md: one row per tester, averages, outcome counts, the cards
most often called overpowered / weak, and every tester's top frustration and top change, so the
designer reads one page before opening individual reports. Reports without a SUMMARY block are
listed as missing.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS = ROOT / "docs" / "playtest" / "claude"
BLOCK = re.compile(r"```\s*\nSUMMARY\s*\n(.*?)```", re.S)


def parse(path: Path) -> dict | None:
    m = BLOCK.search(path.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def num(v: str) -> float | None:
    m = re.match(r"-?\d+(\.\d+)?", v or "")
    return float(m.group(0)) if m else None


def names(v: str) -> list[str]:
    return [] if not v or v.lower().startswith("none") or v.startswith("<") else [x.strip() for x in v.split(",") if x.strip()]


FIGHT = re.compile(r"FIGHT (won|lost) turns=(\d+) hp_lost=(\d+) perfects=(\d+)", re.I)
SESSIONS = ROOT / ".playtest_sessions"


def skill_section(batch: str, rows: list) -> list[str]:
    """How well each tester actually played, from the FIGHT lines in its journal (harness testers)."""
    manifest = SESSIONS / batch / "batch.json"
    tiers = {}
    if manifest.exists():
        tiers = {t["handle"]: t.get("tier", "?") for t in json.loads(manifest.read_text(encoding="utf-8"))["testers"]}
    out = ["## Combat skill (from the testers' FIGHT lines)", "",
           "Difficulty signals only count from testers who play well (designer: Perfects on high slices take almost no damage).", "",
           "| Tester | Tier | Fights | Won | Avg turns | Avg HP lost | Perfects / turn |", "|---|---|---|---|---|---|---|"]
    any_row = False
    for f, s in rows:
        h = s.get("handle", f.stem)
        j = SESSIONS / batch / h / "journal.md"
        if not j.exists():
            continue
        fights = [(m.group(1).lower(), int(m.group(2)), int(m.group(3)), int(m.group(4)))
                  for m in FIGHT.finditer(j.read_text(encoding="utf-8"))]
        if not fights:
            out.append("| %s | %s | 0 | — | — | — | — |" % (h, tiers.get(h, "?")))
            continue
        any_row = True
        turns = sum(x[1] for x in fights)
        out.append("| %s | %s | %d | %d | %.1f | %.1f | %.2f |" % (
            h, tiers.get(h, "?"), len(fights), sum(1 for x in fights if x[0] == "won"), turns / len(fights),
            sum(x[2] for x in fights) / len(fights), sum(x[3] for x in fights) / max(1, turns)))
    if not any_row:
        out.append("")
        out.append("(No FIGHT lines yet: testers from before 2026-10-12 evening did not log them.)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", required=True)
    a = ap.parse_args()
    folder = REPORTS / a.batch
    files = sorted(p for p in folder.glob("*.md") if not p.name.startswith("_"))
    if not files:
        sys.exit("aggregate: no reports in %s" % folder)
    rows, missing = [], []
    for f in files:
        s = parse(f)
        (rows.append((f, s)) if s else missing.append(f.name))

    def avg(key: str) -> str:
        vals = [n for _, s in rows if (n := num(s.get(key, ""))) is not None]
        return "%.1f (n=%d)" % (sum(vals) / len(vals), len(vals)) if vals else "—"

    outcomes = Counter(s.get("outcome", "?").split()[0] for _, s in rows)
    op = Counter(n for _, s in rows for n in names(s.get("op_picks", "")))
    weak = Counter(n for _, s in rows for n in names(s.get("weak_picks", "")))
    lengths = Counter(s.get("netrun_length", "?") for _, s in rows)
    camp = Counter(s.get("campaign_length", "?") for _, s in rows)

    lines = ["# Claude playtest batch %s" % a.batch, "",
             "%d report(s)%s." % (len(rows), ("; missing a SUMMARY: " + ", ".join(missing)) if missing else ""), "",
             "| Tester | Persona | Focus | Outcome | Netruns | Deaths | Raids | Min | Enjoy | RNG | Bugs |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for f, s in rows:
        lines.append("| [%s](%s) | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            s.get("handle", f.stem), f.name, s.get("persona", ""), s.get("focus", ""), s.get("outcome", ""),
            s.get("netruns_completed", ""), s.get("operative_deaths", ""), s.get("raids_survived", ""),
            s.get("playtime_min", ""), s.get("enjoyment", ""), s.get("rng_fairness", ""), s.get("bugs", "")))
    lines += ["",
              "**Averages:** enjoyment %s · RNG fairness %s (1 fair – 5 cheated) · playtime %s min · bugs %s" % (
                  avg("enjoyment"), avg("rng_fairness"), avg("playtime_min"), avg("bugs")),
              "**Outcomes:** " + ", ".join("%s %d" % kv for kv in outcomes.most_common()),
              "**Netrun length:** " + ", ".join("%s %d" % kv for kv in lengths.most_common()),
              "**Campaign length:** " + ", ".join("%s %d" % kv for kv in camp.most_common()),
              "**Called overpowered:** " + (", ".join("%s ×%d" % kv for kv in op.most_common()) or "none"),
              "**Called weak:** " + (", ".join("%s ×%d" % kv for kv in weak.most_common()) or "none"),
              ""]
    lines += skill_section(a.batch, rows)
    lines += ["", "## Top frustrations", ""]
    lines += ["- **%s** (%s): %s" % (s.get("handle", f.stem), s.get("persona", ""), s.get("top_frustration", "")) for f, s in rows]
    lines += ["", "## One change each", ""]
    lines += ["- **%s** (%s): %s" % (s.get("handle", f.stem), s.get("persona", ""), s.get("top_change", "")) for f, s in rows]
    out = folder / "_BATCH.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
