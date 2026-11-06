import sys, numpy as np
from PIL import Image
for p in sys.argv[1:]:
    l = np.asarray(Image.open(p).convert("L").resize((1280, 720)), np.float32) / 255
    print("%s median %.3f <0.10 %.1f%%" % (p[-20:], np.median(l), (l < 0.10).mean() * 100))
