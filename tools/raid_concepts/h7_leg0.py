"""Compute and cache leg 0's two H7 lines for the H7 mockups (tools/raid_concepts/h7_leg0.json).
Planned = the player's own whole-leg plan (beam search stands in for a thoughtful player); greedy = plan B, the
one-raid-at-a-time sketch."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from h7_campaign import greedy, legs, planned  # noqa: E402


def dump(st):
    return [{"raid": i, "buy": list(a[0]), "place": list(a[1]), "crew": a[2], "bank": b, "clean": c}
            for i, a, b, c in st.log]


if __name__ == "__main__":
    leg = legs(1)[0]
    g = greedy(leg)
    p = planned(leg, g)
    out = {"leg": leg, "planned": dump(p), "greedy": dump(g)}
    Path(__file__).with_name("h7_leg0.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k in ("planned", "greedy"):
        for x in out[k]:
            print(k, x)
