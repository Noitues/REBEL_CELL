import sys
import numpy as np
from PIL import Image
# usage: metrics.py img [label] [rect x1 y1]   luma percentiles with the bay corner x<x1 and y<y1 masked (default rect from calibration)
def luma(path):
    im = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
    return im, 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
if __name__ == "__main__":
    im, l = luma(sys.argv[1])
    lab = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
    x1 = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    y1 = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    m = np.ones(l.shape, bool)
    m[:y1, :x1] = False
    p = np.percentile(l[m], [1, 5, 25, 50, 75, 95])
    print(lab, "luma p1/5/25/50/75/95:", " ".join("%.3f" % v for v in p), "median rgb", tuple(int(np.median(im[..., c][m]) * 255) for c in range(3)))
