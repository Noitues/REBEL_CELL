"""Run one GPU batch under the shared lock (D:/rc_scratch/GPU_QUEUE.md), using the shared FIFO helper
docs/concepts/art_deco/scripts/gpu_lock.py with ME = "art_modernart".

python modernart_gpu.py <label> <logfile> -- <cmd1 words> ';;' <cmd2 words> ...
Watchdog on our own child process tree: a command is killed (own PID only, taskkill /PID /T) if the CPU time of its
blender.exe child has not advanced for 15 minutes, or the batch passes 45 minutes. The lock is released in a finally block."""
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "art_deco", "scripts")))
import gpu_lock as GL  # noqa: E402

GL.ME = "art_modernart"


def tree_cpu(pid):
    """Summed CPU seconds of blender.exe processes whose parent chain includes pid (via PowerShell, read-only)."""
    ps = ("$r=0; Get-CimInstance Win32_Process -Filter \"Name='blender.exe'\" | Where-Object { $_.ParentProcessId -eq %d } | "
          "ForEach-Object { $r += (Get-Process -Id $_.ProcessId).CPU }; $r" % pid)
    try:
        o = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60).stdout.strip()
        return float(o or 0.0)
    except Exception:
        return -1.0


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
                p = subprocess.Popen(c, stdout=lf, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
                last, last_t = -1.0, time.time()
                while p.poll() is None:
                    time.sleep(30)
                    cpu = tree_cpu(p.pid)
                    if cpu > last + 1.0:
                        last, last_t = cpu, time.time()
                    stalled = time.time() - last_t > 15 * 60
                    over = time.time() - t0 > 45 * 60
                    if stalled or over:
                        log("watchdog: %s, killing own PID %d" % ("no progress 15 min" if stalled else "45 min cap", p.pid))
                        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
                        break
                log("cmd", " ".join(c)[:120], "exit", p.poll(), "%.0f s" % (time.time() - t1))
                if time.time() - t0 > 45 * 60:
                    log("45 min budget reached, stopping the batch")
                    break
        finally:
            GL.release(log=log)


if __name__ == "__main__":
    main()
