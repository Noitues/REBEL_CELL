"""Round 9: three ways out of "the playout replays a known answer" (designer 2026-10-22: run all three). Each rule is a
designer decision. The base is ghost.py's sweep, plus the M8 critic's shared fixes:
- levers cost different currencies: a GHOST costs GHOST_HEAT Heat (valued HEAT_VALUE Schematics per Heat when ranking
  plans), a DECOY DECOY_COST Schematics, GO DARK the node's next income;
- found assets stay DOWN until repaired (repair = value, carried into the campaign).
Variants:
- SEALED (M9a, zero input): beam 2 is sealed: the forecast shows its CANDIDATES (3 faint lines), and the corp's pick is
  revealed in the playout. The player ranks plans by expected value over the candidates; the forecast shows the range.
- SPOOF (M9b, one input): everything is known, plus one SPOOF press during the playout: landed on a beam crossing a
  node, that beam skips the node. The plan names its spoof target; the forecast shows landed / missed. Landing is a
  timing skill: SPOOF_HIT = the chance a player lands it (for the expected value only).
- BOTH (M9c): sealed beam 2 plus the spoof, which the player spends AFTER the reveal (a reaction, not a plan).
Measured over 30 networks (python ghost2.py): for SEALED, the share of networks where the best plan's outcome still
varies with the reveal (suspense), and the regret of planning for one candidate; for SPOOF, the swing between landed and
missed (stakes of the press) and whether the spoof changes the best allocation; for BOTH, the value of reacting after
the reveal over committing the spoof target in advance."""
from __future__ import annotations

import itertools
import json
import random
import statistics as st
import sys

from ghost import ASSETS, DECOY_COST, EVADE, GHOSTS, H, NODES, W, network

GHOST_HEAT, HEAT_VALUE, SPOOF_HIT, CANDIDATES = 5, 0.4, 0.75, 3
SCARCE = "--scarce" in sys.argv   # 1 ghost slot and 1 decoy: the plan cannot cover every beam
MAX_GHOST, MAX_DECOY = (1, 1) if SCARCE else (GHOSTS, 2)


def lines(rng):
    if rng.random() < 0.5:
        y = rng.randrange(H)
        ln = [(x, y) for x in range(W)]
    else:
        x = rng.randrange(W)
        ln = [(x, y) for y in range(H)]
    return ln if rng.random() < 0.5 else ln[::-1]


def setup(seed):
    assets, beams, own3 = network(500 + seed)
    rng = random.Random(9000 + seed)
    cands = [beams[1]] + [lines(rng) for _ in range(CANDIDATES - 1)]
    return assets, beams[0], cands, own3


def sweep(assets, b1, b2, own3, hidden, decoys, spoof=None):
    """spoof = (beam index 0..2, node): that beam skips that node."""
    found, first = [], None

    def scan(line, k):
        nonlocal first
        for c in line:
            if spoof == (k, c):
                continue
            if c in decoys:
                first = first or c
                return
            if c in assets and c not in hidden and c not in found:
                found.append(c)
                first = first or c
    scan(b1, 0)
    scan(b2, 1)
    scan([(first[0], y) for y in range(H)] if first else own3, 2)
    return found


def value(assets, found, ghost, dark, decoys):
    v = -sum(assets[c] for c in found) - DECOY_COST * len(decoys) - sum(assets[c] // 2 + 1 for c in dark)
    return v + (EVADE if not found else 0) - HEAT_VALUE * GHOST_HEAT * len(ghost)


def allocations(assets):
    a = sorted(assets)
    empty = [n for n in NODES if n not in assets]
    for g in itertools.chain.from_iterable(itertools.combinations(a, k) for k in range(MAX_GHOST + 1)):
        rest = [c for c in a if c not in g]
        for dk in itertools.chain.from_iterable(itertools.combinations(rest, k) for k in range(min(3, len(rest)) + 1)):
            for dc in itertools.chain.from_iterable(itertools.combinations(empty, k) for k in range(MAX_DECOY + 1)):
                yield g, dk, dc


SPOOFS = [None] + [(k, n) for k in range(3) for n in NODES]


def outcome(assets, b1, b2, own3, alloc, spoof=None):
    g, dk, dc = alloc
    f = sweep(assets, b1, b2, own3, set(g) | set(dk), set(dc), spoof)
    return value(assets, f, g, dk, dc)


def measure(seed):
    assets, b1, cands, own3 = setup(seed)
    allocs = list(allocations(assets))
    # SEALED: EV over the candidates
    table = [[outcome(assets, b1, c, own3, a) for c in cands] for a in allocs]
    ev = [sum(r) / len(r) for r in table]
    i_best = max(range(len(allocs)), key=lambda i: ev[i])
    sealed_spread = max(table[i_best]) - min(table[i_best])
    # planning for candidate 0 only (as if it were known), scored in EV
    i_c0 = max(range(len(allocs)), key=lambda i: table[i][0])
    sealed_regret = ev[i_best] - ev[i_c0]
    full_best = max(r[0] for r in table)     # the known-sweep best (ghost.py rules, new costs)
    # SPOOF: all known (beam 2 = candidate 0); plan names the spoof
    best_sp, best_no = None, max(r[0] for r in table)
    for a in allocs:
        miss = outcome(assets, b1, cands[0], own3, a)
        for sp in SPOOFS[1:]:
            hit = outcome(assets, b1, cands[0], own3, a, sp)
            e = SPOOF_HIT * hit + (1 - SPOOF_HIT) * miss
            if best_sp is None or e > best_sp[0]:
                best_sp = (e, hit, miss, a)
    i_no = max(range(len(allocs)), key=lambda i: table[i][0])
    spoof_changes_alloc = best_sp[3] != allocs[i_no]
    # BOTH: sealed + spoof spent after the reveal vs committed in advance
    react_best = commit_best = None
    for a in allocs:
        per = []
        for c in cands:
            miss = outcome(assets, b1, c, own3, a)
            hits = {sp: outcome(assets, b1, c, own3, a, sp) for sp in SPOOFS[1:]}
            per.append((miss, hits))
        react = sum(SPOOF_HIT * max(h.values()) + (1 - SPOOF_HIT) * m for m, h in per) / len(cands)
        commit = max(sum(SPOOF_HIT * h[sp] + (1 - SPOOF_HIT) * m for m, h in per) / len(cands) for sp in SPOOFS[1:])
        if react_best is None or react > react_best[0]:
            react_best = (react, a)
        if commit_best is None or commit > commit_best:
            commit_best = commit
    return {"seed": seed, "full_best": round(full_best, 1), "sealed_ev": round(ev[i_best], 1),
            "sealed_spread": round(sealed_spread, 1), "sealed_regret_c0": round(sealed_regret, 1),
            "spoof_ev": round(best_sp[0], 1), "spoof_swing": round(best_sp[1] - best_sp[2], 1),
            "spoof_gain": round(best_sp[0] - best_no, 1), "spoof_changes_alloc": spoof_changes_alloc,
            "react_ev": round(react_best[0], 1), "commit_ev": round(commit_best, 1),
            "react_gain": round(react_best[0] - commit_best, 1)}


if __name__ == "__main__":
    rows = []
    for seed in range(30):
        rows.append(measure(seed))
        print(json.dumps(rows[-1]), flush=True)
    m = lambda k: round(st.mean(r[k] for r in rows), 2)  # noqa: E731
    summ = {"sealed_suspense_share": sum(r["sealed_spread"] > 0 for r in rows) / len(rows),
            "sealed_mean_spread": m("sealed_spread"), "sealed_mean_regret_c0": m("sealed_regret_c0"),
            "spoof_mean_swing": m("spoof_swing"), "spoof_mean_gain": m("spoof_gain"),
            "spoof_changes_alloc_share": sum(r["spoof_changes_alloc"] for r in rows) / len(rows),
            "react_mean_gain": m("react_gain"), "react_gain_share": sum(r["react_gain"] > 0.5 for r in rows) / len(rows)}
    print("SUMMARY", json.dumps(summ), flush=True)
    json.dump({"summary": summ, "rows": rows}, open(r"D:/rc_tmp/raid_design_lab/ghost2" + ("_scarce" if SCARCE else "") + ".json", "w"), indent=1)
