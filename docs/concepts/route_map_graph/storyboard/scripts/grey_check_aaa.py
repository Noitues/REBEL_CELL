"""Greyscale check (CRITIQUE §6.9): mean and p90 luma of every room's opening on the plate (no UI), ranked.
r2 adds the mean colour (sRGB) and its hue / saturation, to check option 1 against the cool ahead rooms.
python grey_check_aaa.py <plate.png> <bl_dir>"""
import colorsys
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import sgraph3 as G  # noqa: E402

rgb = Image.open(sys.argv[1]).convert("RGB")
im = rgb.convert("L")
A = json.load(open(os.path.join(sys.argv[2], "anchors_O_overview.json")))
a = np.asarray(im, np.float32) / 255.0
c = np.asarray(rgb, np.float32) / 255.0
s = im.size[0] / 1920.0
st, opts = G.states(G.WALK_MID)
rows = []
for i in G.NODES:
    p = A["rooms"][i]["front"]
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon([(q[0] * s, q[1] * s) for q in p], fill=255)
    sel = np.asarray(m) > 0
    v = a[sel]
    mc = c[sel].mean(axis=0)
    h, l_, sat = colorsys.rgb_to_hls(*mc)
    rows.append((float(np.percentile(v, 90)), float(v.mean()), i, st[i], mc, h * 360, sat))
for p90, mean, i, state, mc, h, sat in sorted(rows, key=lambda r: -r[0]):
    print("%-5s %-8s p90 %.2f mean %.2f  rgb (%.2f %.2f %.2f) hue %3.0f sat %.2f" % (i, state, p90, mean, mc[0], mc[1], mc[2], h, sat))
