"""G2 tuning helper (docs/handoff/raid_integration/G2_SIM.md): runs sweep_g1.py on H for a grid of H_* settings
(environment overrides) at 12 and 24 netruns and prints loss / city lost / win / purge / locked / decides per setting.

Run: python tools/raid_concepts/g2_tune.py --campaigns 30 --grid "H_PATCH_PRICE=8,6;H_DOSE_EVERY=3,2" [--variants H]
Output: one JSON per setting under D:/rc_tmp/raid_design_lab/g2/tune/ and a summary line per setting on stdout."""
from __future__ import annotations

import argparse
import itertools
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("G2_TUNE_OUT", r"D:/rc_tmp/raid_design_lab/g2/tune")
COLS = ("loss", "breached", "city_lost", "win", "purge", "locked_at_plan", "response_decides", "b_flip_rate",
        "infected_per_campaign", "home_hit_rate", "sac_rate", "discard_rate")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaigns", type=int, default=30)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--variants", default="H")
    ap.add_argument("--lengths", default="12,24")
    a = ap.parse_args()
    keys, vals = [], []
    for part in a.grid.split(";"):
        k, v = part.split("=")
        keys.append(k)
        vals.append(v.split(","))
    os.makedirs(OUT, exist_ok=True)
    for combo in itertools.product(*vals):
        tag = "_".join("%s%s" % (k[2:].lower(), v.replace(":", "-")) for k, v in zip(keys, combo))
        for n in a.lengths.split(","):
            env = dict(os.environ)
            env.update(dict(zip(keys, combo)))  # keys are H_<NAME> overrides of sweep_g1.H_TUNED
            env["G1_NETRUNS"] = n
            out = os.path.join(OUT, "%s_n%s.json" % (tag, n))
            subprocess.run([sys.executable, os.path.join(HERE, "sweep_g1.py"), "--campaigns", str(a.campaigns),
                            "--variants", a.variants, "--out", out], env=env, check=True, stdout=subprocess.DEVNULL)
            with open(out) as f:
                d = json.load(f)["summary"]
            for v in a.variants.split(","):
                g, nv = d[v]["all"]["greedy"], d[v]["all"]["naive"]
                print("%s n%s %s | G %s | N loss %s" % (tag, n, v, " ".join("%s=%s" % (c, g.get(c)) for c in COLS),
                                                      nv["loss"]), flush=True)


if __name__ == "__main__":
    main()
