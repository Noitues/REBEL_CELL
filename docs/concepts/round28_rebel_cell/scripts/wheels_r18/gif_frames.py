"""Dump selected frames of a GIF into a contact strip: python gif_frames.py <gif> <out.png> [i j k ...]"""
import sys
from PIL import Image, ImageSequence

g = Image.open(sys.argv[1])
fr = [f.convert("RGB").copy() for f in ImageSequence.Iterator(g)]
idx = [int(a) for a in sys.argv[3:]] or list(range(0, len(fr), max(1, len(fr) // 6)))
idx = [i for i in idx if i < len(fr)]
w, h = fr[0].size
sc = min(1.0, 1900 / (w * len(idx)))
tw, th = int(w * sc), int(h * sc)
out = Image.new("RGB", (tw * len(idx), th), (0, 0, 0))
for k, i in enumerate(idx):
    out.paste(fr[i].resize((tw, th)), (k * tw, 0))
out.save(sys.argv[2])
print(len(fr), "frames; shown", idx)
