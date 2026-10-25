"""Lab round 2 (L2) sweep-raid rules: the designer delegated the rulings (2026-10-22: "you call on the choices that
move the score most"). Each rule below is a designer-delegated decision, logged in RECOMMENDATION.md.
- ONE network for the whole leg (3 raids): 4 x 3 cells, ASSETS assets of value v, plus the HOME server (integrity
  HOME_HP). Status per asset: OK / DOWN / TAKEN.
- A find lands on the network: OK -> DOWN (no income until repaired; repair = v // 2, GDD 3.3), DOWN -> TAKEN (lost
  for the leg). A find on HOME costs 1 integrity; 0 = BREACHED (campaign lost). TAKEN cells are corp ground (beams pass).
- Heat sets the raid's strength: beam 1, sealed beam 2 (CANDIDATES lines), hunter; Heat >= EXTRA_AT adds a known extra
  beam and Heat >= STRONG_AT a second one (both scanned after beam 1).
- Levers: 1 GHOST (+GHOST_HEAT Heat at placement), 1 DECOY (DECOY_COST Schematics), GO DARK (up to MAX_DARK; no income from
  that asset this interval), and between raids REPAIR any DOWN asset (v // 2).
- SPOOF = a choice after the reveal: beam 2 skips one node.
- The hunter turns down the column of the first touch (a find or a decoy), else its own line.
- EVADED = the sweep touched nothing (decoys count as a touch): Heat - EVADE_HEAT. Otherwise Heat is unchanged.
- Between raids: Heat + RUN_HEAT; income = sum(v // 3) over OK, not-dark assets.
- Leg score = bank at the end + sum(v) of assets not TAKEN - HOME_LOSS_COST per integrity lost (BREACHED = -BREACH).
Measured (python sweep_l2.py): per leg, the planned line (beam search over raids, EV over the sealed candidates with a
best spoof) against greedy (each raid alone); regret, breach and TAKEN rates, how often the planned line crosses into the
strong band, and distinct near-best first-raid plans."""
from __future__ import annotations

import itertools
import json
import random
import statistics as st
from dataclasses import dataclass, field, replace

W, H, ASSETS, CANDIDATES = 4, 3, 6, 3
NODES = [(x, y) for y in range(H) for x in range(W)]
HOME_HP, EXTRA_AT, STRONG_AT, START_HEAT, RUN_HEAT, MAX_DARK = 3, 50, 75, 44, 12, 1
GHOST_HEAT, DECOY_COST, EVADE_HEAT, START_BANK = 5, 3, 10, 10
HOME_LOSS_COST, BREACH, RAIDS, NEAR = 8, 100, 3, 1.0


def line(rng):
    if rng.random() < 0.5:
        y = rng.randrange(H)
        ln = [(x, y) for x in range(W)]
    else:
        x = rng.randrange(W)
        ln = [(x, y) for y in range(H)]
    return ln if rng.random() < 0.5 else ln[::-1]


@dataclass(frozen=True)
class Raid:
    b1: tuple
    extra: tuple
    extra2: tuple
    cands: tuple
    own3: tuple


@dataclass(frozen=True)
class Leg:
    home: tuple
    values: tuple          # ((cell, v), ...) sorted
    raids: tuple


def make_leg(seed) -> Leg:
    rng = random.Random(4000 + seed)
    cells = rng.sample(NODES, ASSETS + 1)
    home, rest = cells[0], sorted(cells[1:])
    values = tuple((c, rng.choice((4, 6, 8, 10, 12))) for c in rest)
    raids = []
    for _ in range(RAIDS):
        x3 = rng.randrange(W)
        raids.append(Raid(tuple(line(rng)), tuple(line(rng)), tuple(line(rng)), tuple(tuple(line(rng)) for _ in range(CANDIDATES)),
                          tuple((x3, y) for y in range(H))))
    return Leg(home, values, tuple(raids))


@dataclass(frozen=True)
class State:
    heat: int = START_HEAT
    bank: int = START_BANK
    home_hp: int = HOME_HP
    status: tuple = ()      # ((cell, "OK"|"DOWN"|"TAKEN"), ...) sorted


def initial(leg: Leg) -> State:
    return State(status=tuple((c, "OK") for c, _ in leg.values))


def strong(heat: int) -> bool:
    return heat >= STRONG_AT


def sweep(leg: Leg, raid: Raid, st_: State, b2, ghost, dark, decoys, spoof=None, heat=None):
    """Returns (touches in order [(cell, kind)], first-touch column). kind: 'asset' | 'home' | 'decoy'."""
    status = dict(st_.status)
    hidden = set(ghost) | set(dark)
    touched, first = [], None
    seen = set()

    def scan(ln, k):
        nonlocal first
        for c in ln:
            if spoof is not None and k == "b2" and c == spoof:
                continue
            if c in decoys:
                touched.append((c, "decoy"))
                first = first or c
                return
            if c in hidden or c in seen:
                continue
            if c == leg.home:
                touched.append((c, "home"))
                seen.add(c)
                first = first or c
            elif c in status and status[c] != "TAKEN":
                touched.append((c, "asset"))
                seen.add(c)
                first = first or c
    scan(raid.b1, "b1")
    h = st_.heat if heat is None else heat
    if h >= EXTRA_AT:
        scan(raid.extra, "extra")
    if strong(h):
        scan(raid.extra2, "extra2")
    scan(b2, "b2")
    scan([(first[0], y) for y in range(H)] if first else raid.own3, "hunter")
    return touched


def resolve(leg: Leg, raid: Raid, st_: State, b2, alloc, spoof=None):
    """One raid. alloc = (ghost, dark, decoys). Returns the state after the raid (before the between-raid step) and the
    touches."""
    ghost, dark, decoys = alloc
    heat = st_.heat + GHOST_HEAT * len(ghost)
    bank = st_.bank - DECOY_COST * len(decoys)
    touched = sweep(leg, raid, st_, b2, ghost, dark, set(decoys), spoof, heat)
    status = dict(st_.status)
    home_hp = st_.home_hp
    for c, kind in touched:
        if kind == "asset":
            status[c] = "DOWN" if status[c] == "OK" else "TAKEN"
        elif kind == "home":
            home_hp -= 1
    if not touched:
        heat -= EVADE_HEAT
    return State(heat, bank, max(0, home_hp), tuple(sorted(status.items()))), touched


def between(leg: Leg, st_: State, dark, repairs):
    vals = dict(leg.values)
    status = dict(st_.status)
    bank = st_.bank
    for c in repairs:
        if status.get(c) == "DOWN" and bank >= vals[c] // 2:
            bank -= vals[c] // 2
            status[c] = "OK"
    income = sum(vals[c] // 3 for c, s in status.items() if s == "OK" and c not in dark)
    return State(st_.heat + RUN_HEAT, bank + income, st_.home_hp, tuple(sorted(status.items())))


def score(leg: Leg, st_: State) -> float:
    if st_.home_hp <= 0:
        return -BREACH
    vals = dict(leg.values)
    # a DOWN asset is worth its value less the repair it still owes
    return (st_.bank + sum(vals[c] - (vals[c] // 2 if s == "DOWN" else 0) for c, s in st_.status if s != "TAKEN")
            - HOME_LOSS_COST * (HOME_HP - st_.home_hp))


def allocations(leg: Leg, st_: State):
    live = [c for c, s in st_.status if s != "TAKEN"]
    hideable = live + [leg.home]
    empty = [n for n in NODES if n not in dict(leg.values) and n != leg.home]
    for g in itertools.chain([()], ((c,) for c in hideable)):
        rest = [c for c in live if c not in g]
        for dk in itertools.chain.from_iterable(itertools.combinations(rest, k) for k in range(min(MAX_DARK, len(rest)) + 1)):
            for dc in itertools.chain([()], ((n,) for n in empty)):
                if DECOY_COST * len(dc) <= st_.bank:
                    yield (g, dk, dc)


def raid_options(leg: Leg, i: int, st_: State):
    """Per allocation: the after-states per candidate with the player's best spoof (a choice after the reveal)."""
    raid = leg.raids[i]
    out = []
    for a in allocations(leg, st_):
        per = []
        for b2 in raid.cands:
            best = None
            for sp in [None] + [c for c in b2]:
                ns, t = resolve(leg, raid, st_, b2, a, sp)
                key = (score(leg, ns), -len(t))
                if best is None or key > best[0]:
                    best = (key, ns, sp)
            per.append((best[1], best[2]))
        out.append((a, per))
    return out


def repair_sets(leg: Leg, st_: State):
    down = [c for c, s in st_.status if s == "DOWN"]
    for k in range(len(down) + 1):
        for rs in itertools.combinations(down, k):
            yield rs


def greedy_leg(leg: Leg):
    st_ = initial(leg)
    log = []
    for i in range(RAIDS):
        opts = raid_options(leg, i, st_)
        a, per = max(opts, key=lambda o: sum(score(leg, ns) for ns, _ in o[1]) / len(o[1]))
        ns, sp = per[0]   # the corp's real pick: candidate 0 (deterministic per leg)
        log.append({"raid": i, "alloc": a, "spoof": sp, "after": ns})
        if ns.home_hp <= 0:
            return ns, log
        rs = max(repair_sets(leg, ns), key=lambda r: score(leg, between(leg, ns, a[1], r)))
        st_ = between(leg, ns, a[1], rs) if i < RAIDS - 1 else ns
    return st_, log


def planned_leg(leg: Leg, width=40):
    """Beam search over the leg: EV over the sealed candidates for planning; the real pick (candidate 0) for the line."""
    beam = [(0.0, initial(leg), [])]
    for i in range(RAIDS):
        nxt = []
        for _, st_, log in beam:
            for a, per in raid_options(leg, i, st_):
                ev_after = per
                for rs in ([()] if i == RAIDS - 1 else None) or repair_sets(leg, per[0][0]):
                    evs = []
                    for ns, _ in ev_after:
                        bs = between(leg, ns, a[1], tuple(r for r in rs if dict(ns.status).get(r) == "DOWN")) if i < RAIDS - 1 else ns
                        evs.append(score(leg, bs) + (0 if i == RAIDS - 1 else 0.25 * (STRONG_AT - min(STRONG_AT, bs.heat)) / 5))
                    ev = sum(evs) / len(evs)
                    real_ns, sp = per[0]
                    real = between(leg, real_ns, a[1], rs) if i < RAIDS - 1 and real_ns.home_hp > 0 else real_ns
                    nxt.append((ev, real, log + [{"raid": i, "alloc": a, "spoof": sp, "after": real_ns, "repairs": rs}]))
        nxt.sort(key=lambda x: -x[0])
        dedup, seen = [], set()
        for x in nxt:
            k = (x[1].status, x[1].heat, x[1].bank, x[1].home_hp)
            if k not in seen:
                seen.add(k)
                dedup.append(x)
        beam = dedup[:width]
    best = max(beam, key=lambda x: score(leg, x[1]))
    return best[1], best[2]


def naive_leg(leg: Leg):
    """A careless player: ghost the biggest live asset, no decoy, no dark, spoof the first live asset on the revealed
    line, repair whatever the bank allows."""
    st_ = initial(leg)
    vals = dict(leg.values)
    log = []
    for i in range(RAIDS):
        raid = leg.raids[i]
        live = sorted((c for c, s in st_.status if s != "TAKEN"), key=lambda c: (-vals[c], c))
        a = ((live[0],) if live else (), (), ())
        b2 = raid.cands[0]
        sp = next((c for c in b2 if c in vals and dict(st_.status).get(c) != "TAKEN" and c not in a[0]), None)
        ns, t = resolve(leg, raid, st_, b2, a, sp)
        log.append({"raid": i, "alloc": a, "spoof": sp, "after": ns})
        if ns.home_hp <= 0:
            return ns, log
        down = tuple(sorted((c for c, s in ns.status if s == "DOWN"), key=lambda c: (-vals[c], c)))
        st_ = between(leg, ns, (), down) if i < RAIDS - 1 else ns
    return st_, log


def first_raid_near(leg: Leg):
    opts = raid_options(leg, 0, initial(leg))
    vals = sorted((sum(score(leg, ns) for ns, _ in per) / len(per) for _, per in opts), reverse=True)
    return sum(1 for v in vals if v >= vals[0] - NEAR)


if __name__ == "__main__":
    rows = []
    for seed in range(20):
        leg = make_leg(seed)
        g_end, g_log = greedy_leg(leg)
        p_end, p_log = planned_leg(leg)
        n_end, n_log = naive_leg(leg)
        rows.append({"seed": seed, "planned": score(leg, p_end), "greedy": score(leg, g_end),
                     "planned_taken": sum(s == "TAKEN" for _, s in p_end.status),
                     "greedy_taken": sum(s == "TAKEN" for _, s in g_end.status),
                     "planned_breach": p_end.home_hp <= 0, "greedy_breach": g_end.home_hp <= 0, "naive": score(leg, n_end), "naive_breach": n_end.home_hp <= 0,
                     "naive_taken": sum(s == "TAKEN" for _, s in n_end.status), "planned_home_lost": HOME_HP - p_end.home_hp,
                     "planned_strong_raids": sum(strong(x["after"].heat) for x in p_log),
                     "greedy_strong_raids": sum(strong(x["after"].heat) for x in g_log),
                     "first_near": first_raid_near(leg),
                     "downs_planned": sum(sum(1 for _, s in x["after"].status if s == "DOWN") for x in p_log)})
        print(json.dumps(rows[-1]), flush=True)
    m = lambda k: round(st.mean(r[k] for r in rows), 2)  # noqa: E731
    summ = {"mean_regret": round(st.mean(r["planned"] - r["greedy"] for r in rows), 1),
            "regret_share_ge3": sum(r["planned"] - r["greedy"] >= 3 for r in rows) / len(rows),
            "planned_breach": sum(r["planned_breach"] for r in rows) / len(rows),
            "greedy_breach": sum(r["greedy_breach"] for r in rows) / len(rows),
            "naive_breach": sum(r["naive_breach"] for r in rows) / len(rows), "naive_taken": m("naive_taken"),
            "mean_gap_naive": round(st.mean(r["planned"] - r["naive"] for r in rows), 1), "planned_home_lost": m("planned_home_lost"),
            "planned_taken": m("planned_taken"), "greedy_taken": m("greedy_taken"),
            "planned_strong": m("planned_strong_raids"), "greedy_strong": m("greedy_strong_raids"),
            "first_near": m("first_near"), "downs_planned": m("downs_planned")}
    print("SUMMARY", json.dumps(summ), flush=True)
    json.dump({"summary": summ, "rows": rows}, open(r"D:/rc_tmp/raid_design_lab/sweep_l2.json", "w"), indent=1)
