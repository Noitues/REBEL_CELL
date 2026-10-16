"""HQ kit: plates -> finished stills and video frames (the r3 compose_aaa matte method, from hq_halcyon).

python hq_compose.py stills [names|all] [bl_dir]   -> ../H_*.png (2560 x 1440) + ../plates/H_*_plate.png
python hq_compose.py sheet  [names|all] [bl_dir]   -> ../scratch/sheet/<name>.png + plates
python hq_compose.py frames reveal [a b] [sub]     -> <big>/fr_reveal/f###.png (1280 x 720)
The overlay is drawn at 1920 x 1080 twice (on black and on 50 % grey), solved per pixel as out = plate * m + b and
upscaled, so every kit widget is reused unchanged.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import hq_graph as G  # noqa: E402
import hq_overlay as O  # noqa: E402
import hq_post as PO  # noqa: E402
import hq_preset as HP  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
BIG = HP.PRESET["hq"]["out_big"]
W0, H0 = 1920, 1080
FLAT = 0.5


def compose(plate, ov, ui_k=1.0, phase=0.0, focus=None, route_k=1.0):
    W, H = plate.size
    if hasattr(G, "set_shot"):
        G.set_shot(ov.get("extra") or {})
    pose = O.pose_of(ov["pose"])
    walked = ov["walked"]
    mt = ov.get("mt", len(walked) - 1)
    A = O.anchors(pose, walked, mt)
    st, _ = G.states(walked, int(mt))
    hover = ov.get("hover") if ov.get("hover_k", 0) > 0.5 else None
    zoom = ov.get("zoom", 0.0)
    graded = O.grade(plate, A, st, walked[-1], hover, walked, focus=zoom if focus is None else focus)

    def up(a):
        if a.shape[1] == W:
            return a
        return np.stack([np.asarray(Image.fromarray(a[..., c].astype(np.float32), "F").resize((W, H), Image.LANCZOS),
                                    np.float32) for c in range(3)], axis=-1)
    o0 = np.asarray(O.overlay(Image.new("RGB", (W0, H0), (0, 0, 0)), A, ov, ui_k=ui_k, phase=phase).convert("RGB"),
                    np.float32) / 255.0
    o1 = np.asarray(O.overlay(Image.new("RGB", (W0, H0), (int(255 * FLAT),) * 3), A, ov, ui_k=ui_k, phase=phase)
                    .convert("RGB"), np.float32) / 255.0
    M = np.clip(up(np.clip((o1 - o0) / FLAT, 0, 1)), 0, 1)
    B = np.clip(up(o0), 0, 1)
    if route_k < 1.0:
        M = 1.0 - (1.0 - M) * route_k
        B = B * route_k
    P = np.asarray(graded.convert("RGB"), np.float32) / 255.0
    out = np.clip(P * M + B, 0, 1)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8))


def stills(names=None, bl=None, kind="stills"):
    ovs = json.load(open(os.path.join(SCR, "ov_%s.json" % kind)))
    bl = bl or os.path.join(BIG, "bl_" + kind)
    pdir = os.path.join(ROOT, "plates") if kind == "stills" else os.path.join(SCR, kind if kind != "sheet" else "sheet")
    odir = ROOT if kind == "stills" else os.path.join(SCR, kind if kind != "sheet" else "sheet")
    os.makedirs(pdir, exist_ok=True)
    for name, ov in ovs.items():
        if names and name not in names:
            continue
        stem = os.path.join(bl, name)
        if not os.path.exists(stem + "_combined.npy"):
            print("missing", stem)
            continue
        plate = PO.finish(stem, ov["zoom"], t=2.0)
        plate.save(os.path.join(pdir, name + "_plate.png"))
        ex = ov.get("extra") or {}
        img = compose(plate, ov, ui_k=0.0 if ex.get("ui_off") else 1.0, route_k=0.0 if ex.get("ui_off") else 1.0)
        img.save(os.path.join(odir, name + ".png"))
        print("saved", name, flush=True)


def one(args):
    kind, k, bl, out, size, prune = args
    ovs = json.load(open(os.path.join(SCR, "ov_%s.json" % kind)))
    name = "%s%03d" % (kind[0], k)
    ov = ovs[name]
    stem = os.path.join(bl, name)
    if not os.path.exists(stem + "_combined.npy"):
        return k, os.path.exists(os.path.join(out, "f%03d.png" % k))
    t = k / 24.0
    plate = PO.finish(stem, ov["zoom"], t=t)
    ui = ov.get("ui", 1.0)
    rk = max(0.0, min(1.0, ov.get("route", 1.0)))
    img = compose(plate, ov, ui_k=max(0.0, min(1.0, ui)), phase=(k % 24) / 24.0, route_k=rk)
    if img.size != tuple(size):
        img = img.resize(tuple(size), Image.LANCZOS)          # video renders at 960 x 540, frames at 1280 x 720
    img.save(os.path.join(out, "f%03d.png" % k))
    if prune:
        for suf in ("combined", "emit", "voldir", "index", "z"):
            pth = stem + "_" + suf + ".npy"
            if os.path.exists(pth):
                os.remove(pth)
    return k, True


if __name__ == "__main__":
    what = sys.argv[1]
    if what in ("stills", "sheet"):
        stills(sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] != "all" else None,
               sys.argv[3] if len(sys.argv) > 3 else None, kind=what)
    elif what not in ("frames",):
        stills(sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] != "all" else None,
               sys.argv[3] if len(sys.argv) > 3 else None, kind=what)
    elif what == "frames":
        kind = sys.argv[2]
        n = len(json.load(open(os.path.join(SCR, "ov_%s.json" % kind))))
        a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        b = int(sys.argv[4]) if len(sys.argv) > 4 else n
        sub = sys.argv[5] if len(sys.argv) > 5 else ""
        bl = os.path.join(BIG, "bl_" + kind + ("_" + sub if sub else ""))
        out = os.path.join(BIG, "fr_" + kind + ("_" + sub if sub else ""))
        os.makedirs(out, exist_ok=True)
        from multiprocessing import Pool
        with Pool(6) as pool:
            for k, ok in pool.imap_unordered(one, [(kind, k, bl, out, (1280, 720), False) for k in range(a, b)]):
                print("frame", k, "ok" if ok else "missing", flush=True)
