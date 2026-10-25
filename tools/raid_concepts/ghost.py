"""Pitch 11, GHOST PROTOCOL: the pitch critic's kill test (headless enumerator). Prototype rules (designer decisions).

Network: 4 x 3 nodes; ASSETS of them hold an asset of value v (the rest empty). Solace's sweep (shown in advance) is 3
BEAMS in order, each scanning one row or column from one end: it FINDS every visible asset on its line, in order.
Corp-specific interaction: beam 3 is a HUNTER: it scans the column of the first thing beam 1 or 2 found (a decoy counts),
else its own line.
Levers (scarce, each with a cost):
 - GHOST: up to GHOSTS asset nodes are invisible (free; the capacity is the cost).
 - DECOY: up to 2, DECOY_COST Schematics each, on any node: a beam that reaches a decoy stops there (the rest of its line
   is not scanned) and counts it as found (so it can draw the hunter).
 - GO DARK: any asset node is invisible but earns no income next netrun (cost = its income, v // 2 + 1).
A found asset goes DOWN: repair = v. Nothing real found = an evaded sweep: + EVADE (Heat drop, in Schematics terms).
Net = - repairs - decoy costs - dark costs + EVADE if evaded. Measured over 30 seeded networks and patterns: the best,
the median allocation, the share within 5% (or 1) of the best, whether a greedy rule (ghost the two biggest, go dark on
the rest that a beam would find, no decoys) is best, and how many distinct lever mixes tie the best."""
from __future__ import annotations

import itertools
import json
import random
import statistics as st

W, H, ASSETS, GHOSTS, DECOY_COST, EVADE = 4, 3, 6, 2, 3, 6
NODES = [(x, y) for y in range(H) for x in range(W)]


def network(seed):
    rng = random.Random(seed)
    cells = rng.sample(NODES, ASSETS)
    assets = {c: rng.choice((3, 4, 5, 6, 8, 10)) for c in cells}
    beams = []
    for _ in range(2):
        if rng.random() < 0.5:
            y = rng.randrange(H)
            line = [(x, y) for x in range(W)]
        else:
            x = rng.randrange(W)
            line = [(x, y) for y in range(H)]
        beams.append(line if rng.random() < 0.5 else line[::-1])
    x3 = rng.randrange(W)
    own3 = [(x3, y) for y in range(H)]
    return assets, beams, own3


def sweep(assets, beams, own3, hidden, decoys):
    found, first = [], None
    def scan(line):
        nonlocal first
        for c in line:
            if c in decoys:
                first = first or c
                return
            if c in assets and c not in hidden and c not in found:
                found.append(c)
                first = first or c
    for b in beams:
        scan(b)
    scan([(first[0], y) for y in range(H)] if first else own3)
    return found


def net(assets, beams, own3, ghost, dark, decoys):
    hidden = set(ghost) | set(dark)
    found = sweep(assets, beams, own3, hidden, set(decoys))
    v = -sum(assets[c] for c in found) - DECOY_COST * len(decoys) - sum(assets[c] // 2 + 1 for c in dark)
    return v + (EVADE if not found else 0)


def allocations(assets):
    a = sorted(assets)
    for g in itertools.chain.from_iterable(itertools.combinations(a, k) for k in range(GHOSTS + 1)):
        rest = [c for c in a if c not in g]
        for dk in itertools.chain.from_iterable(itertools.combinations(rest, k) for k in range(len(rest) + 1)):
            for dc in itertools.chain.from_iterable(itertools.combinations([n for n in NODES if n not in assets], k)
                                                    for k in range(3)):
                yield g, dk, dc


def greedy(assets, beams, own3):
    g = tuple(sorted(assets, key=lambda c: -assets[c])[:GHOSTS])
    hidden = set(g)
    exposed = sweep(assets, beams, own3, hidden, set())
    return net(assets, beams, own3, g, tuple(exposed), ())


if __name__ == "__main__":
    rows = []
    for seed in range(30):
        assets, beams, own3 = network(500 + seed)
        vals = []
        for g, dk, dc in allocations(assets):
            vals.append((net(assets, beams, own3, g, dk, dc), len(g), len(dk), len(dc)))
        vals.sort(key=lambda x: -x[0])
        b = vals[0][0]
        tol = max(1, abs(b) * 0.05)
        near = [v for v in vals if v[0] >= b - tol]
        mixes = {(v[1], v[2], v[3]) for v in near}
        med = vals[len(vals) // 2][0]
        gr = greedy(assets, beams, own3)
        rows.append({"seed": seed, "best": b, "median": med, "n": len(vals), "near": len(near),
                     "near_share": round(len(near) / len(vals), 4), "lever_mixes": len(mixes),
                     "uses_decoy": any(v[3] for v in near), "greedy": gr, "greedy_is_best": gr >= b - tol})
        print(json.dumps(rows[-1]), flush=True)
    summ = {"mean_best": round(st.mean(r["best"] for r in rows), 1),
            "mean_regret_median": round(st.mean(r["best"] - r["median"] for r in rows), 1),
            "mean_regret_greedy": round(st.mean(r["best"] - r["greedy"] for r in rows), 1),
            "greedy_best_share": sum(r["greedy_is_best"] for r in rows) / len(rows),
            "unique_best_share": sum(r["near"] == 1 for r in rows) / len(rows),
            "mean_lever_mixes": round(st.mean(r["lever_mixes"] for r in rows), 2),
            "decoy_in_near_share": sum(r["uses_decoy"] for r in rows) / len(rows),
            "mean_near_share": round(st.mean(r["near_share"] for r in rows), 4)}
    print("SUMMARY", json.dumps(summ), flush=True)
    json.dump({"summary": summ, "rows": rows}, open(r"D:/rc_tmp/raid_design_lab/ghost.json", "w"), indent=1)
