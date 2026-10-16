"""hq_tethys: the OCCLUSION camera-rig rule, the pure-python twin (copied from hq_meridian/scripts/hq_kit/downtown.py:
occlusion_params / occlusion_state, OCC values unchanged; the shader version is hq_kit/section.py).

Rule (designer 2026-10-15): any city building inside the camera -> HQ (and route) sight cone is section-cut to a
1-2 floor lit stub; if the stub still blocks, it ghosts to ~18 % with its edges kept. Here the cut is applied to the
geometry (the building's height in the zoning copy), which is the same per-instance value Godot would tween; the
ghost step is reported (opacity < 1) but not needed at this camera (no stub reaches into the cone).
"""
import math

OCC = dict(margin=0.10, stub=6.4, ghost=0.18, edge=0.6, tsoft=0.035, vsoft=0.025)
NK = 5


def occlusion_params(cam, pts, cfg=None):
    o = dict(OCC, **((cfg or {}).get("occ") or {}))
    cx, cy, cz = cam
    pts = [tuple(p) for p in pts]
    ox = sum(p[0] for p in pts) / len(pts)
    oy = sum(p[1] for p in pts) / len(pts)
    L = math.hypot(ox - cx, oy - cy) or 1.0
    ux, uy = (ox - cx) / L, (oy - cy) / L
    T, Vv, AL = [], [], []
    for (x, y, z) in pts:
        al = max((x - cx) * ux + (y - cy) * uy, 1.0)
        la = (y - cy) * ux - (x - cx) * uy
        T.append(la / al)
        Vv.append((z - cz) / al)
        AL.append(al)
    msp_t = o["margin"] * max(max(T) - min(T), 0.02)
    msp_v = o["margin"] * max(max(Vv) - min(Vv), 0.02)
    a0, a1 = min(AL), max(AL)
    out = dict(occ_on=1.0, occ_cx=cx, occ_cy=cy, occ_cz=cz, occ_ux=ux, occ_uy=uy, occ_tsoft=o["tsoft"], occ_a0=a0,
               occ_amax=a1, occ_vsoft=o["vsoft"], occ_stub=o["stub"], occ_ghost=o["ghost"], occ_edge=o["edge"])
    for k in range(NK):
        ak = a0 + (a1 - a0) * k / (NK - 1)
        sub = [j for j in range(len(AL)) if AL[j] >= ak - 1e-6] or [AL.index(a1)]
        out["occ_t%d" % k] = min(T[j] for j in sub) - msp_t
        out["occ_T%d" % k] = max(T[j] for j in sub) + msp_t
        out["occ_v%d" % k] = min(Vv[j] for j in sub) - msp_v
    return out


def _knot(p, key, a):
    f = (a - p["occ_a0"]) / max(p["occ_amax"] - p["occ_a0"], 1.0) * (NK - 1)
    f = max(0.0, min(NK - 1.0, f))
    v = p["occ_%s0" % key]
    for k in range(1, NK):
        v += max(0.0, min(1.0, f - (k - 1))) * (p["occ_%s%d" % (key, k)] - p["occ_%s%d" % (key, k - 1)])
    return v


def _sstep(x, w):
    t = max(0.0, min(1.0, x / max(w, 1e-4)))
    return t * t * (3 - 2 * t)


def occlusion_state(p, b):
    """b = (x, y, top, hx, hy) -> (cut height, opacity)."""
    x, y, top, hx, hy = b
    r = max(math.hypot(hx, hy), 0.5)
    dx, dy = x - p["occ_cx"], y - p["occ_cy"]
    al = dx * p["occ_ux"] + dy * p["occ_uy"]
    la = dy * p["occ_ux"] - dx * p["occ_uy"]
    alc = max(al, 1.0)
    tmin, tmax, vmin = _knot(p, "t", al - r), _knot(p, "T", al - r), _knot(p, "v", al - r)
    lat = _sstep((la + r) / alc - tmin, p["occ_tsoft"]) * _sstep(tmax - (la - r) / alc, p["occ_tsoft"])
    front = (1.0 if al > 0 else 0.0) * _sstep(p["occ_amax"] - (al - r), 6.0)

    def blocks(z):
        return _sstep((z - p["occ_cz"]) / max(al + r, 1.0) - vmin, p["occ_vsoft"])
    fc = p["occ_on"] * lat * front * blocks(top)
    stub = min(p["occ_stub"], top)
    zc = stub + (1.0 - fc) * (top + 25.0 - stub)
    g = fc * blocks(stub)
    return min(zc, top), 1.0 - g * (1.0 - p["occ_ghost"])
