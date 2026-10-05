"""Round 32: finish every Blender pass in scratch/bl into scratch/fin (stills 1920 x 1080, GIF frames 960 x 540)."""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import finish as FN

OUT = os.path.dirname(HERE)
SRC = os.path.join(OUT, "scratch", "bl")
DST = os.path.join(OUT, "scratch", "fin")
os.makedirs(DST, exist_ok=True)
for p in sorted(glob.glob(os.path.join(SRC, "*_beauty_night.png"))):
    tag = os.path.basename(p)[:-len("_beauty_night.png")]
    size = (960, 540) if "_f" in tag else (1920, 1080)
    FN.finish(SRC, tag, size).save(os.path.join(DST, tag + ".png"))
    print("fin", tag, flush=True)
