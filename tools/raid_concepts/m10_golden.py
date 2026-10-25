"""Parity golden for the M10 sweep lab (tools/raid_lab_m10): ghost2.py rules with scarce levers, 12 seeded networks.
Per network: assets, beam 1, the three sealed candidates, the hunter's own line, and for a set of allocations
(the best_both plan, the best-sealed plan, "ghost the biggest", and no levers) the found list and value per candidate,
with no spoof and with every spoof (beam index, node). Writes tools/raid_lab_m10/data/m10_golden.json.
    python tools/raid_concepts/m10_golden.py"""
from __future__ import annotations

import json
from pathlib import Path

import ghost2 as G2
from ghost import NODES

G2.MAX_GHOST, G2.MAX_DECOY = 1, 1
OUT = Path(__file__).resolve().parents[1] / "raid_lab_m10" / "data" / "m10_golden.json"


def enc(c):
    return [c[0], c[1]]


def case(seed):
    assets, b1, cands, own3 = G2.setup(seed)
    allocs = list(G2.allocations(assets))

    def ev(a):
        return sum(G2.outcome(assets, b1, c, own3, a) for c in cands) / len(cands)

    def both(a):
        s = 0.0
        for c in cands:
            m = G2.outcome(assets, b1, c, own3, a)
            h = max(G2.outcome(assets, b1, c, own3, a, sp) for sp in G2.SPOOFS[1:])
            s += G2.SPOOF_HIT * h + (1 - G2.SPOOF_HIT) * m
        return s / len(cands)
    plans = {"best_both": max(allocs, key=both), "best_sealed": max(allocs, key=ev),
             "ghost_biggest": (tuple(sorted(assets, key=lambda c: -assets[c])[:1]), (), ()), "none": ((), (), ())}
    rec = {"seed": seed, "assets": [[*enc(c), v] for c, v in sorted(assets.items())], "b1": [enc(c) for c in b1],
           "cands": [[enc(c) for c in ln] for ln in cands], "own3": [enc(c) for c in own3], "plans": {}}
    for name, (g, dk, dc) in plans.items():
        per = []
        for c in cands:
            found = G2.sweep(assets, b1, c, own3, set(g) | set(dk), set(dc))
            spoofs = []
            for sp in G2.SPOOFS[1:]:
                f2 = G2.sweep(assets, b1, c, own3, set(g) | set(dk), set(dc), sp)
                spoofs.append({"beam": sp[0], "node": enc(sp[1]), "found": [enc(x) for x in f2],
                               "value": G2.value(assets, f2, g, dk, dc)})
            per.append({"found": [enc(x) for x in found], "value": G2.value(assets, found, g, dk, dc), "spoofs": spoofs})
        rec["plans"][name] = {"ghost": [enc(c) for c in g], "dark": [enc(c) for c in dk], "decoys": [enc(c) for c in dc],
                              "per_candidate": per}
    return rec


if __name__ == "__main__":
    cfg = {"ghost_heat": G2.GHOST_HEAT, "heat_value": G2.HEAT_VALUE, "decoy_cost": G2.DECOY_COST, "evade": G2.EVADE,
           "max_ghost": G2.MAX_GHOST, "max_decoy": G2.MAX_DECOY, "w": 4, "h": 3, "nodes": [enc(c) for c in NODES],
           "dark_cost": "v // 2 + 1", "value": "-sum(found v) - decoy_cost*decoys - sum(dark cost) + evade if none found - heat_value*ghost_heat*ghosts"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"config": cfg, "cases": [case(s) for s in (0, 1, 3, 7, 12, 14, 17, 20, 21, 22, 25, 28)]},
                              indent=1), encoding="utf-8")
    print("wrote", OUT)
