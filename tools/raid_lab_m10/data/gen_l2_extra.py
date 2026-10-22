"""Lab-side supplement to l2_golden.json (the python generator tools/raid_concepts/l2_golden.py is outside the lab's
scope and does not export the raids' second extra beam `extra2` nor the EXTRA_AT constant, both needed for Heat >= 75).
For the 6 golden legs this writes data/l2_extra.json: EXTRA_AT, per raid `extra2`, and the NAIVE line step by step in
the golden's step format (the golden has only the planned and greedy lines).
    python tools/raid_lab_m10/data/gen_l2_extra.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "raid_concepts"))

import l2_golden as G  # noqa: E402
import sweep_l2 as L  # noqa: E402


def naive_steps(leg: L.Leg):
    st = L.initial(leg)
    vals = dict(leg.values)
    steps = []
    for i in range(L.RAIDS):
        raid = leg.raids[i]
        live = sorted((c for c, s in st.status if s != "TAKEN"), key=lambda c: (-vals[c], c))
        a = ((live[0],) if live else (), (), ())
        b2 = raid.cands[0]
        sp = next((c for c in b2 if c in vals and dict(st.status).get(c) != "TAKEN" and c not in a[0]), None)
        ns, t = L.resolve(leg, raid, st, b2, a, sp)
        rs = ()
        after = ns
        if ns.home_hp > 0 and i < L.RAIDS - 1:
            rs = tuple(sorted((c for c, s in ns.status if s == "DOWN"), key=lambda c: (-vals[c], c)))
            after = L.between(leg, ns, (), rs)
        steps.append({"raid": i, "before": G.enc_state(st), "alloc": G.enc_alloc(a), "spoof": G.c2(sp) if sp else None,
                      "touched": [[*G.c2(c), k] for c, k in t], "after_raid": G.enc_state(ns),
                      "repairs": [G.c2(c) for c in rs], "after": G.enc_state(after), "score_after": L.score(leg, after)})
        if ns.home_hp <= 0:
            break
        st = after
    return steps


if __name__ == "__main__":
    out = {"extra_at": L.EXTRA_AT, "legs": {}}
    for s in G.LEGS:
        leg = L.make_leg(s)
        out["legs"][str(s)] = {"extra2": [[G.c2(c) for c in r.extra2] for r in leg.raids], "naive": naive_steps(leg)}
    (HERE / "l2_extra.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", HERE / "l2_extra.json")
