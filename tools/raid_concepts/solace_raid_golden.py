"""Parity golden for the Solace raid (the Infected Tide, H4): docs/handoff/raid_integration/SOLACE_RAID_SPEC.md.
The oracle is tools/raid_concepts/sweep_g1.py, variant H4 (G4_PHASE1.md). The future GDScript port
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
Run: python tools/raid_concepts/solace_raid_golden.py   (about 10 s)"""
from __future__ import annotations

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g1_geo as G          # noqa: E402
import g4_bloom             # noqa: E402
import sweep_g1 as S        # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "solace_raid_golden.json")
CAMPAIGNS = (("keys", "greedy", 0), ("keys", "greedy", 1), ("greedy", "greedy", 2), ("random", "greedy", 3),
             ("keys", "naive", 0), ("greedy", "naive", 5), ("keys", "greedy", 11), ("greedy", "greedy", 17))
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
    return st


def config_json() -> dict:
    rules = {k: v for k, v in S.H4.items() if not k.startswith("_")}
    return {"variant": "H4", "rules": rules, "real": S.H4["_REAL"],
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
    st = S.campaign_h4(policy, player, seed, rec)
    ref = S.campaign("H4", policy, player, seed)          # the sweep's own run: the golden must match it
    assert (st.won, st.lost, st.heat, st.hp, st.deaths, rec["netruns"]) == \
        (ref["win"], ref["lost"], ref["heat"], ref["hp"], ref["deaths"], ref["netruns"]), (policy, player, seed)
    return {"seed": seed, "policy": policy, "player": player, "steps": rec["golden"], "end": S.state_json(st),
            "netruns": rec["netruns"], "raids": rec["n_raids"]}


def random_raid(geo, st: S.St, rng: random.Random, seed: int, idx: int) -> dict:
    ctx = S.make_ctx(geo, "H4", st, seed, idx)
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
            "tier": tr, "after": S.state_json(ns)}


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
    geo = S.geo_for("H4")
    camps = [play_campaign(*c) for c in CAMPAIGNS]
    rng = random.Random(RNG_SEED)
    pool = [step["after_decay"] if "after_decay" in step else step["before"]
            for c in camps for step in c["steps"] if step["phase"] == "RAID"]
    pool = [p for p in pool if not p["lost"]]
    raids = []
    for i in range(RANDOM_RAIDS):
        st = st_from_json(pool[rng.randrange(len(pool))])
        raids.append(random_raid(geo, st, rng, 9000 + i, rng.randrange(8)))
    betweens = []
    after = [r["after"] for r in raids if not r["after"]["lost"]]
    for i in range(RANDOM_BETWEENS):
        st = st_from_json(after[rng.randrange(len(after))])
        opts = S.between_options(geo, "H4", st)
        o = opts[rng.randrange(len(opts))]
        betweens.append({"before": S.state_json(st), "options": [[x[0], x[1], x[3]] for x in opts],
                         "choice": {"repair": o[0], "build": o[1], "patch": o[3]},
                         "after": S.state_json(S.between(geo, "H4", st, o))})
    out = {"config": config_json(), "graph": graph_json(geo), "campaigns": camps, "random_raids": raids,
           "random_betweens": betweens, "checks": checks()}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, sort_keys=True, separators=(",", ":"))
    n_steps = sum(len(c["steps"]) for c in camps)
    print("golden: %d campaigns (%d phases), %d random raids, %d random betweens -> %s (%d KB)"
          % (len(camps), n_steps, len(raids), len(betweens), OUT, os.path.getsize(OUT) // 1024))
    for c in camps:
        print(" ", c["policy"], c["player"], c["seed"], "netruns", c["netruns"], "raids", c["raids"], "won", c["end"]["won"],
              "lost", c["end"]["lost"] or "-")


if __name__ == "__main__":
    main()
