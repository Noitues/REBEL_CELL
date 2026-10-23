import numpy as np, colorsys
from PIL import Image
D = "D:/rc_scratch/solace_v1/nodes/"
def stats(path, box=(0, 900, 1920, 1070)):
    im = np.asarray(Image.open(path).convert("RGB").crop(box), dtype=np.float64) / 255.0
    lin = np.where(im <= 0.04045, im / 12.92, ((im + 0.055) / 1.055) ** 2.4)
    luma = (0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]).mean()
    mx, mn = im.max(-1), im.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return luma, im.mean(), sat.mean(), (sat * mx).mean()
print("page, linear luma, mean sRGB, mean HSV saturation, chroma (S*V)")
for w, n in (("now", "event"), ("now", "rest"), ("now", "workshop"), ("then", "rest"), ("then", "workshop"), ("then", "event")):
    l, m, s, c = stats(D + "cap_%s/%s.png" % (w, n))
    print("%s %-9s luma %.4f  srgb %.3f  sat %.3f  chroma %.3f" % (w, n, l, m, s, c))
