"""Round 4: measure the barrier-challenging toggles on top of the round-3 package (pool of 5, take 3, crew anywhere).
Adds decision-depth metrics: drafts (of 10) that admit a clean plan, and the patch price of each draft's cheapest
clean plan (a spread of prices = real draft trade-offs; one dominant draft = an obvious answer)."""
import itertools, json, random, sys
sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import *  # noqa: F403
from concept_g3_merged import price

PKG = {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest", "ice_blocks": True}
SETS = [
    ("package (r3)", {}),
    ("+no_cascade", {"no_cascade": True}),
    ("+auditor_hunts", {"auditor_hunts": True}),
    ("+no_cascade +auditor_hunts", {"no_cascade": True, "auditor_hunts": True}),
]
nodes = list(NODE_HP)
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
out = {}
for name, opt in SETS:
    rules = dict(RULES); rules.update(PKG); rules.update(opt)
    total = clean = 0
    plans = []
    best = {}
    for pick in itertools.combinations(POOL, 3):
        for place in itertools.product(nodes, repeat=3):
            a = {}
            for x, n in zip(pick, place):
                a.setdefault(n, []).append(x)
            for crew in nodes:
                r = run(Plan(a, crew, dict(rules)))
                total += 1
                clean += r.clean
                tg = tuple(v["outcome"] for v in r.nodes.values())
                plans.append((pick, place, crew, tg))
                if r.clean:
                    pr = price(r)
                    if pick not in best or pr < best[pick][0]:
                        best[pick] = (pr, place, crew)
    rng = random.Random(7)
    idx = {(p[0], p[1], p[2]): p[3] for p in plans}
    changed = tried = 0
    for p in rng.sample(plans, 400):
        pick, place, crew, tg = p
        i = rng.randrange(3)
        for n in nodes:
            if n == place[i]:
                continue
            q = list(place); q[i] = n
            tried += 1
            changed += idx[(pick, tuple(q), crew)] != tg
    out[name] = {"clean_pct": round(100 * clean / total, 2), "one_move_pct": round(100 * changed / tried, 1),
                 "drafts_with_clean": len(best),
                 "cheapest_clean_by_draft": {"+".join(k): [v[0], dict(zip(k, v[1])), v[2]] for k, v in sorted(best.items(), key=lambda kv: kv[1][0])}}
    print(name, json.dumps(out[name]), flush=True)
json.dump(out, open(r"D:/rc_tmp/raid_design_lab/rule_metrics_r4.json", "w"), indent=1)
