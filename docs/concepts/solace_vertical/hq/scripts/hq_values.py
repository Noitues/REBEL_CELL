"""HQ kit: value checks on a finished plate (no UI) + its object-index pass.

python hq_values.py <plate.png> <stem of the passes> [thumb.png]
  frame: median, share under 0.10, share over 0.85 (the r3 targets: median 0.14, under_010 0.25-0.40, over_085 <= 2.5 %)
  HQ rule (designer audit 2026-10-15): the LANDMARK (pass index 1 compound, 5 rooms, 6 movers) median luma against the
  LOCAL background (index 0 sky + 2 city inside the landmark's bounding box grown by 35 %): ratio 1.5-2.0.
  thumb: the plate at 320 px wide (the silhouette check: name the landmark parts).
"""
import sys

import numpy as np
from PIL import Image


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def check(plate_path, stem, thumb=None):
    im = Image.open(plate_path).convert("RGB")
    a = np.asarray(im, np.float32) / 255.0
    L = lum(a)
    out = dict(median=float(np.median(L)), under_010=float((L < 0.10).mean()), over_085=float((L > 0.85).mean()))
    try:
        idx = np.load(stem + "_index.npy")[..., 0]
        if idx.shape != L.shape:
            idx = np.asarray(Image.fromarray(idx.astype(np.float32), "F").resize(im.size, Image.NEAREST))
        lm = np.isin(np.round(idx), (1, 5, 6))
        ys, xs = np.nonzero(lm)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        gy, gx = int((y1 - y0) * 0.35), int((x1 - x0) * 0.35)
        box = np.zeros_like(lm)
        box[max(0, y0 - gy):y1 + gy, max(0, x0 - gx):x1 + gx] = True
        bg = box & np.isin(np.round(idx), (0, 2))
        out.update(landmark=float(np.median(L[lm])), local_bg=float(np.median(L[bg])) if bg.any() else None,
                   landmark_share=float(lm.mean()))
        if out["local_bg"]:
            out["ratio"] = out["landmark"] / max(1e-4, out["local_bg"])
    except FileNotFoundError:
        pass
    if thumb:
        im.resize((320, int(320 * im.height / im.width)), Image.LANCZOS).save(thumb)
    return out


if __name__ == "__main__":
    r = check(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(" ".join("%s %.3f" % (k, v) if isinstance(v, float) else "%s %s" % (k, v) for k, v in r.items()))
