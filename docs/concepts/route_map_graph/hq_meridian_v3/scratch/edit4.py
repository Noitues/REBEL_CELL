p='meridian_landmark.py'
s=open(p,encoding='utf8').read()
i=s.index('    if getattr(K, "CITY", False):\n        hooks["post_build"]')
tail='''    if getattr(K, "CITY", False):
        hooks["post_build"] = lambda OBJ: None
    else:
        import bpy
        RIMRX = bpy.data.collections.new("rim_rx")
        for k, (rx, ry_, col_) in enumerate(((-220.0, 200.0, "district_a"), (150.0, 240.0, "district_b"))):
            K.add_light("rim_%d" % k, "AREA", (rx, ry_, 90.0), LH["rim_w"], pal(col_), aim=(0.0, GY, 80.0),
                        size=120.0, size_y=60.0, group="corp", shadow=False, receivers=RIMRX)

        def post_build(OBJ):
            for name, ob in OBJ.items():
                if ob is not None and any(c.name == "compound" for c in ob.users_collection):
                    RIMRX.objects.link(ob)
        hooks["post_build"] = post_build
    log("rig")
    return hooks


# ================================================================== the city's landmark-module contract
# city_all_corps/NOTES.md "Landmark modules": build(ctx) -> dict(label, crown, hue). build(K, ...) above is the HQ kit's
# entry; a call with a city ctx (it has SURF and no A) is routed here. Pure python (no bpy), so it can be tested.
_CITY_EMIT_K = 4.0            # an HQ emission strength k maps to emission colour * min(1, k / this)


def _cbox(acc, x0, y0, z0, x1, y1, z1, col, k=0.0, top=True, bottom=False):
    x0, x1, y0, y1, z0, z1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
    acc.face([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], col, k)
    acc.face([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], col, k)
    acc.face([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], col, k)
    acc.face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], col, k)
    if top:
        acc.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], col, k)
    if bottom:
        acc.face([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], col, k)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a):
    n = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def _ctube(acc, p0, p1, r, col, k=0.0, n=8):
    d = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    if math.sqrt(sum(c * c for c in d)) < 1e-4:
        return
    d = _unit(d)
    up = (0.0, 0.0, 1.0) if abs(d[2]) < 0.95 else (1.0, 0.0, 0.0)
    u = _unit(_cross(d, up))
    v = _unit(_cross(d, u))
    ring = [tuple((u[c] * math.cos(2 * math.pi * i / n) + v[c] * math.sin(2 * math.pi * i / n)) * r for c in range(3))
            for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        acc.face([tuple(p0[c] + ring[i][c] for c in range(3)), tuple(p0[c] + ring[j][c] for c in range(3)),
                  tuple(p1[c] + ring[j][c] for c in range(3)), tuple(p1[c] + ring[i][c] for c in range(3))], col, k)


def _cseg_box(acc, p, q, w, h, col, k=0.0):
    d = (q[0] - p[0], q[1] - p[1], q[2] - p[2])
    if math.sqrt(sum(c * c for c in d)) < 1e-4:
        return
    sd = (-d[1], d[0], 0.0)
    sl = math.hypot(sd[0], sd[1])
    sd = (sd[0] / sl * w / 2, sd[1] / sl * w / 2, 0.0) if sl > 1e-6 else (w / 2, 0.0, 0.0)
    a = [(p[0] - sd[0], p[1] - sd[1], p[2]), (q[0] - sd[0], q[1] - sd[1], q[2]),
         (q[0] + sd[0], q[1] + sd[1], q[2]), (p[0] + sd[0], p[1] + sd[1], p[2])]
    b = [(v[0], v[1], v[2] - h) for v in a]
    acc.face(a, col, k)
    acc.face(list(reversed(b)), col, k)
    for i in range(4):
        j = (i + 1) % 4
        acc.face([b[i], b[j], a[j], a[i]], col, k)


class _CityAcc:
    """An HQ accumulator that writes into one of the city's: kind 'surf' (opaque, no windows), 'neon' (emitter; the HQ
    strength k scales the colour) or 'glass'."""

    def __init__(self, ctx, kind):
        self.t = {"surf": ctx.SURF, "neon": ctx.NEON, "glass": ctx.GLASS}[kind]
        self.kind = kind

    def face(self, pts, col, k=0.0):
        pts = [tuple(p) for p in pts]
        if self.kind == "neon":
            e = min(1.0, max(k, 0.0) / _CITY_EMIT_K)
            if e <= 0.0:
                return
            self.t.face(pts, tuple(c * e for c in col[:3]))
        else:
            self.t.face(pts, tuple(col[:3]), None, (0.0, 0.0, 0.0), 0.0, 3, 0.0, 0)


_CITY_KIND = {"civic": "surf", "cut": "surf", "metal": "surf", "rough": "surf", "int": "surf", "ground": "surf",
              "glass": "glass", "trim": "neon", "gold": "neon", "sign": "neon", "small": "neon", "emit": "neon",
              "containers": "surf", "masonry": "surf", "gantry": "surf", "seams": "neon", "train": "surf",
              "train_glass": "glass", "room_srv": "neon"}


def _build_city(ctx):
    import os
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    sys.dont_write_bytecode = True
    import hq_preset as HP
    P = HP.PRESET
    hq = ctx.hq
    k = K_UNITS
    cache = {}

    def acc(name, mat=None, *_):
        key = mat if isinstance(mat, str) else name
        kind = _CITY_KIND.get(key) or _CITY_KIND.get(name, "surf")
        if kind not in cache:
            cache[kind] = _CityAcc(ctx, kind)
        return cache[kind]

    def log(*a):
        print("MERIDIAN", *a, flush=True)

    def add_light(name, kind, loc, energy, col, aim=None, size=0.5, size_y=None, spot=None, blend=0.3, group="",
                  shadow=True, receivers=None):
        if name.startswith("rim_"):
            return None
        tgt = aim if aim is not None else (loc[0], loc[1], 0.0)
        cone = spot if (kind == "SPOT" and spot) else (100.0 if kind == "AREA" else 140.0)
        ctx.spot_at(tgt, loc, tuple(col[:3]), energy, cone)
        return None

    names = ("civic", "cut", "metal", "rough", "int", "ground", "glass", "trim", "gold", "sign", "small")
    K0 = SimpleNamespace(CITY=True, A={n: acc(n) for n in names}, Acc=acc, COLL={"compound": None, "rooms": None},
                         M={n: n for n in ("civic", "cut", "int", "metal", "rough", "glass", "emit", "ground")},
                         box=_cbox, tube=_ctube, seg_box=_cseg_box, add_light=add_light, pal=HP.pal, CP=P["hq"]["compound"],
                         LH=P["hq"]["light"], HZ=P["hq"], log=log, G=None)
    K2 = place(K0, origin=(hq[0], hq[1], 0.0), k=k)
    hooks = build_hq(K2, rooms=False, rail=False)
    crown = hooks["beams"][0][0] if hooks["beams"] else None
    GC = P["hq"]["compound"]["gantry"]
    label = (hq[0] + GC["keep_x"] * k, hq[1] + GC["y"] * k, (GC["keep_top"] + GC["lantern"][2] + 20.0) * k)
    return dict(label=label, crown=crown, hue=(1.0, 0.45, 0.12))


def build(K, rooms=True, rail=True):
    """HQ kit: build(K, rooms, rail) -> hooks. City (landmarks.landmark_ctx): build(ctx) -> dict(label, crown, hue)."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return _build_city(K)
    return build_hq(K, rooms, rail)
'''
s=s[:i]+tail
open(p,'w',encoding='utf8').write(s)
