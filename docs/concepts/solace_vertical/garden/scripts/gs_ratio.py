"""Landmark-to-background ratio in the map frame, garden vs the HQ helix (the "under the HQ's ratio" check).
Three raw cel renders per direction at the same camera: FULL (garden + helix), NOGARDEN (building hidden, lot kept) and NOHELIX. A landmark mask = the pixels that change
when it is hidden (its own pixels and its cast shadow). Ratio = mean luminance of the mask / mean luminance of a 30 px ring round the mask (the local background, the other
landmark's mask excluded), the same definition as the HQ values tool (landmark / local background). python gs_ratio.py A B C"""
import json
import sys

import numpy as np
from PIL import Image, ImageFilter

O = "D:/rc_scratch/solace_v1/garden/out/"


def lum(p):
    a = np.asarray(Image.open(p).convert("RGB"), np.float32) / 255.0
    return a, a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def dil(m, r):
    im = Image.fromarray((m * 255).astype(np.uint8))
    for _ in range(r // 3):
        im = im.filter(ImageFilter.MaxFilter(7))
    return np.asarray(im) > 127


def lab(rgb):
    a = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]], np.float32)
    xyz = a @ M.T / np.array([0.9505, 1.0, 1.089], np.float32)
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


COL = None


def ratio(full, mask, other):
    ring = dil(mask, 30) & ~mask & ~dil(other, 6)
    L1, L2 = lab(COL[mask]).mean(0), lab(COL[ring]).mean(0)
    RES_EXTRA.append(dict(dE=round(float(np.linalg.norm(L1 - L2)), 1), dL=round(float(L1[0] - L2[0]), 1), chroma=round(float(np.hypot(L1[1], L1[2])), 1)))
    return float(full[mask].mean() / max(1e-6, full[ring].mean())), int(mask.sum()), int(ring.sum())


RES_EXTRA = []


res = {}
for k in sys.argv[1:]:
    fa, fl = lum(O + "r%s_full_raw.png" % k)
    COL = fa
    _a, gl = lum(O + "r%s_nog_raw.png" % k)
    _b, hl = lum(O + "r%s_noh_raw.png" % k)
    mg = np.abs(fl - gl) > 0.02
    mh = np.abs(fl - hl) > 0.02
    rg, ng, nrg = ratio(fl, mg, mh)
    rh, nh, nrh = ratio(fl, mh, mg)
    ys, xs = np.where(mg)
    yh, xh = np.where(mh)
    res[k] = dict(garden_ratio=round(rg, 3), hq_ratio=round(rh, 3), garden_px=ng, hq_px=nh, garden_area_vs_hq=round(ng / max(1, nh), 3), garden_lab=RES_EXTRA[-2], hq_lab=RES_EXTRA[-1],
                  garden_h_px=int(np.percentile(ys, 99.5) - np.percentile(ys, 0.5)), hq_h_px=int(np.percentile(yh, 99.5) - np.percentile(yh, 0.5)))
    print(k, res[k])
json.dump(res, open(O + "ratio.json", "w"), indent=1)
