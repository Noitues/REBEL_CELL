"""Orbital v3: post the passes of one quality into plates (no UI), without touching the committed set.

python fix_post.py <pass dir> <out dir> <names,..>      Per-frame exposure trims: preset hq.frame_stops (stops), HQ_EXP_STOPS=name:stops,... overrides.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_post as PO  # noqa: E402
import hq_preset as HP  # noqa: E402
import json  # noqa: E402

src, dst, names = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
os.makedirs(dst, exist_ok=True)
ovs = json.load(open(os.path.join(os.path.dirname(HERE), "scratch", "ov_stills.json")))
trim = dict(HP.PRESET["hq"].get("frame_stops", {}))
trim.update(dict((kv.split(":")[0], float(kv.split(":")[1])) for kv in os.environ.get("HQ_EXP_STOPS", "").split(",") if ":" in kv))
for n in names:
    e0 = PO.P["exposure"]
    PO.P["exposure"] = e0 * 2.0 ** trim.get(n, 0.0)
    try:
        PO.finish(os.path.join(src, n), ovs[n]["zoom"], t=2.0).save(os.path.join(dst, n + "_plate.png"))
    finally:
        PO.P["exposure"] = e0
    print("plate", n)
