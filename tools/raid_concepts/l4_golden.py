"""Parity golden for the L4 sweep lab (tools/raid_lab_m10, round 4): sweep_l4.py rules (real pick and shape order per raid included).
For 6 seeded legs: the leg (home, values, per raid b1 / extra / extra2 / 3 candidates / hunter own line) and the planned,
greedy and naive lines step by step (state before incl. kit, allocation, spoof, touches, tier, state after the raid,
between choice (repairs, intensity, buy), state after the between step), plus 200 random raid resolutions and 200
random between steps. Writes tools/raid_lab_m10/data/l4_golden.json.
    python tools/raid_concepts/l4_golden.py"""
from __future__ import annotations

import json
import random
from pathlib import Path

import sweep_l2 as L
import sweep_l4 as L3

OUT = Path(__file__).resolve().parents[1] / "raid_lab_m10" / "data" / "l4_golden.json"
LEGS = (0, 3, 5, 8, 11, 14)


def c2(c):
    return [c[0], c[1]]


def enc_state(s: L3.State):
    return {"heat": s.heat, "bank": s.bank, "home_hp": s.home_hp, "status": [[*c2(c), v] for c, v in s.status],
            "kit": dict(s.kit)}


def enc_alloc(a):
    g, dk, dc = a
    return {"ghost": [c2(c) for c in g], "dark": [c2(c) for c in dk], "decoys": [c2(c) for c in dc]}


def enc_leg(leg):
    return {"home": c2(leg.home), "values": [[*c2(c), v] for c, v in leg.values],
            "raids": [{"b1": [c2(c) for c in r.b1], "extra": [c2(c) for c in r.extra], "extra2": [c2(c) for c in r.extra2],
                       "cands": [[c2(c) for c in ln] for ln in r.cands], "own3": [c2(c) for c in r.own3],
                       "real": L3.real_pick(leg, i), "shapes": L3.shape_perm(leg, i)} for i, r in enumerate(leg.raids)]}


def replay(leg, log):
    st = L3.initial(leg)
    steps = []
    for x in log:
        i, a, sp = x["raid"], x["alloc"], x["spoof"]
        raid = leg.raids[i]
        ns, touched = L3.resolve(leg, raid, st, raid.cands[L3.real_pick(leg, i)], a, sp)
        b = x["between"]
        after = L3.between(leg, ns, a[1], *b) if b else ns
        steps.append({"raid": i, "before": enc_state(st), "alloc": enc_alloc(a), "spoof": c2(sp) if sp else None,
                      "touched": [[*c2(c), k] for c, k in touched], "tier": L3.tier(st, ns, touched),
                      "after_raid": enc_state(ns),
                      "between": {"repairs": [c2(c) for c in b[0]], "intensity": b[1], "buy": b[2]} if b else None,
                      "after": enc_state(after), "score_after": L3.score(leg, after)})
        st = after
    return steps


def rand_state(rng, leg):
    status = {c: rng.choice(("OK", "OK", "DOWN", "TAKEN")) for c, _ in leg.values}
    return L3.State(heat=rng.choice((44, 48, 50, 60, 70, 74, 75, 80, 90)), bank=rng.randrange(0, 25),
                    home_hp=rng.randrange(1, L.HOME_HP + 1), status=tuple(sorted(status.items())),
                    kit=tuple(sorted({"ghost": rng.randrange(0, 3), "decoy": rng.randrange(0, 3), "spoof": rng.randrange(0, 3), "dark": rng.randrange(0, 3)}.items())))


def randoms(n=200):
    rng = random.Random(91)
    raids, betweens = [], []
    for _ in range(n):
        seed = rng.choice(LEGS)
        leg = L3.make_leg(seed)
        i = rng.randrange(L.RAIDS)
        st = rand_state(rng, leg)
        a = rng.choice(list(L3.allocations(leg, st)))
        k = rng.randrange(L.CANDIDATES)
        b2 = leg.raids[i].cands[k]
        sp = rng.choice([None] + list(b2)) if dict(st.kit)["spoof"] > 0 else None
        ns, touched = L3.resolve(leg, leg.raids[i], st, b2, a, sp)
        raids.append({"leg": seed, "raid": i, "before": enc_state(st), "alloc": enc_alloc(a), "candidate": k,
                      "spoof": c2(sp) if sp else None, "touched": [[*c2(c), kk] for c, kk in touched],
                      "tier": L3.tier(st, ns, touched), "after_raid": enc_state(ns), "score": L3.score(leg, ns)})
    for _ in range(n):
        seed = rng.choice(LEGS)
        leg = L3.make_leg(seed)
        st = rand_state(rng, leg)
        dark = tuple(rng.sample([c for c, s in st.status if s != "TAKEN"], k=min(1, len([c for c, s in st.status if s != "TAKEN"]))))
        rs, inten, buy = rng.choice(list(L3.between_options(leg, st, dark)))
        after = L3.between(leg, st, dark, rs, inten, buy)
        betweens.append({"leg": seed, "before": enc_state(st), "dark": [c2(c) for c in dark],
                         "repairs": [c2(c) for c in rs], "intensity": inten, "buy": buy, "after": enc_state(after)})
    return raids, betweens


if __name__ == "__main__":
    cfg = {k: getattr(L, k) for k in ("W", "H", "ASSETS", "CANDIDATES", "HOME_HP", "EXTRA_AT", "STRONG_AT", "MAX_DARK",
                                      "START_HEAT", "GHOST_HEAT", "EVADE_HEAT", "START_BANK", "HOME_LOSS_COST", "BREACH", "RAIDS")}
    cfg.update({"KIT_START": L3.KIT_START, "PRICES": L3.PRICES, "INTENSITY": {k: list(v) for k, v in L3.INTENSITY.items()},
                "MAX_DECOYS": L3.MAX_DECOYS, "HEAT_CARRY": L3.HEAT_CARRY, "income": "int(sum(v // 3 over OK non-dark) * mult)",
                "tiers": "BREACHED if home 0; DAMAGED if home lost integrity; EVADED if nothing touched; else HOLDS",
                "decoys": "from the kit, no Schematics", "dark": "from the kit (at most 1 per raid)",
                "tiers_l4": "BATTERED if home intact and (2+ assets newly DOWN or any newly TAKEN)"})
    legs = []
    for s in LEGS:
        leg = L3.make_leg(s)
        _, plog = L3.planned_leg(leg)
        _, glog = L3.greedy_leg(leg)
        _, nlog = L3.naive_leg(leg)
        legs.append({"seed": s, "leg": enc_leg(leg), "planned": replay(leg, plog), "greedy": replay(leg, glog),
                     "naive": replay(leg, nlog)})
        print("leg", s, flush=True)
    rr, bb = randoms()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"config": cfg, "legs": legs, "random_raids": rr, "random_betweens": bb}, indent=1),
                   encoding="utf-8")
    print("wrote", OUT)
