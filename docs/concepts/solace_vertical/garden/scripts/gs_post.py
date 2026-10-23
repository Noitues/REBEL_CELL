"""Finish a gs_scene.py stem (npy passes) with the HQ / r3 "real" post (hq_post.finish: HDR bloom, rain, grade, vignette, CA, grain),
at an exposure solved so the median display luminance hits the target (AAA-2: 0.12-0.15). python gs_post.py <stem> <out.png> [median 0.14] [zoom 0.9]"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_post as PO  # noqa: E402


HI_FRAC = 0.035


def lum(im):
    a = np.asarray(im.convert("RGB"), np.float32) / 255.0
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def small_stem(stem, k=2):
    out = stem + "_s%d" % k
    for nm in ("combined", "emit", "voldir"):
        p = stem + "_%s.npy" % nm
        if os.path.exists(p):
            a = np.load(p).astype(np.float32)
            H, W = a.shape[:2]
            np.save(out + "_%s.npy" % nm, PO.resize_f(a, (W // k, H // k)).astype(np.float16))
    return out


def solve(stem, target, zoom):
    ss = small_stem(stem)
    PO.P["exposure_zoom_k"] = 0.0
    lo, hi = 0.05, 40.0
    lo2, hi2 = 0.05, 40.0
    for _ in range(14):
        mid = (lo * hi) ** 0.5
        PO.P["exposure"] = mid
        im_ = PO.finish(ss, zoom, t=2.0)
        L_ = lum(im_)
        m = float(np.median(L_))
        if m < target:
            lo = mid
        else:
            hi = mid
        mid2 = (lo2 * hi2) ** 0.5                                      # the highlight limiter: at most `HI_FRAC` of the frame above 0.85
        PO.P["exposure"] = mid2
        L2 = lum(PO.finish(ss, zoom, t=2.0))
        if float((L2 > 0.85).mean()) > HI_FRAC:
            hi2 = mid2
        else:
            lo2 = mid2
    lo = min(lo, lo2)
    hi = min(hi, hi2)
    for nm in ("combined", "emit", "voldir"):
        p = ss + "_%s.npy" % nm
        if os.path.exists(p):
            os.remove(p)
    return (lo * hi) ** 0.5


def finish(stem, out, target=0.14, zoom=0.9, expo=None):
    PO.P["exposure_zoom_k"] = 0.0
    e = expo if expo else solve(stem, target, zoom)
    PO.P["exposure"] = e
    im = PO.finish(stem, zoom, t=2.0)
    m0 = float(np.median(lum(im)))
    if expo is None and abs(m0 - target) > 0.012:                      # one proportional correction at full size
        for _ in range(2):
            e = e * (target / max(m0, 1e-3)) ** 1.0
            PO.P["exposure"] = e
            im = PO.finish(stem, zoom, t=2.0)
            m0 = float(np.median(lum(im)))
            if abs(m0 - target) <= 0.012:
                break
    im.save(out)
    L = lum(im)
    v = dict(exposure=round(e, 3), median=round(float(np.median(L)), 4), under10=round(float((L < 0.10).mean()), 3), over85=round(float((L > 0.85).mean()), 4))
    print(out, v, flush=True)
    json.dump(v, open(out + ".json", "w"))
    return v


if __name__ == "__main__":
    stem, out = sys.argv[1], sys.argv[2]
    finish(stem, out, float(sys.argv[3]) if len(sys.argv) > 3 else 0.14, float(sys.argv[4]) if len(sys.argv) > 4 else 0.9,
           float(sys.argv[5]) if len(sys.argv) > 5 else None)
