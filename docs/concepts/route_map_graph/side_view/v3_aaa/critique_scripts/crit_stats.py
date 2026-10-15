"""Critique helper: crops + luminance stats of the render (read-only on the source)."""
import sys, os
import numpy as np
from PIL import Image
src = sys.argv[1]; out = sys.argv[2]
os.makedirs(out, exist_ok=True)
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32) / 255.0
L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
print("size", im.size, "mean L %.3f" % L.mean(), "median %.3f" % np.median(L))
for p in (1, 5, 25, 50, 75, 95, 99, 99.9):
    print("p%s %.3f" % (p, np.percentile(L, p)))
print("frac clipped (any ch>=0.99) %.3f" % (a.max(-1) >= 0.99).mean())
print("frac L>0.85 %.3f" % (L > 0.85).mean())
# regions (x0,y0,x1,y1) in 1280x720
R = dict(sky=(200, 0, 1280, 120), towers=(200, 120, 1280, 330), routeband=(200, 330, 1130, 600),
         street=(0, 600, 1280, 690), left_bg=(0, 120, 200, 600))
for k, (x0, y0, x1, y1) in R.items():
    s = a[y0:y1, x0:x1]; l = L[y0:y1, x0:x1]
    hsv = np.asarray(Image.fromarray((s * 255).astype(np.uint8)).convert("HSV")).astype(np.float32) / 255
    print("%-9s meanL %.3f p95 %.3f p5 %.3f sat %.3f clip %.3f" % (k, l.mean(), np.percentile(l, 95), np.percentile(l, 5),
          hsv[..., 1].mean(), (s.max(-1) >= 0.99).mean()))
crops = dict(c_sky=(560, 0, 1000, 250), c_route=(560, 320, 900, 620), c_street=(300, 560, 900, 720),
             c_left=(180, 150, 520, 420), c_right=(980, 150, 1280, 450), c_mid=(840, 80, 1100, 330))
for k, b in crops.items():
    c = im.crop(b); c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS); c.save(os.path.join(out, k + ".png"))
