"""Lab round 5 (L5) sweep-raid rules: L4 (sweep_l4.py) plus the L4 critic's three changes, each a designer-delegated
decision (2026-10-22, "run it"):
- THE RESPONSE AFTER THE REVEAL IS A REAL CHOICE: a spoof (kit) is either SKIP (beam 2 skips one node, as before) or
  JAM (the hunter does not run this raid). Either costs SPOOF_HEAT Heat, added after the sweep, so saving now trades
  against the next raid's beam count. (Measured: JAM as "the hunter runs its own line" was never chosen, and a cost of
  4 left the planned line holding in 13 of 18 raids; 2 keeps the trade real.)
- THE SEALED LINES ALWAYS DIFFER: each raid's 3 candidates are re-drawn (seeded) until they are distinct lines whose
  sets of asset/HOME cells are pairwise different and non-empty (at leg start), so the reveal always matters.
- DAMAGE STICKS: at most REPAIR_SLOTS repairs per between step (one crew). DOWN assets pile up; a second find TAKES.
- BREACH RISK IS A RULE THE BETWEEN SCREEN SHOWS: breach_risk(leg, i, state) = over every allocation the next raid
  allows, the fewest sealed lines that still breach with the best response. The lab shows it per intensity card.
Everything else as L4 (seeded real line, shape shuffle, kit incl. dark, shop, intensity, Heat carry 1.0, tiers)."""
from __future__ import annotations

import itertools
import json
import random
import statistics as st
from dataclasses import dataclass, replace

import sweep_l2 as L
from sweep_l2 import EXTRA_AT, H, HOME_HP, NODES, RAIDS, STRONG_AT, Leg

KIT_START = {"ghost": 2, "decoy": 2, "spoof": 2, "dark": 2}
PRICES = {"ghost": 4, "decoy": 3, "spoof": 3, "dark": 3}
INTENSITY = {"LOW": (6, 0.5), "NORMAL": (12, 1.0), "HOT": (18, 1.5)}
KIT_VALUE = 2.5      # planner heuristic only: the value of an unspent kit item mid-leg
MAX_DECOYS = 2
HEAT_CARRY = 1.0    # leg score: Heat carries into the campaign's next raids; each point above START_HEAT costs this
SPOOF_HEAT = 2      # Heat added after the sweep when a spoof (SKIP or JAM) is used
REPAIR_SLOTS = 1    # repairs per between step
JAM = "JAM"         # the spoof that stops the hunter for this raid


def _hits(leg: Leg, ln) -> frozenset:
    cells = set(dict(leg.values)) | {leg.home}
    return frozenset(c for c in ln if c in cells)


def make_leg(seed) -> Leg:
    """sweep_l2.make_leg, then each raid's candidates re-drawn (seeded) until distinct with pairwise different, non-empty
    asset/HOME hit sets."""
    base = L.make_leg(seed)
    raids = []
    for i, r in enumerate(base.raids):
        cands = r.cands
        rng = random.Random(7000 + 10 * seed + i)
        while True:
            hs = [_hits(base, c) for c in cands]
            if len(set(cands)) == len(cands) and all(hs) and len(set(hs)) == len(hs):
                break
            cands = tuple(tuple(L.line(rng)) for _ in range(L.CANDIDATES))
        raids.append(replace(r, cands=cands))
    return Leg(base.home, base.values, tuple(raids))


@dataclass(frozen=True)
class State:
    heat: int = L.START_HEAT
    bank: int = L.START_BANK
    home_hp: int = HOME_HP
    status: tuple = ()
    kit: tuple = (("dark", 2), ("decoy", 2), ("ghost", 2), ("spoof", 2))


def kitd(s: State) -> dict:
    return dict(s.kit)


def with_kit(s: State, **kw) -> tuple:
    k = kitd(s)
    k.update(kw)
    return tuple(sorted(k.items()))


def initial(leg: Leg) -> State:
    return State(status=tuple((c, "OK") for c, _ in leg.values), kit=tuple(sorted(KIT_START.items())))


def real_pick(leg: Leg, i: int) -> int:
    """The corp's real sealed line for raid i (seeded; the player never sees it before the reveal)."""
    return random.Random(9000 + 31 * i + sum(v for _, v in leg.values) + 7 * leg.home[0] + 13 * leg.home[1]).randrange(L.CANDIDATES)


def shape_perm(leg: Leg, i: int) -> list:
    """The lab's shape per candidate for raid i (0 triangle, 1 square, 2 circle), shuffled per raid."""
    perm = list(range(L.CANDIDATES))
    random.Random(5000 + 17 * i + sum(v for _, v in leg.values) + 3 * leg.home[0] + 5 * leg.home[1]).shuffle(perm)
    return perm


def tier(before: State, after: State, touched) -> str:
    if after.home_hp <= 0:
        return "BREACHED"
    if after.home_hp < before.home_hp:
        return "DAMAGED"
    if not touched:
        return "EVADED"
    b, a = dict(before.status), dict(after.status)
    new_down = sum(1 for c, s in a.items() if s == "DOWN" and b.get(c) == "OK")
    new_taken = sum(1 for c, s in a.items() if s == "TAKEN" and b.get(c) != "TAKEN")
    return "BATTERED" if new_down >= 2 or new_taken >= 1 else "HOLDS"


def sweep(leg: Leg, raid: L.Raid, st_: State, b2, ghost, dark, decoys, spoof, heat):
    """sweep_l2.sweep with the JAM spoof: the hunter does not run."""
    status = dict(st_.status)
    hidden = set(ghost) | set(dark)
    touched, first = [], None
    seen = set()
    skip = spoof if spoof is not None and spoof != JAM else None

    def scan(ln, k):
        nonlocal first
        for c in ln:
            if k == "b2" and c == skip:
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
    if heat >= EXTRA_AT:
        scan(raid.extra, "extra")
    if heat >= STRONG_AT:
        scan(raid.extra2, "extra2")
    scan(b2, "b2")
    if spoof != JAM:
        scan([(first[0], y) for y in range(H)] if first else raid.own3, "hunter")
    return touched


def resolve(leg: Leg, raid: L.Raid, st_: State, b2, alloc, spoof=None):
    """One raid. spoof: None, a cell on b2 (SKIP) or JAM. Returns (state after the raid, touches)."""
    ghost, dark, decoys = alloc
    k = kitd(st_)
    assert len(ghost) <= k["ghost"] and len(decoys) <= k["decoy"] and len(dark) <= k["dark"] and (spoof is None or k["spoof"] > 0)
    heat = st_.heat + L.GHOST_HEAT * len(ghost)
    touched = sweep(leg, raid, st_, b2, ghost, dark, set(decoys), spoof, heat)
    status = dict(st_.status)
    home_hp = st_.home_hp
    for c, kind in touched:
        if kind == "asset":
            status[c] = "DOWN" if status[c] == "OK" else "TAKEN"
        elif kind == "home":
            home_hp -= 1
    if not touched:
        heat -= L.EVADE_HEAT
    if spoof is not None:
        heat += SPOOF_HEAT
    ns = State(heat, st_.bank, max(0, home_hp), tuple(sorted(status.items())),
               with_kit(st_, ghost=k["ghost"] - len(ghost), decoy=k["decoy"] - len(decoys), dark=k["dark"] - len(dark),
                        spoof=k["spoof"] - (1 if spoof is not None else 0)))
    return ns, touched


def spoof_options(st_: State, b2) -> list:
    """The responses after the reveal: hold, SKIP one node of the revealed line, or JAM (no hunter this raid)."""
    return [None] + ((list(b2) + [JAM]) if kitd(st_)["spoof"] > 0 else [])


def between(leg: Leg, st_: State, dark, repairs, intensity: str, buy: str | None):
    """Repairs (at most REPAIR_SLOTS, in the order given; repairs past the slot count are ignored), one buy, intensity."""
    vals = dict(leg.values)
    status = dict(st_.status)
    bank = st_.bank
    for c in repairs[:REPAIR_SLOTS]:
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
        for dk in itertools.chain([()], ((c,) for c in rest) if k["dark"] > 0 else ()):
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
            for sp in spoof_options(st_, b2):
                ns, t = resolve(leg, raid, st_, b2, a, sp)
                key = (score(leg, ns, mid), -len(t))
                if best is None or key > best[0]:
                    best = (key, ns, sp, t)
            per.append((best[1], best[2], best[3]))
        out.append((a, per))
    return out


def between_options(leg: Leg, ns: State, dark):
    down = [c for c, s in ns.status if s == "DOWN"]
    for k in range(min(REPAIR_SLOTS, len(down)) + 1):
        for rs in itertools.combinations(down, k):
            for inten in INTENSITY:
                for buy in (None, "ghost", "decoy", "spoof", "dark"):
                    yield rs, inten, buy


def breach_risk(leg: Leg, i: int, st_: State) -> int:
    """For raid i from state st_: the fewest sealed lines that still breach, over every allocation, with the best response
    per line (a line breaches when every response breaches). 0 = some plan avoids a breach on every line."""
    raid = leg.raids[i]
    best = L.CANDIDATES
    for a in allocations(leg, st_):
        n = 0
        for b2 in raid.cands:
            if all(resolve(leg, raid, st_, b2, a, sp)[0].home_hp <= 0 for sp in spoof_options(st_, b2)):
                n += 1
        best = min(best, n)
        if best == 0:
            return 0
    return best


def planned_leg(leg: Leg, width=30):
    beam = [(0.0, initial(leg), [])]
    for i in range(RAIDS):
        nxt = []
        for _, st_, log in beam:
            for a, per in raid_options(leg, i, st_):
                real_ns, sp, touched = per[real_pick(leg, i)]
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
        ns, sp, touched = per[real_pick(leg, i)]
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
        b2 = raid.cands[real_pick(leg, i)]
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


def response_matters(leg: Leg, i: int, st_: State, alloc) -> bool:
    """True if, on the real sealed line, the responses give at least two different leg scores."""
    raid = leg.raids[i]
    b2 = raid.cands[real_pick(leg, i)]
    return len({score(leg, resolve(leg, raid, st_, b2, alloc, sp)[0], True) for sp in spoof_options(st_, b2)}) > 1


def befores(leg: Leg, log):
    st_ = initial(leg)
    out = []
    for x in log:
        out.append(st_)
        if x["between"]:
            st_ = between(leg, x["after"], x["alloc"][1], *x["between"])
    return out


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
                     "p_ghost_raids": sum(bool(x["alloc"][0]) for x in p_log), "p_dark_raids": sum(bool(x["alloc"][1]) for x in p_log), "p_decoys": sum(len(x["alloc"][2]) for x in p_log),
                     "p_spoofs": sum(x["spoof"] is not None for x in p_log), "p_raids": len(p_log),
                     "p_tiers": [x["tier"] for x in p_log], "p_intensity": [b[1] for b in bw], "p_buys": [b[2] for b in bw],
                     "p_repairs": sum(len(b[0]) for b in bw), "first_near": first_raid_near(leg),
                     "p_strong": sum(x["after"].heat >= STRONG_AT for x in p_log),
                     "p_skip": sum(x["spoof"] is not None and x["spoof"] != JAM for x in p_log),
                     "p_jam": sum(x["spoof"] == JAM for x in p_log),
                     "p_resp_matters": sum(response_matters(leg, x["raid"], b, x["alloc"]) for x, b in zip(p_log, befores(leg, p_log))),
                     "p_down_end": sum(s_ == "DOWN" for _, s_ in p_end.status), "p_taken_end": sum(s_ == "TAKEN" for _, s_ in p_end.status)})
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
            "dark_use_per_raid": round(sum(r["p_dark_raids"] for r in rows) / raids, 2),
            "spoof_use_per_raid": round(sum(r["p_spoofs"] for r in rows) / raids, 2),
            "skip_per_raid": round(sum(r["p_skip"] for r in rows) / raids, 2), "jam_per_raid": round(sum(r["p_jam"] for r in rows) / raids, 2),
            "response_matters_share": round(sum(r["p_resp_matters"] for r in rows) / raids, 2),
            "down_at_end": round(st.mean(r["p_down_end"] for r in rows), 2), "taken_at_end": round(st.mean(r["p_taken_end"] for r in rows), 2),
            "decoys_per_raid": round(sum(r["p_decoys"] for r in rows) / raids, 2),
            "intensity_mix": {k: ints.count(k) for k in INTENSITY}, "tier_mix": {t: tiers.count(t) for t in set(tiers)},
            "buys": {b: sum(x == b for r in rows for x in r["p_buys"]) for b in ("ghost", "decoy", "spoof", "dark", None)},
            "first_near": round(st.mean(r["first_near"] for r in rows), 1)}
    print("SUMMARY", json.dumps(summ), flush=True)
    json.dump({"summary": summ, "rows": rows}, open(r"D:/rc_tmp/raid_design_lab/sweep_l5.json", "w"), indent=1)
