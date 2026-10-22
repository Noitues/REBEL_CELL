"""Run a command while holding the shared GPU lock as ME = solace_bloom_port (D:/rc_scratch/GPU_QUEUE.md), release afterwards.

python gpu_run.py "<label>" <cmd> [args...]
"""
import subprocess
import sys
import time

sys.path.insert(0, r"D:/rc_art/art-pass/docs/concepts/solace_vertical/district/scripts")
sys.dont_write_bytecode = True
import gpu_lock

gpu_lock.ME = "solace_bloom_port"
label = sys.argv[1]
cmd = sys.argv[2:]
gpu_lock.acquire("bloom_port " + label, poll=20)
t0 = time.time()
try:
    r = subprocess.run(cmd)
finally:
    gpu_lock.release()
print("GPU_RUN %s exit %s wall %.0f s" % (label, r.returncode, time.time() - t0), flush=True)
sys.exit(r.returncode)
