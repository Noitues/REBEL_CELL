import importlib.util, os, types, sys
class A:
    def __init__(s): s.n = 0; s.zmax = 0; s.lo=[1e9]*2; s.hi=[-1e9]*2
    def face(s, pts, col, uv=None, wc=(0,0,0), wl=0, wm=3, bid=0, wet=0):
        s.n += 1
        for p in pts:
            s.zmax = max(s.zmax, p[2]); s.lo=[min(s.lo[0],p[0]),min(s.lo[1],p[1])]; s.hi=[max(s.hi[0],p[0]),max(s.hi[1],p[1])]
spots = []
ctx = types.SimpleNamespace(corp="meridian", hq=(18.0, 222.0), SURF=A(), SMOOTH=A(), NEON=A(), GLASS=A(), STREAK=A(),
                            spot_at=lambda t, f, c, p, cone=30: spots.append((t, f, c, p, cone)))
here = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(here, "..", "scripts", "meridian_landmark.py")
spec = importlib.util.spec_from_file_location("lm_meridian", path); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
r = mod.build(ctx)
print(r)
for n in ("SURF", "NEON", "GLASS"):
    a = getattr(ctx, n); print(n, a.n, "zmax %.1f" % a.zmax, [round(v,1) for v in a.lo], [round(v,1) for v in a.hi])
print("spots", len(spots))
