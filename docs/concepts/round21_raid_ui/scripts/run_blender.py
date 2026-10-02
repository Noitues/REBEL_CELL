"""Render every round 20 district variant with Blender 5.2 headless into ../scratch/bl (logs in ../scratch/logs).

python run_blender.py            -> all jobs
python run_blender.py <name> ... -> only the named jobs
"""
import os
import subprocess
import sys

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "scratch", "bl")
LOGS = os.path.join(ROOT, "scratch", "logs")
FHD = "res=1920x1080"
JOBS = {
    "setup1": ["setup", "1"],
    "setup1_decoy": ["setup", "1", "decoy=relay", "tag=setup_h1_decoy"],
    "wave2": ["wave", "2"],
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    names = sys.argv[1:] or list(JOBS)
    for name in names:
        a = JOBS[name]
        args = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "district.py"), "--", a[0], a[1], OUT] + a[2:]
        log = os.path.join(LOGS, name + ".log")
        with open(log, "w") as f:
            subprocess.run(args, stdout=f, stderr=subprocess.STDOUT)
        ok = "DONE" in open(log).read()
        print(name, "ok" if ok else "FAILED (see %s)" % log, flush=True)
