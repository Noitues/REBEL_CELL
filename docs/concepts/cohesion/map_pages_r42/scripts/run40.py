"""Round 40: Blender jobs for the raid-gif district (camera from layout40.json cam_real), one child process per variant.

python run40.py [setup noice decoy cars]
  setup  -> setup_h1   (all defences)          noice -> setup_h1_noice (no ICE LOCK on the Firewall)
  decoy  -> setup_h1_decoy (DECOY on the Relay)  cars -> the car-LOD renders (CARS38=models) for cars_lod.png
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = os.path.join(ROOT, "scratch", "bl")
LOGS = os.path.join(ROOT, "scratch", "logs")
sys.path.insert(0, HERE)


def job(name, cams, env):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    cf = os.path.join(ROOT, "scratch", "cams_%s.json" % name)
    json.dump(cams, open(cf, "w"), indent=1)
    e = dict(os.environ)
    e.update(env)
    log = os.path.join(LOGS, name + ".log")
    with open(log, "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "unified40.py"), "--", "meridian_hq", OUT, cf],
                       stdout=f, stderr=subprocess.STDOUT, env=e)
    print(name, "ok" if "DONE" in open(log).read() else "FAILED (see %s)" % log, flush=True)


if __name__ == "__main__":
    import layout36 as L
    lay = json.load(open(os.path.join(L.DST, "layout40.json")))
    cr = lay["cam_real"]
    t = L.lots(cr["target"][0], cr["target"][1])
    cam = dict(t=[t[0], t[1]], ortho=cr["ortho"], res=[2880, 1620], ghost=True)
    env0 = dict(NET36="net_scope.json")
    which = sys.argv[1:] or ["setup", "noice", "decoy"]
    if "setup" in which:
        job("setup", [dict(cam, tag="setup_h1")], dict(env0, DEF40=""))
    if "noice" in which:
        job("noice", [dict(cam, tag="setup_h1_noice")], dict(env0, DEF40="noice"))
    if "decoy" in which:
        job("decoy", [dict(cam, tag="setup_h1_decoy")], dict(env0, DEF40="decoy=relay"))
