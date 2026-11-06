"""Values per held shot on the composed frames: python values_r3.py <frames dir>"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import sb_cams as SB
import sb_ocjobs as OJ
D = OJ.derive()
FR = sys.argv[1]
segs = {}
for f in range(SB.NF):
    segs.setdefault(OJ.full_at(f, D)[0], []).append(f)
for s in ("ov", "zoom", "dec", "hin", "h1", "hmove", "h2"):
    fs = segs.get(s, [])
    if not fs:
        continue
    pick = fs[len(fs) // 2:len(fs) // 2 + 1] + fs[::max(1, len(fs) // 4)]
    med, low = [], []
    for f in sorted(set(pick)):
        l = np.asarray(Image.open(os.path.join(FR, "f_%04d.png" % f)).convert("L"), np.float32) / 255
        med.append(np.median(l))
        low.append((l < 0.10).mean() * 100)
    print("%-6s f %d-%d  median %.3f  <0.10 %.1f%%" % (s, fs[0], fs[-1], np.mean(med), np.mean(low)))
