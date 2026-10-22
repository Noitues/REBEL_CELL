"""Round 6: trade-off depth. If node losses are NOT folded into one net (each node feeds a different part of the run:
VAULT = Schematics income, RELAY = netrun reach, SAFE = the crew, FW = home's gun, PROXY = a corp-side foothold),
how many genuinely different plans are Pareto-optimal? A plan's outcome vector: home loss, per node (0 holds,
1 scuffed, 2 down, 3 taken), kills. A plan is dominated if another is no worse on every entry and better on one.
Reports, per scenario, the number of distinct "protected sets" (nodes that hold) on the front: 1 = one right answer;
3+ = a real "what do you give up" choice. Uses G's plan space (3 of 5) on depth_harness's 10 scenarios."""
from __future__ import annotations

import json
import sys

sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import run  # noqa: E402
from depth_harness import CONCEPTS, scenarios, with_traits  # noqa: E402

RANK = {"holds": 0, "scuffed": 0, "down": 2, "taken": 3, "breached": 3}   # scuffs go into one patch number
KEYS = ["FW", "VAULT", "SAFE", "RELAY", "PROXY"]


def vec(r):
    kills = len({t for ev in r.steps for t, _ in ev["kills"]})
    patch = sum(v["before"] - v["after"] for k, v in r.nodes.items() if v["outcome"] == "scuffed" and k != "HOME")
    return tuple([r.home_before - r.home_after] + [RANK[r.nodes[k]["outcome"]] for k in KEYS] + [-kills, patch])


def front(vs):
    vs = sorted(set(vs))
    out = []
    for v in vs:
        if any(all(a <= b for a, b in zip(w, v)) and w != v for w in vs):
            continue
        out.append(v)
    return out


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "G"
    space, rules = CONCEPTS[key]
    scen = scenarios() if key != "K" else with_traits(scenarios())
    res = []
    for sc in scen:
        vs = {}
        for pick, pk, plan in space(rules):
            r = run(plan, threats=list(sc))
            v = vec(r)
            if r.breached:
                continue
            vs.setdefault(v, (pick, pk))
        f = [v for v in front(list(vs)) if v[0] == 0]      # home untouched only
        protected = {tuple(k for k, s in zip(KEYS, v[1:6]) if s <= 1) for v in f}
        lost_sets = {tuple(k for k, s in zip(KEYS, v[1:6]) if s >= 2) for v in f}
        res.append({"threats": sc, "front": len(f), "protected_sets": len(protected), "lost_sets": sorted(lost_sets),
                    "examples": [[list(v), "+".join(vs[v][0])] for v in f[:6]]})
        print(key, len(f), len(protected), sorted(lost_sets), flush=True)
    summ = {"mean_front": sum(r["front"] for r in res) / len(res),
            "mean_protected_sets": sum(r["protected_sets"] for r in res) / len(res),
            "share_with_3plus": sum(r["protected_sets"] >= 3 for r in res) / len(res)}
    print(key, "SUMMARY", summ, flush=True)
    json.dump({"summary": summ, "per": res}, open(rf"D:/rc_tmp/raid_design_lab/pareto_{key}.json", "w"), indent=1)
