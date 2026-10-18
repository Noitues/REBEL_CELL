#!/usr/bin/env python3
"""N19: aggregation of the per-phase sim metrics (schema: docs/handoff/N19_METRICS_SCHEMA.md).

Pure functions over result records; records without a `metrics` key (pre-N19 files) are skipped, never an error.
CLI (used by the schema test):  python tools/balance/phase_metrics.py aggregate FILE.json
"""
import json
import math
import sys

TARGET_MIN, TARGET_MAX = 3, 4      # turns per phase the class targets want (inclusive)
HEAL_LIMIT = 1                     # heal turns per phase, at most
BOSS_WIN_TARGET, BOSS_WIN_TOL = 0.5, 0.15   # boss at ICE 0: ~50 % win (designer 2026-10-18)


def p90(values):
    """Nearest-rank 90th percentile; None for an empty list."""
    v = sorted(values)
    if not v:
        return None
    return v[max(0, math.ceil(0.9 * len(v)) - 1)]


def mean(values):
    return sum(values) / len(values) if values else None


def in_target(turns):
    """True when a phase took 3-4 turns."""
    return TARGET_MIN <= turns <= TARGET_MAX


def phase_rows(records):
    """Every phase dict of every record that has metrics."""
    return [p for r in records if r.get("metrics") for p in r["metrics"].get("phases", [])]


def aggregate(records):
    """Metrics for one group's records, or None when no record carries them."""
    with_m = [r for r in records if r.get("metrics")]
    if not with_m:
        return None
    phases = phase_rows(with_m)
    fight_turns = [sum(p["turns"] for p in r["metrics"]["phases"]) for r in with_m]
    wins = [r.get("scalars", {}).get("won", 0) for r in with_m]
    complete = [p for p in phases if not p.get("incomplete")]
    pt = [p["turns"] for p in complete]
    tm = {"own": 0, "enemy": 0, "both": 0, "none": 0}
    for r in with_m:
        for k, v in (r["metrics"].get("turn_manipulation") or {}).items():
            tm[k] = tm.get(k, 0) + v
    turns_all = sum(tm.values())
    heal = [p["heal_turns"] for p in phases]
    return {
        "fights": len(with_m),
        "win_rate": mean(wins),
        "turns_mean": mean(fight_turns),
        "turns_p90": p90(fight_turns),
        "phase_turns_mean": mean(pt),
        "in_target": (sum(1 for t in pt if in_target(t)) / len(pt)) if pt else None,
        "phases_over_4": sum(1 for t in pt if t > TARGET_MAX),
        "heal_turns_per_phase_max": max(heal) if heal else 0,
        "heal_over_limit": sum(1 for h in heal if h > HEAL_LIMIT),
        "parked_mean": mean([sum(p["parked"] for p in r["metrics"]["phases"]) for r in with_m]),
        "intake_mean": mean([sum(p["intake"] for p in r["metrics"]["phases"]) for r in with_m]),
        "resistance_absorbed_mean": mean([sum(p["resistance_absorbed"] for p in r["metrics"]["phases"]) for r in with_m]),
        "enrage_step_max": max(r["metrics"].get("enrage_step", 0) for r in with_m),
        "turns_with_both_share": (tm["both"] / turns_all) if turns_all else None,
    }


def warnings(group, agg, boss=False):
    """Human-readable pass-criteria warnings for one group's aggregate (never failures)."""
    out = []
    if not agg:
        return out
    if agg["heal_over_limit"]:
        out.append("%s: %d phase(s) with more than %d heal turn" % (group, agg["heal_over_limit"], HEAL_LIMIT))
    if boss:
        if group.startswith("boss@ice0") and agg["win_rate"] is not None and abs(agg["win_rate"] - BOSS_WIN_TARGET) > BOSS_WIN_TOL:
            out.append("%s: win rate %.0f %% is outside ~50 %%" % (group, 100 * agg["win_rate"]))
        if agg["phases_over_4"]:
            out.append("%s: %d phase(s) over 4 turns (boss: warning only)" % (group, agg["phases_over_4"]))
    return out


COLUMNS = [("in_target", "in target (3-4)", 2), ("phase_turns_mean", "turns/phase", 2), ("heal_turns_per_phase_max", "heal turns/phase max", 0),
           ("parked_mean", "parked", 1), ("intake_mean", "intake", 1), ("resistance_absorbed_mean", "resist absorbed", 1),
           ("enrage_step_max", "enrage step", 0), ("turns_with_both_share", "both-wheel turns", 2)]


def fmt(x, nd):
    return "-" if x is None else ("%." + str(nd) + "f") % x


def render_table(groups):
    """Markdown table: one row per group, one column per metric. `groups` = {name: aggregate or None}."""
    head = ["group", "fights"] + [c[1] for c in COLUMNS]
    lines = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for g in sorted(groups):
        a = groups[g]
        if not a:
            lines.append("| " + " | ".join([g, "-"] + ["-"] * len(COLUMNS)) + " |")
        else:
            lines.append("| " + " | ".join([g, str(a["fights"])] + [fmt(a[k], nd) for k, _, nd in COLUMNS]) + " |")
    return "\n".join(lines) + "\n"


def by_group(records):
    acc = {}
    for r in records:
        acc.setdefault(r["group"], []).append(r)
    return {g: aggregate(rs) for g, rs in acc.items()}


def main(argv):
    if len(argv) == 3 and argv[1] == "aggregate":
        data = json.load(open(argv[2], encoding="utf-8"))
        print(json.dumps(aggregate(data["records"] if isinstance(data, dict) else data), sort_keys=True))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
