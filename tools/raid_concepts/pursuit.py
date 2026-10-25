"""Pitch 2, PURSUIT (designer 2026-10-22, FTL's rebel fleet): the kill test the pitch critic set. Prototype rules (each a
designer decision).

Grid: COLS columns x ROWS rows of City Grid nodes; edges to the neighbour rows in the next / previous column and to
the lateral neighbours. The cell starts at (0, 1); the corp core is a node past the last column.
Each node: value v (Schematics) and noise h (Heat it adds when run), correlated, seeded.
Turn (one netrun): move to a neighbour, then RUN it (+v, Heat += HEAT_PER_NOISE * h; once per node) or LAY LOW
(Heat -= LAY_LOW). Then the FRONT (Solace's net, starting behind the cell) advances by SPEED(Heat) columns; nodes it
covers are swallowed (no value). If the cell's node is swallowed, it is CAUGHT: an ambush costs CATCH_BASE +
Heat // CATCH_HEAT_DIV, and the cell breaks contact (front pushed back KNOCKBACK).
Score = Schematics - catch costs + (CORE_WIN if the core is reached by MAX_TURNS else -CORE_FAIL) - Heat_at_core // 5.
Measurement (python pursuit.py): 50 seeded grids; beam search (the planned line), the shortest path running every
node (the minimum path) and a greedy line. Kill if the minimum path is within 5% of the best on > 70% of seeds or best
play's catches fall outside 3-5. Also counts distinct near-optimal routes (by the set of high-value nodes run)."""
from __future__ import annotations

import json
import random
import statistics as st

COLS, ROWS, MAX_TURNS = 10, 3, 16
HEAT_PER_NOISE, LAY_LOW, HEAT_CAP = 4, 8, 100
FRONT_START, KNOCKBACK = -1.5, 1.5
CATCH_BASE, CATCH_HEAT_DIV = 4, 8
CORE_WIN, CORE_FAIL = 20, 60
BEAM, NEAR = 1500, 3
LOW_STAYS, KEY = False, 0  # v2: LAY LOW holds position; the core needs KEY Schematics to breach
CORE = (COLS, 1)


def speed(heat: int) -> float:
    return 0.5 if heat < 25 else 0.75 if heat < 50 else 1.0 if heat < 75 else 1.25


def grid(seed: int):
    rng = random.Random(seed)
    nodes = {}
    for c in range(COLS):
        for r in range(ROWS):
            v = rng.choice((0, 1, 2, 2, 3, 4, 5, 6, 8))
            h = max(1, min(5, v // 2 + rng.choice((-1, 0, 0, 1))))
            nodes[(c, r)] = (v, h)
    nodes[(0, 1)] = (0, 0)
    nodes[CORE] = (0, 0)
    return nodes


def nbrs(n):
    c, r = n
    out = []
    for dc in (-1, 0, 1):
        for dr in (-1, 0, 1):
            if (dc, dr) == (0, 0) or (dc == 0 and abs(dr) != 1):
                continue
            m = (c + dc, r + dr)
            if 0 <= m[0] < COLS and 0 <= m[1] < ROWS:
                out.append(m)
    if c == COLS - 1 and r == 1:
        out.append(CORE)
    return out


def step(state, move, act, nodes):
    """state = (node, heat, front, run(frozenset), sch, catches, cost). Returns the new state."""
    node, heat, front, run, sch, catches, cost = state
    if not (LOW_STAYS and act == "LOW"):
        node = move
    if act == "RUN" and node not in run and node[0] > front:
        v, h = nodes[node]
        sch += v
        heat = min(HEAT_CAP, heat + HEAT_PER_NOISE * h)
        run = run | {node}
    elif act == "LOW":
        heat = max(0, heat - LAY_LOW)
    front += speed(heat)
    if node != CORE and node[0] <= front:
        catches += 1
        cost += CATCH_BASE + heat // CATCH_HEAT_DIV
        front -= KNOCKBACK
    return (node, heat, front, run, sch, catches, cost)


def score(state):
    node, heat, _, _, sch, _, cost = state
    return sch - cost + (CORE_WIN - heat // 5 if node == CORE and sch >= KEY else -CORE_FAIL)


def potential(state):
    """Beam ordering: the partial score as if the cell reaches the core."""
    node, heat, _, _, sch, _, cost = state
    return sch - cost - heat // 5 - 2 * (COLS - node[0])


def beam(nodes):
    start = ((0, 1), 0, FRONT_START, frozenset(), 0, 0, 0)
    layer, done = [(start, ())], []
    for _ in range(MAX_TURNS):
        nxt = {}
        for s, path in layer:
            if s[0] == CORE:
                done.append((s, path))
                continue
            for m in nbrs(s[0]):
                for act in ("RUN", "LOW"):
                    t = step(s, m, act, nodes)
                    key = (t[0], t[1], round(t[2], 2), t[3])
                    if key not in nxt or t[4] - t[6] > nxt[key][0][4] - nxt[key][0][6]:
                        nxt[key] = (t, path + ((m, act),))
        layer = sorted(nxt.values(), key=lambda x: -potential(x[0]))[:BEAM]
    done += layer
    return sorted(done, key=lambda x: -score(x[0]))


def play(nodes, policy):
    s = ((0, 1), 0, FRONT_START, frozenset(), 0, 0, 0)
    for _ in range(MAX_TURNS):
        if s[0] == CORE:
            break
        m, act = policy(s, nodes)
        s = step(s, m, act, nodes)
    return s


def shortest(s, nodes):
    c, r = s[0]
    m = (c + 1, r + (1 if r < 1 else -1 if r > 1 else 0)) if c < COLS - 1 else (CORE if r == 1 else (c, 1))
    return m, "RUN"


def greedy(s, nodes):
    best = None
    for m in nbrs(s[0]):
        for act in ("RUN", "LOW"):
            t = step(s, m, act, nodes)
            val = (t[4] - t[6]) - t[1] // 5 + 3 * (m[0] - s[0][0]) - (8 if t[5] > s[5] else 0)
            if best is None or val > best[0]:
                best = (val, m, act)
    return best[1], best[2]


def sig(state, nodes):
    return frozenset(n for n in state[3] if nodes[n][0] >= 5)


if __name__ == "__main__":
    rows = []
    for seed in range(50):
        nodes = grid(1000 + seed)
        res = beam(nodes)
        b = score(res[0][0])
        near = [x for x in res if score(x[0]) >= b - NEAR]
        sp, gr = play(nodes, shortest), play(nodes, greedy)
        rows.append({"seed": seed, "best": b, "best_catches": res[0][0][5], "best_heat": res[0][0][1],
                     "lowlay": sum(a == "LOW" for _, a in res[0][1]), "turns": len(res[0][1]),
                     "shortest": score(sp), "shortest_catches": sp[5], "greedy": score(gr), "greedy_catches": gr[5],
                     "near_routes": len({sig(x[0], nodes) for x in near})})
        print(json.dumps(rows[-1]), flush=True)
    sp_opt = sum(r["shortest"] >= r["best"] - max(1, 0.05 * abs(r["best"])) for r in rows) / len(rows)
    cat = [r["best_catches"] for r in rows]
    summ = {"mean_best": round(st.mean(r["best"] for r in rows), 1),
            "shortest_within_5pct_share": sp_opt,
            "mean_gap_best_shortest": round(st.mean(r["best"] - r["shortest"] for r in rows), 1),
            "mean_gap_best_greedy": round(st.mean(r["best"] - r["greedy"] for r in rows), 1),
            "best_catches_mean": round(st.mean(cat), 2), "best_catches_sd": round(st.pstdev(cat), 2),
            "best_catches_in_3_5": sum(3 <= c <= 5 for c in cat) / len(cat),
            "greedy_catches_mean": round(st.mean(r["greedy_catches"] for r in rows), 2),
            "mean_near_routes": round(st.mean(r["near_routes"] for r in rows), 2),
            "share_3plus_routes": sum(r["near_routes"] >= 3 for r in rows) / len(rows),
            "mean_lay_low": round(st.mean(r["lowlay"] for r in rows), 2)}
    print("SUMMARY", json.dumps(summ), flush=True)
    json.dump({"summary": summ, "rows": rows}, open(r"D:/rc_tmp/raid_design_lab/pursuit.json", "w"), indent=1)
