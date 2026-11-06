"""Build C War Table frames: python build.py [name-substring ...]  -> ../<name>.png (+ strips, sims, sheet)"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wt_frames import *
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
want = sys.argv[1:]
for name, fn in FRAMES:
    if want and not any(w in name for w in want):
        continue
    t = time.time()
    cv = fn()
    img = cv.final()
    img.save(os.path.join(OUT, name + ".png"))
    print(name, round(time.time() - t, 1), flush=True)
