"""Debug: where a pixel's ray crosses given heights (city a, b in lots)."""
import json, math, sys
import numpy as np
import city_preset as CP
stem, cam, x, y = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
A = json.load(open(stem + "_anchors.json"))
Wd, H = A["res"]
C = CP.CAMS[cam]
yw, pt = math.radians(C["yaw"]), math.radians(C["pitch"])
f = np.array([math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt)])
r = np.array([math.sin(yw), -math.cos(yw), 0.0])
u = np.cross(r, f)
loc = np.array(A["cam"]["loc"])
k = C["lens"] / 36.0
xc = (x + 0.5) / Wd - 0.5 + C.get("sx", 0.0)
yc = (H / 2 - y - 0.5) / Wd + C.get("sy", 0.0)
d = f + r * xc / k + u * yc / k
d /= np.linalg.norm(d)
for zz in (2.5, 0, -10, -30, -60, -120):
    t = (zz - loc[2]) / d[2]
    p = loc + d * t
    lx, ly = p[0] / 6 + 6, -p[1] / 6 + 6
    print("z %6.1f  a %.1f b %.1f  lot (%.1f, %.1f)" % (zz, ((lx - 6) - (ly - 6)) / math.sqrt(2), -((lx - 6) + (ly - 6)) / math.sqrt(2), lx, ly))
