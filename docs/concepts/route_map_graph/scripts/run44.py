"""Round 44: Blender 5.2 headless jobs for the map screens (one child process per job; nothing else is touched).

python run44.py [hq] [veh]
  hq   -> h_hq: the HQ / City Grid page camera (solid buildings, no ghost passes), framed on the Cell's network with the
          selected Site (Priority Lane Exchange) near the top and CORE clear of the crew row. target (19.8, 15.6), ortho 440.
  veh  -> the round 20 vehicle matrix (veh_beauty.png + veh_layout.json) for the THREAT INTEL scanned silhouettes.
The raid camera (r_raid) and the transit camera (t_run38) are rendered by run39.py r39 and run38.py (round 39/38 presets).
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
HQ_CAM = dict(tag="h_hq", t=[19.8, 15.6], ortho=440.0, res=[2880, 1620])


def run(args, name, env=None):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    log = os.path.join(LOGS, name + ".log")
    e = dict(os.environ)
    e.update(env or {})
    with open(log, "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python"] + args, stdout=f, stderr=subprocess.STDOUT, env=e)
    txt = open(log, errors="replace").read()
    print(name, "ok" if ("DONE" in txt or "veh_layout" in txt or "Saved" in txt) else "CHECK %s" % log, flush=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["hq", "veh"]
    if "hq" in which:
        cf = os.path.join(ROOT, "scratch", "cams_h44.json")
        json.dump([HQ_CAM], open(cf, "w"), indent=1)
        run([os.path.join(HERE, "unified39.py"), "--", "meridian_hq", OUT, cf], "h44", dict(NET36="net_scope.json"))
    if "veh" in which:
        run([os.path.join(HERE, "vehicles20.py"), "--", OUT], "veh20")
