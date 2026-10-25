"""Pursuit tuning sweep: front speed table, turn budget and catch cost against the kill criteria (20 seeds, beam 600)."""
import itertools
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pursuit as P  # noqa: E402

P.BEAM = 600
SPEEDS = {"slow": (0.5, 0.75, 1.0, 1.25), "mid": (0.75, 1.0, 1.25, 1.5), "fast": (1.0, 1.25, 1.5, 1.75)}
P.LOW_STAYS = True
out = []
for (sname, tab), turns, base in itertools.product(SPEEDS.items(), (16,), (25, 40)):
    P.speed = lambda h, t=tab: t[0] if h < 25 else t[1] if h < 50 else t[2] if h < 75 else t[3]
    P.MAX_TURNS, P.KEY = turns, base
    rows = []
    for seed in range(20):
        nodes = P.grid(1000 + seed)
        res = P.beam(nodes)
        b = P.score(res[0][0])
        sp = P.play(nodes, P.shortest)
        near = [x for x in res if P.score(x[0]) >= b - P.NEAR]
        rows.append((b, P.score(sp), res[0][0][5], len({P.sig(x[0], nodes) for x in near}), res[0][0][0] == P.CORE))
    cat = [r[2] for r in rows]
    rec = {"speed": sname, "turns": turns, "key": base, "best": round(st.mean(r[0] for r in rows), 1),
           "short_opt": sum(r[1] >= r[0] - max(1, 0.05 * abs(r[0])) for r in rows) / 20,
           "catch_mean": round(st.mean(cat), 2), "catch_sd": round(st.pstdev(cat), 2),
           "catch_3_5": sum(3 <= c <= 5 for c in cat) / 20, "routes": round(st.mean(r[3] for r in rows), 1),
           "reach": sum(r[4] for r in rows) / 20}
    out.append(rec)
    print(json.dumps(rec), flush=True)
json.dump(out, open(r"D:/rc_tmp/raid_design_lab/pursuit_sweep2.json", "w"), indent=1)
print("DONE", flush=True)
