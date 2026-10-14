"""Route map graph: render the city plate(s) in one headless Blender child (unified39.py, locked round 39/40 city).
NET36=net_scope.json python render_plates.py  -> ../scratch/bl/t_run38_* (the round 38 v3 transit camera, 2880x1620)"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
os.environ.setdefault("NET36", "net_scope.json")
import layout36 as L  # noqa: E402

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = os.path.join(ROOT, "scratch", "bl")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    tr = L.load_net()["transit"]
    cams = [dict(tag="t_run38", t=list(tr["t"]), ortho=tr["ortho"], res=[2880, 1620], ghost=True)]
    cf = os.path.join(ROOT, "scratch", "cams_rmg.json")
    json.dump(cams, open(cf, "w"), indent=1)
    log = os.path.join(ROOT, "scratch", "rmg.log")
    with open(log, "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "unified39.py"), "--", "meridian_hq", OUT, cf],
                       stdout=f, stderr=subprocess.STDOUT)
    print("ok" if "DONE" in open(log).read() else "FAILED, see " + log)
