"""Round 44: finish a rendered tag with the plain owned network and mark node ids, to plan framings.
NET36=net_scope.json python probe44.py <tag> [SOLID40=1 via env]"""
import os
import sys

os.environ.setdefault("NET36", "net_scope.json")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import ImageDraw  # noqa: E402

import post40 as P  # noqa: E402
import screens38_base as B  # noqa: E402

tag = sys.argv[1]


def deco(net):
    for l in P.NET["links"]:
        if l["state"] == "owned":
            net.link(l["pts"], P.LINK_COL["owned"], k=1.0)
    for n in P.NET["nodes"]:
        if n["state"] in ("owned", "core"):
            net.node(n)


img, cam = P.finish(tag, decorate=deco, t=0.2, sky=False)
cv = B.to_rgba(img)
d = ImageDraw.Draw(cv)
for n in P.NET["nodes"]:
    x, y = B.prj(cam, n["lot"], 0)
    d.text((x + 6, y + 6), n["id"], fill=(255, 255, 255, 255))
for k, v in P.NET["hq"].items():
    x, y = B.prj(cam, v, 0)
    d.text((x, y), "HQ " + k, fill=(255, 80, 80, 255))
print(cam)
cv.convert("RGB").save(os.path.join(HERE, "..", "scratch", "probe_%s.jpg" % tag), quality=85)
