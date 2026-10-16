"""Rebel Cell v3 value checks: the frame band (median ~0.14, 25-40 % under 0.10) and the 2x LANDMARK rule on the
TARGET (designer, round 1 review: the MAINFRAME sign over the target is the brightest thing, about 2x its local
background; no 10x neon exception any more).

check(plate.png, stem) -> dict
  median, under_010, over_085          the frame (no UI)
  mf_median                            the MAINFRAME sign (object index 3) median luma
  mf_local_bg                          the median luma of everything else in the sign's box grown by 60 % each way
  mf_ratio                             mf_median / mf_local_bg   (target about 2)
  mf_rank                              the share of the frame brighter than the sign's median (the brightest thing: small)
"""
import sys

import numpy as np
from PIL import Image


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def check(plate_path, stem):
    im = Image.open(plate_path).convert("RGB")
    L = lum(np.asarray(im, np.float32) / 255.0)
    out = dict(median=float(np.median(L)), under_010=float((L < 0.10).mean()), over_085=float((L > 0.85).mean()))
    try:
        idx = np.load(stem + "_index.npy")[..., 0]
    except FileNotFoundError:
        return out
    if idx.shape != L.shape:
        idx = np.asarray(Image.fromarray(idx.astype(np.float32), "F").resize(im.size, Image.NEAREST))
    mf = np.abs(idx - 3) < 0.5
    if mf.sum() < 20:
        out["mf_visible"] = False
        return out
    ys, xs = np.nonzero(mf)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    gy, gx = int((y1 - y0) * 0.6) + 4, int((x1 - x0) * 0.6) + 4
    box = np.zeros_like(mf)
    box[max(0, y0 - gy):y1 + gy, max(0, x0 - gx):x1 + gx] = True
    bg = box & ~mf
    m = float(np.median(L[mf]))
    out.update(mf_visible=True, mf_median=m, mf_local_bg=float(np.median(L[bg])),
               mf_ratio=m / max(1e-4, float(np.median(L[bg]))), mf_rank=float((L > m).mean()),
               mf_px=int(mf.sum()))
    return out


def target_check(plate_path, ov):
    """t4 (designer): the TARGET REGION as the landmark = DISPATCH's building front (the lot round the server room,
    street to roof) + the MAINFRAME sign over it, projected with the frame's pose; ratio of its median luma to the
    median of a ring round it (its box grown 60 %)."""
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import hq_cam as CR
    import hq_preset as HP
    HZ = HP.PRESET["hq"]
    V3, ST = HZ["v3"], HZ["compound"]["stack"]
    fy = ST["cut"] + 0.6
    mx, mw, mz0 = ST["dispatch_x"], V3["mf_w"], V3["mf_z0"]
    mz1 = mz0 + mw * 999 / 246
    lot = next(l_ for l_ in V3["lots"] if l_[0] < mx < l_[1])
    pts = [(lot[0], fy, 0.0), (lot[1], fy, 0.0), (lot[0], fy, lot[2]), (lot[1], fy, lot[2]),
           (mx - mw / 2, fy - 2.4, mz1), (mx + mw / 2, fy - 2.4, mz1)]
    pose = CR.pose_of(ov["pose"])
    im = Image.open(plate_path).convert("RGB")
    L = lum(np.asarray(im, np.float32) / 255.0)
    H, W = L.shape
    q = [pose.proj(p) for p in pts]
    if any(v is None for v in q):
        return dict(target_visible=False)
    s = W / CR.W
    xs, ys = [v[0] * s for v in q], [v[1] * s for v in q]
    x0, x1, y0, y1 = int(max(0, min(xs))), int(min(W, max(xs))), int(max(0, min(ys))), int(min(H, max(ys)))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return dict(target_visible=False)
    reg = np.zeros_like(L, bool)
    reg[y0:y1, x0:x1] = True
    gx, gy = int((x1 - x0) * 0.6), int((y1 - y0) * 0.6)
    box = np.zeros_like(reg)
    box[max(0, y0 - gy):y1 + gy, max(0, x0 - gx):x1 + gx] = True
    bg = box & ~reg
    m, b = float(np.median(L[reg])), float(np.median(L[bg]))
    return dict(target_visible=True, target_median=m, target_local_bg=b, target_ratio=m / max(1e-4, b),
                target_clipped=bool(x1 >= W - 1 or x0 <= 0), target_mean_ratio=float(L[reg].mean() / max(1e-4, L[bg].mean())))


if __name__ == "__main__":
    r = check(sys.argv[1], sys.argv[2])
    print(" ".join("%s %.3f" % (k, v) if isinstance(v, float) else "%s %s" % (k, v) for k, v in r.items()))
