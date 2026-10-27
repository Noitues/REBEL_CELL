"""Parity golden for the Solace raid (the Infected Tide, H7C): docs/handoff/raid_integration/SOLACE_RAID_SPEC.md.
The oracle is tools/raid_concepts/sweep_g1.py, variant H7C (H4 + the 2026-10-25 Phase 1 rule changes = H5, + the
2026-10-26 rulings R-I CITY LOST at raid end and R-J known beams aim at owned Sites = H6, + the 2026-10-26 rulings
R-K TAKEN Sites can be retaken, R-L a sentry shields its Site, R-M BATTERED named SITES LOST = H7, + the 2026-10-26
ruling H7c: cadence 3, the shield lasts one beam, an unguarded DOWN Site falls at the raid's close). The GDScript port
(scripts/core/solace_tide_rules.gd) reads tools/raid_concepts/data/solace_raid_golden.json in its parity test.

Contents:
- config: the H4 numbers (rules), the real content numbers they came from (g4_real), and the planner weights
  (oracle-only, never ported).
- graph: the Solace board as the raid sees it (Sites, tiers, base and locked links, Exploits, objectives) and the
  P-target route pool (every Genome Core -> HOME path of at most 5 links, locked links included).
- campaigns: seeded Solace campaigns, every phase in order (NETRUN, BREACH, RAID with DECAY, DRAW, hand, PLAN,
  RESPONSE, the corp's lean and B pick, trace, tier, HQ step), with the state before and after each phase. A campaign
  is replayed by feeding its draws (lines, hand) to the port, never by re-rolling: the port's RngService streams differ
  from Python's random.Random.
- random_raids: random legal raids on states reached in those campaigns (random placement among placements, random
  response among response_options, random A and hunter street, the corp's B by rule).
- random_betweens: random legal HQ steps.
- checks: the small rule functions (hand size, beams fired, HOME damage, breach chance, prices, the Bloom start gap).
Run: python tools/raid_concepts/solace_raid_golden.py [--variant H7C|H7|H6|H5|H4]   (a few seconds)
H7C writes data/solace_raid_golden.json (the port's golden); H7 writes data/solace_raid_golden_h7.json (the H7 golden of
commit 11eb2ec8), H6 data/solace_raid_golden_h6.json (the Phase 3b golden), H5 data/solace_raid_golden_h5.json (the Phase 2 golden of commit 1ea858b0) and H4
data/solace_raid_golden_h4.json (the G4 golden of commit 82322009), all kept reproducible byte for byte."""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g1_geo as G          # noqa: E402
import g4_bloom             # noqa: E402
import sweep_g1 as S        # noqa: E402

OUT = {"H7C": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "solace_raid_golden.json"),
       "H7": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "solace_raid_golden_h7.json"),
       "H6": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "solace_raid_golden_h6.json"),
       "H5": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "solace_raid_golden_h5.json"),
       "H4": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "solace_raid_golden_h4.json")}
VARIANT = "H7C"
FAM = "H7"      # the oracle's concept code of VARIANT (H7C plays as H7 with its levers set)
CAMPAIGNS = (("keys", "greedy", 0), ("keys", "greedy", 1), ("greedy", "greedy", 2), ("random", "greedy", 3),
             ("keys", "naive", 0), ("greedy", "naive", 5), ("keys", "greedy", 11), ("greedy", "greedy", 17))
# H5 only: a second breach failure then a re-take and a win (keys/greedy 5), CITY LOST (keys/naive 4), BREACHED for
# the skilled player (greedy/greedy 4), two DIVERTs (keys/greedy 83); found by search over seeds 0..199.
H5_EXTRA = (("keys", "greedy", 5), ("keys", "naive", 4), ("greedy", "greedy", 4), ("keys", "greedy", 83))
# H6 only (R-I): DECAY puts INFECTED over healthy, the raid is still played, and the campaign ends at its close: CITY LOST
# (random/naive 30) and BREACHED, HOME 0 being checked first (keys/naive 20); found by search over seeds 0..119.
H6_EXTRA = (("random", "naive", 30), ("keys", "naive", 20))
# H7 only: R-K retakes of TAKEN Sites not next to the territory, R-L shields (a sentry's block then a later beam that
# passes its Site): keys/greedy 76 (2 retakes away from the territory) and greedy/greedy 103 (3), both won; found by
# search over seeds 0..199.
H7_EXTRA = (("keys", "greedy", 76), ("greedy", "greedy", 103))
# H7C needs no extra campaign: in its golden a one-beam shield that a later beam passes shows in 21 of the 120 random
# raids (13 campaign raids) and an unguarded hit Site falling at the close in 55 (46).
RANDOM_RAIDS = 120
RANDOM_BETWEENS = 80
RNG_SEED = 2510


def st_from_json(d: dict) -> S.St:
    st = S.St()
    st.heat, st.bank, st.hp = d["heat"], d["bank"], d["home"]
    st.owned = {s: v for s, v in d["owned"]}
    st.deck = tuple(tuple(x) for x in d["deck"])
    st.ghost = d["ghost"]
    st.held = frozenset(d["held"])
    st.pending = tuple(d["pending"])
    st.obj_done = frozenset(d["obj_done"])
    st.deaths, st.lost, st.won = d["deaths"], d["lost"], d["won"]
    st.crossed_h = tuple(d["crossed_heat"])
    st.purge_q = d["purge_queued"]
    st.lost_flag, st.last_lost, st.inf_n = d["lost_since_raid"], d["last_lost"], d["inf_n"]
    st.dose_n, st.asset_n, st.last_sac, st.cools = d["dose_n"], d["asset_n"], d["last_sac"], d["cools"]
    st.wounds_total, st.sites_lost, st.dose_spent = d["infected_total"], d["sites_lost"], d["dose_spent"]
    st.bfails = d.get("breach_fails", 0)
    return st


def config_json() -> dict:
    nums = S.H7 if FAM == "H7" else S.H6 if VARIANT == "H6" else S.H5 if VARIANT == "H5" else S.H4
    rules = {k: v for k, v in nums.items() if not k.startswith("_")}
    if VARIANT == "H4":     # the G4 golden had no H5 keys
        for k in ("HOME_INF", "BREACH_LOSE", "DIVERT", "PENDING_TERRITORY"):
            rules.pop(k, None)
    return {"variant": VARIANT, "rules": rules, "real": nums["_REAL"],
            "lab": {"START_DECK": [list(x) for x in S.START_DECK], "HAND_BASE": S.HAND_BASE,
                    "MAX_PLACED": S.MAX_PLACED, "GHOST_START": S.GHOST_START, "GHOST_HEAT": S.GHOST_HEAT,
                    "SPOOF_HEAT": S.SPOOF_HEAT, "TYPES": list(S.TYPES)},
            "planner_oracle_only": {"SITE_V": S.H4_SITE_V, "HOME_PT": S.H4_HOME_PT, "LETHAL": S.H4_LETHAL,
                                    "HEAT_W": S.H4_HEAT_W, "BAND_W": S.H4_BAND_W, "INF_W": S.H4_INF_W,
                                    "DOSE_V": S.H4_DOSE_V, "GHOST_V": S.H4_GHOST_V, "DOWN_RISK": S.H4_DOWN_RISK,
                                    "EXPLOIT_V": S.H4_EXPLOIT_V, "LOST": S.H4_LOST, "TOP_KEYS": S.TOP_KEYS},
            "python_rng_streams": {"draw": "raid:<seed>:<raid>", "hand": "hand:<seed>:<raid>",
                                   "claim": "claim:<seed>", "death": "death:<seed>:<netrun>",
                                   "asset": "asset:<seed>:<netrun>", "breach": "breach:<seed>:<netrun>"}}


def graph_json(geo) -> dict:
    sites = {}
    for s in geo.sites:
        sites[s] = {"tier": geo.tier[s], "links": sorted(G.SOL_LINKS.get(s, [])),
                    "locked": sorted(b for a, b in G.SOL_LOCKED if a == s), "exploit": s in geo.exploits,
                    "objective_heat": geo.objective_heat.get(s, 0)}
    return {"sites": sites, "home_links": sorted(G.SOL_LINKS["home"]), "core": G.CORE,
            "route_pool": [list(p) for p in geo._all_paths]}


def play_campaign(policy: str, player: str, seed: int) -> dict:
    rec = {"raids": [], "between": [], "golden": []}
    st = S.campaign_h4(policy, player, seed, rec, FAM)
    ref = S.campaign(VARIANT, policy, player, seed)          # the sweep's own run: the golden must match it
    assert (st.won, st.lost, st.heat, st.hp, st.deaths, rec["netruns"]) == \
        (ref["win"], ref["lost"], ref["heat"], ref["hp"], ref["deaths"], ref["netruns"]), (policy, player, seed)
    return {"seed": seed, "policy": policy, "player": player, "steps": rec["golden"], "end": S.state_json(st),
            "netruns": rec["netruns"], "raids": rec["n_raids"]}


def random_raid(geo, st: S.St, rng: random.Random, seed: int, idx: int) -> dict:
    ctx = S.make_ctx(geo, FAM, st, seed, idx)
    places = S.placements(ctx, st, ctx.rel, True)
    place = places[rng.randrange(len(places))]
    heat, sw0, rhand = S.launch(ctx, st, place)
    opts = S.response_options(ctx, sw0, rhand)
    resp = opts[rng.randrange(len(opts))]
    k, h = rng.randrange(3), rng.randrange(2)
    ctx.trace = True
    ns, tr, sw = S.play_one(ctx, st, place, resp, k, 0, None, h)
    return {"seed": seed, "raid": idx, "before": S.state_json(st),
            "draw": S.draw_json(ctx.draw, S.n_known(ctx, heat)), "hand": list(ctx.hand),
            "place": {"sentries": [[c, j] for c, j in sorted(place[0].items())], "ghost": place[1]},
            "n_placements": len(places), "response_options": [list(o) for o in opts], "response": list(resp),
            "a": k, "hunter": h, "lean": sw.lean, "b_pick": sw.bpick, "home_dmg": sw.home_dmg, "trace": sw.trace,
            "tier": tr, "after": S.state_json(ns),
            **({"divert_neighbors": [[list(p) for p in x] for x in ctx.nbrs]} if ctx.nbrs is not None else {})}


def checks() -> dict:
    st = S.St()
    out = {"hand_size": [[h, S.h4_hand(h)] for h in range(0, 101, 5)],
           "known_fired": [[h, S.h4_n_known(h)] for h in range(0, 101, 5)],
           "home_damage": [[h, False, S.h4_home_dmg(h)] for h in range(0, 101, 5)] + [[100, True, S.h4_home_dmg(100, True)]],
           "band": [[h, S.h4_band(h)] for h in (0, 24, 25, 49, 50, 74, 75, 99, 100)]}
    br = []
    for n in range(13):
        st.deck = tuple(sorted(S.START_DECK + tuple(("w%03d" % i, "t1_a", "WOUND") for i in range(n))))
        br.append([n, round(S.h4_breach_chance(st), 6)])
    out["breach_chance"] = br
    out["cool_price"] = [[k, S.H4["_REAL"]["heat_purchase_cost"] + S.H4["_REAL"]["heat_purchase_increment"] * k]
                         for k in range(4)]
    pc = []
    for home, bank in ((50, 0), (40, 3), (21, 100), (7, 12), (1, 0)):
        st.hp, st.bank = home, bank
        pc.append([home, bank] + list(S.h4_patch_cost(st)))
    out["patch"] = pc
    # R-D: the street Bloom's start gap with n INFECTED cards: start_gap(tier) - n * entry_pace(tier, band, keys)
    r = S.H4["_REAL"]
    gaps = []
    for tier in (1, 2, 3):
        for band in range(5):
            for keys in (0, 1):
                ep = g4_bloom.entry_pace(tier, band, keys)
                for n in (0, 1, 2, 3):
                    gaps.append([tier, band, keys, n, ep, r["bloom_start_gap_milli_by_tier"][tier - 1] - n * ep])
    out["bloom_start_gap"] = gaps
    out["breach_chance_formula"] = "max(BREACH_MIN, BREACH_BASE - BREACH_K * infected)"
    return out


def main() -> None:
    global VARIANT, FAM
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="H7C", choices=("H7C", "H7", "H6", "H5", "H4"))
    VARIANT = ap.parse_args().variant
    FAM = S.concept_of(VARIANT)
    S.apply_variant(VARIANT)
    S.set_family(FAM)
    geo = S.geo_for(VARIANT)
    extra = H6_EXTRA if FAM == "H6" else H6_EXTRA + H7_EXTRA if FAM == "H7" else ()
    camps = [play_campaign(*c) for c in (CAMPAIGNS + H5_EXTRA + extra if FAM in S.H5FAM else CAMPAIGNS)]
    rng = random.Random(RNG_SEED)
    pool = [step["after_decay"] if "after_decay" in step else step["before"]
            for c in camps for step in c["steps"] if step["phase"] == "RAID"]
    pool = [p for p in pool if not p["lost"]]
    raids = []
    S.set_family(FAM)
    for i in range(RANDOM_RAIDS):
        st = st_from_json(pool[rng.randrange(len(pool))])
        raids.append(random_raid(geo, st, rng, 9000 + i, rng.randrange(8)))
    betweens = []
    after = [r["after"] for r in raids if not r["after"]["lost"]]
    for i in range(RANDOM_BETWEENS):
        st = st_from_json(after[rng.randrange(len(after))])
        opts = S.between_options(geo, FAM, st)
        o = opts[rng.randrange(len(opts))]
        betweens.append({"before": S.state_json(st), "options": [[x[0], x[1], x[3]] for x in opts],
                         "choice": {"repair": o[0], "build": o[1], "patch": o[3]},
                         "after": S.state_json(S.between(geo, FAM, st, o))})
    out = {"config": config_json(), "graph": graph_json(geo), "campaigns": camps, "random_raids": raids,
           "random_betweens": betweens, "checks": checks()}
    out_path = OUT[VARIANT]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, sort_keys=True, separators=(",", ":"))
    n_steps = sum(len(c["steps"]) for c in camps)
    print("golden: %d campaigns (%d phases), %d random raids, %d random betweens -> %s (%d KB)"
          % (len(camps), n_steps, len(raids), len(betweens), out_path, os.path.getsize(out_path) // 1024))
    for c in camps:
        print(" ", c["policy"], c["player"], c["seed"], "netruns", c["netruns"], "raids", c["raids"], "won", c["end"]["won"],
              "lost", c["end"]["lost"] or "-")


if __name__ == "__main__":
    main()
