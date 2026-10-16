"""HQ kit: one GPU-locked Cycles test batch of stills, composed into ../scratch/test/ with value checks.

python hq_test.py <names,..> [quality=test] [key=value ...]
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import gpu_lock  # noqa: E402
import hq_preset as HP  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "scratch", "test")
os.makedirs(OUT, exist_ok=True)
names = sys.argv[1]
q = sys.argv[2] if len(sys.argv) > 2 else "test"
extra = sys.argv[3:]
if not os.environ.get("HQ_LOCK_HELD"):
    gpu_lock.acquire(os.path.basename(ROOT) + " test " + names)
try:
    t0 = time.time()
    subprocess.run([sys.executable, "hq_jobs.py", "stills", q, names] + extra, cwd=HERE)
    print("render %.0f s" % (time.time() - t0), flush=True)
finally:
    if not os.environ.get("HQ_LOCK_HELD"):
        gpu_lock.release()
bl = os.path.join(HP.PRESET["hq"]["out_big"], "bl_stills_" + q)
import hq_compose as C  # noqa: E402
import hq_post as PO  # noqa: E402
import hq_values as V  # noqa: E402
ovs = json.load(open(os.path.join(ROOT, "scratch", "ov_stills.json")))
for n in names.split(","):
    stem = os.path.join(bl, n)
    plate = PO.finish(stem, ovs[n]["zoom"], t=2.0)
    pp = os.path.join(OUT, n + "_plate.png")
    plate.save(pp)
    C.compose(plate, ovs[n]).save(os.path.join(OUT, n + ".png"))
    print(n, V.check(pp, stem, os.path.join(OUT, n + "_thumb.png")), flush=True)
