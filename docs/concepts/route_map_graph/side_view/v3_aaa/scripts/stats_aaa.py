"""The critic's acceptance numbers for a render (CRITIQUE §5), plus the critic's own crit_stats.py on a 1280 copy.

python stats_aaa.py <image.png> [label]
Prints: median L, p95, % of pixels under 0.10, % over 0.85, saturation of bright pixels (L > 0.6), and PASS / MISS
against the targets (median 0.14-0.18, p95 0.65-0.75, >= 25 % < 0.10, <= 2.5 % > 0.85, bright sat >= 0.25).
"""
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def stats(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, np.float32) / 255.0
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    hsv = np.asarray(im.convert("HSV"), np.float32) / 255.0
    bright = L > 0.6
    return dict(median=float(np.median(L)), p95=float(np.percentile(L, 95)), under=float((L < 0.10).mean() * 100),
                over=float((L > 0.85).mean() * 100), bsat=float(hsv[..., 1][bright].mean()) if bright.any() else 0.0)


def verdict(s):
    t = [("median", 0.14 <= s["median"] <= 0.18), ("p95", 0.65 <= s["p95"] <= 0.75), ("under", s["under"] >= 25),
         ("over", s["over"] <= 2.5), ("bsat", s["bsat"] >= 0.25)]
    return " ".join("%s:%s" % (k, "ok" if v else "MISS") for k, v in t)


def line(path, label=None):
    s = stats(path)
    return "%-28s median %.3f  p95 %.3f  <0.10 %5.1f %%  >0.85 %4.1f %%  bright-sat %.2f  | %s" % (
        label or os.path.basename(path), s["median"], s["p95"], s["under"], s["over"], s["bsat"], verdict(s))


if __name__ == "__main__":
    p = sys.argv[1]
    print(line(p, sys.argv[2] if len(sys.argv) > 2 else None))
    tmp = os.path.join(ROOT, "scratch", "stats_1280.png")
    Image.open(p).convert("RGB").resize((1280, 720), Image.LANCZOS).save(tmp)
    crit = os.path.join(ROOT, "critique_scripts", "crit_stats.py")
    if os.path.exists(crit):
        out = subprocess.run([sys.executable, crit, tmp, os.path.join(ROOT, "scratch", "crit_out")], capture_output=True, text=True)
        print(out.stdout.strip())
