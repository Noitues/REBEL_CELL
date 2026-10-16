"""HQ Halcyon: plates -> finished stills and video frames (the r3 compose_aaa matte method).

python hq_compose.py stills [names]          -> ../H_*.png (2560 x 1440) + ../plates/H_*_plate.png
python hq_compose.py frames orbit|reveal [a b] [test]  -> ../scratch/fr_<kind>/f###.png (1280 x 720)
The overlay is drawn at 1920 x 1080 twice (on black and on 50 % grey), solved per pixel as out = plate * m + b and
upscaled, so every kit widget is reused unchanged (r3: compose_aaa.py).
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

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
BIG = r"D:\rc_scratch\halcyon"          # render passes and frames (C: is short of space); never inside D:\Godot\rebel_cell
os.makedirs(BIG, exist_ok=True)
W0, H0 = 1920, 1080
FLAT = 0.5


def compose(plate, ov, ui_k=1.0, phase=0.0, focus=None, route_k=1.0):
    W, H = plate.size
    pose = O.pose_of(ov["pose"])
    walked = ov["walked"]
    A = O.anchors(pose, walked)
    st, _ = G.states(walked)
    sc, _ = G.scanned(walked)
    hover = ov.get("hover") if ov.get("hover_k", 0) > 0.5 else None
    zoom = ov.get("zoom", 0.0)
    graded = O.grade(plate, A, st, walked[-1], hover, walked, sc, focus=zoom if focus is None else focus)

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
    if route_k < 1.0:                         # the reveal: the whole overlay draws in at the end (M -> 1, B -> 0)
        M = 1.0 - (1.0 - M) * route_k
        B = B * route_k
    P = np.asarray(graded.convert("RGB"), np.float32) / 255.0
    out = np.clip(P * M + B, 0, 1)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8))


def stills(names=None, bl="bl_stills"):
    ovs = json.load(open(os.path.join(SCR, "ov_stills.json")))
    os.makedirs(os.path.join(ROOT, "plates"), exist_ok=True)
    for name, ov in ovs.items():
        if names and name not in names:
            continue
        stem = os.path.join(BIG, bl, name)                    # HQ_REV_V2: every quality lives in BIG
        if not os.path.exists(stem + "_combined.npy"):
            print("missing", stem)
            continue
        plate = PO.finish(stem, ov["zoom"], t=2.0)
        sfx = "_v2"
        plate.save(os.path.join(ROOT, "plates", name + sfx + "_plate.png"))
        img = compose(plate, ov)
        img.save(os.path.join(ROOT, name + sfx + ".png"))
        print("saved", name, flush=True)


def one(args):
    kind, k, bl, out, size, prune = args
    ovs = json.load(open(os.path.join(SCR, "ov_%s.json" % kind)))
    name = "%s%03d" % (kind[0], k)
    ov = ovs[name]
    stem = os.path.join(BIG if not bl.endswith(("_mini", "_test")) else SCR, bl, name)
    if not os.path.exists(stem + "_combined.npy"):
        return k, os.path.exists(os.path.join(out, "f%03d.png" % k))
    t = k / 24.0
    flash = 0.0
    fxy = None
    if kind == "reveal" and ov.get("t_flash") is not None:
        flash = float(np.exp(-((ov["t"] - ov["t_flash"]) / 0.12) ** 2))
        pose = O.pose_of(ov["pose"])
        e = G.eye_pos()
        p = pose.proj(e, w=size[0])
        fxy = p if p else (size[0] / 2, size[1] * 0.25)
    plate = PO.finish(stem, ov["zoom"], t=t, flash=flash, flash_xy=fxy, iris=0.3 if kind == "reveal" else None)
    ui = ov.get("ui", 1.0) if kind == "reveal" else 1.0
    rk = max(0.0, min(1.0, ui)) if kind == "reveal" else 1.0
    img = compose(plate, ov, ui_k=1.0, phase=(k % 24) / 24.0, route_k=rk)
    img.save(os.path.join(out, "f%03d.png" % k))
    if prune:                                  # the passes are not needed once the frame is composited
        for suf in ("combined", "emit", "voldir", "index", "z"):
            pth = stem + "_" + suf + ".npy"
            if os.path.exists(pth):
                os.remove(pth)
    return k, True


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "stills":
        stills(sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] != "all" else None,
               sys.argv[3] if len(sys.argv) > 3 else "bl_stills")
    elif what == "frames":
        kind = sys.argv[2]
        n = len(json.load(open(os.path.join(SCR, "ov_%s.json" % kind))))
        a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        b = int(sys.argv[4]) if len(sys.argv) > 4 else n
        sub = sys.argv[5] if len(sys.argv) > 5 else ""
        bl = "bl_" + kind + ("_" + sub if sub else "")
        out = os.path.join(BIG if not sub else SCR, "fr_" + kind)
        os.makedirs(out, exist_ok=True)
        from multiprocessing import Pool
        with Pool(6) as pool:
            for k, ok in pool.imap_unordered(one, [(kind, k, bl, out, (1280, 720), not sub and kind != "reveal") for k in range(a, b)]):
                print("frame", k, "ok" if ok else "missing", flush=True)
