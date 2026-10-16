"""HQ Rebel Cell (option A): the whole delivery in GPU-queue batches, timing every stage into ../scratch/timings.json.

python hq_all.py [stages]   stages: stills,options,red,reveal,post (default all)
The red sequence and the reveal render the whole district (HQ_DISTRICT_ONLY=1); the rest is the option A section.
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

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
PY = sys.executable
TP = os.path.join(SCR, "timings.json")
T = json.load(open(TP)) if os.path.exists(TP) else {}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def step(name, args, district=False):
    t0 = time.time()
    env = dict(os.environ, HQ_VARIANT="A")
    if district:
        env["HQ_DISTRICT_ONLY"] = "1"
    else:
        env.pop("HQ_DISTRICT_ONLY", None)
    r = subprocess.run([PY] + args, cwd=HERE, env=env)
    T[name] = round(time.time() - t0, 1)
    json.dump(T, open(TP, "w"), indent=1)
    log("STAGE", name, "exit", r.returncode, "%.0f s" % T[name])
    return r.returncode


def gpu_batch(name, cmds):
    gpu_lock.acquire(name, log=log)
    try:
        for nm, args, dist in cmds:
            step(nm, args, dist)
    finally:
        gpu_lock.release(log=log)


stages = sys.argv[1].split(",") if len(sys.argv) > 1 else ["stills", "options", "red", "reveal", "post"]
if "stills" in stages or "options" in stages or "red" in stages:
    cmds = []
    if "stills" in stages:
        cmds.append(("gpu_stills", ["hq_jobs.py", "stills", "final", "all"], False))
    if "options" in stages:
        cmds.append(("gpu_options", ["hq_jobs.py", "shots", "OPTION_SHOTS", "final"], False))
    if "red" in stages:
        cmds.append(("gpu_red", ["hq_jobs.py", "shots", "RED_SHOTS", "final"], True))
    gpu_batch("hq_rebel_cell stills", cmds)
    if "stills" in stages:
        step("compose_stills", ["hq_compose.py", "stills", "all"])
    if "options" in stages:
        step("compose_options", ["hq_compose.py", "OPTION_SHOTS", "all", os.path.join(r"D:\rc_scratch\hq_rebel_cell",
                                                                                     "bl_OPTION_SHOTS_final")])
    if "red" in stages:
        step("compose_red", ["hq_compose.py", "RED_SHOTS", "all", os.path.join(r"D:\rc_scratch\hq_rebel_cell",
                                                                              "bl_RED_SHOTS_final")], True)
    step("sheet", ["hq_sheet.py"])
if "reveal" in stages:
    n = 156
    gpu_batch("hq_rebel_cell reveal a", [("gpu_reveal_a", ["hq_jobs.py", "reveal", "video", "0", str(n // 2)], True)])
    gpu_batch("hq_rebel_cell reveal b", [("gpu_reveal_b", ["hq_jobs.py", "reveal", "video", str(n // 2), str(n)], True)])
if "post" in stages or "reveal" in stages:
    step("compose_reveal", ["hq_compose.py", "frames", "reveal"], True)
    step("encode_reveal", ["hq_encode.py", "reveal"], True)
log("ALL DONE")
