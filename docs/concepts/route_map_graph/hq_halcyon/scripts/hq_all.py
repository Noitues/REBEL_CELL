"""HQ Halcyon: the whole delivery in priority order, following the GPU queue protocol (D:\\rc_scratch\\GPU_QUEUE.md):
every GPU batch first acquires D:\\rc_scratch\\GPU_LOCK (waiting with GPU_WAITING_halcyon while another agent holds it or
an earlier-ordered agent waits), holds it for at most ~45 min, then releases it. Timings go to ../scratch/timings.json.

python hq_all.py [stages]     stages: hover,orbit,reveal,stills (default hover,orbit,reveal)
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
PY = sys.executable
Q = r"D:\rc_scratch"
LOCK = os.path.join(Q, "GPU_LOCK")
WAIT = os.path.join(Q, "GPU_WAITING_halcyon")
EARLIER = ["storyboard", "new_corps"]    # queue order: storyboard -> hq_halcyon -> ...; new_corps has a designer override block
T = {}
TP = os.path.join(SCR, "timings.json")
if os.path.exists(TP):
    T = json.load(open(TP))


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def acquire():
    while True:
        busy = os.path.exists(LOCK)
        earlier = [e for e in EARLIER if os.path.exists(os.path.join(Q, "GPU_WAITING_" + e))]
        if not busy and not earlier:
            try:
                fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                continue
            os.write(fd, ("hq_halcyon %s" % time.strftime("%Y-%m-%d %H:%M:%S")).encode())
            os.close(fd)
            if os.path.exists(WAIT):
                os.remove(WAIT)
            log("LOCK acquired")
            return
        if not os.path.exists(WAIT):
            with open(WAIT, "w") as f:
                f.write("halcyon waiting since %s" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        log("waiting:", open(LOCK).read().strip() if busy else "", "earlier waiting:", earlier)
        time.sleep(150)


def release():
    if os.path.exists(LOCK) and open(LOCK).read().startswith("hq_halcyon"):
        os.remove(LOCK)
        log("LOCK released")


def step(name, args, gpu=False):
    if gpu:
        acquire()
    t0 = time.time()
    try:
        r = subprocess.run([PY] + args, cwd=HERE)
    finally:
        if gpu:
            release()
    T[name] = round(time.time() - t0, 1)
    json.dump(T, open(TP, "w"), indent=1)
    log("STAGE", name, "exit", r.returncode, "%.0f s" % T[name])
    return r.returncode


stages = sys.argv[1].split(",") if len(sys.argv) > 1 else ["hover", "orbit", "reveal"]
if "stills" in stages:
    step("gpu_stills_main", ["hq_jobs.py", "stills", "final", "H_overview,H_decision_S,H_decision_E"], gpu=True)
if "hover" in stages or "stills" in stages:
    step("gpu_stills_hover", ["hq_jobs.py", "stills", "final", "H_hover_S,H_hover_E"], gpu=True)
    step("compose_stills", ["hq_compose.py", "stills", "all"])
    step("sheet", ["hq_sheet.py"])
for kind in ("orbit", "reveal"):
    if kind in stages:
        for a, b in ((0, 72), (72, 144)):
            step("gpu_%s_%d_%d" % (kind, a, b), ["hq_jobs.py", kind, "video", str(a), str(b)], gpu=True)
            step("compose_%s_%d_%d" % (kind, a, b), ["hq_compose.py", "frames", kind, str(a), str(b)])
        step("encode_" + kind, ["hq_encode.py", kind])
if "flash" in stages:
    # re-render the frames round the beam pass (their passes were pruned) and re-post them with the auto-iris
    step("gpu_reveal_flash", ["hq_jobs.py", "reveal", "video", "60", "72"], gpu=True)
    step("compose_reveal_flash", ["hq_compose.py", "frames", "reveal", "60", "84"])
    step("encode_reveal", ["hq_encode.py", "reveal"])
log("ALL DONE")
