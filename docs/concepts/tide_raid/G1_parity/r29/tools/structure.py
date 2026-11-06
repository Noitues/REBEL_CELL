import sys
import numpy as np
from PIL import Image, ImageFilter
# usage: structure.py label img [label img ...]
# Squint structure metrics on the 320 px wide box downsample (luma 0..1):
#  edge   = mean Sobel gradient magnitude (edge energy)
#  local  = mean |L - gaussian(L, 3 px)| (local contrast)
#  coarse = std of the 80 px wide box downsample (district-scale value structure)
def luma(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def sobel(l):
    gx = (l[:-2, 2:] + 2 * l[1:-1, 2:] + l[2:, 2:]) - (l[:-2, :-2] + 2 * l[1:-1, :-2] + l[2:, :-2])
    gy = (l[2:, :-2] + 2 * l[2:, 1:-1] + l[2:, 2:]) - (l[:-2, :-2] + 2 * l[:-2, 1:-1] + l[:-2, 2:])
    return np.sqrt(gx * gx + gy * gy) / 4.0
def measure(path, crop=None):
    im = Image.open(path).convert("RGB")
    if crop:
        im = im.crop(crop)
    w, h = im.size
    s = im.resize((320, round(320 * h / w)), Image.BOX)
    l = luma(s)
    g = Image.fromarray((l * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
    loc = np.abs(l - np.asarray(g).astype(np.float32) / 255.0).mean()
    c = luma(im.resize((80, round(80 * h / w)), Image.BOX))
    return sobel(l).mean(), loc, c.std()
if __name__ == "__main__":
    a = sys.argv[1:]
    core = (200, 130, 1500, 780)
    print("label | full frame: edge local coarse | core crop 200,130-1500,780: edge local coarse")
    for i in range(0, len(a), 2):
        f = measure(a[i + 1])
        c = measure(a[i + 1], core)
        print("%-10s %.4f %.4f %.4f | %.4f %.4f %.4f" % ((a[i],) + f + c))
