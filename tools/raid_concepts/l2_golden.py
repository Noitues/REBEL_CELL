"""Parity golden for the L2 sweep lab (tools/raid_lab_m10, round 2): sweep_l2.py rules.
For 6 seeded legs: the leg (home, asset values, per raid beam 1 / extra / 3 candidates / hunter own line), the planned
and greedy lines step by step (state before, allocation, spoof, touches, state after the raid, repairs, state after the
between-raid step), and 200 seeded random single-raid resolutions (state, allocation, candidate, spoof -> touches,
after). Writes tools/raid_lab_m10/data/l2_golden.json.
    python tools/raid_concepts/l2_golden.py"""
from __future__ import annotations

import json
import random
from pathlib import Path

import sweep_l2 as L

OUT = Path(__file__).resolve().parents[1] / "raid_lab_m10" / "data" / "l2_golden.json"
LEGS = (0, 3, 5, 8, 11, 14)


def c2(c):
    return [c[0], c[1]]


def enc_state(s: L.State):
    return {"heat": s.heat, "bank": s.bank, "home_hp": s.home_hp, "status": [[*c2(c), v] for c, v in s.status]}


def enc_alloc(a):
    g, dk, dc = a
    return {"ghost": [c2(c) for c in g], "dark": [c2(c) for c in dk], "decoys": [c2(c) for c in dc]}


def enc_leg(leg: L.Leg):
    return {"home": c2(leg.home), "values": [[*c2(c), v] for c, v in leg.values],
            "raids": [{"b1": [c2(c) for c in r.b1], "extra": [c2(c) for c in r.extra], "extra2": [c2(c) for c in r.extra2],
                       "cands": [[c2(c) for c in ln] for ln in r.cands], "own3": [c2(c) for c in r.own3]}
                      for r in leg.raids]}


def replay(leg, log):
    st = L.initial(leg)
    steps = []
    for x in log:
        i, a, sp = x["raid"], x["alloc"], x["spoof"]
        raid = leg.raids[i]
        ns, touched = L.resolve(leg, raid, st, raid.cands[0], a, sp)
        rs = tuple(x.get("repairs", ()))
        if "repairs" not in x and i < L.RAIDS - 1 and ns.home_hp > 0:
            rs = max(L.repair_sets(leg, ns), key=lambda r: L.score(leg, L.between(leg, ns, a[1], r)))
        after = L.between(leg, ns, a[1], rs) if i < L.RAIDS - 1 and ns.home_hp > 0 else ns
        steps.append({"raid": i, "before": enc_state(st), "alloc": enc_alloc(a), "spoof": c2(sp) if sp else None,
                      "touched": [[*c2(c), k] for c, k in touched], "after_raid": enc_state(ns),
                      "repairs": [c2(c) for c in rs], "after": enc_state(after), "score_after": L.score(leg, after)})
        st = after
        if ns.home_hp <= 0:
            break
    return steps


def randoms(n=200):
    rng = random.Random(77)
    out = []
    for _ in range(n):
        seed = rng.choice(LEGS)
        leg = L.make_leg(seed)
        i = rng.randrange(L.RAIDS)
        st = L.initial(leg)
        status = {c: rng.choice(("OK", "OK", "DOWN", "TAKEN")) for c, _ in leg.values}
        st = L.State(heat=rng.choice((48, 60, 70, 74, 75, 80, 90)), bank=rng.randrange(0, 20),
                     home_hp=rng.randrange(1, L.HOME_HP + 1), status=tuple(sorted(status.items())))
        allocs = list(L.allocations(leg, st))
        a = rng.choice(allocs)
        k = rng.randrange(L.CANDIDATES)
        b2 = leg.raids[i].cands[k]
        sp = rng.choice([None] + list(b2))
        ns, touched = L.resolve(leg, leg.raids[i], st, b2, a, sp)
        out.append({"leg": seed, "raid": i, "before": enc_state(st), "alloc": enc_alloc(a), "candidate": k,
                    "spoof": c2(sp) if sp else None, "touched": [[*c2(c), kk] for c, kk in touched],
                    "after_raid": enc_state(ns), "score": L.score(leg, ns)})
    return out


if __name__ == "__main__":
    cfg = {k: getattr(L, k) for k in ("W", "H", "ASSETS", "CANDIDATES", "HOME_HP", "EXTRA_AT", "MAX_DARK", "STRONG_AT", "START_HEAT", "RUN_HEAT",
                                      "GHOST_HEAT", "DECOY_COST", "EVADE_HEAT", "START_BANK", "HOME_LOSS_COST", "BREACH", "RAIDS")}
    legs = []
    for s in LEGS:
        leg = L.make_leg(s)
        _, glog = L.greedy_leg(leg)
        _, plog = L.planned_leg(leg)
        legs.append({"seed": s, "leg": enc_leg(leg), "planned": replay(leg, plog), "greedy": replay(leg, glog)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"config": cfg, "legs": legs, "random_raids": randoms()}, indent=1), encoding="utf-8")
    print("wrote", OUT)
