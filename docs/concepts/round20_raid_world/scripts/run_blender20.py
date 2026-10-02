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
    "roofA": ["setup", "1", "roof=A", "cams=" + ncams("A")],
    "roofC": ["setup", "1", "roof=C", "cams=" + ncams("C")],
    # B (recommended) + the stationed operative: each camera also renders an 'e_' set without the figure
    "roofB": ["setup", "1", "roof=B", "op=breaker", "figtoggle",
              "cams=" + ncams("B") +
              ";B_opsafe:30,-104,46,1200x1040;B_opadj:24,-80,150,1920x1080;B_full:20.01,-38.88,440,1920x1080"],
    # threat vehicles v2 on the map: a mixed-corp wave, close-up and full map
    "wave": ["wave", "1", "roof=B", "op=breaker", "veh=mixed", "cams=W_close:104,-82,150,1920x1080;W_full:20.01,-38.88,440,1920x1080"],
    # heat at raid start (25 / 50 / 75): 20-frame loops of the circling choppers and drones
    "anim1": ["setup", "1", "roof=B", "op=breaker", "anim=20", "tag=anim_h1", "res=960x540"],
    "anim2": ["setup", "2", "roof=B", "op=breaker", "anim=20", "tag=anim_h2", "res=960x540"],
    "anim3": ["setup", "3", "roof=B", "op=breaker", "anim=20", "tag=anim_h3", "res=960x540"],
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
