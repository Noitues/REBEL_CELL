"""DRAFT for the art-pass session; unverified (no render).
# provenance: model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id lm__solace; status ok; tokens in 29663 cache-write 0 cache-read 132454 out 17729; cost $0.132; ast.parse: parses
SOLACE LANDMARK: THE TWIN HELIX (tube helix v3), an importable landmark module. Pure Python (no bpy, no numpy).

ENTRY POINTS
    import solace_landmark as SL
    info = SL.build(ctx)                       # THE CITY HOOK (spec 8.6c): ctx = landmarks.landmark_ctx("solace")
                                               #   -> dict(label=(x, y, z), crown=(x, y, z), hue=(r, g, b))
    hooks = SL.build(K, rooms=True, rail=False)    # HQ netrun kit (spec 8.5): K as in meridian_landmark.py
    K2 = SL.place(K, origin=(hx, hy, 0.0), k=SL.K_UNITS * k_fit)    # drop the HQ build into a one-city lot
    SL.landmark_info()                         # constants for the checks (spec 12.2)
    build() dispatches: a ctx with SURF and no A is the city; anything with A is the HQ kit.

WHAT IT BUILDS
  City scale (a port of landmarks.solace(); same rules, same lights):
    plinth       drum r 12.0, z 0..2.5, with a lit hue ring at z 2.55
    helix        two smooth swept tubes (tube r 3.4, centreline radius 7.5, 16 sides, 90 steps), z 2.5..86, one full
                 turn per 62 BU of height (phase 0 and pi), porcelain tint, porthole texture through the SMOOTH
                 accumulator's uv / window arguments, a dome crown cap in the hue on each tube
    bridges      one bow-tie skybridge per 4.2 BU of height between the tubes (wide 2.6 each side at the tubes,
                 0.7 at the waist), hue edges
    beacons      one red beacon per tube top
    lights       a cool-white key from the camera side and a hue fill (both scaled by CP.SOLACE_LIFT)
  HQ scale (reduced port of hq_solace/scripts/hq_build.py, see NOTES in the hand-off): the two strand tubes, the
    downlight rings, the mint seam, route-floor bow-tie bridges, the crown with THE GENOME CORE and the pink halo
    ring, the dark plaza podium with the lit entry and the SOLACE name, the ground spots and the rim. The node
    cutaway windows, office floors and interior-mapping atlas are NOT ported (Blender material graphs / hq_office).
    Route rooms are cut by K.room_shell when the corp graph module G is given (slots come from G, spec 8.4).

UNITS / PLACING IN THE CITY
    City build: world BU (1 lot = 6 BU), x east, y north, z up, geometry around ctx.hq. It stays inside a drum of
    radius 12.0 BU (the helix reaches 7.5 + 3.4 = 10.9; the plinth 12.0), far inside the landmark clearance
    (landmark_r 5.6 lots = 33.6 BU).
    HQ build: HQ-kit units (1 storey = 8 BU) around (0, 0, 0). place() maps it to one-city units
    (k_units 0.2375, spec 8.6) and `k_fit` for the lot (spec 8.6); lights x k^2.

SEEDS
    The city build has no random draws (as the built-in). The HQ build uses art streams named "landmark.solace.<use>"
    derived from ctx.seed / K seed by fnv1a64 + splitmix64 (spec 3.5); the legacy literal 6330 / 6331 is kept as
    LEGACY_SEEDS for golden-image parity only.
"""
import math
import random
from types import SimpleNamespace

# ---------------------------------------------------------------- constants (spec 8.5, GDD 11.7 working names)
CORP = "solace"
CENTRAL_SERVER_NAME = "THE GENOME CORE"
K_UNITS = 0.2375                       # HQ kit storey 8 BU -> one floor 1.9 BU (spec 8.6)
LEAF = (0.588, 1.0, 0.275)             # Solace leaf #96FF46 (HQ preset), linear-ish as the HQ palette uses it
PINK = (1.0, 0.275, 0.588)
LEGACY_SEEDS = {"windows": 6330, "podium": 6331, "bridge": 6420}

# city-scale numbers (landmarks.solace)
C_PLINTH_R = 12.0
C_PLINTH_Z = (0.0, 2.5)
C_R, C_RT = 7.5, 3.4                    # helix centreline radius, tube radius
C_Z0, C_Z1 = 2.5, 86.0
C_PITCH = 62.0
C_STEPS, C_NSEG = 90, 16
C_BRIDGE_STEP = 4.2
C_CROWN_LABEL_DZ = 12.0
TUBE_COL = (0.82, 0.86, 0.84)
WIN_TINT = (0.82, 1.0, 0.88)


# ---------------------------------------------------------------- seeds
def _fnv1a64(data):
    h = 0xCBF29CE484222325
    for b in data.encode("utf-8"):
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def _splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return z ^ (z >> 31)


def art_rng(seed, stream, *keys):
    """Named per-object stream (spec 3.5 rule 3): keyed by content ids, never by draw order."""
    txt = "[" + ",".join(repr(x) for x in (seed, "art/landmark." + CORP + "." + stream) + tuple(keys)) + "]"
    return random.Random(_splitmix64(_fnv1a64(txt)))


# ---------------------------------------------------------------- small vector helpers (tuples)
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a):
    n = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


# ================================================================== placing (HQ kit -> city units)
class _AccProxy:
    def __init__(self, acc, f):
        self._acc, self._f = acc, f

    def face(self, pts, col, k=0.0):
        self._acc.face([self._f(p) for p in pts], col, k)

    def __getattr__(self, n):
        return getattr(self._acc, n)


def place(K, origin=(0.0, 0.0, 0.0), k=K_UNITS):
    """A copy of K whose accumulators and lights are moved to origin and scaled by k (same contract as Meridian)."""
    ox, oy, oz = origin

    def f(p):
        return (p[0] * k + ox, p[1] * k + oy, p[2] * k + oz)
    K2 = SimpleNamespace(**vars(K))
    K2.A = {n: _AccProxy(a, f) for n, a in K.A.items()}
    K2.Acc = lambda *a, **kw: _AccProxy(K.Acc(*a, **kw), f)

    def add_light(name, kind, loc, energy, col, aim=None, size=0.5, size_y=None, **kw):
        return K.add_light(name, kind, f(loc), energy * k * k, col, aim=None if aim is None else f(aim),
                           size=size * k, size_y=None if size_y is None else size_y * k, **kw)
    K2.add_light = add_light
    K2.place_f = f
    return K2


# ================================================================== CITY HOOK (port of landmarks.solace)
def _footprint_radius(ctx):
    fp = getattr(ctx, "footprint", None)
    if isinstance(fp, (int, float)):
        return float(fp)
    if isinstance(fp, (tuple, list)) and fp:
        try:
            return float(max(fp))
        except (TypeError, ValueError):
            return None
    return None


def _build_city(ctx):
    SURF, SMOOTH, NEON = ctx.SURF, ctx.SMOOTH, ctx.NEON
    box, cyl, dome, bar, ring_line, sc, spot_at = ctx.box, ctx.cyl, ctx.dome, ctx.bar, ctx.ring_line, ctx.sc, ctx.spot_at
    hx, hy = ctx.hq
    D = ctx.district
    lift = getattr(ctx.CP, "SOLACE_LIFT", 1.0)
    R, rt, z0, z1 = C_R, C_RT, C_Z0, C_Z1
    pitch, steps, nseg = C_PITCH, C_STEPS, C_NSEG

    # the plinth drum and its lit ring
    cyl(SURF, hx, hy, C_PLINTH_Z[0], C_PLINTH_Z[1], C_PLINTH_R, 24, (0.38, 0.44, 0.42),
        wc=D["win"][0], wl=0.4, wm=1, bid=0.2)
    ring_line(NEON, hx, hy, 2.55, C_PLINTH_R + 0.05, 0.35, D["hue"], n=24)

    def cpos(ph, z):
        t = 2 * math.pi * (z - z0) / pitch + ph
        return (hx + R * math.cos(t), hy + R * math.sin(t), z)

    for ph in (0.0, math.pi):
        rings = []
        for k in range(steps + 1):
            z = z0 + (z1 - z0) * k / steps
            c = cpos(ph, z)
            tng = _unit(_sub(cpos(ph, z + 0.2), cpos(ph, z - 0.2)))
            nrm = _unit((c[0] - hx, c[1] - hy, 0.0))
            bnm = _unit(_cross(tng, nrm))
            nrm = _unit(_cross(bnm, tng))
            rings.append([tuple(c[i] + (nrm[i] * math.cos(2 * math.pi * m / nseg)
                                        + bnm[i] * math.sin(2 * math.pi * m / nseg)) * rt for i in range(3))
                          for m in range(nseg)])
        circ = 2 * math.pi * rt
        for k in range(steps):
            v0 = (z1 - z0) * k / steps
            v1 = (z1 - z0) * (k + 1) / steps
            for m in range(nseg):
                m1 = (m + 1) % nseg
                u0, u1 = circ * m / nseg, circ * (m + 1) / nseg
                SMOOTH.face([rings[k][m], rings[k][m1], rings[k + 1][m1], rings[k + 1][m]], TUBE_COL,
                            [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], WIN_TINT, 0.62, 2, 0.3 + ph * 0.1, 0)
        top = cpos(ph, z1)
        dome(SMOOTH, top[0], top[1], z1, rt, sc(D["hue"], 0.5), n=nseg, rings=4)      # crown cap

    # bow-tie bridges, one per floor (every 4.2 BU): wide at the tubes, pinched at the axis, hue edges
    z = z0 + 3.0
    while z < z1 - 2:
        a, c = cpos(0.0, z), cpos(math.pi, z)
        d = _unit(_sub(c, a))
        s = (-d[1], d[0], 0.0)
        m = _mul(_add(a, c), 0.5)
        pts = [_add(a, _mul(s, 2.6)), _add(m, _mul(s, 0.7)), _add(c, _mul(s, 2.6)),
               _sub(c, _mul(s, 2.6)), _sub(m, _mul(s, 0.7)), _sub(a, _mul(s, 2.6))]
        SURF.face(pts, (0.7, 0.75, 0.72))
        for i in range(6):
            bar(NEON, _add(pts[i], (0, 0, 0.05)), _add(pts[(i + 1) % 6], (0, 0, 0.05)), 0.14, D["hue"])
        z += C_BRIDGE_STEP

    # red beacons on the two tube tops
    for ph in (0.0, math.pi):
        c = cpos(ph, z1 + rt)
        box(NEON, c[0] - 0.5, c[1] - 0.5, c[2], c[0] + 0.5, c[1] + 0.5, c[2] + 1.2, (1.0, 0.25, 0.25))

    # lights: a cool-white key from the camera side, a hue fill (designer r3b: a little brighter via SOLACE_LIFT)
    spot_at((hx, hy, 40), (hx + 70, hy - 70, 10), (0.85, 1.0, 0.9), 1.6e6 * lift, 40)
    spot_at((hx, hy, 50), (hx - 50, hy - 80, 5), D["hue"], 1.2e6 * lift, 36)

    r = _footprint_radius(ctx)
    if r is not None and r < C_PLINTH_R:
        print("SOLACE warning: footprint radius", r, "< plinth radius", C_PLINTH_R, flush=True)
    return dict(label=(hx, hy, z1 + C_CROWN_LABEL_DZ), crown=(hx, hy, z1 + 3), hue=D["hue"])


# ================================================================== HQ KIT BUILD (reduced port of hq_build.py)
def build_hq(K, rooms=True, rail=False):
    """HQ-kit-unit build. rail is accepted for API parity and ignored (Solace has no rail).
    Reads CP keys: radius, floor_h, floors, twist (default 13.33), tube_r, route_floors, tower_w, tower_d,
    crown_h, podium (px, py, ph), bridge_w (wide, waist), start. Uses K.G (corp graph module) only for
    floor_z / tube_pt / room slots when rooms=True."""
    CP, pal, LH = K.CP, K.pal, K.LH
    G = getattr(K, "G", None) if rooms else None
    A, Acc, box, tube = K.A, K.Acc, K.box, K.tube
    log = K.log
    hooks = {"accs": {}, "beams": [], "mover_lights": {}}
    seed = getattr(K, "seed", None)
    seed = LEGACY_SEEDS["podium"] if seed is None else seed

    POR, CLIN = pal("porcelain"), pal("clinic")
    leaf, pink = pal("leaf"), pal("pink")
    R, FH, TOPF = CP["radius"], CP["floor_h"], CP["floors"]
    rt = CP["tube_r"]
    twist = CP.get("twist", 13.33)
    RFS = sorted(CP["route_floors"])
    px, py, ph = CP["podium"]
    wide, waist = CP["bridge_w"]
    TW, TD, CH = CP["tower_w"], CP["tower_d"], CP["crown_h"]

    PORC = Acc("porc", K.M["civic"], 1, K.COLL["compound"])
    hooks["accs"]["porc"] = PORC

    def floor_z(f):
        return G.floor_z(f) if G is not None and hasattr(G, "floor_z") else ph + f * FH
    ztop = floor_z(TOPF)
    zbase = ph

    def axis(t, z):
        """The tube axis at height z. Prefer the corp graph's own tube_pt so rooms and strands agree."""
        if G is not None and hasattr(G, "tube_pt"):
            p = G.tube_pt(t, z, 0.0, 0.0)
            return (p[0], p[1], z)
        th = math.radians(90.0 + twist * (z - zbase) / FH + (180.0 if t == "B" else 0.0))
        return (R * math.cos(th), R * math.sin(th), z)          # ASSUMPTION: azimuth measured from +x

    # ---- the strands: swept tubes (segment tubes at 1.5 BU steps; the real build uses one shared-vertex mesh)
    for t in ("A", "B"):
        z = zbase
        while z < ztop - 1e-6:
            z2 = min(ztop, z + 1.5)
            tube(PORC, axis(t, z), axis(t, z2), rt, POR, n=20)
            z = z2
        # the mint light seam up the back band (never the route lime)
        prev = None
        z = zbase
        while z <= ztop:
            c = axis(t, z)
            if G is not None and hasattr(G, "stair_phi") and hasattr(G, "tube_pt"):
                p = G.tube_pt(t, z, G.stair_phi(t) + math.pi, rt + 0.1)
            else:
                ang = math.atan2(c[1], c[0]) + math.pi         # ASSUMPTION: the outward side stands in for "back"
                p = (c[0] + (rt + 0.1) * math.cos(ang), c[1] + (rt + 0.1) * math.sin(ang), z)
            if prev is not None:
                tube(A["trim"], prev, p, 0.45, (0.55, 1.0, 0.72), LH["atrium_k"], n=6)
            prev = p
            z += 2.0
        # the downlight ring under every floor
        for f in range(TOPF):
            zd = floor_z(f) + 0.3
            c = axis(t, zd)
            n_ = 48
            for q in range(n_):
                a0, a1 = 2 * math.pi * q / n_, 2 * math.pi * (q + 1) / n_
                p0 = (c[0] + (rt + 0.08) * math.cos(a0), c[1] + (rt + 0.08) * math.sin(a0), zd)
                p1 = (c[0] + (rt + 0.08) * math.cos(a1), c[1] + (rt + 0.08) * math.sin(a1), zd)
                A["trim"].face([p0, p1, (p1[0], p1[1], zd + 0.25), (p0[0], p0[1], zd + 0.25)], (1.0, 0.95, 0.85),
                               LH["down_k"])

    # ---- bow-tie skybridges on the route floors only (the A <-> B cross-links)
    for f in RFS:
        zb = G.deck_z(f) if G is not None and hasattr(G, "deck_z") else floor_z(f)
        a, b = axis("A", zb), axis("B", zb)
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        e, q = (dx / L, dy / L), (-dy / L, dx / L)
        s0, s1 = rt * 0.8, L - rt * 0.8
        half = (s1 - s0) / 2.0
        mid = (s0 + s1) / 2.0

        def hw(s):
            return waist / 2 + (wide - waist) / 2 * (min(abs(s - mid), half) / half) ** 1.6

        def P(s, side, z):
            w = hw(s)
            return (a[0] + e[0] * s + q[0] * side * w, a[1] + e[1] * s + q[1] * side * w, z)
        NS = 16
        for k in range(NS):
            u0 = s0 + (s1 - s0) * k / NS
            u1 = s0 + (s1 - s0) * (k + 1) / NS
            PORC.face([P(u0, -1, zb - 0.01), P(u1, -1, zb - 0.01), P(u1, 1, zb - 0.01), P(u0, 1, zb - 0.01)][::-1], POR)
            PORC.face([P(u0, 1, zb - 0.8), P(u1, 1, zb - 0.8), P(u1, -1, zb - 0.8), P(u0, -1, zb - 0.8)], POR)
            for side in (-1, 1):
                PORC.face([P(u0, side, zb - 0.8), P(u1, side, zb - 0.8), P(u1, side, zb - 0.01), P(u0, side, zb - 0.01)], POR)
                A["glass"].face([P(u0, side, zb + 0.3), P(u1, side, zb + 0.3), P(u1, side, zb + 3.5), P(u0, side, zb + 3.5)],
                                (0.8, 0.95, 0.9))
                A["trim"].face([P(u0, side, zb + 0.3), P(u1, side, zb + 0.3), P(u1, side, zb + 0.55), P(u0, side, zb + 0.55)],
                               (0.75, 1.0, 0.85), LH["bridge_wall_k"] * 8.0)
            A["trim"].face([P(u0, -0.25, zb + 0.02), P(u1, -0.25, zb + 0.02), P(u1, 0.25, zb + 0.02), P(u0, 0.25, zb + 0.02)],
                           CLIN, LH["bridge_route_k"] * 0.45)
            PORC.face([P(u0, -1, zb + 3.5), P(u1, -1, zb + 3.5), P(u1, 1, zb + 3.7), P(u0, 1, zb + 3.7)], POR)
    log("solace strands + bridges")

    # ---- the crown joining the towers, THE GENOME CORE open in its middle (the TARGET), the pink halo ring
    zc = ztop
    cen = ((axis("A", zc)[0] + axis("B", zc)[0]) / 2.0, (axis("A", zc)[1] + axis("B", zc)[1]) / 2.0)
    span = R + TD / 2
    for (s0_, s1_) in ((-span, -11.0), (11.0, span)):
        box(PORC, cen[0] + s0_, cen[1] - TW / 2, zc, cen[0] + s1_, cen[1] + TW / 2, zc + 1.5, POR)
        box(A["glass"], cen[0] + s0_, cen[1] - TW / 2, zc + 1.5, cen[0] + s1_, cen[1] + TW / 2, zc + CH, (0.015, 0.04, 0.03))
        box(PORC, cen[0] + s0_, cen[1] - TW / 2, zc + CH, cen[0] + s1_, cen[1] + TW / 2, zc + CH + 1.5, POR)
    # ASSUMPTION: the crown axis is x here; the real build orients it on the A-tower normal via oquad / obox frames
    emv = K.ROOM_EMIT.setdefault("srv", Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"])) if hasattr(K, "ROOM_EMIT") \
        else A["trim"]
    so = G.ROOM["srv"]["o"] if G is not None and "srv" in getattr(G, "ROOM", {}) else (cen[0], cen[1], zc)
    tube(A["metal"], (so[0], so[1], zc + 1.5), (so[0], so[1], zc + CH), 3.4, (0.08, 0.08, 0.1), n=16)
    for k_ in range(8):
        zz = zc + 2.5 + k_ * 1.4
        tube(emv, (so[0], so[1], zz), (so[0], so[1], zz + 0.3), 3.5, (1.0, 0.22, 0.08), 6.0, n=24)
    for k in range(48):
        a0, a1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 1) / 48
        tube(A["trim"], (cen[0] + math.sin(a0) * 20, cen[1] + math.cos(a0) * 20, zc + CH + 8.0),
             (cen[0] + math.sin(a1) * 20, cen[1] + math.cos(a1) * 20, zc + CH + 8.0), 0.5, pink, 3.0, n=4)
    K.add_light("crown_glow", "POINT", (cen[0], cen[1], zc + CH + 6.0), 2.0e4, pink, size=3.0, group="corp", shadow=False)

    # ---- the plaza podium: dark, dressed, the lit entry, the SOLACE name
    PL = (0.09, 0.10, 0.10)
    box(PORC, -px, -py, 0.0, px, py, ph, PL)
    prr = art_rng(seed, "podium")
    for (qx, qy) in ((-46.0, -34.0), (46.0, -34.0), (-46.0, 34.0), (46.0, 34.0), (-52.0, 0.0), (52.0, 0.0)):
        box(A["rough"], qx - 6.0, qy - 3.0, ph, qx + 6.0, qy + 3.0, ph + 1.0, (0.06, 0.07, 0.06))
        box(A["trim"], qx - 6.05, qy - 3.05, ph + 0.95, qx + 6.05, qy + 3.05, ph + 1.05, leaf, LH["trim_k"] * 0.5)
        for _ in range(5):
            tx_, ty_ = qx + prr.uniform(-5, 5), qy + prr.uniform(-2.4, 2.4)
            tube(A["rough"], (tx_, ty_, ph + 1.0), (tx_, ty_, ph + prr.uniform(2.0, 3.6)), prr.uniform(0.5, 0.9),
                 (0.03, 0.08, 0.04), n=6)
    box(A["glass"], -12.0, -py + 0.5, ph, 12.0, -py + 6.0, ph + 7.0, (0.02, 0.05, 0.04))
    box(A["trim"], -11.0, -py + 0.45, ph + 0.4, 11.0, -py + 0.5, ph + 6.2, (1.0, 0.92, 0.78), 2.6)
    box(PORC, -13.0, -py - 1.5, ph + 7.0, 13.0, -py + 6.5, ph + 8.0, PL)
    box(A["trim"], -13.0, -py - 1.55, ph + 7.2, 13.0, -py - 1.5, ph + 7.8, leaf, LH["trim_k"])
    for s in range(6):
        box(PORC, -18.0, -py - (6 - s) * 1.4, 0.0, 18.0, -py, ph * (s + 1) / 6, PL)
        box(A["trim"], -18.0, -py - (6 - s) * 1.4 - 0.03, ph * (s + 1) / 6 - 0.12, 18.0, -py - (6 - s) * 1.4,
            ph * (s + 1) / 6 - 0.04, (1.0, 0.9, 0.75), 1.2)
    STEN = {"S": ["0111", "1000", "0110", "0001", "1110"], "O": ["0110", "1001", "1001", "1001", "0110"],
            "L": ["1000", "1000", "1000", "1000", "1111"], "A": ["0110", "1001", "1111", "1001", "1001"],
            "C": ["0111", "1000", "1000", "1000", "0111"], "E": ["1111", "1000", "1110", "1000", "1111"]}
    if hasattr(K, "oquad"):
        rec = dict(o=(30.0, -py - 0.1, 0.0), n=(0.0, -1.0))
        cell = 0.62
        word = "SOLACE"
        uu = -sum((len(STEN[c][0]) + 1) * cell for c in word) / 2
        for ch_ in word:
            gph = STEN[ch_]
            for row, bits in enumerate(gph):
                for cix, bit in enumerate(bits):
                    if bit == "1":
                        K.oquad(A["sign"], rec, 0.05, -(uu + (cix + 1) * cell - cell * 0.15), 0.9 + (4 - row) * cell * 0.8,
                                -(uu + cix * cell), 0.9 + (5 - row) * cell * 0.8 - cell * 0.12, leaf,
                                6.0 * LH["sign_k"] * 4)
            uu += (len(gph[0]) + 1) * cell
    for k, (wx, wy) in enumerate(((-34.0, -26.0), (34.0, -26.0), (-34.0, 26.0), (34.0, 26.0))):
        K.add_light("plaza_wash_%d" % k, "AREA", (wx, wy, ph + 16.0), LH["plaza_wash_w"], (1.0, 0.78, 0.55),
                    aim=(wx, wy, ph), size=40.0, size_y=30.0, group="corp", shadow=False)

    # ---- the landmark rig: ground spots up the towers (no plinth beams: v3), the rim from the city behind
    for k in range(8):
        ang = math.radians(22.5 + 45.0 * k)
        v = (math.sin(ang), math.cos(ang))                       # ASSUMPTION: az_vec(a) = (sin a, cos a), azimuth from north
        p = (v[0] * 58.0, v[1] * 46.0, ph + 0.4)
        K.add_light("ground_spot_%d" % k, "SPOT", p, LH["ground_spot_w"], CLIN if k % 2 else (0.75, 1.0, 0.7),
                    aim=(v[0] * 6.0, v[1] * 6.0, 110.0), size=1.5, spot=26, blend=0.5, group="corp")
        box(A["small"], p[0] - 1.2, p[1] - 1.2, p[2], p[0] + 1.2, p[1] + 1.2, p[2] + 0.6, CLIN, 8.0)
    for k in range(4):
        ang = math.radians(45.0 + 90.0 * k)
        v = (math.sin(ang), math.cos(ang))
        K.add_light("rim_%d" % k, "AREA", (v[0] * 230.0, v[1] * 230.0, 70.0), LH["rim_w"],
                    pal("district_a" if k % 2 else "district_b"), aim=(0.0, 0.0, 90.0), size=90.0, size_y=140.0,
                    group="corp", shadow=False)

    # ---- the route rooms: slots come from the game graph mapped by G (spec 8.4), never generated here
    if G is not None and hasattr(K, "room_shell"):
        for i in G.NODES:
            if i in getattr(G, "TOWER", {}):
                K.room_shell(i, G.ROOM[i])
    log("solace rig")
    return hooks


# ================================================================== dispatcher and info
def build(K, rooms=True, rail=False):
    """City hook: build(ctx) -> dict(label, crown, hue). HQ kit: build(K, rooms, rail) -> hooks."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return _build_city(K)
    return build_hq(K, rooms, rail)


def landmark_info():
    """Constants for the pipeline checks (spec 12.2 / 8.6b). Lengths in city BU unless noted."""
    return dict(
        corp=CORP,
        central_server_name=CENTRAL_SERVER_NAME,
        footprint_bu=2.0 * C_PLINTH_R,                      # drum diameter (plinth); the helix spans 2 * (7.5 + 3.4)
        footprint_radius_bu=C_PLINTH_R,
        tier_heights=dict(plinth_top=C_PLINTH_Z[1], helix_base=C_Z0, helix_top=C_Z1,
                          crown_label=C_Z1 + C_CROWN_LABEL_DZ, bridge_step=C_BRIDGE_STEP),
        pass_indices=dict(compound=1, rooms=5, movers=6),   # HQ kit object pass indices (spec 8.1)
        hue=None,                                           # the district hue comes from ctx.district at build time
    )
