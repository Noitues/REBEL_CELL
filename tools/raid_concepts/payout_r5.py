"""Round 5: the payout sweep with the GDScript rounding fix, plus the `plating` corp-trait toggle. For each card:
its marginal value = best net with the card - best net without it (the round-5 draft preview)."""
import itertools, json, sys
sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import *  # noqa: F403
from concept_g3_merged import price as price_r3

SALVAGE, BONUS = 4, 6
PKG = {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest", "ice_blocks": True, "no_cascade": True}
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
nodes = list(NODE_HP)


def price(r):
    return price_r3(r) + sum(INSTALL[k] for k, v in r.nodes.items() if v["outcome"] == "taken")


def net(r):
    k = len({t for ev in r.steps for t, _ in ev["kills"]})
    return SALVAGE * k + (BONUS if r.clean else 0) - price(r)


out = {}
CASES = (("heat50", ROSTER_50, {}), ("heat50 +plating", ROSTER_50, {"plating": True}),
         ("heat75", ROSTER_75, {}), ("heat75 +plating", ROSTER_75, {"plating": True}))
for name, roster, opt in CASES:
    best = {}
    nclean = total = 0
    for pick in itertools.combinations(POOL, 3):
        for place in itertools.product(nodes, repeat=3):
            a = {}
            for x, n in zip(pick, place):
                a.setdefault(n, []).append(x)
            for crew in nodes:
                r = run(Plan(a, crew, dict(RULES, **PKG, **opt)), threats=list(roster))
                total += 1
                nclean += r.clean
                n_ = net(r)
                if pick not in best or n_ > best[pick][0]:
                    best[pick] = (n_, r.clean, {k: v for k, v in a.items()}, crew)
    marg = {}
    for c in POOL:
        w = max(v[0] for k, v in best.items() if c in k)
        wo = max(v[0] for k, v in best.items() if c not in k)
        marg[c] = w - wo
    rows = sorted(best.items(), key=lambda kv: -kv[1][0])
    out[name] = {"clean_pct": round(100 * nclean / total, 2), "marginal": marg,
                 "drafts": [("+".join(k), v) for k, v in rows]}
    print(name, out[name]["clean_pct"], marg, flush=True)
    for k, v in rows[:5]:
        print("   ", "+".join(k), v, flush=True)
json.dump(out, open(r"D:/rc_tmp/raid_design_lab/payout_r5.json", "w"), indent=1)
json.dump({k: {"clean_pct": v["clean_pct"], "marginal": v["marginal"], "best": v["drafts"][:3]} for k, v in out.items()},
          open(r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts/r5_marginal.json", "w"), indent=1)
