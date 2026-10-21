"""Run one GPU batch under the shared lock (D:/rc_scratch/GPU_QUEUE.md): acquire, run each command line in order, release.

python deco_gpu.py <label> <logfile> -- <cmd1 words> ';;' <cmd2 words> ...
The lock is released in a finally block (only if it is ours). A batch must stay under about 45 minutes.
"""
import subprocess
import sys
import time

import rat_gpu_lock as GL

HERE = __import__("os").path.dirname(__import__("os").path.abspath(__file__))


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
                r = subprocess.run(c, stdout=lf, stderr=subprocess.STDOUT)
                log("cmd", " ".join(c)[:120], "exit", r.returncode, "%.0f s" % (time.time() - t1))
                if time.time() - t0 > 45 * 60:
                    log("45 min budget reached, stopping the batch")
                    break
        finally:
            GL.release(log=log)


if __name__ == "__main__":
    main()
