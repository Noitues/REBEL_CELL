"""Round 36: write a cams file and run unified37.py headless (one child process; nothing else is touched).
python run36.py <name> <cams.json written by the caller or one of the presets: stills | preview | zoom>"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import layout36 as L

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
OUT = os.path.join(ROOT, "scratch", "bl")
LOGS = os.path.join(ROOT, "scratch", "logs")


def views():
    net = L.load_net()
    tr = net["transit"]
    return dict(city=dict(t=L.VIEWS["city"]["t"], ortho=L.VIEWS["city"]["ortho"]), raid=dict(t=L.VIEWS["raid"]["t"], ortho=L.VIEWS["raid"]["ortho"]),
                transit=dict(t=tr["t"], ortho=tr["ortho"]))


def zoom_path(n):
    """grid -> raid -> transit: ortho is log-interpolated, the target eased (the camera never cuts)."""
    v = views()
    keys = [v["city"], v["raid"], v["transit"]]
    out = []
    for k in range(n):
        u = k / (n - 1) * 2
        seg = min(1, int(u))
        f = u - seg
        f = f * f * (3 - 2 * f)
        a, b = keys[seg], keys[seg + 1]
        o = math.exp(math.log(a["ortho"]) * (1 - f) + math.log(b["ortho"]) * f)
        # the target follows in screen terms: weight the move by the zoom so the destination stays framed
        g = (a["ortho"] - o) / (a["ortho"] - b["ortho"]) if a["ortho"] != b["ortho"] else f
        t = (a["t"][0] * (1 - g) + b["t"][0] * g, a["t"][1] * (1 - g) + b["t"][1] * g)
        out.append(dict(t=list(t), ortho=o))
    return out


def preset(name):
    v = views()
    if name == "stills":
        return [dict(tag=k, t=list(v[k]["t"]), ortho=v[k]["ortho"], res=[2880, 1620], ghost=k != "city") for k in ("city", "raid", "transit")]
    if name == "preview":
        return [dict(tag="p_" + k, t=list(v[k]["t"]), ortho=v[k]["ortho"], res=[960, 540], samples=4, ghost=True) for k in ("city", "raid", "transit")]
    if name == "zoom":
        return [dict(tag="z%02d" % i, t=c["t"], ortho=c["ortho"], res=[960, 540], samples=8, ghost=True) for i, c in enumerate(zoom_path(30))]
    raise KeyError(name)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    name = sys.argv[1]
    cams = preset(name)
    cf = os.path.join(ROOT, "scratch", "cams_%s.json" % name)
    json.dump(cams, open(cf, "w"), indent=1)
    log = os.path.join(LOGS, name + ".log")
    with open(log, "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "unified37.py"), "--", "meridian_hq", OUT, cf],
                       stdout=f, stderr=subprocess.STDOUT)
    txt = open(log).read()
    print(name, "ok" if "DONE" in txt else "FAILED (see %s)" % log, flush=True)
