"""Round 4: graded payout (designer decision). Schematics = SALVAGE per threat killed + CLEAN_BONUS if clean; net =
payout - patch price. Prints each draft's best net plan, to see whether the best answer spreads across drafts."""
import itertools, json, sys
sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import *  # noqa: F403
from concept_g3_merged import price as price_r3


def price(r):
    """Round 4: a TAKEN node also costs its full install (rebuilt after the reclaim netrun)."""
    return price_r3(r) + sum(INSTALL[k] for k, v in r.nodes.items() if v["outcome"] == "taken")

PKG = {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest", "ice_blocks": True, "no_cascade": True}
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
nodes = list(NODE_HP)


def payout(r, salvage, bonus):
    return salvage * len({k for ev in r.steps for k, _ in ev["kills"]}) + (bonus if r.clean else 0)


out = {}
for salvage, bonus in ((0, 12), (4, 6), (5, 0)):
    best = {}
    nets = []
    for pick in itertools.combinations(POOL, 3):
        for place in itertools.product(nodes, repeat=3):
            a = {}
            for x, n in zip(pick, place):
                a.setdefault(n, []).append(x)
            for crew in nodes:
                r = run(Plan(a, crew, dict(RULES, **PKG)))
                net = payout(r, salvage, bonus) - price(r)
                nets.append(net)
                if pick not in best or net > best[pick][0]:
                    best[pick] = (net, r.clean, dict(zip(pick, place)), crew, {k: v["outcome"] for k, v in r.nodes.items() if v["outcome"] != "holds"}, r.home_before - r.home_after)
    rows = sorted(best.items(), key=lambda kv: -kv[1][0])
    key = f"salvage {salvage} + clean {bonus}"
    out[key] = [("+".join(k), v) for k, v in rows]
    print(key, "top3 net:", [(k, v[0], v[1]) for k, v in out[key][:4]], "gap 1-2:", rows[0][1][0] - rows[1][1][0], flush=True)
json.dump(out, open(r"D:/rc_tmp/raid_design_lab/payout_r4.json", "w"), indent=1)
