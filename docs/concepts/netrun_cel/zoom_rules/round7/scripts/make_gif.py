import sys, glob
import numpy as np
from PIL import Image
src, dst, width = sys.argv[1], sys.argv[2], int(sys.argv[3])
files = sorted(glob.glob(src + "/gif_*.png"))
ims = [Image.open(f).convert("RGB") for f in files]
a0 = np.asarray(ims[0]).astype(np.int16)
stats = []
for i, im in enumerate(ims):
    d = np.abs(np.asarray(im).astype(np.int16) - a0)
    stats.append((i, float(d.mean()), int((d.max(axis=2) > 24).sum())))
print("frames", len(ims))
for s in stats:
    print("frame %02d mean|d| vs 0 = %.3f  px>24 = %d" % s)
h = int(ims[0].height * width / ims[0].width)
small = [im.resize((width, h), Image.LANCZOS).quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in ims]
dur = [80, 80, 90] * (len(small) // 3) + [80] * (len(small) % 3)
small[0].save(dst, save_all=True, append_images=small[1:], duration=dur, loop=0, optimize=False)
print("wrote", dst, sum(dur) / 1000.0, "s")
