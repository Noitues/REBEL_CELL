"""Meridian v3: the TARGET (the keep) against its local background, on a finished plate (designer round 2: the keep
~2x its local background).

python target_values.py <name>     (reads ../scratch/test/<name>_plate.png, the index pass, ../scratch/ov_stills.json)
  target = landmark pixels (pass index 1 / 5) inside the keep's projected box (body top storey + the lantern + spires);
  local background = city / sky pixels (index 0 / 2) in that box grown by 60 %.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_cam as CR  # noqa: E402
import hq_preset as HP  # noqa: E402

name = sys.argv[1]
ROOT = os.path.dirname(HERE)
GC = HP.PRESET["hq"]["compound"]["gantry"]
KX, GY, KT = GC["keep_x"], GC["y"], GC["keep_top"]
hx, hy = GC["keep"]
lz = GC["lantern"][2]
pts = [(KX + sx * (hx + 4), GY + sy * (hy + 4), z) for sx in (-1, 1) for sy in (-1, 1) for z in (KT - 14, KT + lz + 17)]
ov = json.load(open(os.path.join(ROOT, "scratch", "ov_stills.json")))[name]
pose = CR.pose_of(ov["pose"])
im = Image.open(os.path.join(ROOT, "scratch", "test", name + "_plate.png")).convert("RGB")
W, H = im.size
q = [pose.proj(p, w=W) for p in pts]
xs, ys = [p[0] for p in q], [p[1] for p in q]
x0, x1, y0, y1 = int(min(xs)), int(max(xs)), int(min(ys)), int(max(ys))
a = np.asarray(im, np.float32) / 255.0
L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
idx = np.load(os.path.join(HP.PRESET["hq"]["out_big"], "bl_stills_test", name + "_index.npy"))[..., 0]
if idx.shape != L.shape:
    idx = np.asarray(Image.fromarray(idx.astype(np.float32), "F").resize(im.size, Image.NEAREST))
idx = np.round(idx)
box = np.zeros_like(L, bool)
box[max(0, y0):min(H, y1), max(0, x0):min(W, x1)] = True
gx, gy = int((x1 - x0) * 0.6), int((y1 - y0) * 0.6)
big = np.zeros_like(L, bool)
big[max(0, y0 - gy):min(H, y1 + gy), max(0, x0 - gx):min(W, x1 + gx)] = True
tgt = box & np.isin(idx, (1, 5))
bg = big & ~box & np.isin(idx, (0, 2))
t, b = float(np.median(L[tgt])), float(np.median(L[bg]))
print("%s keep box px %d..%d x %d..%d  target %.3f  local bg %.3f  ratio %.2f" % (name, x0, x1, y0, y1, t, b, t / max(b, 1e-4)))
