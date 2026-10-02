"""Render every district variant with Blender 5.2 headless into ../scratch/bl (logs in ../scratch/logs).

python run_blender.py [variant heat ...]
"""
import os
import subprocess
import sys

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "scratch", "bl")
LOGS = os.path.join(ROOT, "scratch", "logs")
JOBS = [("setup", 1, True), ("setup", 2, False), ("setup", 3, False), ("wave", 2, False)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    jobs = JOBS
    if len(sys.argv) > 2:
        jobs = [(sys.argv[1], int(sys.argv[2]), "day" in sys.argv[3:])]
    for v, h, day in jobs:
        args = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "district.py"), "--", v, str(h), OUT]
        if day:
            args.append("day")
        log = os.path.join(LOGS, "%s_h%d.log" % (v, h))
        with open(log, "w") as f:
            r = subprocess.run(args, stdout=f, stderr=subprocess.STDOUT)
        ok = "DONE" in open(log).read()
        print(v, h, "ok" if ok else "FAILED (see %s)" % log, flush=True)
