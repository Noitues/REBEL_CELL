"""Render every round 19 district variant with Blender 5.2 headless into ../scratch/bl (logs in ../scratch/logs).

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
    "setup1": ["setup", "1", "day"],
    "setup1_cyan": ["setup", "1", "link=cyan", "tag=setup_h1_cyan"],
    "setup2": ["setup", "2"],
    "setup3": ["setup", "3"],
    "wave2": ["wave", "2"],
    "anim3": ["setup", "3", "anim=24", "tag=anim_h3", "res=960x540"],
    # close-ups of the three building-node designs (server room / rooftop dish / shopfront)
    "bn_vault": ["setup", "1", "cam=96,-34,78", "tag=bn_vault", FHD, "day"],
    "bn_relay": ["setup", "1", "cam=-44,-30,92", "tag=bn_relay", FHD, "day"],
    "bn_safe": ["setup", "1", "cam=26,-106,74", "tag=bn_safe", FHD, "day"],
    # world detail before / after (round 18 facets vs round 19)
    "wd_new": ["setup", "1", "cam=-20,-15,150", "tag=wd_new", FHD, "noheat", "day"],
    "wd_old": ["setup", "1", "cam=-20,-15,150", "tag=wd_old", FHD, "noheat", "old", "day"],
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
