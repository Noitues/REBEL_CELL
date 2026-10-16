"""Run one command while holding the shared GPU lock (D:/rc_scratch/GPU_LOCK, owner meridian_v3), then release it.

python locked.py <what> -- <command ...>
Waits (writing D:/rc_scratch/GPU_WAITING_meridian_v3) while another agent holds the lock or an earlier agent waits.
Keep each call's batch under 15 min.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import gpu_lock  # noqa: E402

what = sys.argv[1]
cmd = sys.argv[sys.argv.index("--") + 1:]
gpu_lock.acquire(what, poll=60)
try:
    env = dict(os.environ, HQ_LOCK_HELD="1")
    r = subprocess.run(cmd, cwd=HERE, env=env)
finally:
    gpu_lock.release()
sys.exit(r.returncode)
