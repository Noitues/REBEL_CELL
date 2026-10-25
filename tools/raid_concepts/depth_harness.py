"""Round 6 depth harness: is a concept's raid a solved puzzle, or a decision? Runs each single-raid concept's whole plan
space on 10 seeded scenarios (content threats, random entries) and reports, per scenario and overall:
- best net (payout - full repair bill), and whether a CLEAN plan exists;
- modal-draft share: how often the same draft is best across scenarios (1.0 = one answer always wins);
- near ties: distinct drafts within NEAR of the best net (1 = an obvious answer; 2-4 = a real choice);
- fragility: share of one-piece moves away from the best plan that lose more than NEAR net (a precise puzzle).
Concepts: K (counters: G's draft against threats with visible traits), G (anchor: 3 of 5, the round-5 package), J (Switchyard: route shaping with barriers and jams),
I (Circuit: adjacency synergy, 4 of 5). H (Bastion, persistent) is measured by bastion_campaign.py.
Prototype only; seeded random.Random is fine here (not game code)."""
from __future__ import annotations

import itertools
import json
import random
import sys
from collections import Counter

sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import INSTALL, LINKS, NODE_HP, RULES, Plan, run  # noqa: E402

SALVAGE, BONUS, NEAR = 4, 6, 3
PKG = {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest", "ice_blocks": True, "no_cascade": True}
NODES = list(NODE_HP)
CELL_LINKS = [l for l in LINKS if not (l[0].startswith("C") or l[1].startswith("C"))]
THREAT_POOL = ["COLLECTOR", "AUDITOR", "ENFORCER", "COURIER", "INSPECTOR", "BAILIFF", "HAULER", "LOCKDOWN"]


def scenarios(n=10, seed=6):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        ids = rng.sample(THREAT_POOL, 3)
        out.append([(t, rng.choice(["C1", "C2"])) for t in ids])
    return out


def price(r) -> int:
    c = r.home_before - r.home_after
    for k, v in r.nodes.items():
        if k == "HOME":
            continue
        if v["outcome"] == "scuffed":
            c += v["before"] - v["after"]
        elif v["outcome"] == "down":
            c += INSTALL[k] // 2
        elif v["outcome"] == "taken":
            c += INSTALL[k]
    return c


def net(r) -> int:
    kills = len({t for ev in r.steps for t, _ in ev["kills"]})
    return SALVAGE * kills + (BONUS if r.clean else 0) - price(r)


# ---- plan spaces: yield (draft, plan_key, Plan) ----
def space_g(rules):
    pool = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
    for pick in itertools.combinations(pool, 3):
        for place in itertools.product(NODES, repeat=3):
            a = {}
            for x, n in zip(pick, place):
                a.setdefault(n, []).append(x)
            for crew in sorted(set(place) | {"SAFE"}):
                yield pick, (place, crew), Plan(a, crew, dict(rules))


def space_j(rules):
    pool = ["TURRET", "ICE", "DECOY", "RAILGUN", "BARRIER", "BARRIER2"]
    for pick in itertools.combinations(pool, 3):
        slots = [CELL_LINKS if p.startswith("BARRIER") else NODES for p in pick]
        for place in itertools.product(*slots):
            bars = [pl for p, pl in zip(pick, place) if p.startswith("BARRIER")]
            if len(bars) == 2 and bars[0] >= bars[1]:
                continue
            a = {}
            for x, n in zip(pick, place):
                if not x.startswith("BARRIER"):
                    a.setdefault(n, []).append(x)
            nodes_used = [pl for p, pl in zip(pick, place) if not p.startswith("BARRIER")]
            for crew in sorted(set(nodes_used) | {"SAFE"}):
                yield pick, (place, crew), Plan(a, crew, dict(rules), barriers=bars)


def space_i(rules):
    pool = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
    for pick in itertools.combinations(pool, 4):
        for place in itertools.product(NODES, repeat=4):
            a = {}
            for x, n in zip(pick, place):
                a.setdefault(n, []).append(x)
            for crew in sorted(set(place) | {"SAFE"}):
                yield pick, (place, crew), Plan(a, crew, dict(rules))


TRAITS = ["ARMORED", "PLATED", "FROSTPROOF", "BLIND"]


def with_traits(scen, seed=61):
    """Concept K: each threat carries one visible trait (or none, 1 in 5), seeded per scenario."""
    rng = random.Random(seed)
    out = []
    for sc in scen:
        out.append([(t, e, (rng.choice(TRAITS),) if rng.random() < 0.8 else ()) for t, e in sc])
    return out


CONCEPTS = {
    "G": (space_g, dict(RULES, **PKG)),
    "K": (space_g, dict(RULES, **PKG)),
    "J": (space_j, dict(RULES, **PKG, jam=True)),
    "I": (space_i, dict(RULES, **PKG, circuit=True)),
}


def measure(key: str, scen):
    space, rules = CONCEPTS[key]
    if key == "K":
        scen = with_traits(scen)
    per = []
    for sc in scen:
        best_by_draft: dict = {}
        all_plans = {}
        any_clean = False
        for pick, pk, plan in space(rules):
            r = run(plan, threats=list(sc))
            n = net(r)
            any_clean |= r.clean
            all_plans[(pick, pk)] = n
            if pick not in best_by_draft or n > best_by_draft[pick][0]:
                best_by_draft[pick] = (n, pk)
        ranked = sorted(best_by_draft.items(), key=lambda kv: (-kv[1][0], kv[0]))
        best_pick, (best_n, best_pk) = ranked[0]
        near = sum(1 for _, (n, _) in ranked if n >= best_n - NEAR)
        # fragility: move one piece of the best plan to every other slot (same draft, same crew)
        place, crew = best_pk
        moves = drops = 0
        for i in range(len(place)):
            for (pick, (pl2, cr2)), n2 in all_plans.items():
                if pick != best_pick or cr2 != crew:
                    continue
                diff = [j for j in range(len(place)) if pl2[j] != place[j]]
                if diff == [i]:
                    moves += 1
                    drops += n2 < best_n - NEAR
        per.append({"threats": sc, "best_net": best_n, "best_draft": "+".join(best_pick), "best_plan": [list(place), crew],
                    "near_ties": near, "fragility": round(drops / max(1, moves), 2), "clean_exists": any_clean,
                    "plans": len(all_plans)})
        print(key, per[-1], flush=True)
    modal = Counter(p["best_draft"] for p in per).most_common(1)[0]
    summary = {"modal_draft": modal[0], "modal_share": modal[1] / len(per),
               "mean_near_ties": round(sum(p["near_ties"] for p in per) / len(per), 2),
               "mean_fragility": round(sum(p["fragility"] for p in per) / len(per), 2),
               "clean_exists_share": sum(p["clean_exists"] for p in per) / len(per),
               "mean_best_net": round(sum(p["best_net"] for p in per) / len(per), 1)}
    print(key, "SUMMARY", summary, flush=True)
    return {"summary": summary, "per_scenario": per}


if __name__ == "__main__":
    keys = sys.argv[1:] or list(CONCEPTS)
    scen = scenarios()
    out = {}
    for k in keys:
        out[k] = measure(k, scen)
        json.dump(out, open(rf"D:/rc_tmp/raid_design_lab/depth_{'_'.join(keys)}.json", "w"), indent=1)
