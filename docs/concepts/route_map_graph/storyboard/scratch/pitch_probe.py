import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
os.chdir(os.path.join(HERE, "..", "scripts"))
import sb_onecity as OC
D = json.load(open(os.path.join(HERE, "oc_derive.json")))
rooms = D["rooms"]
pts = [p for r in rooms.values() for p in r["front"] + r["back"]]
zs = [p[2] for p in pts]
print("rooms z", min(zs), max(zs))
ov = D["overview"]
print("ov", ov["yaw"], ov["pitch"], ov["dist"], ov["persp"])
sy = D["street"]["a"][1]
face = min(p[1] for r in rooms.values() for p in r["front"])
xs = [p[0] for p in pts]
xm = (min(xs) + max(xs)) / 2
for pitch in [float(a) for a in sys.argv[1:]] or [6.0]:
    c = OC.frame(pts, ov["yaw"], pitch, 40.0, 0.95, 0.90)
    loc = c["persp"]["loc"]
    base = OC.proj(c, (xm, face, 0.0))
    kerb = OC.proj(c, (xm, sy - 4.0, 0.0))
    top = min(OC.proj(c, p)[1] for p in pts)
    dh = math.hypot(loc[0] - xm, loc[1] - sy)
    print("pitch %.1f dist %.1f cam z %.1f elev(street) %.1f  base y %.0f kerb y %.0f rooms top y %.0f sy %.3f" % (
        pitch, c["dist"], loc[2], math.degrees(math.atan2(loc[2], dh)), base[1], kerb[1], top, c["persp"]["sy"]))
