"""HQ others: ONE GPU-locked batch of commands across corps, then CPU commands (compose / encode) after the release.

python hq_batch.py "gpu:<corp>:<script args...>" ... "cpu:<corp>:<script args...>" ...   (env: KEY=VAL;KEY=VAL after a
second '|' e.g. "gpu:rebel_cell:hq_jobs.py reveal video|HQ_DISTRICT_ONLY=1")
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import gpu_lock  # noqa: E402

BASE = os.path.dirname(os.path.dirname(HERE))


def run(item):
    kind, corp, rest = item.split(":", 2)
    cmd, _, envs = rest.partition("|")
    env = dict(os.environ)
    for kv in filter(None, envs.split(";")):
        k, _, v = kv.partition("=")
        env[k] = v
    d = os.path.join(BASE, "hq_" + corp, "scripts")
    t0 = time.time()
    r = subprocess.run([sys.executable] + cmd.split(), cwd=d, env=env)
    print(time.strftime("%H:%M:%S"), kind, corp, cmd, envs, "exit", r.returncode, "%.0f s" % (time.time() - t0), flush=True)


gpu = [a for a in sys.argv[1:] if a.startswith("gpu:")]
cpu = [a for a in sys.argv[1:] if a.startswith("cpu:")]
if gpu:
    gpu_lock.acquire("batch " + " / ".join(a.split(":")[1] for a in gpu))
    try:
        for a in gpu:
            run(a)
    finally:
        gpu_lock.release()
for a in cpu:
    run(a)
print("BATCH DONE", flush=True)
