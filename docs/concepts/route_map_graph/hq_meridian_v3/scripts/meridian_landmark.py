"""MERIDIAN v3 LANDMARK: THE GATEHOUSE GANTRY, an importable Blender build (DESIGN.md).

ENTRY POINT
    import meridian_landmark as ML
    hooks = ML.build(K, rooms=True, rail=True)

    K        the helper namespace (the HQ kit's hq_scene passes it; any caller can build its own):
               A        {"metal", "rough", "civic", "glass", "trim", "small", "ground", "int", "cut"...}: accumulators with
                        .face(points, colour, k) (k = emission strength for emission accumulators)
               Acc      Acc(name, material, pass_index, collection) -> a new accumulator (it must have .face / .build)
               box, tube, seg_box, new_mat, attr, pos_sep, mth, nn, smooth, vsc, vmul, mixc   (hq_scene signatures)
               add_light(name, kind, loc, energy, colour, aim=, size=, size_y=, spot=, blend=, group=, shadow=, receivers=)
               M        {"rough", "civic", "emit", ...} materials;  COLL {"compound", "rooms"} collections
               CP       the compound numbers (hq_preset.PRESET["hq"]["compound"]); LH the light numbers; pal(name)
               HZ       PRESET["hq"] (for HZ["beams"]); log(*a)
               G        hq_graph (room slots) when rooms=True; ROOM_EMIT {}; room_shell(id, rec) (hq_scene's cutaway)
    rooms    True: cut the route slots (hq_graph.ROOM) and build their cutaway rooms; False: a solid landmark (the city)
    rail     True: build the freight line (meridian_rail.centreline: the N-edge tracks, the train, the viaduct to the
             port); False: the landmark only (the city has its own line)
    returns  hooks: {"accs": {name: Acc}, "beams": [(origin, dir, colour, power, cone)], "mover_lights": {},
             "post_build": fn(OBJ)} (the kit builds the accs and calls post_build)

UNITS / PLACING IN THE CITY
    Geometry is emitted in HQ-kit units (1 storey = 8 BU) around the HQ centre (0, 0, 0), north = +y. To drop it into
    the one-city map (1 floor = 1.9 BU), wrap K first:
        K2 = ML.place(K, origin=(hx, hy, 0.0), k=0.2375)     # every face, light and beam is moved and scaled
        hooks = ML.build(K2, rooms=False, rail=False)
    place() proxies the accumulators (all geometry goes through .face) and add_light (position, aim, size x k,
    energy x k^2), so the build itself never changes. The landmark fills the lot |x|, |y| <= CP["lot"] (120 kit BU
    = 28.5 city BU half size).

Everything is placed by rule from CP (hq_preset "compound"); seeds 5410 (container colours), 5411 (yard stacks),
5412 (trucks). Coordinator round 2 (2026-10-16): rust-orange paint + sodium-white lit edges; everything inside the lot;
big rail-gate arches; lit truck cabs + bay-lane lights; the train a lit high-speed set with noses; the line on the
city polyline to the port (deck 73.7 kit = 17.5 city BU); the keep parked.
"""
import math
import random
from types import SimpleNamespace

K_UNITS = 0.2375


# ================================================================== placing (for the city)
class _AccProxy:
    def __init__(self, acc, f):
        self._acc, self._f = acc, f

    def face(self, pts, col, k=0.0):
        self._acc.face([self._f(p) for p in pts], col, k)

    def __getattr__(self, n):
        return getattr(self._acc, n)


def place(K, origin=(0.0, 0.0, 0.0), k=K_UNITS):
    """A copy of K whose accumulators and lights are moved to origin and scaled by k (see the module doc)."""
    ox, oy, oz = origin

    def f(p):
        return (p[0] * k + ox, p[1] * k + oy, p[2] * k + oz)
    K2 = SimpleNamespace(**vars(K))
    K2.A = {n: _AccProxy(a, f) for n, a in K.A.items()}
    K2.Acc = lambda *a, **kw: _AccProxy(K.Acc(*a, **kw), f)

    def add_light(name, kind, loc, energy, col, aim=None, size=0.5, size_y=None, **kw):
        return K.add_light(name, kind, f(loc), energy * k * k, col, aim=None if aim is None else f(aim), size=size * k,
                           size_y=None if size_y is None else size_y * k, **kw)
    K2.add_light = add_light
    K2.place_f = f
    return K2


# ================================================================== the build
def build_hq(K, rooms=True, rail=True):
    CP, pal, LH = K.CP, K.pal, K.LH
    G = getattr(K, "G", None) if rooms else None
    A, Acc, tube, box = K.A, K.Acc, K.tube, K.box
    hooks = {"accs": {}, "beams": [], "mover_lights": {}}
    place_f = getattr(K, "place_f", None)
    rr = random.Random(5410)
    CRS = CP["course"]
    L, WT, NC = CP["lot"], CP["wall"]["t"], CP["wall"]["courses"]
    WTOP = NC * CRS
    STEEL = pal("steel_alt")
    RED, YW, YC, HAZ = pal("corp_red"), pal("yard_white"), pal("yard_cool"), pal("hazard")
    SOD, GANT, STONE, KEEPC, EDGE = pal("sodium"), pal("gantry"), pal("stone"), pal("keep"), pal("edge")
    TRAIN, TLIGHT = pal("train"), pal("train_light")
    log = K.log
    GC = CP["gantry"]
    GY = GC["y"]
    LEGX = L - WT / 2
    LHX, LHY = GC["leg"]
    SZ0, SZ1 = GC["span_z"]
    SH = GC["span_half"]
    KX = GC["keep_x"]
    KHX, KHY = GC["keep"]
    KTOP = GC["keep_top"]
    LTOP = GC["leg_top"]
    RG = CP["railgate"]
    RC = CP["rail"]
    YIN = RC["y"][0]

    # ------------------------------------------------------------ materials: the container (corrugated, wet, rust)
    m = None
    if not getattr(K, "CITY", False):          # the container shader (the city module has its own facade shader)
        m, nt = K.new_mat("container")
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        b = nt.nodes.new("ShaderNodeBsdfPrincipled")
        col = K.attr(nt, "col")
        g, ps, ns = K.pos_sep(nt)
        u_ = K.mth(nt, "ADD", ps.outputs["X"], ps.outputs["Y"])
        rib = K.mth(nt, "SINE", K.mth(nt, "MULTIPLY", u_, 4.2))
        n1 = K.nn(nt, "ShaderNodeTexNoise", Scale=0.18, Detail=6.0, Roughness=0.62)
        nt.links.new(g.outputs["Position"], n1.inputs["Vector"])
        rust = K.smooth(nt, n1.outputs["Fac"], 0.48, 0.70)
        n2 = K.nn(nt, "ShaderNodeTexNoise", Scale=1.1, Detail=3.0)
        nt.links.new(K.vmul(nt, g.outputs["Position"], (1.0, 1.0, 0.07)), n2.inputs["Vector"])
        streak = K.smooth(nt, n2.outputs["Fac"], 0.5, 0.78)
        base = K.vsc(nt, col.outputs["Color"], K.mth(nt, "MULTIPLY", K.mth(nt, "ADD", 0.85, K.mth(nt, "MULTIPLY", rib, 0.08)),
                                                      K.mth(nt, "SUBTRACT", 1.0, K.mth(nt, "MULTIPLY", streak, 0.25))))
        base = K.mixc(nt, K.mth(nt, "MULTIPLY", rust, 0.45), base, (0.16, 0.05, 0.018))
        nt.links.new(base, b.inputs["Base Color"])
        nt.links.new(K.mth(nt, "ADD", 0.22, K.mth(nt, "MULTIPLY", rust, 0.45)), b.inputs["Roughness"])
        b.inputs["Metallic"].default_value = 0.35
        b.inputs["Coat Weight"].default_value = 0.3
        b.inputs["Coat Roughness"].default_value = 0.1
        bump = K.nn(nt, "ShaderNodeBump", Strength=0.35, Distance=0.08)
        nt.links.new(rib, bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
        nt.links.new(b.outputs[0], out.inputs[0])
    C = Acc("containers", m, 1, K.COLL["compound"])
    hooks["accs"]["containers"] = C
    MASON = Acc("masonry", K.M["rough"], 1, K.COLL["compound"])           # the towers' dark cast concrete
    GANTRY = Acc("gantry", K.M["civic"], 1, K.COLL["compound"])           # the crane: panelled, wet, rust-orange
    SEAM = Acc("seams", K.M["emit"], 1, K.COLL["compound"])               # the landmark's lit edges
    TRAINA = Acc("train", K.M["civic"], 1, K.COLL["compound"])
    TGLASS = Acc("train_glass", K.M["glass"], 1, K.COLL["compound"])
    for n_, a_ in (("masonry", MASON), ("gantry", GANTRY), ("seams", SEAM), ("train", TRAINA), ("train_glass", TGLASS)):
        hooks["accs"][n_] = a_

    # ------------------------------------------------------------ solids with cavities, crenellations, slits
    def cav_of(i):
        r = G.ROOM[i]
        n = r["n"]
        ox, oy, z0 = r["o"]
        t = (n[1], -n[0])
        hw = r["w"] / 2 + 0.6
        pts = [(ox + t[0] * s * hw - n[0] * dd, oy + t[1] * s * hw - n[1] * dd) for s in (-1, 1) for dd in (-0.5, r["d"] + 0.4)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return (min(xs), min(ys), z0 - 0.7, max(xs), max(ys), z0 + r["h"] + 0.7)

    def solid(acc, x0, y0, z0, x1, y1, z1, col, cavs=(), k=0.0):
        """A box minus cavity boxes (rooms, arches): sliced in z at the cavities, each slab a grid of cells."""
        cv = [c for c in cavs if c and c[0] < x1 and c[3] > x0 and c[1] < y1 and c[4] > y0 and c[2] < z1 and c[5] > z0]
        if not cv:
            box(acc, x0, y0, z0, x1, y1, z1, col, k)
            return
        zs = sorted({z0, z1} | {min(z1, max(z0, c[2])) for c in cv} | {min(z1, max(z0, c[5])) for c in cv})
        for za, zb in zip(zs, zs[1:]):
            if zb - za < 1e-3:
                continue
            hs = [c for c in cv if c[2] < zb - 1e-4 and c[5] > za + 1e-4]
            if not hs:
                box(acc, x0, y0, za, x1, y1, zb, col, k)
                continue
            xs = sorted({x0, x1} | {min(x1, max(x0, c[0])) for c in hs} | {min(x1, max(x0, c[3])) for c in hs})
            ys = sorted({y0, y1} | {min(y1, max(y0, c[1])) for c in hs} | {min(y1, max(y0, c[4])) for c in hs})
            for xa, xb in zip(xs, xs[1:]):
                for ya, yb in zip(ys, ys[1:]):
                    if xb - xa < 1e-3 or yb - ya < 1e-3:
                        continue
                    mx_, my_ = (xa + xb) / 2, (ya + yb) / 2
                    if any(c[0] < mx_ < c[3] and c[1] < my_ < c[4] for c in hs):
                        continue
                    box(acc, xa, ya, za, xb, yb, zb, col, k)

    def merlons(acc, x0, y0, x1, y1, z, col, step=5.0, h=4.0, t=2.4, sides="SENW"):
        for side in sides:
            if side in "SN":
                y = y0 if side == "S" else y1 - t
                n = max(2, int((x1 - x0) / step))
                for k in range(0, n, 2):
                    a = x0 + (x1 - x0) * k / n
                    box(acc, a, y, z, a + (x1 - x0) / n, y + t, z + h, col)
            else:
                x = x0 if side == "W" else x1 - t
                n = max(2, int((y1 - y0) / step))
                for k in range(0, n, 2):
                    a = y0 + (y1 - y0) * k / n
                    box(acc, x, a, z, x + t, a + (y1 - y0) / n, z + h, col)

    def slits(acc, x0, y0, x1, y1, z0, z1, side, col, kk, n=3, rows=(0.35, 0.65), w=0.8, hgt=4.0):
        for fz in rows:
            zc = z0 + (z1 - z0) * fz
            for j in range(n):
                f = (j + 0.5) / n
                if side in "SN":
                    x = x0 + (x1 - x0) * f
                    y = y0 - 0.05 if side == "S" else y1 + 0.05
                    q = [(x - w / 2, y, zc - hgt / 2), (x + w / 2, y, zc - hgt / 2), (x + w / 2, y, zc + hgt / 2),
                         (x - w / 2, y, zc + hgt / 2)]
                    acc.face(q if side == "S" else q[::-1], col, kk)
                else:
                    y = y0 + (y1 - y0) * f
                    x = x0 - 0.05 if side == "W" else x1 + 0.05
                    q = [(x, y + w / 2, zc - hgt / 2), (x, y - w / 2, zc - hgt / 2), (x, y - w / 2, zc + hgt / 2),
                         (x, y + w / 2, zc + hgt / 2)]
                    acc.face(q if side == "W" else q[::-1], col, kk)

    def drum(acc, cx, cy, r, z0, z1, col, cap=True):
        tube(acc, (cx, cy, z0), (cx, cy, z1), r, col, n=16)
        if cap:
            acc.face([(cx + r * math.cos(2 * math.pi * i / 16), cy + r * math.sin(2 * math.pi * i / 16), z1)
                      for i in range(16)], col)
        for k in range(0, 12, 2):
            a = 2 * math.pi * k / 12
            box(acc, cx + (r - 0.8) * math.cos(a) - 0.9, cy + (r - 0.8) * math.sin(a) - 0.9, z1,
                cx + (r - 0.8) * math.cos(a) + 0.9, cy + (r - 0.8) * math.sin(a) + 0.9, z1 + 3.4, col)

    def beacon(x, y, z):
        box(A["small"], x - 0.8, y - 0.8, z, x + 0.8, y + 0.8, z + 1.6, RED, 14.0)

    ROOMS = [i for i in G.NODES if i not in ("start", "srv")] if G else []
    CAVS = {i: cav_of(i) for i in ROOMS if G.SLOT.get(i) not in ("truck_box", "train_box")}

    def cav(*ids):
        return [CAVS[i] for i in ids if i in CAVS]

    # ------------------------------------------------------------ ground: the lot, lanes, the quay
    box(A["ground"], -L, -L, -0.02, L, L, 0.0, (0.30, 0.30, 0.31), k=1.0)
    LN = CP["lane"]
    lanes = [(-L + WT, LN["s_y"] - 7, L - WT, LN["s_y"] + 7, "x"),
             (-LN["ew_x"] - 7, -L + WT, -LN["ew_x"] + 7, LN["n_end"], "y"),
             (LN["ew_x"] - 7, -L + WT, LN["ew_x"] + 7, LN["n_end"], "y")]
    for (x0, y0, x1, y1, ax) in lanes:
        box(A["ground"], x0, y0, 0.0, x1, y1, 0.01, (0.07, 0.07, 0.075), k=0.0)
        # bay-lane lights: amber edge lines, a lamp post every 22 BU, one sodium area light over the lane
        if ax == "x":
            for yy in (y0 + 0.3, y1 - 0.3):
                box(SEAM, x0, yy - 0.15, 0.02, x1, yy + 0.15, 0.08, HAZ, 2.0)
            u = x0 + 8
            while u < x1 - 4:
                box(A["metal"], u - 0.25, y1 - 0.6, 0.0, u + 0.25, y1 - 0.1, 12.0, (0.2, 0.2, 0.22))
                box(A["small"], u - 1.2, y1 - 2.6, 11.6, u + 1.2, y1 - 0.1, 12.0, SOD, 10.0)
                u += 22.0
        else:
            for xx in (x0 + 0.3, x1 - 0.3):
                box(SEAM, xx - 0.15, y0, 0.02, xx + 0.15, y1, 0.08, HAZ, 2.0)
            xo_ = x0 + 0.1 if x0 > 0 else x1 - 0.6
            v = y0 + 8
            while v < y1 - 4:
                box(A["metal"], xo_, v - 0.25, 0.0, xo_ + 0.5, v + 0.25, 12.0, (0.2, 0.2, 0.22))
                box(A["small"], xo_ - 1.0, v - 1.2, 11.6, xo_ + 1.5, v + 1.2, 12.0, SOD, 10.0)
                v += 22.0
        K.add_light("lane_%s_%d" % (ax, int(x0)), "AREA", ((x0 + x1) / 2, (y0 + y1) / 2, 13.0), LH["lane_w"], SOD,
                    aim=((x0 + x1) / 2, (y0 + y1) / 2, 0.0), size=x1 - x0, size_y=y1 - y0, group="corp", shadow=False)
    for k in range(-12, 13):
        box(A["small"], k * 7.5 - 1.6, LN["s_y"] - 0.12, 0.012, k * 7.5 + 1.6, LN["s_y"] + 0.12, 0.02, HAZ, 0.4)
    q0, q1 = CP["quay"]
    box(A["ground"], -L + WT, q0, 0.0, L - WT, q1, 1.4, (0.24, 0.24, 0.25), k=1.0)
    box(SEAM, -L + WT, q1 - 0.4, 1.4, L - WT, q1, 1.46, HAZ, 1.5)
    # the platform lights (designer round 2): a lamp every 11 BU on the platform edge, a lit canopy line, real spots
    for k in range(-8, 9):
        px = k * 11.0
        box(A["metal"], px - 0.25, q1 - 2.0, 1.4, px + 0.25, q1 - 1.5, 12.0, (0.2, 0.2, 0.22))
        box(A["small"], px - 1.2, q1 - 3.4, 11.6, px + 1.2, q1 - 0.2, 12.0, YW, 12.0)
        if k % 3 == 0:
            K.add_light("quay_%d" % k, "SPOT", (px, q1 - 1.8, 11.4), LH["sodium_w"] * 1.5, YW, aim=(px, q1 + 4.0, 0.0),
                        size=0.6, spot=110, blend=0.8, group="corp", shadow=False)
    box(SEAM, -88.0, q1 - 1.9, 11.0, 88.0, q1 - 1.6, 11.3, YW, LH["seam_k"])

    # ------------------------------------------------------------ the curtain walls (crosswise containers)
    def container_x(x0, x1, y0, y1, z0, z1, c, out_face):
        box(C, x0, y0 + 0.15, z0 + 0.15, x1, y1 - 0.15, z1, c)
        fx = x0 - 0.06 if out_face == "W" else x1 + 0.06
        for f in (0.2, 0.42, 0.58, 0.8):
            yy = y0 + (y1 - y0) * f
            box(A["metal"], fx - 0.1, yy - 0.09, z0 + 0.5, fx + 0.1, yy + 0.09, z1 - 0.4, (0.05, 0.05, 0.055))

    def container_y(x0, x1, y0, y1, z0, z1, c, out_face):
        box(C, x0 + 0.15, y0, z0 + 0.15, x1 - 0.15, y1, z1, c)
        fy = y0 - 0.06 if out_face == "S" else y1 + 0.06
        for f in (0.2, 0.42, 0.58, 0.8):
            xx = x0 + (x1 - x0) * f
            box(A["metal"], xx - 0.09, fy - 0.1, z0 + 0.5, xx + 0.09, fy + 0.1, z1 - 0.4, (0.05, 0.05, 0.055))

    WALL_ROOMS = [i for i in ROOMS if G.SLOT.get(i) in ("wall_outer", "wall_inner")]
    GHW = CP["gate"]["half"]
    GTX = CP["gate"]["tower"][0]
    gate_gap = GHW + 2 * GTX
    CH = CP["corner"]["half"]

    def in_room(x0, y0, x1, y1, z0, z1):
        for i in WALL_ROOMS:
            c = CAVS[i]
            if c[0] < x1 - 0.2 and c[3] > x0 + 0.2 and c[1] < y1 - 0.2 and c[4] > y0 + 0.2 and c[2] < z1 - 0.2 and c[5] > z0 + 0.2:
                return True
        return False

    SLOTW = 6.6
    for sx in (-1, 1):                                                  # the E / W walls (runways)
        xo, xi = sx * L, sx * (L - WT)
        ya, yb = -L + 2 * CH, RG["y0"]
        gy0, gy1 = CP["gate"]["ew_y"] - gate_gap, CP["gate"]["ew_y"] + gate_gap
        for c in range(NC):
            z0, z1 = c * CRS, c * CRS + CRS - 0.4
            y = ya
            while y < yb - 1.0:
                y1 = min(y + SLOTW, yb)
                if not (gy0 - 0.5 < (y + y1) / 2 < gy1 + 0.5) and not in_room(min(xo, xi), y, max(xo, xi), y1, z0, z1):
                    container_x(min(xo, xi), max(xo, xi), y, y1, z0, z1, STEEL[rr.randrange(len(STEEL))],
                                "W" if sx < 0 else "E")
                y = y1
        y = ya
        k = 0
        while y < yb - 1.0:
            if k % 2 == 0 and not (gy0 < y + 3 < gy1):
                box(C, min(xo, xo - sx * 4.2), y + 0.2, WTOP, max(xo, xo - sx * 4.2), y + SLOTW - 0.2,
                    WTOP + CP["wall"]["merlon_h"], STEEL[rr.randrange(len(STEEL))])
            y += SLOTW
            k += 1
        box(A["rough"], min(xo, xi), -L + WT, WTOP - 0.4, max(xo, xi), L, WTOP, (0.10, 0.10, 0.11))
        for o_ in (-4.0, 4.0):
            box(A["metal"], sx * LEGX + o_ - 0.35, -L + WT, WTOP, sx * LEGX + o_ + 0.35, L, WTOP + 0.7, (0.35, 0.35, 0.37))
        box(SEAM, xo - 0.2, ya, WTOP - 1.2, xo + 0.2, yb, WTOP - 0.8, EDGE, LH["seam_k"])
        box(SEAM, xi - 0.15, ya, WTOP - 1.2, xi + 0.15, yb, WTOP - 0.8, SOD, LH["seam_k"] * 0.6)
    yo, yi = -L, -L + WT
    xa, xb = -L + 2 * CH, L - 2 * CH
    gx0, gx1 = CP["gate"]["s_x"] - gate_gap, CP["gate"]["s_x"] + gate_gap
    for c in range(NC):
        z0, z1 = c * CRS, c * CRS + CRS - 0.4
        x = xa
        while x < xb - 1.0:
            x1 = min(x + SLOTW, xb)
            if not (gx0 - 0.5 < (x + x1) / 2 < gx1 + 0.5) and not in_room(x, yo, x1, yi, z0, z1):
                container_y(x, x1, yo, yi, z0, z1, STEEL[rr.randrange(len(STEEL))], "S")
            x = x1
    x = xa
    k = 0
    while x < xb - 1.0:
        if k % 2 == 0 and not (gx0 < x + 3 < gx1):
            box(C, x + 0.2, yo, WTOP, x + SLOTW - 0.2, yo + 4.2, WTOP + CP["wall"]["merlon_h"], STEEL[rr.randrange(len(STEEL))])
        x += SLOTW
        k += 1
    box(A["rough"], xa, yo, WTOP - 0.4, xb, yi, WTOP, (0.10, 0.10, 0.11))
    box(SEAM, xa, yo - 0.2, WTOP - 1.2, xb, yo + 0.05, WTOP - 0.8, EDGE, LH["seam_k"])
    # wall washers: street-level spots grazing up the outer container faces
    for k in range(-3, 4):
        u = k * 28.0 + 14.0
        if abs(u) < 26 or abs(u) > 90:
            continue
        K.add_light("wash_s_%d" % k, "SPOT", (u, -L - 6.0, 0.6), LH["wash_w"], SOD if k % 2 else YW,
                    aim=(u, -L, WTOP * 0.8), size=0.8, spot=55, blend=0.7, group="corp", shadow=False)
        for sx in (-1, 1):
            K.add_light("wash_%d_%d" % (sx, k), "SPOT", (sx * (L + 6.0), u - 30.0, 0.6), LH["wash_w"],
                        SOD if k % 2 else YW, aim=(sx * L, u - 30.0, WTOP * 0.8), size=0.8, spot=55, blend=0.7,
                        group="corp", shadow=False)
    log("walls")

    # ------------------------------------------------------------ towers (all inside the lot)
    for sx in (-1, 1):
        cx, cy = sx * (L - CH), -L + CH
        x0, y0, x1, y1 = cx - CH, cy - CH, cx + CH, cy + CH
        H = CP["corner"]["h"]
        solid(MASON, x0, y0, 0.0, x1, y1, H, STONE, cav("tw", "te"))
        merlons(MASON, x0, y0, x1, y1, H, STONE, step=4.6, h=4.2, t=2.4)
        box(SEAM, x0 - 0.2, y0 - 0.2, H - 0.9, x1 + 0.2, y0 + 0.05, H - 0.5, EDGE, LH["seam_k"])
        box(SEAM, (x0 if sx < 0 else x1) - 0.2, y0, H - 0.9, (x0 if sx < 0 else x1) + 0.2, y1, H - 0.5, EDGE, LH["seam_k"])
        slits(A["small"], x0, y0, x1, y1, 4.0, 32.0, "S", YW, 3.0, n=3)
        slits(A["small"], x0, y0, x1, y1, 4.0, 52.0, "W" if sx < 0 else "E", YW, 3.0, n=3, rows=(0.2, 0.45, 0.7))
        beacon(cx, cy, H + 4.2)
        K.add_light("tflood_%d" % sx, "SPOT", (cx - sx * 10, cy + 10, H + 6.0), 1.2e5, SOD,
                    aim=(cx * 0.3, -20.0, 0.0), size=1.5, spot=70, blend=0.6, group="corp")
        # the RAIL GATE: the runway wall bridges both tracks on one big stepped arch (to the lot edge); drum turrets
        # on its inner side, both ends
        rx0, rx1 = sx * L - (WT if sx > 0 else 0), sx * L + (WT if sx < 0 else 0)
        ry0, ry1 = RG["y0"], L
        a0, a1 = RG["arch"]
        AH = RG["arch_h"]
        arches = [(rx0 - 1, a0, 0.0, rx1 + 1, a1, AH - 6.0), (rx0 - 1, a0 + 2.5, 0.0, rx1 + 1, a1 - 2.5, AH - 2.5),
                  (rx0 - 1, a0 + 6.5, 0.0, rx1 + 1, a1 - 6.5, AH)]
        solid(MASON, rx0, ry0, 0.0, rx1, ry1, WTOP, STONE, arches)
        merlons(MASON, rx0, ry0, rx1, ry1, WTOP, STONE, step=4.6, h=4.2, t=2.4, sides="W" if sx < 0 else "E")
        for xo_ in (rx0 - 0.1, rx1 + 0.1):                              # the arch outline, lit (cold: the rail's colour)
            for (ya_, yb_, za_) in ((a0, a0 + 0.5, AH - 6.0), (a1 - 0.5, a1, AH - 6.0)):
                box(SEAM, xo_ - 0.15, ya_, 0.0, xo_ + 0.15, yb_, za_, TLIGHT, LH["seam_k"])
            box(SEAM, xo_ - 0.15, a0, AH - 6.4, xo_ + 0.15, a0 + 2.5, AH - 6.0, TLIGHT, LH["seam_k"])
            box(SEAM, xo_ - 0.15, a1 - 2.5, AH - 6.4, xo_ + 0.15, a1, AH - 6.0, TLIGHT, LH["seam_k"])
            box(SEAM, xo_ - 0.15, a0 + 2.5, AH - 2.9, xo_ + 0.15, a0 + 6.5, AH - 2.5, TLIGHT, LH["seam_k"])
            box(SEAM, xo_ - 0.15, a1 - 6.5, AH - 2.9, xo_ + 0.15, a1 - 2.5, AH - 2.5, TLIGHT, LH["seam_k"])
            box(SEAM, xo_ - 0.15, a0 + 6.5, AH - 0.4, xo_ + 0.15, a1 - 6.5, AH, TLIGHT, LH["seam_k"])
        box(SEAM, (rx0 if sx < 0 else rx1) - 0.2, ry0, WTOP - 1.2, (rx0 if sx < 0 else rx1) + 0.2, ry1, WTOP - 0.8, EDGE,
            LH["seam_k"])
        r_ = RG["drum_r"]
        for ty in (ry0 - r_ + 1.0, L - r_):
            dx_ = sx * (L - WT - r_ + 0.5)
            drum(MASON, dx_, ty, r_, 0.0, RG["drum_h"], STONE)
            box(SEAM, dx_ - r_ - 0.1, ty - r_ - 0.1, RG["drum_h"] - 1.6, dx_ + r_ + 0.1, ty + r_ + 0.1, RG["drum_h"] - 1.2,
                EDGE, LH["seam_k"])
            beacon(dx_, ty, RG["drum_h"] + 3.4)
        K.add_light("railgate_%d" % sx, "AREA", (sx * (L - WT / 2), (a0 + a1) / 2, AH - 1.0), LH["sodium_w"] * 3, TLIGHT,
                    aim=(sx * (L - WT / 2), (a0 + a1) / 2, 0.0), size=WT, size_y=a1 - a0 - 8, group="corp", shadow=False)

    def gatehouse(side):
        GH, AH = CP["gate"]["h"], CP["gate"]["arch_h"]
        if side == "S":
            gx = CP["gate"]["s_x"]
            for s in (-1, 1):
                tx = gx + s * (GHW + GTX)
                solid(MASON, tx - GTX, -L, 0.0, tx + GTX, -L + WT + 6, GH, STONE)
                merlons(MASON, tx - GTX, -L, tx + GTX, -L + WT + 6, GH, STONE, step=4.0, h=4.0, t=2.0)
                slits(A["small"], tx - GTX, -L, tx + GTX, -L + WT + 6, 6.0, GH - 4, "S", YW, 3.0, n=2, rows=(0.25, 0.5, 0.75))
                box(SEAM, tx - GTX, -L - 0.25, GH - 0.9, tx + GTX, -L, GH - 0.5, EDGE, LH["seam_k"])
                box(A["small"], tx - s * (GTX - 0.4) - 0.6, -L - 0.5, AH - 3, tx - s * (GTX - 0.4) + 0.6, -L, AH - 1.4, RED, 12.0)
            solid(MASON, gx - GHW, -L + 1.6, AH, gx + GHW, -L + WT + 2, GH - 4, STONE, cav("gs"))
            merlons(MASON, gx - GHW, -L + 1.6, gx + GHW, -L + WT + 2, GH - 4, STONE, step=3.6, h=3.6, t=2.0, sides="SN")
            for k in range(7):
                xx = gx - GHW + 1.3 + k * (2 * GHW - 2.6) / 6
                box(MASON, xx - 0.6, -L, GH - 9, xx + 0.6, -L + 1.6, GH - 6.5, STONE)
            for k in range(9):
                xx = gx - GHW + 1 + k * (2 * GHW - 2) / 8
                box(A["metal"], xx - 0.18, -L + 2.0, AH * 0.45, xx + 0.18, -L + 2.4, AH, (0.06, 0.06, 0.07))
            for k in range(4):
                zz = AH * 0.45 + k * AH * 0.55 / 4
                box(A["metal"], gx - GHW, -L + 2.0, zz, gx + GHW, -L + 2.4, zz + 0.3, (0.06, 0.06, 0.07))
            box(SEAM, gx - GHW, -L + 1.3, AH - 0.4, gx + GHW, -L + 1.6, AH, EDGE, LH["seam_k"] * 1.5)
            K.add_light("gate_S", "SPOT", (gx, -L - 14, AH + 6), LH["gate_w"], YW, aim=(gx, -L, AH * 0.6), size=1.0,
                        spot=60, blend=0.6, group="corp")
        else:
            sx = -1 if side == "W" else 1
            gyc = CP["gate"]["ew_y"]
            xo = sx * L
            for s in (-1, 1):
                ty = gyc + s * (GHW + GTX)
                xa_, xb_ = sorted((xo, sx * (L - WT - 6)))
                solid(MASON, xa_, ty - GTX, 0.0, xb_, ty + GTX, GH, STONE)
                merlons(MASON, xa_, ty - GTX, xb_, ty + GTX, GH, STONE, step=4.0, h=4.0, t=2.0)
                slits(A["small"], xa_, ty - GTX, xb_, ty + GTX, 6.0, GH - 4, "W" if sx < 0 else "E", YW, 3.0, n=2,
                      rows=(0.25, 0.5, 0.75))
                box(SEAM, xo - 0.15, ty - GTX, GH - 0.9, xo + 0.15, ty + GTX, GH - 0.5, EDGE, LH["seam_k"])
                box(A["small"], xo - 0.3, ty - s * (GTX - 0.4) - 0.6, AH - 3, xo + 0.3, ty - s * (GTX - 0.4) + 0.6, AH - 1.4,
                    RED, 12.0)
            xa_, xb_ = sorted((xo - sx * 1.6, sx * (L - WT - 2)))
            solid(MASON, xa_, gyc - GHW, AH, xb_, gyc + GHW, GH - 4, STONE)
            merlons(MASON, xa_, gyc - GHW, xb_, gyc + GHW, GH - 4, STONE, step=3.6, h=3.6, t=2.0, sides="EW")
            for k in range(9):
                yy = gyc - GHW + 1 + k * (2 * GHW - 2) / 8
                box(A["metal"], xo - sx * 2.4 - 0.2, yy - 0.18, AH * 0.45, xo - sx * 2.0 + 0.2, yy + 0.18, AH, (0.06, 0.06, 0.07))
            box(SEAM, xo - sx * 1.6 - 0.15, gyc - GHW, AH - 0.4, xo - sx * 1.6 + 0.15, gyc + GHW, AH, EDGE, LH["seam_k"] * 1.5)
            K.add_light("gate_" + side, "SPOT", (xo + sx * 14, gyc, AH + 6), LH["gate_w"], YW, aim=(xo, gyc, AH * 0.6),
                        size=1.0, spot=60, blend=0.6, group="corp")
    for s_ in ("W", "S", "E"):
        gatehouse(s_)
    log("towers")

    # ------------------------------------------------------------ trucks: lit cabs, marker lights
    rt = random.Random(5412)

    def truck(x, y, ax, cbox=True, lit=False, name=None):
        s = 1 if ax[0] == "+" else -1
        alongx = ax[1] == "x"
        cab = (0.55, 0.16, 0.04) if rt.random() < 0.6 else (0.70, 0.70, 0.68)

        def B(acc, a0, a1, w0, w1, z0, z1, c, k=0.0):
            if alongx:
                box(acc, x + s * a0, y + w0, z0, x + s * a1, y + w1, z1, c, k)
            else:
                box(acc, x + w0, y + s * a0, z0, x + w1, y + s * a1, z1, c, k)
        B(A["metal"], -9.0, 6.0, -1.6, 1.6, 0.8, 1.6, (0.05, 0.05, 0.06))
        for a in (-7.5, -5.0, 2.0, 7.0):
            B(A["metal"], a - 0.9, a + 0.9, -2.6, 2.6, 0.0, 1.5, (0.02, 0.02, 0.02))
        B(A["rough"], 4.0, 9.6, -2.4, 2.4, 1.0, 5.6, cab)
        B(A["trim"], 9.55, 9.75, -2.0, 2.0, 3.6, 5.2, (1.0, 0.82, 0.55), LH["cab_k"])          # the lit windscreen
        for sg in (-1, 1):                                                                     # lit side windows
            B(A["trim"], 6.0, 9.0, sg * 2.4 - 0.05, sg * 2.4 + 0.05, 3.8, 5.0, (1.0, 0.82, 0.55), LH["cab_k"] * 0.7)
        B(A["small"], 5.0, 9.0, -2.0, 2.0, 5.6, 5.9, HAZ, 6.0)                                  # roof marker bar
        B(A["small"], 9.6, 9.8, -2.2, -1.3, 1.6, 2.3, YW, 10.0)
        B(A["small"], 9.6, 9.8, 1.3, 2.2, 1.6, 2.3, YW, 10.0)
        B(A["small"], -9.2, -9.05, -2.4, -1.6, 1.6, 2.2, RED, 8.0)
        B(A["small"], -9.2, -9.05, 1.6, 2.4, 1.6, 2.2, RED, 8.0)
        if cbox:
            B(C, -9.0, 3.6, -2.9, 2.9, 1.8, 8.8, STEEL[rt.randrange(len(STEEL))])
        if lit:
            p = (x + (s * 10 if alongx else 0), y + (0 if alongx else s * 10), 2.0)
            q = (p[0] + (s * 30 if alongx else 0), p[1] + (0 if alongx else s * 30), 0.0)
            K.add_light(name or "truck", "SPOT", p, LH["truck_w"], YW, aim=q, size=0.3, spot=50, blend=0.5, group="corp",
                        shadow=False)

    for k, xx in enumerate((-82.0, -58.0, -34.0, 34.0, 58.0, 82.0)):
        truck(xx, LN["s_y"], "+x" if k < 3 else "-x")
    ex = LN["ew_x"]
    room_truck = G.ROOM["tb"]["o"] if (G and "tb" in G.ROOM) else None
    for sx in (-1, 1):
        for yy in (-78.0, -62.0, 4.0, 26.0, 48.0):
            if room_truck and abs(sx * ex - (room_truck[0] - 3.0)) < 1.0 and abs(yy - room_truck[1]) < 1.0:
                truck(sx * ex, yy, "+y", cbox=False)                  # the route's truck: its box is a room
                continue
            truck(sx * ex, yy, "+y" if yy > 0 else "-y")
    # ------------------------------------------------------------ the truck RING ROAD (designer round 2): 6 lanes all
    # round the lot, a lit median, sodium mast lamps, truck queues in the two inbound lanes at each gate (lit cabs),
    # moving traffic as light streaks (the route-map rule: no car geometry for traffic), and the 3 highway on-ramps
    if rail:
        import meridian_rail as MRr
        RGD = CP["ring"]
        r0, r1 = RGD["r"]
        lw_ = (r1 - r0) / RGD["lanes"]
        sides = {"S": (0.0, -1.0), "N": (0.0, 1.0), "W": (-1.0, 0.0), "E": (1.0, 0.0)}

        def rbox(acc, side, d0, d1, u0, u1, z0, z1, col_, k=0.0):
            """A box in a ring side's frame: d = distance out from the centre, u = along the side (x for S/N, y W/E)."""
            nx, ny = sides[side]
            if ny:
                box(acc, u0, ny * d0, z0, u1, ny * d1, z1, col_, k)
            else:
                box(acc, nx * d0, u0, z0, nx * d1, u1, z1, col_, k)
        for side in "SNWE":
            ext = r1 if side in "SN" else r0
            rbox(A["ground"], side, r0, r1, -ext, ext, 0.0, 0.012, (0.055, 0.055, 0.06), 0.0)
            rbox(A["ground"], side, L, r0, -r0, r0, 0.0, 0.25, (0.22, 0.22, 0.23), 1.0)        # the lot-side kerb
            mid = r0 + lw_ * RGD["lanes"] / 2
            rbox(A["rough"], side, mid - 0.4, mid + 0.4, -ext, ext, 0.0, 1.0, (0.25, 0.25, 0.26))
            rbox(SEAM, side, mid - 0.15, mid + 0.15, -ext, ext, 1.0, 1.08, SOD, 1.2)
            for li in range(1, RGD["lanes"]):
                if li == RGD["lanes"] // 2:
                    continue
                d = r0 + li * lw_
                u = -ext + 2.0
                while u < ext - 4:
                    rbox(A["small"], side, d - 0.12, d + 0.12, u, u + 3.0, 0.013, 0.03, (0.9, 0.9, 0.85), 0.35)
                    u += 9.0
            u = -ext + 6.0
            while u < ext - 4:                                       # mast lamps on the outer kerb
                rbox(A["metal"], side, r1 - 0.8, r1 - 0.3, u - 0.25, u + 0.25, 0.0, 16.0, (0.2, 0.2, 0.22))
                rbox(A["small"], side, r1 - 4.0, r1 - 0.3, u - 1.0, u + 1.0, 15.6, 16.0, SOD, 10.0)
                u += 30.0
            nx, ny = sides[side]
            c = (nx * (r0 + r1) / 2, ny * (r0 + r1) / 2, 15.0)
            K.add_light("ring_" + side, "AREA", c, LH["ring_w"], SOD, aim=(c[0], c[1], 0.0),
                        size=(2 * ext) if ny else (r1 - r0), size_y=(r1 - r0) if ny else (2 * ext), group="corp",
                        shadow=False)
            # moving traffic: head (white) and tail (red) streaks in the four outer lanes
            rs_ = random.Random(5413 + "SNWE".index(side))
            for li in range(2, RGD["lanes"]):
                d = r0 + (li + 0.5) * lw_
                colr = (1.0, 0.95, 0.85) if li < RGD["lanes"] // 2 + 1 else (1.0, 0.08, 0.04)
                u = -ext + rs_.uniform(0, 20)
                while u < ext - 10:
                    ln = rs_.uniform(8, 34)
                    rbox(A["streaks"], side, d - 0.14, d + 0.14, u, min(u + ln, ext), 0.55, 0.7, colr, LH["streak_k"])
                    u += ln + rs_.uniform(6, 30)
        # the queues: bumper to bumper in the two inbound lanes, toward each gate (the first truck's lights are real)
        q = 0
        for (side, gate_u) in (("S", CP["gate"]["s_x"]), ("W", CP["gate"]["ew_y"]), ("E", CP["gate"]["ew_y"])):
            nx, ny = sides[side]
            for li in (0, 1):
                d = r0 + (li + 0.5) * lw_
                for sgn in (-1, 1):
                    n_ = 4 if li == 0 else 2
                    for k in range(n_):
                        u = gate_u + sgn * (16.0 + li * 8.0 + k * 21.0)
                        if abs(u) > r0 - 6:
                            continue
                        head = ("+x" if sgn < 0 else "-x") if ny else ("+y" if sgn < 0 else "-y")
                        x_, y_ = (u, ny * d) if ny else (nx * d, u)
                        truck(x_, y_, head, lit=(k == 0 and li == 0), name="tq_%d" % q)
                        q += 1
        for k, xx in enumerate((-80.0, -40.0, 30.0, 75.0)):           # the N side: outbound to the highways
            truck(xx, r0 + 4.5 * lw_, "+x" if k % 2 else "-x")
        # the rail's level crossings on the W / E ring sides: red signal lamps
        for sx in (-1, 1):
            for yy in (RC["y"][0] - 7.0, RC["y"][1] + 7.0):
                for d in (r0 + 1.0, r1 - 1.0):
                    box(A["metal"], sx * d - 0.2, yy - 0.2, 0.0, sx * d + 0.2, yy + 0.2, 6.0, (0.15, 0.15, 0.15))
                    box(A["small"], sx * d - 0.5, yy - 0.5, 6.0, sx * d + 0.5, yy + 0.5, 7.0, RED, 12.0)
        # the highway on-ramps and the elevated highways (the city's highways hub here: exits in DESIGN.md)
        Vec = K.Vector
        for name, pts in MRr.highways(CP).items():
            for (p, qq) in zip(pts, pts[1:]):
                P_, Q_ = Vec(p), Vec(qq)
                d_ = Q_ - P_
                hz = math.hypot(d_.x, d_.y)
                side = Vec((-d_.y / hz, d_.x / hz, 0.0))
                up = Vec((0, 0, 1.0))
                dw = RGD["deck_w"]
                K.seg_box(A["rough"], P_ + up * 0.3, Q_ + up * 0.3, dw, 1.8, (0.12, 0.12, 0.13))
                for sgn in (-1, 1):
                    K.seg_box(A["rough"], P_ + side * sgn * dw / 2 + up * 1.3, Q_ + side * sgn * dw / 2 + up * 1.3, 0.6, 1.0,
                              (0.18, 0.18, 0.19))
                    K.seg_box(SEAM, P_ + side * sgn * (dw / 2 + 0.35) + up * 0.1, Q_ + side * sgn * (dw / 2 + 0.35) + up * 0.1,
                              0.12, 0.25, EDGE, LH["seam_k"] * 0.8)
                K.seg_box(A["rough"], P_ + up * 1.3, Q_ + up * 1.3, 0.6, 1.0, (0.2, 0.2, 0.21))
                rs_ = random.Random(sum(map(ord, name)) * 1000 + int(p[0] + p[1]))
                for (off, colr) in ((-8.5, (1.0, 0.95, 0.85)), (-4.0, (1.0, 0.95, 0.85)), (4.0, (1.0, 0.08, 0.04)),
                                    (8.5, (1.0, 0.08, 0.04))):
                    t = rs_.uniform(0, 0.1)
                    while t < 0.98:
                        t1 = min(1.0, t + rs_.uniform(10, 40) / hz)
                        a_ = P_.lerp(Q_, t) + side * off + up * 0.55
                        b_ = P_.lerp(Q_, t1) + side * off + up * 0.55
                        K.seg_box(A["streaks"], a_, b_, 0.28, 0.12, colr, LH["streak_k"])
                        t = t1 + rs_.uniform(8, 40) / hz
                n = int(hz / RGD["pier_step"])
                for i in range(n + 1):
                    c_ = P_.lerp(Q_, (i + 0.5) / (n + 1))
                    if c_.z > 5.0:
                        box(A["rough"], c_.x - 2.2, c_.y - 2.2, 0.0, c_.x + 2.2, c_.y + 2.2, c_.z - 1.5, (0.13, 0.13, 0.14))
                        box(A["rough"], c_.x - side.x * dw * 0.45 - 1.2, c_.y - side.y * dw * 0.45 - 1.2, c_.z - 3.0,
                            c_.x + side.x * dw * 0.45 + 1.2, c_.y + side.y * dw * 0.45 + 1.2, c_.z - 1.5, (0.13, 0.13, 0.14))
        log("ring road", q, "queued trucks")
    if G and "tb" in G.ROOM:
        K.room_shell("tb", G.ROOM["tb"])
    log("trucks")

    # ------------------------------------------------------------ the bailey
    ry = random.Random(5411)
    x0_, x1_, y0_, y1_ = CP["yard"]
    xx = x0_
    while xx < x1_ - 14:
        yy = y0_
        while yy < y1_ - 6:
            if abs(yy - (GY - 6)) < 4.0 and abs(xx + 7 - KX) < 30:
                yy += 7.0
                continue
            nh = ry.choice((1, 2, 2, 3, 3, 4))
            for kz in range(nh):
                box(C, xx, yy, kz * 6.8 + 0.1, xx + 14.0, yy + 6.2, kz * 6.8 + 6.4, STEEL[ry.randrange(len(STEEL))])
            yy += 7.0
            if int(round((yy - y0_) / 7.0)) % 5 == 0:
                yy += 6.0
        xx += 14.6 if (xx - x0_) % 44 < 30 else 22.0
    log("yard")

    # ------------------------------------------------------------ the freight line (meridian_rail): tracks, viaduct
    if rail:
        import meridian_rail as MR
        CL = MR.centreline(CP)
        half = (RC["y"][1] - RC["y"][0]) / 2.0
        Vec = K.Vector
        dw = RC["deck_w"]
        s_acc = 0.0
        for (p, q) in zip(CL, CL[1:]):
            P_, Q_ = Vec(p), Vec(q)
            d = Q_ - P_
            hz = math.hypot(d.x, d.y)
            if hz < 1e-3:
                continue
            side = Vec((-d.y / hz, d.x / hz, 0.0))
            elev = max(p[2], q[2]) > 1.5
            lift = Vec((0, 0, 1.0))
            if elev:
                K.seg_box(A["rough"], P_ + lift * 0.5, Q_ + lift * 0.5, dw, 2.4, (0.14, 0.14, 0.15))     # the deck
                for sgn in (-1, 1):                                                                       # parapets + lit edge
                    K.seg_box(A["rough"], P_ + side * sgn * dw / 2 + lift * 1.8, Q_ + side * sgn * dw / 2 + lift * 1.8,
                              0.6, 1.3, (0.16, 0.16, 0.17))
                    K.seg_box(SEAM, P_ + side * sgn * (dw / 2 + 0.35) + lift * 0.2, Q_ + side * sgn * (dw / 2 + 0.35) + lift * 0.2,
                              0.12, 0.25, TLIGHT, LH["seam_k"])
                n = int(hz / RC["pier_step"])
                for i in range(n + 1):
                    t = (i + 0.5) / (n + 1)
                    c_ = P_.lerp(Q_, t)
                    if c_.z > 4.0:
                        box(A["rough"], c_.x - 2.6, c_.y - 2.6, 0.0, c_.x + 2.6, c_.y + 2.6, c_.z - 1.9, (0.13, 0.13, 0.14))
                        box(A["rough"], c_.x - 1.2 - side.x * dw * 0.45, c_.y - 1.2 - side.y * dw * 0.45, c_.z - 3.4,
                            c_.x + 1.2 + side.x * dw * 0.45, c_.y + 1.2 + side.y * dw * 0.45, c_.z - 1.9, (0.13, 0.13, 0.14))
            else:
                K.seg_box(A["rough"], P_ + lift * 0.5, Q_ + lift * 0.5, 2 * half + 8.4, 0.52, (0.08, 0.08, 0.085))
            for sgn in (-1, 1):
                for o_ in (-1.6, 1.6):
                    off = side * (sgn * half + o_)
                    K.seg_box(A["metal"], P_ + off + lift * 0.95, Q_ + off + lift * 0.95, 0.4, 0.45, (0.55, 0.55, 0.58))
            # catenary masts every 40 BU along the line
            nm = int((s_acc + hz) / 40.0) - int(s_acc / 40.0)
            for i in range(nm):
                t = ((int(s_acc / 40.0) + i + 1) * 40.0 - s_acc) / hz
                c_ = P_.lerp(Q_, min(t, 1.0))
                box(A["metal"], c_.x - 0.4, c_.y - 0.4, c_.z, c_.x + 0.4, c_.y + 0.4, c_.z + 15.0, (0.2, 0.2, 0.22))
                box(A["metal"], c_.x - side.x * (half + 1) - 0.3, c_.y - side.y * (half + 1) - 0.3, c_.z + 14.0,
                    c_.x + side.x * (half + 1) + 0.3, c_.y + side.y * (half + 1) + 0.3, c_.z + 14.6, (0.2, 0.2, 0.22))
            s_acc += hz
        K.add_light("rail_glint", "AREA", (0.0, sum(RC["y"]) / 2, 10.0), LH["sodium_w"] * 10, SOD, aim=(0.0, 101.5, 0.0),
                    size=2 * L, size_y=14.0, group="corp", shadow=False)

        # the high-speed set on the inner track: two power cars with long noses, lit carriages (one cut open: r1)
        tya = YIN
        txa, txb = RC["train_x"]
        BODY_H = 7.6

        def nose(xb_, s):
            prof = [(0.0, BODY_H, 3.4), (6.0, BODY_H - 0.4, 3.3), (11.0, BODY_H - 1.6, 3.0), (15.0, 4.2, 2.6),
                    (18.0, 2.6, 2.0), (19.6, 1.4, 1.2)]
            for (a0, h0, w0), (a1, h1, w1) in zip(prof, prof[1:]):
                p00, p01 = (xb_ + s * a0, tya - w0, 1.0), (xb_ + s * a0, tya + w0, 1.0)
                p10, p11 = (xb_ + s * a1, tya - w1, 1.0), (xb_ + s * a1, tya + w1, 1.0)
                t00, t01 = (p00[0], p00[1], 1.0 + h0), (p01[0], p01[1], 1.0 + h0)
                t10, t11 = (p10[0], p10[1], 1.0 + h1), (p11[0], p11[1], 1.0 + h1)
                for q in ([p00, p10, t10, t00], [p11, p01, t01, t11], [t00, t10, t11, t01]):
                    TRAINA.face(q[::-1] if s < 0 else q, TRAIN)
            e = xb_ + s * 19.6
            TRAINA.face([(e, tya - 1.2, 1.0), (e, tya + 1.2, 1.0), (e, tya + 1.2, 2.4), (e, tya - 1.2, 2.4)][::(1 if s > 0 else -1)],
                        TRAIN)
            # the cab windscreen (lit, on the nose's upper slope) and the headlamps
            for sg in (-1, 1):
                box(A["small"], xb_ + s * 16.8 - 0.4, tya + sg * 1.9 - 0.5, 2.6, xb_ + s * 16.8 + 0.4, tya + sg * 1.9 + 0.5, 3.4,
                    (0.95, 0.97, 1.0), 30.0)
            box(A["trim"], xb_ + s * 8.0 - 2.4, tya - 3.0, BODY_H - 0.9, xb_ + s * 8.0 + 2.4, tya + 3.0, BODY_H + 0.2,
                (0.8, 0.9, 1.0), LH["train_k"] * 0.4)
            box(SEAM, xb_ + s * 0.2 - 0.1, tya - 3.45, 3.0, xb_ + s * 15.0, tya + 3.45, 3.5, TLIGHT, LH["train_k"])
        pcl = 24.0
        for (a_, b_, s) in ((txa, txa + pcl, -1), (txb - pcl, txb, 1)):
            box(TRAINA, a_, tya - 3.4, 1.0, b_, tya + 3.4, 1.0 + BODY_H, TRAIN)
            box(SEAM, a_, tya - 3.46, 3.0, b_, tya + 3.46, 3.5, TLIGHT, LH["train_k"])
            box(A["metal"], (a_ + b_) / 2 - 3, tya - 0.3, 1.0 + BODY_H, (a_ + b_) / 2 + 3, tya + 0.3, 12.6, (0.2, 0.2, 0.22))
            nose(b_ if s > 0 else a_, s)
        r1o = G.ROOM["r1"]["o"] if (G and "r1" in G.ROOM) else None
        xc = txa + pcl + 0.8
        while xc < txb - pcl - 10:
            x2 = min(xc + 22.0, txb - pcl - 0.8)
            cut = r1o is not None and xc - 1 < r1o[0] < x2 + 1
            if cut:                                                    # the route's carriage: cut open on its S side
                box(TRAINA, xc, tya - 3.4, 1.0, x2, tya + 3.4, 2.4, TRAIN)
                box(TRAINA, xc, tya + 2.8, 2.4, x2, tya + 3.4, 1.0 + BODY_H, TRAIN)
                box(TRAINA, xc, tya - 3.4, 1.0 + BODY_H - 0.6, x2, tya + 3.4, 1.0 + BODY_H, TRAIN)
                for xe in (xc, x2 - 0.6):
                    box(TRAINA, xe, tya - 3.4, 2.4, xe + 0.6, tya + 3.4, 1.0 + BODY_H, TRAIN)
            else:
                box(TRAINA, xc, tya - 3.4, 1.0, x2, tya + 3.4, 1.0 + BODY_H, TRAIN)
                # the lit window band both sides (cold white), in panes
                u = xc + 1.2
                while u < x2 - 2.0:
                    for sg in (-1, 1):
                        box(A["trim"], u, tya + sg * 3.45 - 0.05, 4.4, u + 1.8, tya + sg * 3.45 + 0.05, 6.4, (0.85, 0.93, 1.0),
                            LH["train_k"] * 1.0)
                    u += 2.4
            box(SEAM, xc, tya - 3.46, 2.2, x2, tya + 3.46, 2.6, TLIGHT, LH["train_k"])
            box(A["metal"], x2, tya - 2.6, 1.6, x2 + 0.8, tya + 2.6, BODY_H, (0.03, 0.03, 0.03))      # the gangway
            xc = x2 + 0.8
        if G and "r1" in G.ROOM:
            K.room_shell("r1", G.ROOM["r1"])
        K.add_light("train_head", "SPOT", (txb + 20.5, tya, 2.4), LH["head_w"], (0.85, 0.92, 1.0), aim=(txb + 220, tya, 0.0),
                    size=0.4, spot=18, blend=0.4, group="corp", shadow=False)
        K.add_light("train_glow", "AREA", ((txa + txb) / 2, tya - 6.0, 12.0), LH["train_area_w"], TLIGHT,
                    aim=((txa + txb) / 2, tya - 6.0, 0.0), size=txb - txa, size_y=6.0, group="corp", shadow=False)
        # a second set on the ramp / deck toward the port (lit carriages only: the line reads as live)
        ramp = [(CL[i], CL[i + 1]) for i in range(len(CL) - 1) if CL[i][2] > 10 or CL[i + 1][2] > 10]
        if ramp:
            p, q = ramp[min(len(ramp) - 1, len(ramp) // 2)]
            P_, Q_ = Vec(p), Vec(q)
            d = (Q_ - P_)
            Ld = d.length
            dn = d / Ld
            side = Vec((-dn.y, dn.x, 0.0)).normalized()
            for i in range(7):
                a = P_ + dn * (Ld * 0.25 + i * 23.0) - side * half
                b2 = a + dn * 22.0
                if (a - P_).length > Ld:
                    break
                K.seg_box(TRAINA, a + Vec((0, 0, 9.0)), b2 + Vec((0, 0, 9.0)), 6.6, 7.6, TRAIN)
                K.seg_box(A["trim"], a + Vec((0, 0, 7.0)) - side * 3.35, b2 + Vec((0, 0, 7.0)) - side * 3.35, 0.1, 2.0,
                          (0.85, 0.93, 1.0), LH["train_k"] * 0.5)
                K.seg_box(SEAM, a + Vec((0, 0, 4.4)) - side * 3.4, b2 + Vec((0, 0, 4.4)) - side * 3.4, 0.1, 0.4, TLIGHT,
                          LH["train_k"])
        log("rail", len(CL), "points")

    # ------------------------------------------------------------ THE GANTRY (rust-orange, sodium-white edges)
    LEGC = cav("le1", "le2", "lw1", "lw2")
    for sx in (-1, 1):
        cx = sx * LEGX
        y0, y1 = GY - LHY, GY + LHY
        for yb_ in (y0 - 2.0, y1 + 2.0):
            box(A["metal"], cx - 6, yb_ - 3, WTOP + 0.7, cx + 6, yb_ + 3, WTOP + 3.2, (0.06, 0.06, 0.07))
            box(A["small"], cx - 6.1, yb_ - 3.1, WTOP + 2.6, cx + 6.1, yb_ + 3.1, WTOP + 3.0, HAZ, 1.2)
        box(GANTRY, cx - LHX - 1, y0 - 4, WTOP + 3.2, cx + LHX + 1, y1 + 4, WTOP + 6.0, GANT)
        solid(GANTRY, cx - LHX, y0, WTOP + 6.0, cx + LHX, y1, LTOP, GANT, LEGC)
        for (px, py) in ((cx - LHX, y0), (cx + LHX, y0), (cx - LHX, y1), (cx + LHX, y1)):
            box(GANTRY, px - 1.4, py - 1.4, WTOP + 6.0, px + 1.4, py + 1.4, LTOP - 12.0, GANT)
            tube(GANTRY, (px, py, LTOP - 16.0), (px, py, LTOP + 6.0), 3.2, GANT, n=12)
            box(GANTRY, px - 3.2, py - 3.2, LTOP + 6.0, px + 3.2, py + 3.2, LTOP + 6.6, GANT)
            box(GANTRY, px - 2.2, py - 2.2, LTOP + 6.6, px + 2.2, py + 2.2, LTOP + 9.6, GANT)
            box(SEAM, px - 3.3, py - 3.3, LTOP + 5.2, px + 3.3, py + 3.3, LTOP + 5.7, EDGE, LH["seam_k"])
        merlons(GANTRY, cx - LHX, y0, cx + LHX, y1, LTOP, GANT, step=3.4, h=4.6, t=1.6)
        box(SEAM, cx - LHX - 0.2, y0 - 0.25, LTOP - 1.0, cx + LHX + 0.2, y0 + 0.05, LTOP - 0.5, EDGE, LH["seam_k"])
        box(SEAM, (cx - LHX if sx < 0 else cx + LHX) - 0.25, y0, LTOP - 1.0, (cx - LHX if sx < 0 else cx + LHX) + 0.25, y1,
            LTOP - 0.5, EDGE, LH["seam_k"])
        slits(A["small"], cx - LHX, y0, cx + LHX, y1, WTOP + 10, LTOP - 8, "W" if sx < 0 else "E", YW, 4.0, n=3,
              rows=(0.12, 0.3, 0.48, 0.66, 0.84))
        slits(A["small"], cx - LHX, y0, cx + LHX, y1, WTOP + 10, LTOP - 8, "N", YW, 4.0, n=2, rows=(0.2, 0.5, 0.8))
        beacon(cx, GY, LTOP + 9.6)
        for (px, py) in ((cx - LHX, y0), (cx + LHX, y0), (cx - LHX, y1), (cx + LHX, y1)):     # rim: sodium-white vertical edges
            box(SEAM, px - 0.3, py - 0.3, WTOP + 6.0, px + 0.3, py + 0.3, LTOP, EDGE, LH["seam_k"] * 1.3)
        for (px, py) in ((cx - LHX, y0), (cx + LHX, y0), (cx - LHX, y1), (cx + LHX, y1)):     # rim: sodium-white vertical edges
            box(SEAM, px - 0.3, py - 0.3, WTOP + 6.0, px + 0.3, py + 0.3, LTOP, EDGE, LH["seam_k"] * 1.3)
        K.add_light("legup_s_%d" % sx, "SPOT", (cx, y0 - 9.0, WTOP + 7.0), LH["leg_up_w"], YW, aim=(cx, y0, LTOP),
                    size=1.0, spot=40, blend=0.6, group="corp")
        K.add_light("legup_o_%d" % sx, "SPOT", (cx + sx * 12.0, GY, WTOP + 7.0), LH["leg_up_w"] * 0.6, SOD,
                    aim=(cx + sx * LHX, GY, LTOP), size=1.0, spot=40, blend=0.6, group="corp")
    sx0, sx1 = -LEGX + LHX, LEGX - LHX
    sy0, sy1 = GY - SH, GY + SH
    solid(GANTRY, sx0, sy0, SZ0, sx1, sy1, SZ1, GANT, cav("spe", "spw"))
    merlons(GANTRY, sx0, sy0, sx1, sy1, SZ1, GANT, step=4.4, h=4.4, t=1.6, sides="SN")
    for k in range(int((sx1 - sx0) / 6.0) + 1):
        xx = sx0 + 3.0 + k * 6.0
        if xx > sx1 - 1:
            break
        for (ya, yb) in ((sy0 - 1.6, sy0 + 1.0), (sy1 - 1.0, sy1 + 1.6)):
            box(GANTRY, xx - 1.0, ya, SZ0 - 4.0, xx + 1.0, yb, SZ0 + 0.1, GANT)
    box(GANTRY, sx0, sy0 - 1.6, SZ0 - 0.6, sx1, sy1 + 1.6, SZ0, GANT)
    box(SEAM, sx0, sy0 - 1.75, SZ0 - 0.9, sx1, sy0 - 1.6, SZ0 - 0.45, EDGE, LH["seam_k"])
    box(SEAM, sx0, sy0 - 0.3, SZ1 - 0.2, sx1, sy0 + 0.3, SZ1 + 0.4, EDGE, LH["seam_k"] * 1.4)         # rim: the span's top edges
    box(SEAM, sx0, sy1 - 0.3, SZ1 - 0.2, sx1, sy1 + 0.3, SZ1 + 0.4, EDGE, LH["seam_k"] * 1.4)
    box(SEAM, sx0, sy0 - 0.3, SZ1 - 0.2, sx1, sy0 + 0.3, SZ1 + 0.4, EDGE, LH["seam_k"] * 1.4)         # rim: the span's top edges
    box(SEAM, sx0, sy1 - 0.3, SZ1 - 0.2, sx1, sy1 + 0.3, SZ1 + 0.4, EDGE, LH["seam_k"] * 1.4)
    box(SEAM, sx0, sy0 - 0.25, SZ1 - 1.0, sx1, sy0 + 0.05, SZ1 - 0.55, EDGE, LH["seam_k"])
    box(SEAM, sx0, sy1 - 0.05, SZ0 + 0.2, sx1, sy1 + 0.25, SZ0 + 0.65, EDGE, LH["seam_k"] * 0.7)
    STEN = {"M": ["10001", "11011", "10101", "10001", "10001"], "E": ["1111", "1000", "1110", "1000", "1111"],
            "R": ["1110", "1001", "1110", "1010", "1001"], "I": ["111", "010", "010", "010", "111"],
            "D": ["1110", "1001", "1001", "1001", "1110"], "A": ["0110", "1001", "1111", "1001", "1001"],
            "N": ["1001", "1101", "1011", "1001", "1001"]}
    cell = 1.45
    word = "MERIDIAN"
    wl = sum((len(STEN[ch][0]) + 1) * cell for ch in word) - cell
    u0 = 14.0 - wl / 2
    zt = SZ0 + (SZ1 - SZ0) / 2 - 2.5 * cell
    box(A["metal"], u0 - 1.2, sy0 - 0.35, zt - 1.0, u0 + wl + 1.2, sy0, zt + 5 * cell + 1.0, (0.03, 0.03, 0.03))
    uu = u0
    for ch in word:
        gph = STEN[ch]
        for row, bits in enumerate(gph):
            for cix, bit in enumerate(bits):
                if bit == "1":
                    box(SEAM, uu + cix * cell, sy0 - 0.5, zt + (4 - row) * cell, uu + (cix + 1) * cell - cell * 0.12,
                        sy0 - 0.35, zt + (5 - row) * cell - cell * 0.12, EDGE, LH["logo_k"] * 4)
        uu += (len(gph[0]) + 1) * cell
    for k, xx in enumerate((-84.0, -50.0, 14.0, 48.0, 84.0)):
        box(A["small"], xx - 2.0, GY - 2.0, SZ0 - 4.6, xx + 2.0, GY + 2.0, SZ0 - 4.1, YW, 10.0)
        K.add_light("span_down_%d" % k, "SPOT", (xx, GY, SZ0 - 5.0), LH["span_down_w"], YW if k % 2 else SOD,
                    aim=(xx, GY + 26.0, 0.0), size=2.0, spot=46, blend=0.7, group="corp")
    for o_ in (-4.0, 4.0):
        box(A["metal"], sx0, GY + o_ - 0.35, SZ1, sx1, GY + o_ + 0.35, SZ1 + 0.7, (0.35, 0.35, 0.37))
    log("gantry")

    # ------------------------------------------------------------ the KEEP = THE TARGET (parked): a body, a corbelled
    # battlement, four corner turrets with spires, and the open LANTERN crown with THE MASTER MANIFEST visible inside
    kx0, kx1, ky0, ky1 = KX - KHX, KX + KHX, GY - KHY, GY + KHY
    KZ0 = SZ1 + 1.2
    LWX, LWY, LHT = GC["lantern"]
    box(A["metal"], kx0 + 2, ky0 + 2, SZ1 + 0.7, kx1 - 2, ky1 - 2, KZ0, (0.06, 0.06, 0.07))
    box(GANTRY, kx0, ky0, KZ0, kx1, ky1, KTOP - 3.0, KEEPC)
    box(GANTRY, kx0 - 1.4, ky0 - 1.4, KTOP - 3.0, kx1 + 1.4, ky1 + 1.4, KTOP, KEEPC)            # the corbelled band
    for k in range(9):
        xx = kx0 + 1.0 + k * (kx1 - kx0 - 2.0) / 8
        box(GANTRY, xx - 0.5, ky0 - 1.4, KTOP - 5.0, xx + 0.5, ky0, KTOP - 3.0, KEEPC)
    for k in range(7):
        yy = ky0 + 1.0 + k * (ky1 - ky0 - 2.0) / 6
        for xe in (kx0 - 1.4, kx1):
            box(GANTRY, xe, yy - 0.5, KTOP - 5.0, xe + 1.4, yy + 0.5, KTOP - 3.0, KEEPC)
    merlons(GANTRY, kx0 - 1.4, ky0 - 1.4, kx1 + 1.4, ky1 + 1.4, KTOP, KEEPC, step=3.0, h=3.4, t=1.2)
    box(SEAM, kx0 - 1.6, ky0 - 1.65, KTOP - 3.3, kx1 + 1.6, ky0 - 1.35, KTOP - 2.9, EDGE, LH["seam_k"] * 1.3)
    box(SEAM, kx1 + 1.35, ky0 - 1.6, KTOP - 3.3, kx1 + 1.65, ky1 + 1.6, KTOP - 2.9, EDGE, LH["seam_k"] * 1.3)
    for zz in (KZ0 + 5.0, KZ0 + 13.0):                                # tall narrow windows, two storeys
        for k in range(4):
            xx = kx0 + 5.0 + k * (kx1 - kx0 - 10.0) / 3
            box(A["trim"], xx - 0.7, ky0 - 0.12, zz, xx + 0.7, ky0 + 0.02, zz + 5.0, YW, LH["trim_k"] * 0.7)
        for k in range(3):
            yy = ky0 + 5.0 + k * (ky1 - ky0 - 10.0) / 2
            box(A["trim"], kx0 - 0.12, yy - 0.7, zz, kx0 + 0.02, yy + 0.7, zz + 5.0, YW, LH["trim_k"] * 0.7)
            box(A["trim"], kx1 - 0.02, yy - 0.7, zz, kx1 + 0.12, yy + 0.7, zz + 5.0, YW, LH["trim_k"] * 0.7)

    def cone(acc, cx, cy, r, z0, z1, col, n=12):
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            acc.face([(cx + r * math.cos(a0), cy + r * math.sin(a0), z0), (cx + r * math.cos(a1), cy + r * math.sin(a1), z0),
                      (cx, cy, z1)], col)
    for (px, py) in ((kx0, ky0), (kx1, ky0), (kx0, ky1), (kx1, ky1)):  # corner turrets with spires
        tube(GANTRY, (px, py, KZ0 + 4.0), (px, py, KTOP + 7.0), 3.4, KEEPC, n=14)
        box(GANTRY, px - 3.9, py - 3.9, KTOP + 6.0, px + 3.9, py + 3.9, KTOP + 7.0, KEEPC)
        cone(GANTRY, px, py, 3.9, KTOP + 7.0, KTOP + 17.0, GANT)
        box(SEAM, px - 4.0, py - 4.0, KTOP + 5.4, px + 4.0, py + 4.0, KTOP + 5.9, EDGE, LH["seam_k"])
        slits(A["small"], px - 3.4, py - 3.4, px + 3.4, py + 3.4, KZ0 + 6, KTOP + 4, "S", YW, 3.0, n=1, rows=(0.4, 0.8))
    # the LANTERN: an open glazed crown, posts and mullions only, lit from within by the server
    vx, vy, vz = KX, GY, KTOP
    if G and "srv" in G.ROOM:
        vx, vy, vz = G.ROOM["srv"]["o"]
    lx0, lx1, ly0, ly1 = vx - LWX, vx + LWX, vy - LWY, vy + LWY
    box(A["metal"], lx0, ly0, KTOP - 0.2, lx1, ly1, KTOP + 0.4, (0.10, 0.10, 0.11))
    for k in range(5):
        xx = lx0 + k * (lx1 - lx0) / 4
        for yy in (ly0, ly1):
            box(GANTRY, xx - 0.5, yy - 0.5, KTOP, xx + 0.5, yy + 0.5, KTOP + LHT, KEEPC)
    for k in range(1, 4):
        yy = ly0 + k * (ly1 - ly0) / 4
        for xx in (lx0, lx1):
            box(GANTRY, xx - 0.5, yy - 0.5, KTOP, xx + 0.5, yy + 0.5, KTOP + LHT, KEEPC)
    for zz in (KTOP + 0.4, KTOP + LHT - 0.6):                         # lit sill and lintel lines
        box(SEAM, lx0 - 0.55, ly0 - 0.6, zz, lx1 + 0.55, ly0 - 0.45, zz + 0.4, EDGE, LH["seam_k"] * 1.5)
        box(SEAM, lx1 + 0.45, ly0 - 0.55, zz, lx1 + 0.6, ly1 + 0.55, zz + 0.4, EDGE, LH["seam_k"] * 1.5)
        box(SEAM, lx0 - 0.6, ly0 - 0.55, zz, lx0 - 0.45, ly1 + 0.55, zz + 0.4, EDGE, LH["seam_k"] * 1.5)
    emv = K.ROOM_EMIT.setdefault("srv", Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"])) if hasattr(K, "ROOM_EMIT") \
        else SEAM
    tube(A["metal"], (vx, vy, KTOP + 0.4), (vx, vy, KTOP + LHT - 1.5), 3.0, (0.08, 0.08, 0.1), n=16)
    for k_ in range(7):
        zz = KTOP + 1.2 + k_ * 1.4
        tube(emv, (vx, vy, zz), (vx, vy, zz + 0.4), 3.1, (1.0, 0.28, 0.08), 7.0, n=24)
    for (rx_, ry_) in ((lx0 + 2.0, vy), (lx1 - 2.0, vy)):            # two racks either side of the core
        box(A["metal"], rx_ - 0.9, ry_ - 4.0, KTOP + 0.4, rx_ + 0.9, ry_ + 4.0, KTOP + 8.0, (0.06, 0.06, 0.07))
        for k in range(5):
            box(emv, rx_ - 0.95, ry_ - 3.6, KTOP + 1.4 + k * 1.3, rx_ + 0.95, ry_ + 3.6, KTOP + 1.6 + k * 1.3,
                (1.0, 0.45, 0.12), 5.0)
    box(A["trim"], lx0 + 0.6, ly0 + 0.6, KTOP + LHT - 0.25, lx1 - 0.6, ly1 - 0.6, KTOP + LHT - 0.1, (1.0, 0.6, 0.3),
        LH["trim_k"] * 0.8)                                            # the lantern ceiling glows
    K.add_light("lantern", "POINT", (vx, vy, KTOP + LHT * 0.55), LH["lantern_w"], (1.0, 0.42, 0.16), size=2.5,
                group="corp", shadow=False)
    # the cap, its battlement and the spire with the beacon + beam
    cz = KTOP + LHT
    box(GANTRY, lx0 - 1.6, ly0 - 1.6, cz, lx1 + 1.6, ly1 + 1.6, cz + 1.6, KEEPC)
    merlons(GANTRY, lx0 - 1.6, ly0 - 1.6, lx1 + 1.6, ly1 + 1.6, cz + 1.6, KEEPC, step=2.6, h=2.6, t=1.0)
    box(SEAM, lx0 - 1.7, ly0 - 1.75, cz + 0.5, lx1 + 1.7, ly0 - 1.55, cz + 1.0, RED, LH["seam_k"] * 1.5)
    tube(A["metal"], (vx, vy, cz + 1.6), (vx, vy, cz + 16.0), 0.7, (0.1, 0.1, 0.11), n=8)
    beacon(vx, vy, cz + 16.0)
    bo = (vx, vy, cz + 18.0)
    hooks["beams"].append((place_f(bo) if place_f else bo, (0.0, 0.0, 1.0), (1.0, 0.45, 0.12),
                           K.HZ["beams"]["power"] * 1.6, K.HZ["beams"]["cone"] * 1.3))
    for sx in (-1, 1):
        K.add_light("keep_wash_%d" % sx, "SPOT", (KX + sx * 46.0, GY - 16.0, SZ1 + 2.0), LH["keep_wash_w"],
                    YW if sx < 0 else SOD, aim=(KX, GY, KTOP - 8.0), size=1.5, spot=40, blend=0.5, group="corp")
    K.add_light("keep_key", "SPOT", (KX + 60.0, GY - 70.0, SZ1 + 6.0), LH["keep_key_w"], YW,
                aim=(KX, ky0, KTOP - 6.0), size=3.0, spot=22, blend=0.6, group="corp")
    box(A["glass"], KX - 6.0, GY - 9.0, SZ0 - 12.0, KX + 6.0, GY - 2.0, SZ0 - 4.4, (0.02, 0.03, 0.04))
    box(A["trim"], KX - 5.6, GY - 9.1, SZ0 - 9.0, KX + 5.6, GY - 8.95, SZ0 - 7.8, YC, LH["trim_k"])
    box(GANTRY, KX - 6.6, GY - 9.6, SZ0 - 4.4, KX + 6.6, GY - 1.4, SZ0 - 4.0, KEEPC)
    hz = GC["hook_z"]
    for (ox_, oy_) in ((-6.0, -2.6), (6.0, -2.6), (-6.0, 2.6), (6.0, 2.6)):
        tube(A["metal"], (KX + ox_, GY + oy_, hz + 9.2), (KX + ox_, GY + oy_, SZ0 - 4.0), 0.22, (0.1, 0.1, 0.1), n=6)
    box(A["metal"], KX - 7.6, GY - 3.4, hz + 7.4, KX + 7.6, GY + 3.4, hz + 9.2, (0.85, 0.6, 0.05))
    box(A["small"], KX - 7.7, GY - 3.5, hz + 7.4, KX + 7.7, GY + 3.5, hz + 7.7, HAZ, 3.0)
    box(C, KX - 7.0, GY - 3.0, hz, KX + 7.0, GY + 3.0, hz + 7.2, STEEL[1])
    K.add_light("hook_spot", "SPOT", (KX, GY - 6.0, SZ0 - 12.5), 1.2e4, YW, aim=(KX, GY - 6.0, 0.0), size=0.6, spot=30,
                blend=0.5, group="corp")
    log("keep")

    # ------------------------------------------------------------ the route rooms (slots)
    if G:
        for i in ROOMS:
            if i in ("tb", "r1"):
                continue
            K.room_shell(i, G.ROOM[i])

    # ------------------------------------------------------------ rim: the city glow behind grazes the landmark only
    if getattr(K, "CITY", False):
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
