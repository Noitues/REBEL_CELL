import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
a = np.asarray(Image.open(sys.argv[1]).convert("RGB"), dtype=np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB"), dtype=np.int16)
d = np.abs(a - b).max(axis=2)
print("%s vs %s: differing pixels %d of %d, max channel diff %d" % (sys.argv[1].split("/")[-2], sys.argv[2].split("/")[-2], int((d > 0).sum()), d.size, int(d.max())))
