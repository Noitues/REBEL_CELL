"""City-all-corps (revision 2): the beam rule check on a finished AAA-2 image.

python beam_check.py <image.png> <anchors.json>

Per landmark (luma of the final sRGB image, scaled from the anchors' resolution):
  landmark peak  = the 99th percentile in a disc round the crown anchor (r = 40 px at 3840 wide)
  local bg       = the median of the annulus 140..260 px round it
  beam peak      = the 99th percentile of 7x7 px windows along the beam axis, from 25 % to 100 % of its visible length
Rule (art director): landmark peak >= 1.5 x local bg, and beam peak < landmark peak. Also: every beam end in frame.
"""
import json
import sys

import numpy as np
from PIL import Image


def main(img_p, anc_p):
    im = np.asarray(Image.open(img_p).convert("RGB"), np.float32) / 255
    l = im[..., 0] * 0.2126 + im[..., 1] * 0.7152 + im[..., 2] * 0.0722
    H, W = l.shape
    A = json.load(open(anc_p))
    k = W / A["res"][0]
    s = W / 3840.0
    yy, xx = np.mgrid[0:H, 0:W]
    out = {}
    for name, (a, b) in sorted(A["anchors"].get("_beams", {}).items()):
        cr = A["anchors"][name]["crown"]
        cx, cy = cr[0] * k, cr[1] * k
        d = np.hypot(xx - cx, yy - cy)
        lm = float(np.percentile(l[d < 40 * s], 99))
        bg = float(np.median(l[(d > 140 * s) & (d < 260 * s)]))
        ax, ay, bx, by = a[0] * k, a[1] * k, b[0] * k, b[1] * k
        vals = []
        for t in np.linspace(0.25, 1.0, 60):
            px, py = int(ax + (bx - ax) * t), int(ay + (by - ay) * t)
            if 3 <= px < W - 3 and 3 <= py < H - 3:
                vals.append(l[py - 3:py + 4, px - 3:px + 4].max())
        bp = float(np.percentile(vals, 99)) if vals else 0.0
        inside = 0 <= bx < W and 0 <= by < H
        out[name] = dict(landmark=round(lm, 3), bg=round(bg, 3), ratio=round(lm / max(bg, 1e-4), 2), beam=round(bp, 3),
                         ok=bool(lm >= 1.5 * bg and bp < lm and inside), end_in_frame=inside)
    for kk, v in out.items():
        print(kk, v)
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
