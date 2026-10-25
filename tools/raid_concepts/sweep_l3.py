"""Lab round 3 (L3) sweep-raid rules: the L2 rules (sweep_l2.py) plus the L2 critic's depth changes, each a
designer-delegated decision (2026-10-22, "run it"):
- LEG KIT: levers are scarce across the leg, not per raid. Start with KIT_START ghosts / decoys / spoofs for 3 raids;
  per raid at most 1 ghost and up to 2 decoys from the kit. A spoof is spent only if the player uses it after the reveal.
- SHOP between raids: the bank buys kit refills (GHOST_PRICE, DECOY_PRICE, SPOOF_PRICE; one item per interval), so
  repairs compete with kit for Schematics.
- RUN INTENSITY between raids: LOW / NORMAL / HOT = Heat +6 / +12 / +18 and income x0.5 / x1 / x1.5 (rounded down), so
  Heat responds to play and the Heat bands (extra beams at 50 and 75) become a choice.
- HEAT CARRIES: the leg score charges HEAT_CARRY per Heat point above the start (Heat feeds the campaign's later raids),
  so HOT is a real trade.
- OUTCOME TIERS: EVADED (nothing touched), HOLDS (assets hit, home intact), DAMAGED (home hit), BREACHED (home 0 =
  campaign lost).
Unchanged from L2: one network for the leg, OK -> DOWN -> TAKEN, home integrity, Heat bands, the sealed beam, the hunter,
the ghost's +5 Heat, the evade's Heat -10, repair = v // 2, go dark (at most 1 per raid, no income).
Measured (python sweep_l3.py): planned (beam search) vs greedy vs naive over 20 legs; lever use per raid (want < 100%),
intensity mix, breach rates, distinct near-best first-raid plans."""
from __future__ import annotations

import itertools
import json
import statistics as st
from dataclasses import dataclass

import sweep_l2 as L
from sweep_l2 import EXTRA_AT, HOME_HP, NODES, RAIDS, STRONG_AT, Leg, make_leg

KIT_START = {"ghost": 2, "decoy": 2, "spoof": 2}
PRICES = {"ghost": 6, "decoy": 4, "spoof": 5}
INTENSITY = {"LOW": (6, 0.5), "NORMAL": (12, 1.0), "HOT": (18, 1.5)}
KIT_VALUE = 2.5      # planner heuristic only: the value of an unspent kit item mid-leg
MAX_DECOYS = 2
HEAT_CARRY = 1.0    # leg score: Heat carries into the campaign's next raids; each point above START_HEAT costs this


@dataclass(frozen=True)
class State:
    heat: int = L.START_HEAT
    bank: int = L.START_BANK
    home_hp: int = HOME_HP
    status: tuple = ()
    kit: tuple = (("decoy", 2), ("ghost", 2), ("spoof", 2))


def kitd(s: State) -> dict:
    return dict(s.kit)


def with_kit(s: State, **kw) -> tuple:
    k = kitd(s)
    k.update(kw)
    return tuple(sorted(k.items()))


def initial(leg: Leg) -> State:
    return State(status=tuple((c, "OK") for c, _ in leg.values), kit=tuple(sorted(KIT_START.items())))


def tier(before: State, after: State, touched) -> str:
    if after.home_hp <= 0:
        return "BREACHED"
    if after.home_hp < before.home_hp:
        return "DAMAGED"
    return "EVADED" if not touched else "HOLDS"


def resolve(leg: Leg, raid: L.Raid, st_: State, b2, alloc, spoof=None):
    ghost, dark, decoys = alloc
    k = kitd(st_)
    assert len(ghost) <= k["ghost"] and len(decoys) <= k["decoy"] and (spoof is None or k["spoof"] > 0)
    l2_before = L.State(st_.heat, st_.bank + L.DECOY_COST * len(decoys), st_.home_hp, st_.status)
    ns2, touched = L.resolve(leg, raid, l2_before, b2, alloc, spoof)   # decoys come from the kit: no Schematics
    ns = State(ns2.heat, st_.bank, ns2.home_hp, ns2.status,
               with_kit(st_, ghost=k["ghost"] - len(ghost), decoy=k["decoy"] - len(decoys),
                        spoof=k["spoof"] - (1 if spoof is not None else 0)))
    return ns, touched


def between(leg: Leg, st_: State, dark, repairs, intensity: str, buy: str | None):
    vals = dict(leg.values)
    status = dict(st_.status)
    bank = st_.bank
    for c in repairs:
        if status.get(c) == "DOWN" and bank >= vals[c] // 2:
            bank -= vals[c] // 2
            status[c] = "OK"
    kit = kitd(st_)
    if buy is not None and bank >= PRICES[buy]:
        bank -= PRICES[buy]
        kit[buy] += 1
    dh, mult = INTENSITY[intensity]
    income = int(sum(vals[c] // 3 for c, s in status.items() if s == "OK" and c not in dark) * mult)
    return State(st_.heat + dh, bank + income, st_.home_hp, tuple(sorted(status.items())), tuple(sorted(kit.items())))


def score(leg: Leg, st_: State, mid: bool = False) -> float:
    base = L.score(leg, L.State(st_.heat, st_.bank, st_.home_hp, st_.status))
    if base <= -L.BREACH:
        return base
    base -= HEAT_CARRY * max(0, st_.heat - L.START_HEAT)
    return base + (KIT_VALUE * sum(v for _, v in st_.kit) if mid else 0)


def allocations(leg: Leg, st_: State):
    k = kitd(st_)
    live = [c for c, s in st_.status if s != "TAKEN"]
    hideable = live + [leg.home]
    empty = [n for n in NODES if n not in dict(leg.values) and n != leg.home]
    ghosts = [()] + ([(c,) for c in hideable] if k["ghost"] > 0 else [])
    for g in ghosts:
        rest = [c for c in live if c not in g]
        for dk in itertools.chain([()], ((c,) for c in rest)):
            for nd in range(min(MAX_DECOYS, k["decoy"]) + 1):
                for dc in itertools.combinations(empty, nd):
                    yield (g, dk, dc)


def raid_options(leg: Leg, i: int, st_: State, mid: bool = True):
    """Per allocation, per sealed candidate: the after-state with the player's best spoof use (or none)."""
    raid = leg.raids[i]
    out = []
    for a in allocations(leg, st_):
        per = []
        for b2 in raid.cands:
            best = None
            sps = [None] + (list(b2) if kitd(st_)["spoof"] > 0 else [])
            for sp in sps:
                ns, t = resolve(leg, raid, st_, b2, a, sp)
                key = (score(leg, ns, mid), -len(t))
                if best is None or key > best[0]:
                    best = (key, ns, sp, t)
            per.append((best[1], best[2], best[3]))
        out.append((a, per))
    return out


def between_options(leg: Leg, ns: State, dark):
    down = [c for c, s in ns.status if s == "DOWN"]
    for k in range(len(down) + 1):
        for rs in itertools.combinations(down, k):
            for inten in INTENSITY:
                for buy in (None, "ghost", "decoy", "spoof"):
                    yield rs, inten, buy


def planned_leg(leg: Leg, width=30):
    beam = [(0.0, initial(leg), [])]
    for i in range(RAIDS):
        nxt = []
        for _, st_, log in beam:
            for a, per in raid_options(leg, i, st_):
                real_ns, sp, touched = per[0]
                if i == RAIDS - 1 or real_ns.home_hp <= 0:
                    ev = sum(score(leg, ns) for ns, _, _ in per) / len(per)
                    nxt.append((ev, real_ns, log + [{"raid": i, "alloc": a, "spoof": sp, "after": real_ns,
                                                       "tier": tier(st_, real_ns, touched), "between": None}]))
                    continue
                best_b = None
                for rs, inten, buy in between_options(leg, real_ns, a[1]):
                    evs = []
                    for ns, _, _ in per:
                        if ns.home_hp <= 0:
                            evs.append(score(leg, ns))
                            continue
                        rs_ok = tuple(r for r in rs if dict(ns.status).get(r) == "DOWN")
                        bs = between(leg, ns, a[1], rs_ok, inten, buy)
                        band_pen = (2.0 if bs.heat >= EXTRA_AT else 0) + (3.0 if bs.heat >= STRONG_AT else 0)
                        evs.append(score(leg, bs, True) - band_pen)
                    ev = sum(evs) / len(evs)
                    if best_b is None or ev > best_b[0]:
                        best_b = (ev, rs, inten, buy)
                    nxt.append((ev, between(leg, real_ns, a[1], rs, inten, buy),
                                log + [{"raid": i, "alloc": a, "spoof": sp, "after": real_ns,
                                        "tier": tier(st_, real_ns, touched), "between": (rs, inten, buy)}]))
        nxt.sort(key=lambda x: -x[0])
        dedup, seen = [], set()
        for x in nxt:
            kk = (x[1].status, x[1].heat, x[1].bank, x[1].home_hp, x[1].kit)
            if kk not in seen:
                seen.add(kk)
                dedup.append(x)
        beam = dedup[:width]
    best = max(beam, key=lambda x: score(leg, x[1]))
    return best[1], best[2]


def greedy_leg(leg: Leg):
    """Raid by raid: maximize this raid's EV (kit valued mid-leg), then the best single between-step, myopically."""
    st_ = initial(leg)
    log = []
    for i in range(RAIDS):
        a, per = max(raid_options(leg, i, st_), key=lambda o: sum(score(leg, ns, True) for ns, _, _ in o[1]) / len(o[1]))
        ns, sp, touched = per[0]
        entry = {"raid": i, "alloc": a, "spoof": sp, "after": ns, "tier": tier(st_, ns, touched), "between": None}
        log.append(entry)
        if ns.home_hp <= 0 or i == RAIDS - 1:
            return ns, log
        opt = max(between_options(leg, ns, a[1]), key=lambda o: score(leg, between(leg, ns, a[1], *o), True))
        entry["between"] = opt
        st_ = between(leg, ns, a[1], *opt)
    return st_, log


def naive_leg(leg: Leg):
    """Careless: ghost the biggest live asset every raid while the kit lasts, no decoys, spoof the first live asset on
    the revealed line, repair all, NORMAL intensity, never shop."""
    st_ = initial(leg)
    vals = dict(leg.values)
    log = []
    for i in range(RAIDS):
        raid = leg.raids[i]
        live = sorted((c for c, s in st_.status if s != "TAKEN"), key=lambda c: (-vals[c], c))
        g = (live[0],) if live and kitd(st_)["ghost"] > 0 else ()
        a = (g, (), ())
        b2 = raid.cands[0]
        sp = None
        if kitd(st_)["spoof"] > 0:
            sp = next((c for c in b2 if c in vals and dict(st_.status).get(c) != "TAKEN" and c not in g), None)
        ns, touched = resolve(leg, raid, st_, b2, a, sp)
        log.append({"raid": i, "alloc": a, "spoof": sp, "after": ns, "tier": tier(st_, ns, touched), "between": None})
        if ns.home_hp <= 0 or i == RAIDS - 1:
            return ns, log
        down = tuple(sorted((c for c, s in ns.status if s == "DOWN"), key=lambda c: (-vals[c], c)))
        log[-1]["between"] = (down, "NORMAL", None)
        st_ = between(leg, ns, (), down, "NORMAL", None)
    return st_, log


def first_raid_near(leg: Leg, near=1.0):
    opts = raid_options(leg, 0, initial(leg))
    vals = sorted((sum(score(leg, ns, True) for ns, _, _ in per) / len(per) for _, per in opts), reverse=True)
    return sum(1 for v in vals if v >= vals[0] - near)


if __name__ == "__main__":
    rows = []
    for seed in range(20):
        leg = make_leg(seed)
        p_end, p_log = planned_leg(leg)
        g_end, g_log = greedy_leg(leg)
        n_end, n_log = naive_leg(leg)
        bw = [x["between"] for x in p_log if x["between"]]
        rows.append({"seed": seed, "planned": score(leg, p_end), "greedy": score(leg, g_end), "naive": score(leg, n_end),
                     "p_breach": p_end.home_hp <= 0, "g_breach": g_end.home_hp <= 0, "n_breach": n_end.home_hp <= 0,
                     "p_ghost_raids": sum(bool(x["alloc"][0]) for x in p_log), "p_decoys": sum(len(x["alloc"][2]) for x in p_log),
                     "p_spoofs": sum(x["spoof"] is not None for x in p_log), "p_raids": len(p_log),
                     "p_tiers": [x["tier"] for x in p_log], "p_intensity": [b[1] for b in bw], "p_buys": [b[2] for b in bw],
                     "p_repairs": sum(len(b[0]) for b in bw), "first_near": first_raid_near(leg),
                     "p_strong": sum(x["after"].heat >= STRONG_AT for x in p_log)})
        print(json.dumps(rows[-1]), flush=True)
    raids = sum(r["p_raids"] for r in rows)
    ints = [i for r in rows for i in r["p_intensity"]]
    tiers = [t for r in rows for t in r["p_tiers"]]
    summ = {"mean_regret_vs_greedy": round(st.mean(r["planned"] - r["greedy"] for r in rows), 1),
            "regret_share_ge3": sum(r["planned"] - r["greedy"] >= 3 for r in rows) / len(rows),
            "mean_gap_naive": round(st.mean(r["planned"] - r["naive"] for r in rows), 1),
            "breach_planned": sum(r["p_breach"] for r in rows) / len(rows),
            "breach_greedy": sum(r["g_breach"] for r in rows) / len(rows),
            "breach_naive": sum(r["n_breach"] for r in rows) / len(rows),
            "ghost_use_per_raid": round(sum(r["p_ghost_raids"] for r in rows) / raids, 2),
            "spoof_use_per_raid": round(sum(r["p_spoofs"] for r in rows) / raids, 2),
            "decoys_per_raid": round(sum(r["p_decoys"] for r in rows) / raids, 2),
            "intensity_mix": {k: ints.count(k) for k in INTENSITY}, "tier_mix": {t: tiers.count(t) for t in set(tiers)},
            "buys": {b: sum(x == b for r in rows for x in r["p_buys"]) for b in ("ghost", "decoy", "spoof", None)},
            "first_near": round(st.mean(r["first_near"] for r in rows), 1)}
    print("SUMMARY", json.dumps(summ), flush=True)
    json.dump({"summary": summ, "rows": rows}, open(r"D:/rc_tmp/raid_design_lab/sweep_l3.json", "w"), indent=1)
