import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ["NET36"] = "net_scope.json"
import numpy as np
from PIL import ImageDraw
import r42lib as R
import hq44 as H
A = [float(v) for v in sys.argv[1:7]] if len(sys.argv) > 6 else [875, 303, 15.3, 7.5, -15.3, 7.5]
cam = R.Aff(A[0], A[1], (A[2], A[3]), (A[4], A[5]))
img = R.backdrop().convert("RGBA")
sh = H.shown_ids()
for l in H.NET["links"]:
    if l["a"] in sh and l["b"] in sh:
        col = {"owned": (212,255,0), "border": (255,140,26), "grey": (150,150,150), "white": (255,255,255)}[l["state"]]
        R.link(img, cam, l["pts"], col, width=4, k=1.0)
d = ImageDraw.Draw(img)
for k in sh:
    x, y = cam.prj(H.NODES[k]["lot"])
    d.ellipse([x-12,y-12,x+12,y+12], outline=(255,0,0), width=3); d.text((x+14,y-6), k, fill=(255,255,255))
img.convert("RGB").save(os.path.join(HERE, "..", "scratch", "probe_hq.png"))
