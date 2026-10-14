"""V3 dynamic: the occlusion check (run on every still and every video frame).

For each available room (and the current room) of a shot, inside its projected front opening (shrunk 3 px):
  blocked = pixels whose sem class is a facade, mid-row, far, ground or foreground occluder, or a cut / room surface of
            ANOTHER column (a building in front of it);
  links   = pixels covered by link structure (allowed: the route runs in front of rooms, reported only).
python check_occlusion.py stills | video   (prints a table; exits 1 if any available room is > 8 % blocked)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import sgraph3 as G  # noqa: E402
import cam_rig as R  # noqa: E402

SCR = os.path.join(os.path.dirname(HERE), "scratch")
LIMIT = 0.08


def load_sem(path, size=(1920, 1080)):
    im = Image.open(path)
    a = np.asarray(im, np.float32)
    if im.mode.startswith("I;16") or a.max() > 255:
        a = a / 65535.0
    else:
        a = a / 255.0
    if a.ndim == 2:
        a = np.stack([a] * 3, -1)
    img = Image.fromarray((a * 255 + 0.5).astype(np.uint8)).resize(size, Image.NEAREST)
    return np.asarray(img, np.float32) / 255.0


def check(sem, A, nodes):
    out = {}
    for i in nodes:
        p = A["rooms"][i]["front"]
        if not p or any(q is None for q in p):
            out[i] = (None, None)
            continue
        m = Image.new("L", (sem.shape[1], sem.shape[0]), 0)
        ImageDraw.Draw(m).polygon([tuple(q) for q in p], fill=255)
        m = np.asarray(m.filter(ImageFilter.MinFilter(7)), np.float32) > 0
        n = m.sum()
        if n == 0:
            out[i] = (None, None)
            continue
        cls, col = sem[..., 0], sem[..., 2]
        near = lambda v: np.abs(cls - v) < 0.035  # noqa: E731
        other_col = np.abs(col - G.LAYER[i] / 10.0) > 0.035
        blocked = near(0.1) | near(0.6) | near(0.85) | near(0.95) | near(0.2) | ((near(0.3) | near(0.5)) & other_col)
        links = near(0.7)
        out[i] = (float((blocked & m).sum() / n), float((links & m).sum() / n))
    return out


def run(shots, bl):
    worst = 0.0
    for name, state in shots:
        A = json.load(open(os.path.join(bl, "anchors_%s.json" % name)))
        sem = load_sem(os.path.join(bl, "%s_sem.png" % name))
        st, opts = G.states(state["walked"])
        if state.get("zoom", 0) > 0.5:
            nodes = opts
        else:
            nodes = [state["walked"][-1]] + opts
        res = check(sem, A, nodes)
        row = []
        for i in nodes:
            b, l = res[i]
            if b is None:
                row.append("%s off" % i)
                continue
            if i in opts:
                worst = max(worst, b)
            row.append("%s %s blk %4.1f%% lnk %4.1f%%" % (i, "opt" if i in opts else "cur", b * 100, l * 100))
        print("%-12s hidden_fg=%s | %s" % (name, A.get("hidden_fg"), " | ".join(row)))
    print("worst available-room block: %.1f%%" % (worst * 100))
    return worst


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "stills":
        st = R.stills()
        w = run([(n, st[n][1]) for n in st], os.path.join(SCR, "bl"))
    else:
        fr, _ = R.timeline()
        w = run([("v%03d" % k, fr[k][1]) for k in range(len(fr))], os.path.join(SCR, "blv"))
    sys.exit(1 if w > LIMIT else 0)
