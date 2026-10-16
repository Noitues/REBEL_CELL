"""Rebel Cell v3: one GPU-locked Cycles batch (the shared queue, D:/rc_scratch/GPU_QUEUE.md), then compose + values.

python run_v3.py <tag> <quality> <job> [<job> ...]
  job: stills:<names>          e.g. stills:H_overview,H_decision
       shots:<FN>              a graph shot list (e.g. RED_SHOTS; runs with HQ_DISTRICT_ONLY=1 when FN is RED_SHOTS)
Holds D:/rc_scratch/GPU_LOCK only while Blender renders (released before composing). Composes every frame into
D:/rc_scratch/hq_rev/tests/rebel_cell_<name>_<tag>.png (+ _plate.png) and writes values_rebel_cell_<tag>.json.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import gpu_lock  # noqa: E402

TESTS = r"D:\rc_scratch\hq_rev\tests"
LOG = os.path.join(r"D:\rc_scratch\hq_rev\rebel_cell", "v3_batches.log")
os.makedirs(TESTS, exist_ok=True)


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, "a") as f:
        f.write(s + "\n")


tag, q, jobs = sys.argv[1], sys.argv[2], sys.argv[3:]
gpu_lock.acquire("rebel_cell v3 %s %s" % (tag, " ".join(jobs)), log=log)
t0 = time.time()
try:
    for j in jobs:
        kind, _, arg = j.partition(":")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        if kind == "stills":
            args = ["hq_jobs.py", "stills", q, arg]
        else:
            args = ["hq_jobs.py", "shots", arg, q]
            if arg == "RED_SHOTS":
                env["HQ_DISTRICT_ONLY"] = "1"
        t1 = time.time()
        r = subprocess.run([sys.executable] + args, cwd=HERE, env=env)
        log("JOB", " ".join(args), "exit", r.returncode, "%.0f s" % (time.time() - t1))
finally:
    gpu_lock.release(log=log)
log("render batch %s done %.0f s" % (tag, time.time() - t0))

import hq_compose as C  # noqa: E402
import hq_post as PO  # noqa: E402
import hq_preset as HP  # noqa: E402
import rc_values3 as V  # noqa: E402

big = HP.PRESET["hq"]["out_big"]
res = {}
for j in jobs:
    kind, _, arg = j.partition(":")
    if kind == "stills":
        ovs = json.load(open(os.path.join(os.path.dirname(HERE), "scratch", "ov_stills.json")))
        bl = os.path.join(big, "bl_stills" + ("" if q in ("final", "video", "sheet") else "_" + q))
        names = arg.split(",")
    else:
        ovs = json.load(open(os.path.join(os.path.dirname(HERE), "scratch", "ov_%s.json" % arg)))
        bl = os.path.join(big, "bl_%s_%s" % (arg, q))
        names = list(ovs)
    for n in names:
        stem = os.path.join(bl, n)
        if not os.path.exists(stem + "_combined.npy"):
            log("missing", stem)
            continue
        plate = PO.finish(stem, ovs[n]["zoom"], t=2.0)
        pp = os.path.join(TESTS, "rebel_cell_%s_%s_plate.png" % (n, tag))
        plate.save(pp)
        ex = ovs[n].get("extra") or {}
        if not ex.get("ui_off"):
            C.compose(plate, ovs[n]).save(os.path.join(TESTS, "rebel_cell_%s_%s.png" % (n, tag)))
        else:
            plate.save(os.path.join(TESTS, "rebel_cell_%s_%s.png" % (n, tag)))
        res[n] = V.check(pp, stem)
        if kind == "stills":
            try:
                res[n].update(V.target_check(pp, ovs[n]))
            except Exception as e:  # noqa: BLE001
                log("target_check failed", n, e)
        log(n, " ".join("%s %.3f" % (k, v) if isinstance(v, float) else "%s %s" % (k, v) for k, v in res[n].items()))
json.dump(res, open(os.path.join(TESTS, "values_rebel_cell_%s.json" % tag), "w"), indent=1)
log("composed", tag)
