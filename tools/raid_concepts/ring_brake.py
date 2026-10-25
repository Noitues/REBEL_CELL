"""Round 9, the SPINNER (designer's ring idea) with one BRAKE press (designer decision): once per raid the player may
hold one ring still for one beat, a timing press during the playout. Measured on depth_harness's 10 raids plus the same
raids with a fourth threat (Heat 75):
- gain: the best plan with a brake against the best without (does the press matter?);
- swing: the brake plan landed against missed (the stakes of the press; a miss = no brake);
- brake_shapes: distinct (beat, ring) presses within 1 of the best for the best layout (one obvious moment or several);
- plan_changes: whether planning around the brake changes the layout."""
from __future__ import annotations

import json
import sys
import random
import statistics as st

from depth_harness import scenarios
import ring_siege
from ring_siege import CAP, RINGS, climb, net, random_plan, resolve

if "--survivors" in sys.argv:
    ring_siege.SURVIVOR_COST = 3

SNAP = "--snap" in sys.argv   # the press jumps a ring one slice (+-5 ticks) instead of holding it a tick
BRAKES = ([(b, k, dt) for b in range(1, CAP + 1) for k in range(RINGS) for dt in (-5, 5)] if SNAP else
          [(b, k) for b in range(1, CAP + 1) for k in range(RINGS)])
POOL9 = ["SHIM"] * 4 + ["OVERFLOW"] + ["DEFRAG"] * 2 + ["SANDBOX"] + ["DETOUR"]
SCARCE = "--scarce" in sys.argv   # a 9-slice pool: the plan cannot cover every spoke


def best_brake(plan, sc):
    vals = sorted(((net(resolve(plan, sc, br)), br) for br in BRAKES), key=lambda x: -x[0])
    return vals


def run():
    rows = []
    scs = scenarios()
    import sys
    if "--hard" in sys.argv:   # 6 threats, 2 per spoke: the best plan cannot hold everything
        scs = [sc + [("BAILIFF", "C1"), ("HAULER", "C2"), ("ENFORCER#2", "C1")] for sc in scs]
    else:
        scs = scs + [sc + [("BAILIFF", "C1")] for sc in scs]
    for si, sc in enumerate(scs):
        rng = random.Random(300 + si)
        cache: dict = {}
        best = None
        for _ in range(8):
            q, v = climb(random_plan(rng, POOL9 if SCARCE else None), sc, cache)
            if best is None or v > best[1]:
                best = (q, v)
        plan, nobrake = best
        bb = best_brake(plan, sc)
        # re-climb a few layouts scored WITH their best brake (does the brake change the plan?)
        joint = (plan, bb[0][0], bb[0][1])
        for _ in range(3):
            q, _v = climb(random_plan(rng, POOL9 if SCARCE else None), sc, cache)
            b2 = best_brake(q, sc)
            if b2[0][0] > joint[1]:
                joint = (q, b2[0][0], b2[0][1])
        shapes = sum(1 for v, _ in bb if v >= bb[0][0] - 1)
        rows.append({"scenario": si, "threats": len(sc), "nobrake": nobrake, "brake": joint[1],
                     "gain": joint[1] - nobrake, "swing": joint[1] - net(resolve(joint[0], sc)),
                     "brake_shapes": shapes, "plan_changes": joint[0].key() != plan.key(), "press": joint[2]})
        print(json.dumps(rows[-1]), flush=True)
    summ = {"mean_gain": round(st.mean(r["gain"] for r in rows), 1),
            "gain_share": sum(r["gain"] > 0 for r in rows) / len(rows),
            "mean_swing": round(st.mean(r["swing"] for r in rows), 1),
            "mean_brake_shapes": round(st.mean(r["brake_shapes"] for r in rows), 1),
            "plan_changes_share": sum(r["plan_changes"] for r in rows) / len(rows)}
    print("SUMMARY", json.dumps(summ), flush=True)
    json.dump({"summary": summ, "rows": rows}, open(r"D:/rc_tmp/raid_design_lab/ring_brake" + "".join(f for f in ("_hard", "_snap", "_scarce", "_survivors") if "-" + f[1:] in " ".join(sys.argv) or "--" + f[1:] in sys.argv) + ".json", "w"), indent=1)


if __name__ == "__main__":
    run()
