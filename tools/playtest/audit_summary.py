"""Summarise replay audits (tools/agent/replay_audit.gd output): how well testers played each turn.

    python tools/playtest/audit_summary.py .playtest_sessions/_audit/*.jsonl

Per file (one tester): turns, how often a Perfect was reachable, how often the tester landed one, how
often the best plan does, and damage dealt / taken per turn for the tester vs the best plan and vs
doing nothing. The gap between "reachable" and "landed" is the Perfect-legibility signal.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def summarize(path: Path) -> dict:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    n = len(rows) or 1
    avail = sum(r["perfect_available"] for r in rows)
    landed = sum(r["tester"]["own_perfect"] for r in rows)
    landed_when = sum(r["tester"]["own_perfect"] for r in rows if r["perfect_available"])
    passive = sum(r["no_action"]["own_perfect"] for r in rows)
    acted = sum(1 for r in rows if r["tester_actions"] > 0)
    return {"tester": rows[0]["tag"] if rows else path.stem, "turns": len(rows),
            "perfect_reachable_pct": round(100 * avail / n), "tester_perfect_pct": round(100 * landed / n),
            "tester_perfect_when_reachable_pct": round(100 * landed_when / max(1, avail)),
            "perfect_with_no_action_pct": round(100 * passive / n), "turns_with_any_action_pct": round(100 * acted / n),
            "dealt_tester": round(sum(r["tester"]["dealt"] for r in rows) / n, 1),
            "dealt_best": round(sum(r["best"]["dealt"] for r in rows) / n, 1),
            "taken_tester": round(sum(r["tester"]["taken"] for r in rows) / n, 1),
            "taken_best": round(sum(r["best"]["taken"] for r in rows) / n, 1),
            "taken_no_action": round(sum(r["no_action"]["taken"] for r in rows) / n, 1)}


def table(paths: list[Path]) -> str:
    rows = [summarize(p) for p in paths if p.exists() and p.stat().st_size > 0]
    if not rows:
        return ""
    keys = list(rows[0].keys())
    return "\n".join(["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
                     + ["| " + " | ".join(str(r[k]) for k in keys) + " |" for r in rows])


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rows = [summarize(Path(p)) for p in sys.argv[1:]]
    keys = list(rows[0].keys()) if rows else []
    print("| " + " | ".join(keys) + " |")
    print("|" + "---|" * len(keys))
    for r in rows:
        print("| " + " | ".join(str(r[k]) for k in keys) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
