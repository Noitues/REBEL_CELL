"""Measure candidate rule changes on the lab scenario (pool of 5, take 3, crew anywhere)."""
import sys, itertools, json, random
sys.path.insert(0, r"D:/Godot/rebel_cell/.claude/worktrees/raid-design-lab-2d2e2e/tools/raid_concepts")
from sim import *
nodes = list(NODE_HP)
POOL = ["TURRET", "ICE", "DECOY", "SENTRY", "RAILGUN"]
SETS = [
    ("today", {}),
    ("+lock", {"target_lock": True}),
    ("+lock +avoid_home", {"target_lock": True, "avoid_home": True}),
    ("+lock +avoid_home +weakest_tie", {"target_lock": True, "avoid_home": True, "tiebreak": "weakest"}),
    ("+... +decoy_radius", {"target_lock": True, "avoid_home": True, "tiebreak": "weakest", "decoy_radius": True}),
    ("+... +ice_blocks", {"target_lock": True, "avoid_home": True, "tiebreak": "weakest", "decoy_radius": True, "ice_blocks": True}),
    ("fixed_routes", {"fixed_routes": True}),
    ("fixed_routes +avoid_home +weakest_tie", {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest"}),
    ("fixed_routes +avoid_home +weakest_tie +ice_blocks", {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest", "ice_blocks": True}),
    ("fixed_routes +avoid_home +ice_blocks +decoy_radius", {"fixed_routes": True, "avoid_home": True, "tiebreak": "weakest", "ice_blocks": True, "decoy_radius": True}),
]
def tags(r):
    return tuple(v["outcome"] for v in r.nodes.values())
def readability(r):
    retarget = 0; via_home = 0; revisits = 0
    for t, path in r.paths.items():
        seen = set()
        for n in path:
            if n in seen: revisits += 1
            seen.add(n)
        tg = [ev["targets"].get(t) for ev in r.steps if t in ev["targets"]]
        retarget += sum(1 for a, b in zip(tg, tg[1:]) if a != b)
        first = r.steps[0]["targets"].get(t) if r.steps else None
        if first and first != "HOME" and path and path[-1] == "HOME": via_home += 1
    return retarget, via_home, revisits
out = {}
for name, opt in SETS:
    rules = dict(RULES); rules.update(opt)
    total = clean = 0; rt = vh = rv = 0; plans = []
    for pick in itertools.combinations(POOL, 3):
        for place in itertools.product(nodes, repeat=3):
            a = {}
            for x, n in zip(pick, place): a.setdefault(n, []).append(x)
            for crew in nodes:
                r = run(Plan(a, crew, dict(rules)))
                total += 1; clean += r.clean
                x, y, z = readability(r); rt += x; vh += y; rv += z
                plans.append((pick, place, crew, tags(r), r.clean))
    # single-move sensitivity on a random sample of plans
    rng = random.Random(7); idx = {(p[0], p[1], p[2]): p[3] for p in plans}
    changed = tried = 0
    for p in rng.sample(plans, 400):
        pick, place, crew, tg, _ = p
        i = rng.randrange(3)
        for n in nodes:
            if n == place[i]: continue
            q = list(place); q[i] = n
            tried += 1; changed += idx[(pick, tuple(q), crew)] != tg
    bare = run(Plan({}, "SAFE", dict(rules)))
    out[name] = {"clean_pct": round(100 * clean / total, 2), "retargets_per_raid": round(rt / total, 2),
                 "spent_at_home_not_target_per_raid": round(vh / total, 3), "revisits_per_raid": round(rv / total, 2),
                 "one_move_changes_outcome_pct": round(100 * changed / tried, 1), "bare": summary(bare)}
    print(name, json.dumps(out[name]))
json.dump(out, open(r"D:/rc_tmp/raid_design_lab/rule_metrics.json", "w"), indent=1)
