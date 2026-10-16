"""Debug: world position (and a, b, z in the city frame) of the reddest pixels of a render (uses depth + camera)."""
import json, math, sys
import numpy as np
sys.path.insert(0, ".")
import city_preset as CP
stem = sys.argv[1]
cam = sys.argv[2]
rgb = np.load(stem + "_rgb.npy").astype(np.float32)
z = np.load(stem + "_z.npy")[..., 0]
A = json.load(open(stem + "_anchors.json"))
H, Wd = z.shape
C = CP.CAMS[cam]
yw, pt = math.radians(C["yaw"]), math.radians(C["pitch"])
f = np.array([math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt)])
r = np.array([math.sin(yw), -math.cos(yw), 0.0])
u = np.cross(r, f)
loc = np.array(A["cam"]["loc"])
k = C["lens"] / 36.0
red = rgb[..., 0] - np.maximum(rgb[..., 1], rgb[..., 2])
if len(sys.argv) > 4:
    y0, y1 = int(sys.argv[3]), int(sys.argv[4])
    red[:y0] = -9
    red[y1:] = -9
idx = np.argsort(red.ravel())[-8:]
for i in idx:
    y, x = divmod(int(i), Wd)
    xc = (x + 0.5) / Wd - 0.5 + C.get("sx", 0.0)
    yc = (H / 2 - y - 0.5) / Wd + C.get("sy", 0.0)
    d = f + r * xc / k + u * yc / k
    d /= np.linalg.norm(d)
    p = loc + d * z[y, x] / np.dot(d, f)
    lx, ly = p[0] / 6 + 6, -p[1] / 6 + 6
    a = ((lx - 6) - (ly - 6)) / math.sqrt(2)
    b = -((lx - 6) + (ly - 6)) / math.sqrt(2)
    print("px", x, y, "rgb", np.round(rgb[y, x], 3), "world", np.round(p, 1), "a %.1f b %.1f" % (a, b))
