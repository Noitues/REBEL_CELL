"""HQ kit: the whole delivery for one corp in GPU-queue batches, timing every stage into ../scratch/timings.json.

python hq_all.py [stages]   stages: stills,reveal,post (default all)
Batches (each holds D:/rc_scratch/GPU_LOCK, at most ~45 min): 1 stills (final) + the sheet shots; 2 + 3 the reveal in
two halves. Compositing, the sheet and the encode run without the lock.
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


def step(name, args):
    t0 = time.time()
    r = subprocess.run([PY] + args, cwd=HERE)
    T[name] = round(time.time() - t0, 1)
    json.dump(T, open(TP, "w"), indent=1)
    log("STAGE", name, "exit", r.returncode, "%.0f s" % T[name])
    return r.returncode


EXTRA_GPU = [("gpu_board", ["hq_jobs.py", "launch", "board"]), ("gpu_strike", ["hq_jobs.py", "launch", "strike"])]


def gpu_batch(name, cmds):
    gpu_lock.acquire(name, log=log)
    try:
        for nm, args in cmds:
            step(nm, args)
    finally:
        gpu_lock.release(log=log)


stages = sys.argv[1].split(",") if len(sys.argv) > 1 else ["stills", "reveal", "post"]
if "one" in stages:
    # everything that needs the GPU in ONE locked batch (the queue is contended), then the CPU stages
    n = int(subprocess.run([PY, "-c", "import sys; sys.path.insert(0, '.'); sys.dont_write_bytecode = True; "
                            "import hq_jobs as J; print(len(J.reveal()))"], cwd=HERE, capture_output=True,
                           text=True).stdout.strip() or 156)
    gpu_batch(os.path.basename(ROOT) + " finals", [("gpu_stills", ["hq_jobs.py", "stills", "final", "all"]),
                                                  ("gpu_sheet", ["hq_jobs.py", "sheet", "sheet", "all"]),
                                                  ("gpu_reveal", ["hq_jobs.py", "reveal", "video", "0", str(n)])]
              + [(nm, a) for nm, a in EXTRA_GPU])
    stages = ["compose", "post"]
if "compose" in stages:
    step("compose_stills", ["hq_compose.py", "stills", "all"])
    step("compose_sheet", ["hq_compose.py", "sheet", "all"])
    step("sheet", ["hq_sheet.py"])
    step("launch_board", ["hq_launch_board.py"])
if "stills" in stages:
    gpu_batch(os.path.basename(ROOT) + " stills", [("gpu_stills", ["hq_jobs.py", "stills", "final", "all"]),
                                                  ("gpu_sheet", ["hq_jobs.py", "sheet", "sheet", "all"])])
    step("compose_stills", ["hq_compose.py", "stills", "all"])
    step("compose_sheet", ["hq_compose.py", "sheet", "all"])
    step("sheet", ["hq_sheet.py"])
    step("launch_board", ["hq_launch_board.py"])
if "reveal" in stages:
    n = int(subprocess.run([PY, "-c", "import sys; sys.path.insert(0, '.'); sys.dont_write_bytecode = True; "
                            "import hq_jobs as J; print(len(J.reveal()))"], cwd=HERE, capture_output=True,
                           text=True).stdout.strip() or 156)
    h = n // 2
    gpu_batch(os.path.basename(ROOT) + " reveal a", [("gpu_reveal_a", ["hq_jobs.py", "reveal", "video", "0", str(h)])])
    gpu_batch(os.path.basename(ROOT) + " reveal b", [("gpu_reveal_b", ["hq_jobs.py", "reveal", "video", str(h), str(n)])])
if "post" in stages or "reveal" in stages:
    step("compose_reveal", ["hq_compose.py", "frames", "reveal"])
    step("encode_reveal", ["hq_encode.py", "reveal"])
log("ALL DONE")
