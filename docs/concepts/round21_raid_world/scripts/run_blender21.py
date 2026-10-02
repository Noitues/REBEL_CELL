"""Render every round 20 district job with Blender 5.2 headless into ../scratch/bl (logs in ../scratch/logs).

python run_blender20.py            -> all jobs
python run_blender20.py <name> ... -> only the named jobs
Then: blender -b --factory-startup --python vehicles20.py -- <abs>/scratch/bl   (vehicle matrix)
"""
import os
import subprocess
import sys

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "scratch", "bl")
LOGS = os.path.join(ROOT, "scratch", "logs")
# close-up cameras on the three node buildings shown in building_nodes_v2 (same 3/4 angle as the map)
NODE_CAMS = "fw:27,37,72,1200x1040;vault:96,-31,72,1200x1040;safe:27,-104,72,1200x1040"


def ncams(prefix):
    return ";".join(prefix + "_" + c for c in NODE_CAMS.split(";"))


JOBS = {
    # R3 class beacon tiles (Safehouse pad, no figure) + the full map for the dossier polaroids
    "roofB": ["setup", "1", "roof=B", "r3", "cams=B_r3:44,-82,64,1920x1080;B_full:20.01,-38.88,440,1920x1080"],
    # vehicle toggle v2: the round 20 mixed-corp wave, close-up and full map
    "wave": ["wave", "1", "roof=B", "veh=mixed", "cams=W_close:104,-82,150,1920x1080;W_full:20.01,-38.88,440,1920x1080"],
    # station bonus gifs: a Halcyon wave closing on the Safehouse at Heat 75 (chopper on the Safehouse), and the same
    # frame without the heat rigs (the levelled drone operator shoots the chopper down)
    "bonus": ["wave", "3", "roof=B", "r3", "veh=bonus", "t=0.62", "cams=S_bonus:52,-100,165,1920x1080"],
    "bonus_nh": ["wave", "3", "roof=B", "r3", "veh=bonus", "noheat", "tag=S_bonus_nh", "cams=S_bonus_nh:52,-100,165,1920x1080"],
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    names = sys.argv[1:] or list(JOBS)
    for name in names:
        a = JOBS[name]
        args = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "district20.py"), "--", a[0], a[1], OUT] + a[2:]
        log = os.path.join(LOGS, name + ".log")
        with open(log, "w") as f:
            subprocess.run(args, stdout=f, stderr=subprocess.STDOUT)
        ok = "DONE" in open(log).read()
        print(name, "ok" if ok else "FAILED (see %s)" % log, flush=True)
