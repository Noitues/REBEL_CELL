"""Round 10, MANHUNT ALARM: the Invisible, Inc. model (calibration: the only shipped system above 7 on both P and S keeps
local information certain and the escalation unknown). Each rule is a designer decision.
- Local information is certain: beams 1 and 2 and the hunter rule are shown in full (no sealed beam).
- The ALARM is the unknown: Heat pre-fills it (--start=N; Heat 50+ = 1), and every asset the sweep finds raises the alarm by 1 (a dial). At ALARM_AT the corp sends a
  REINFORCEMENT beam, one of CANDIDATES lines the player cannot see in advance (the dial shows only that it will come).
  Your plan decides WHETHER the alarm trips; the corp decides WHERE the reinforcement sweeps.
- One SPOOF press (reactive): a landed spoof makes one beam skip one node; the player can hold it for the reinforcement.
- The forecast is local: which nodes each known beam reaches, and the alarm count it ends at. It does not compute a net
  or name a best reaction.
- Scarce levers as round 9 (1 ghost for +5 Heat, 1 decoy for 3, go dark for income).
Measured over 30 networks (python ghost3.py):
- edge_share: networks whose best plan ends the known beams exactly one below ALARM_AT (one more find trips it);
- trip_share: networks whose best plan trips the alarm anyway (the reinforcement is the raid's climax);
- spread: max - min outcome over the reinforcement candidates for the best plan (suspense);
- react_gain: holding the spoof for after the reveal against spending it on a known beam;
- near_plans: distinct allocations within 1 of the best (depth: several good answers, not one)."""
from __future__ import annotations

import itertools
import json
import random
import statistics as st

import ghost2 as G2
from ghost import H, NODES, W, network

ALARM_AT, CANDIDATES = 2, 3
ALARM_START = int(next((a.split('=')[1] for a in __import__('sys').argv if a.startswith('--start=')), 0))  # Heat pre-fills the alarm (Heat 50+ = 1)
G2.MAX_GHOST, G2.MAX_DECOY = 1, 1


def lines(rng):
    return G2.lines(rng)


def setup(seed):
    assets, beams, own3 = network(500 + seed)
    rng = random.Random(7000 + seed)
    return assets, beams[0], beams[1], own3, [lines(rng) for _ in range(CANDIDATES)]


def sweep(assets, b1, b2, own3, reinf, hidden, decoys, spoof=None):
    """Known beams, then the reinforcement if the alarm trips. spoof = (beam index 0..3, node). Returns (found, tripped)."""
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
    tripped = ALARM_START + len(found) >= ALARM_AT
    if tripped:
        scan(reinf, 3)
    return found, tripped


def known_found(assets, b1, b2, own3, alloc):
    g, dk, dc = alloc
    f, _ = sweep(assets, b1, b2, own3, [], set(g) | set(dk), set(dc))
    return f


def outcome(assets, b1, b2, own3, reinf, alloc, spoof=None):
    g, dk, dc = alloc
    f, tripped = sweep(assets, b1, b2, own3, reinf, set(g) | set(dk), set(dc), spoof)
    return G2.value(assets, f, g, dk, dc), tripped


SPOOFS = [(k, n) for k in range(4) for n in NODES]


def measure(seed):
    assets, b1, b2, own3, cands = setup(seed)
    allocs = list(G2.allocations(assets))
    rows = []
    for a in allocs:
        per = []
        for r in cands:
            miss, trip = outcome(assets, b1, b2, own3, r, a)
            best_react = max(outcome(assets, b1, b2, own3, r, a, sp)[0] for sp in SPOOFS)
            per.append((miss, best_react, trip))
        react = sum(G2.SPOOF_HIT * h + (1 - G2.SPOOF_HIT) * m for m, h, _ in per) / len(cands)
        # committing the spoof before the reveal: one fixed target for every candidate
        commit = max(sum(G2.SPOOF_HIT * outcome(assets, b1, b2, own3, r, a, sp)[0] + (1 - G2.SPOOF_HIT) * m
                         for r, (m, _h, _t) in zip(cands, per)) / len(cands) for sp in SPOOFS)
        rows.append((react, commit, a, per))
    rows.sort(key=lambda x: -x[0])
    react, commit, a, per = rows[0]
    kf = known_found(assets, b1, b2, own3, a)
    near = sum(1 for r in rows if r[0] >= react - 1)
    outs = [h for _m, h, _t in per]
    return {"seed": seed, "best": round(react, 1), "known_found": len(kf), "edge": ALARM_START + len(kf) == ALARM_AT - 1,
            "tripped": any(t for _m, _h, t in per), "spread": round(max(outs) - min(outs), 1),
            "react_gain": round(react - commit, 1), "near_plans": near, "n": len(rows)}


if __name__ == "__main__":
    out = []
    for seed in range(30):
        out.append(measure(seed))
        print(json.dumps(out[-1]), flush=True)
    m = lambda k: round(st.mean(r[k] for r in out), 2)  # noqa: E731
    summ = {"edge_share": sum(r["edge"] for r in out) / len(out), "trip_share": sum(r["tripped"] for r in out) / len(out),
            "suspense_share": sum(r["spread"] > 0 for r in out) / len(out), "mean_spread": m("spread"),
            "mean_react_gain": m("react_gain"), "react_gain_share": sum(r["react_gain"] > 0.5 for r in out) / len(out),
            "mean_near_plans": m("near_plans"), "share_3plus_near": sum(r["near_plans"] >= 3 for r in out) / len(out)}
    print("SUMMARY", json.dumps(summ), flush=True)
    json.dump({"summary": summ, "rows": out}, open(rf"D:/rc_tmp/raid_design_lab/ghost3_start{ALARM_START}.json", "w"), indent=1)
