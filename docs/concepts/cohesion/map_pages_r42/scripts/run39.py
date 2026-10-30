"""Round 36: write a cams file and run unified39.py headless (one child process; nothing else is touched).
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
    if name == "scope":                                  # NET36=net_scope.json: the real campaign graph + the fitted raid
        net = L.load_net()
        return [dict(tag="s_city", t=list(v["city"]["t"]), ortho=v["city"]["ortho"], res=[2880, 1620]),
                dict(tag="s_raid", t=net["raid"]["t"], ortho=net["raid"]["ortho"], res=[2880, 1620], ghost=True),
                dict(tag="s_transit", t=net["transit"]["t"], ortho=net["transit"]["ortho"], res=[2880, 1620], ghost=True)]
    if name == "cars":                                   # CARS38=models: the same city with model cars, grid + transit + close
        return [dict(tag="c_city", t=list(v["city"]["t"]), ortho=v["city"]["ortho"], res=[2880, 1620]),
                dict(tag="c_transit", t=list(v["transit"]["t"]), ortho=v["transit"]["ortho"], res=[2880, 1620], ghost=True),
                dict(tag="c_close", t=[2.9, 0.9], ortho=26.0, res=[1920, 1080], samples=24)]
    if name == "r39":                                    # NET36=net_scope.json (the real campaign graph)
        import scope39
        net = L.load_net()
        nb = {n["id"]: n for n in net["nodes"]}
        hq, core = net["hq"]["meridian"], nb["core"]["lot"]
        beyond = (hq[0] + (hq[0] - core[0]) * 0.35, hq[1] + (hq[1] - core[1]) * 0.35)     # room for the HQ + TARGET circle
        below = (core[0] - (hq[0] - core[0]) * 0.15, core[1] - (hq[1] - core[1]) * 0.15)   # room above the legend strip
        vis = [L.W(n["lot"]) for n in net["nodes"] if n["state"] in ("owned", "core", "available", "grey")] + [L.W(below)]
        g = scope39.fit(vis, margin=1.12, lo=380.0, hi=440.0)
        av = sorted((n for n in net["nodes"] if n["state"] == "available"), key=lambda n: (math.hypot(n["lot"][0] - hq[0], n["lot"][1] - hq[1]), n["id"]))
        below2 = (core[0] - (hq[0] - core[0]) * 0.22, core[1] - (hq[1] - core[1]) * 0.22)
        own = [L.W(n["lot"]) for n in net["nodes"] if n["state"] in ("owned", "core")] + [L.W(av[i]["lot"]) for i in (0, 3, 6)] + [L.W(below2)]
        rd = scope39.fit(own, margin=1.45, lo=220.0, hi=380.0)
        print("g_zoom", g, "raid", rd, flush=True)
        if os.environ.get("ONLY39"):
            keep = os.environ["ONLY39"].split(",")
        else:
            keep = None
        out = [dict(tag="g_zoom", t=g["t"], ortho=g["ortho"], res=[2880, 1620]),
                dict(tag="g_full", t=list(v["city"]["t"]), ortho=1000.0, res=[1280, 720], samples=8),
                dict(tag="r_raid", t=rd["t"], ortho=rd["ortho"], res=[2880, 1620], ghost=True),
                dict(tag="t_run", t=net["transit"]["t"], ortho=net["transit"]["ortho"], res=[2880, 1620], ghost=True)]
        return [c for c in out if keep is None or c["tag"] in keep]
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
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "unified39.py"), "--", "meridian_hq", OUT, cf],
                       stdout=f, stderr=subprocess.STDOUT)
    txt = open(log).read()
    print(name, "ok" if "DONE" in txt else "FAILED (see %s)" % log, flush=True)
