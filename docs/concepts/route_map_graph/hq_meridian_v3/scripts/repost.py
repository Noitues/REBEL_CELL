"""Re-run only the post + compose + value checks on rendered passes (no Blender, no GPU).

python repost.py <names,..> [quality=test]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_compose as C  # noqa: E402
import hq_post as PO  # noqa: E402
import hq_preset as HP  # noqa: E402
import hq_values as V  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "scratch", "test")
q = sys.argv[2] if len(sys.argv) > 2 else "test"
bl = os.path.join(HP.PRESET["hq"]["out_big"], "bl_stills_" + q)
ovs = json.load(open(os.path.join(ROOT, "scratch", "ov_stills.json")))
for n in sys.argv[1].split(","):
    stem = os.path.join(bl, n)
    plate = PO.finish(stem, ovs[n]["zoom"], t=2.0)
    pp = os.path.join(OUT, n + "_plate.png")
    plate.save(pp)
    C.compose(plate, ovs[n]).save(os.path.join(OUT, n + ".png"))
    print(n, V.check(pp, stem, os.path.join(OUT, n + "_thumb.png")), flush=True)
