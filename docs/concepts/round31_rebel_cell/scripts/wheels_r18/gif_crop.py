"""Crop one GIF frame: python gif_crop.py <gif> <frame> <x0> <y0> <x1> <y1> <out.png>"""
import sys
from PIL import Image, ImageSequence

g = Image.open(sys.argv[1])
fr = [f.convert("RGB").copy() for f in ImageSequence.Iterator(g)]
i, x0, y0, x1, y1 = (int(v) for v in sys.argv[2:7])
fr[i].crop((x0, y0, x1, y1)).save(sys.argv[7])
