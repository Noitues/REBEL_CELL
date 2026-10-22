"""Run one GPU batch under the shared lock (D:/rc_scratch/GPU_QUEUE.md): acquire, run each command line in order, release.

python deco_gpu.py <label> <logfile> -- <cmd1 words> ';;' <cmd2 words> ...
The lock is released in a finally block (only if it is ours). A batch must stay under about 45 minutes.
"""
import subprocess
import sys
import time

import mg_gpu_lock as GL

HERE = __import__("os").path.dirname(__import__("os").path.abspath(__file__))


WATCH_DIR = r"D:/rc_scratch/hq_styles/meridian_mughal"
NO_PROGRESS_S = 15 * 60


def _latest(root):
    """Newest mtime (and total size) of every file under the scratch tree: any output, log or pass file counts as progress."""
    import os
    best, size = 0.0, 0
    for dp, dn, fn in os.walk(root):
        for f in fn:
            try:
                st = os.stat(os.path.join(dp, f))
            except OSError:
                continue
            best = max(best, st.st_mtime)
            size += st.st_size
    return best, size


def run_watched(cmd, lf, log):
    """Run cmd; kill ONLY its own process tree (taskkill /PID <pid> /T) if nothing under WATCH_DIR changed for 15 minutes."""
    p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)
    last, t_last = _latest(WATCH_DIR), time.time()
    while p.poll() is None:
        time.sleep(20)
        cur = _latest(WATCH_DIR)
        if cur != last:
            last, t_last = cur, time.time()
        elif time.time() - t_last > NO_PROGRESS_S:
            log("watchdog: no progress for 15 min, killing own pid", p.pid)
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"])
            break
    return p


def main():
    label, logf = sys.argv[1], sys.argv[2]
    cmds, cur = [], []
    for a in sys.argv[4:]:
        if a == ";;":
            cmds.append(cur)
            cur = []
        else:
            cur.append(a)
    if cur:
        cmds.append(cur)
    with open(logf, "a") as lf:
        def log(*a):
            s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
            print(s, flush=True)
            lf.write(s + "\n")
            lf.flush()
        GL.acquire(label, poll=150, log=log)
        t0 = time.time()
        try:
            for c in cmds:
                t1 = time.time()
                r = run_watched(c, lf, log)
                log("cmd", " ".join(c)[:120], "exit", r.returncode, "%.0f s" % (time.time() - t1))
                if time.time() - t0 > 45 * 60:
                    log("45 min budget reached, stopping the batch")
                    break
        finally:
            GL.release(log=log)


if __name__ == "__main__":
    main()
