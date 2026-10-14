"""Round 38 netrun transit: render the close transit camera (one Blender child process).
NET36=net_scope.json python run38.py  -> ../scratch/bl/t_run38_* (still, 2880) and t_run38g_* (GIF frames, 1920)"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault("NET36", "net_scope.json")
import layout36 as L  # noqa: E402

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = os.path.join(ROOT, "scratch", "bl")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    tr = L.load_net()["transit"]
    cams = [dict(tag="t_run38", t=list(tr["t"]), ortho=tr["ortho"], res=[2880, 1620], ghost=True),
            dict(tag="t_run38g", t=list(tr["t"]), ortho=tr["ortho"], res=[1920, 1080], samples=8, ghost=True),
            dict(tag="g_full", t=[5.0, 9.0], ortho=1000.0, res=[1280, 720], samples=8)]
    cf = os.path.join(ROOT, "scratch", "cams_r38.json")
    json.dump(cams, open(cf, "w"), indent=1)
    log = os.path.join(ROOT, "scratch", "r38.log")
    with open(log, "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "unified39.py"), "--", "meridian_hq", OUT, cf],
                       stdout=f, stderr=subprocess.STDOUT)
    print("ok" if "DONE" in open(log).read() else "FAILED, see " + log)
