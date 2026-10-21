"""python batch.py <label> <log> -- <cmd words> ';;' <cmd words> ... : take the shared GPU lock, run each command in order, release."""
import subprocess, sys, time
import gpu_lock as GL
label, logf = sys.argv[1], sys.argv[2]
cmds, cur = [], []
for a in sys.argv[4:]:
    if a == ";;":
        cmds.append(cur); cur = []
    else:
        cur.append(a)
if cur:
    cmds.append(cur)
with open(logf, "a") as lf:
    def log(*a):
        lf.write(time.strftime("%H:%M:%S ") + " ".join(map(str, a)) + "\n"); lf.flush()
    GL.acquire(label, poll=60, log=log)
    t0 = time.time()
    try:
        for c in cmds:
            t1 = time.time()
            r = subprocess.run(c, stdout=lf, stderr=subprocess.STDOUT)
            log("cmd", " ".join(c)[-150:], "exit", r.returncode, "%.0f s" % (time.time() - t1))
            if time.time() - t0 > 40 * 60:
                log("40 min budget reached"); break
    finally:
        GL.release(log=log)
