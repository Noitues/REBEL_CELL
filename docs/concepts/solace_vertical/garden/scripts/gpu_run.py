"""v5 helper: run a command while holding the shared GPU lock (ME = solace_garden), release it afterwards.

python gpu_run.py "<label>" <cmd> [args...]
"""
import subprocess
import sys
import time

import gpu_lock

label = sys.argv[1]
cmd = sys.argv[2:]
gpu_lock.acquire("garden " + label, poll=30)
t0 = time.time()
try:
    r = subprocess.run(cmd)
finally:
    gpu_lock.release()
print("GPU_RUN %s exit %s wall %.0f s" % (label, r.returncode, time.time() - t0), flush=True)
sys.exit(r.returncode)
