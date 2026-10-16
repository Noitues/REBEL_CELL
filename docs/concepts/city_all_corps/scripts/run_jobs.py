"""City-all-corps: run Blender jobs; Cycles jobs go through the shared GPU queue (D:/rc_scratch/GPU_QUEUE.md).

python run_jobs.py main <cam> [res_k]                 Eevee mainline (no lock: a short preview-class render)
python run_jobs.py aaa <cam>[,<cam>] <res_k> <spp>   Cycles AAA-2: waits for the lock (last in order), renders, releases

The lock: GPU_LOCK created atomically only when absent and no earlier-ordered agent has a GPU_WAITING_<name> file;
GPU_WAITING_city_all_corps is kept while waiting and removed on acquiring; release removes our lock only.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import city_preset as CP  # noqa: E402

Q = r"D:\rc_scratch"
LOCK = os.path.join(Q, "GPU_LOCK")
ME = "city_all_corps"
EARLIER = ("storyboard", "halcyon", "hq_halcyon", "hq_others", "new_corps")   # hq_rev queues after city_all_corps (its gpu_lock.EARLIER)
LOG = os.path.join(CP.SCR, "run_jobs.log")


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, "a") as f:
        f.write(s + "\n")


def acquire(what, poll=120):
    wf = os.path.join(Q, "GPU_WAITING_" + ME)
    t0 = time.time()
    while True:
        early = [n for n in EARLIER if os.path.exists(os.path.join(Q, "GPU_WAITING_" + n))]
        if not os.path.exists(LOCK) and not early:
            try:
                fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, ("%s %s %s\n" % (ME, time.strftime("%Y-%m-%d %H:%M:%S"), what)).encode())
                os.close(fd)
                if os.path.exists(wf):
                    os.remove(wf)
                log("GPU lock acquired after %.0f s (%s)" % (time.time() - t0, what))
                return
            except FileExistsError:
                pass
        if not os.path.exists(wf):
            with open(wf, "w") as f:
                f.write("%s %s waiting for %s\n" % (ME, time.strftime("%Y-%m-%d %H:%M:%S"), what))
        time.sleep(poll)


def release():
    if os.path.exists(LOCK) and open(LOCK, errors="replace").read().startswith(ME):
        os.remove(LOCK)
        log("GPU lock released")


def blender(mode, cam, outdir, res_k, spp=64):
    os.makedirs(outdir, exist_ok=True)
    lp = os.path.join(outdir, "%s_%s.log" % (cam, mode))
    t0 = time.time()
    with open(lp, "w") as f:
        r = subprocess.run([CP.BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "city_build.py"), "--",
                            mode, cam, outdir, str(res_k), str(spp)], stdout=f, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    tail = open(lp, errors="replace").read().splitlines()
    tl = [l for l in tail if l.startswith(("TIME", "DONE", "Error", "Traceback")) or "Error" in l]
    log("%s %s res_k %s spp %s: exit %d, %.0f s wall; %s" % (mode, cam, res_k, spp, r.returncode, dt, " | ".join(tl[-4:])))
    return r.returncode


if __name__ == "__main__":
    mode, cams = sys.argv[1], sys.argv[2].split(",")
    res_k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    spp = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    out = os.path.join(CP.SCR, sys.argv[5] if len(sys.argv) > 5 else ("final" if res_k >= 1 else "test"))
    if mode == "aaa":
        acquire("aaa %s %s %s" % (",".join(cams), res_k, spp))
        try:
            for c in cams:
                blender(mode, c, out, res_k, spp)
        finally:
            release()
    else:
        for c in cams:
            blender(mode, c, out, res_k, spp)
