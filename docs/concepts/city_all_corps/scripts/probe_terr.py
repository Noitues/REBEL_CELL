"""Probe: plot the one-city layout's territories (top view) to plan the zoning."""
import json, sys
from PIL import Image, ImageDraw
L = json.load(open(sys.argv[1]))
S = 4
im = Image.new("RGB", (250 * S, 250 * S), (10, 10, 14))
d = ImageDraw.Draw(im)
T = {k: tuple(int(c * 255) for c in v) for k, v in L["terr"].items()}
T[""] = (90, 90, 90)
f = lambda p: ((p[0] + 120) * S, (p[1] + 120) * S)
for t in L["tiles"]:
    d.polygon([f(p) for p in t["q"]], fill=(40, 40, 50))
for b in L["buildings"]:
    c = T[b["terr"]]
    k = min(1.0, 0.35 + b["h"] / 80.0)
    d.polygon([f(p) for p in b["q"]], fill=tuple(int(v * k) for v in c))
for k, v in L["hqs"].items():
    x, y = f(v); d.ellipse([x - 8, y - 8, x + 8, y + 8], outline=(255, 255, 255), width=3); d.text((x + 10, y), k, fill=(255, 255, 255))
x, y = f(L["cell_base"]); d.ellipse([x - 8, y - 8, x + 8, y + 8], outline=(255, 0, 0), width=3)
x, y = f(L["centre"]); d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 0))
for k in range(-120, 130, 20):
    d.line([f((k, -120)), f((k, 130))], fill=(60, 60, 60)); d.text(f((k, -118)), str(k), fill=(200, 200, 200))
    d.line([f((-120, k)), f((130, k))], fill=(60, 60, 60)); d.text(f((-118, k)), str(k), fill=(200, 200, 200))
im.save(sys.argv[2])
import collections
hs = collections.defaultdict(list)
for b in L["buildings"]:
    hs[b["terr"]].append(b["h"] + b["z0"])
for k, v in hs.items():
    v.sort(); print(k, len(v), "median h", v[len(v)//2], "p90", v[int(len(v)*.9)], "max", v[-1])
