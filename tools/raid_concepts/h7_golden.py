"""Golden data for the H7 Godot lab's parity check (tools/raid_lab_h7/parity_check.gd).
Writes tools/raid_concepts/h7_golden.json: the first 5 seeded legs (rosters), and for leg 0 both cached lines
(h7_leg0.json) re-run through the H7 rules, with per raid: the telegraphed roster (entry, traits), the frozen links,
each node's outcome and integrity after, kills, survivors, the raid net, and the bank after (income included)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from h7_campaign import State, legs, raid_result, roster_for, settle  # noqa: E402

HERE = Path(__file__).parent


def replay(leg, line):
    st = State()
    out = []
    for x in line:
        i = x["raid"]
        roster = roster_for(leg, i, st)
        act = (tuple(x["buy"]), tuple(x["place"]), x["crew"])
        fort, r = raid_result(st, act[0], act[1], act[2], roster)
        ns, raid_net = settle(st, {k: list(v) for k, v in fort.items()}, r, roster, i, act, len(leg))
        kills = sorted({t for ev in r.steps for t, _ in ev["kills"]})
        out.append({
            "raid": i, "buy": list(act[0]), "place": list(act[1]), "crew": act[2],
            "roster": [[t[0], t[1], list(t[2]) if len(t) > 2 else []] for t in roster],
            "frozen": [list(f) for f in r.frozen], "steps": len(r.steps),
            "nodes": {k: [v["outcome"], v["after"]] for k, v in r.nodes.items()},
            "kills": kills, "clean": r.clean, "breached": r.breached,
            "net": raid_net, "bank": ns.bank, "lost": list(ns.lost), "survivors": [list(s) for s in ns.surv],
        })
        st = ns
    return out


if __name__ == "__main__":
    cached = json.loads((HERE / "h7_leg0.json").read_text(encoding="utf-8"))
    leg0 = [[tuple(t) for t in raid] for raid in cached["leg"]]
    gold = {"legs": [[[list(t) for t in raid] for raid in leg] for leg in legs(5)],
            "leg0": {"planned": replay(leg0, cached["planned"]), "greedy": replay(leg0, cached["greedy"])}}
    (HERE / "h7_golden.json").write_text(json.dumps(gold, indent=1), encoding="utf-8")
    for k in ("planned", "greedy"):
        print(k, [(x["net"], x["bank"], x["clean"]) for x in gold["leg0"][k]])
