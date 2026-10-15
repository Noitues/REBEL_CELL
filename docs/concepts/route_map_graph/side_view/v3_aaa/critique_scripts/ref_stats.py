"""Luminance/saturation stats for the render and the designer's 2077 screencaps (reference only, never copied
into renders). Converts the .webp to a PNG in <outdir> so it can be viewed.
usage: python ref_stats.py <outdir> <image> [<image> ...]"""
import sys, os
import numpy as np
from PIL import Image

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for p in sys.argv[2:]:
    im = Image.open(p).convert("RGB")
    if p.lower().endswith(".webp"):
        im.save(os.path.join(out, "ref_webp.png"))
    a = np.asarray(im).astype(np.float32) / 255.0
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    hsv = np.asarray(im.convert("HSV")).astype(np.float32) / 255.0
    bright = L > 0.6
    sat_hi = hsv[..., 1][bright].mean() if bright.any() else 0
    print("%-28s %4dx%-4d meanL %.3f p5 %.3f p50 %.3f p95 %.3f  L<0.1 %.2f  L>0.85 %.3f  sat %.2f  sat(L>0.6) %.2f" % (
        os.path.basename(p)[:28], im.width, im.height, L.mean(), np.percentile(L, 5), np.median(L),
        np.percentile(L, 95), (L < 0.1).mean(), (L > 0.85).mean(), hsv[..., 1].mean(), sat_hi))
