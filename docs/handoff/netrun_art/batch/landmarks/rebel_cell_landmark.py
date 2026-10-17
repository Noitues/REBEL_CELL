"""DRAFT for the art-pass session; unverified (no render).
# provenance: model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id lm__rebel_cell; status ok; tokens in 17410 cache-write 132454 cache-read 0 out 14197; cost $0.254; ast.parse: parses
REBEL_CELL / DISPATCH landmark: THE MAINFRAME BLADE SIGN on a Tokyo-canyon shop front (no landmark building). Reusable module.

ENTRY POINTS
    import rebel_cell_landmark as RL
    d = RL.build(ctx)                      # city hook: ctx = landmarks.landmark_ctx("rebel_cell")
                                           #   -> dict(label=(x, y, z), crown=None, hue=(r, g, b))
    hooks = RL.build(K, rooms=True, rail=False)    # HQ netrun (option A section); K as in meridian_landmark.py
    K2 = RL.place(K, origin=(hx, hy, 0.0), k=0.2375)   # wrap K to drop the kit build into the one city
    info = RL.landmark_info()              # constants for check 12.2 (landmark ratio) and 8.6b

What it builds (city hook, port of landmarks.rebel_cell, spec 8.5 / 8.6c)
  No building, no tower, no crown beam (designer). The landmark is the district (building language "tenement", the
  fist in red windows by the zoning crest rule) plus the red MAINFRAME blade sign (3 x 12 BU, z 2.4 .. 14.4, the sign's
  own 1:4 aspect, texture mainframe_blade.png). Rule: the REBEL_CELL building nearest the HQ lot (the Cell's anchor),
  at least 10 BU tall, not drowned, with a camera-facing street face >= 4 BU long, carries it at that face's corner,
  out over the street. Ties break by (distance, building key, face index). Also: a red wash strip on the shop front and
  one red spot (3.0e4, cone 70). The sign quad is appended to ctx.station["signs"] as (four corners, image path) for the
  city renderer (the built-in used the module global SIGNS); ctx.station["mainframe"] gets the sign's anchor point.

What it builds (HQ netrun, spec 8.4 / 8.5): option A, "three stacked lanes in one section" (hq_build_A.py, non-v3
  path): lane buildings (ground floor = street rooms, roof = rooftop rooms), detour huts on a steel frame, the earth
  cut open (service tunnel lane R, deeper detour level), the switch column and service shaft up to DISPATCH, the
  rooms through K.room_shell, start hut, walkways, tunnel / sodium / roof lights, a rim from the city. The district
  (rc_district), the alley (rc_alley) and the sewer v3 are NOT supplied; they come in through K hooks (see build_hq).
  Topology (G.ROOM, G.PATH ...) is MOCK route data per spec 8.4; the pipeline must feed slots from the game graph.

UNITS / PLACING
  City hook: world BU (x east, y north, z up; dry street z 0), no scaling. build_hq: HQ-kit units (1 storey = 8 BU);
  wrap with place(K, origin, k=0.2375) for the one city (spec 8.6). Rebel Cell has no lot-filling compound: the sign
  sits on a map building, so k_fit does not apply (ASSUMPTION; see landmark_info).

SEEDS
  Named streams via _rng(seed, name): random.Random(seed * 1000003 + sum(ord)) with seed = ctx.seed
  (CP.SEEDS["landmark"]). The city hook is fully rule-based and draws nothing; the stream helper serves build_hq.
"""
import math
import random
from types import SimpleNamespace

# ------------------------------------------------------------------ constants (names per GDD 11.7 working names)
CORP = "rebel_cell"
CENTRAL_SERVER_NAME = "DISPATCH"
LANDMARK_NAME = "THE MAINFRAME BLADE SIGN"
K_UNITS = 0.2375
CITY_FOOTPRINT_BU = None          # ASSUMPTION: no lot footprint (ctx.footprint is None for rebel_cell); sign only
SIGN_W = 3.0                      # BU out over the street
SIGN_Z = (2.4, 14.4)              # BU, bottom / top of the blade
SIGN_TEX = "mainframe_blade.png"
SIGN_RED = (1.0, 0.16, 0.12)
SPOT_RED = (1.0, 0.12, 0.08)
SPOT_POWER = 3.0e4
SPOT_CONE = 70.0
MIN_BUILDING_H = 10.0             # BU
MIN_FACE_LEN = 4.0                # BU
LABEL_Z = 34.0
CROWN = None                      # no crown, no beam (designer; built-in note 8)


def _rng(seed, name):
    return random.Random(int(seed or 0) * 1000003 + sum(ord(c) for c in name))


def landmark_info():
    """Constants the pipeline checks (12.2 ratio, 8.6b silhouette) can read. All BU, city units."""
    return dict(corp=CORP, central_server_name=CENTRAL_SERVER_NAME, landmark=LANDMARK_NAME,
                footprint_bu=CITY_FOOTPRINT_BU,
                tier_heights=dict(sign_bottom=SIGN_Z[0], sign_top=SIGN_Z[1], sign_width=SIGN_W,
                                  label=LABEL_Z, min_building=MIN_BUILDING_H),
                crown=CROWN, pass_indices_note="sign = emissive quad; check 12.2 must use the sign box, not a compound")


# ------------------------------------------------------------------ the city hook
def _seen(a, b, cx, cy, cam):
    """Port stand-in for the city's seen(): (visible, outward unit normal, length) of edge a->b of a footprint
    whose centroid is (cx, cy); visible = the normal faces the camera (cam = ctx.camdir, xy used)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return False, (0.0, 0.0), 0.0
    nx, ny = dy / L, -dx / L
    mx, my = (a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy
    if nx * mx + ny * my < 0:
        nx, ny = -nx, -ny
    cl = math.hypot(cam[0], cam[1]) or 1.0
    vis = (nx * cam[0] + ny * cam[1]) / cl > 0.05
    return vis, (nx, ny), L


def build_city(ctx):
    O, W, CP = ctx.O, ctx.W, ctx.CP
    NEON = ctx.NEON
    core_lot = ctx.hq_lot
    best = None
    for b in O["buildings"]:
        if b["terr"] != CORP or b["h"] * CP.KH < MIN_BUILDING_H or b.get("wet"):
            continue
        q = [W(p) for p in b["q"]]
        n = len(q)
        cxq, cyq = sum(p[0] for p in q) / n, sum(p[1] for p in q) / n
        for i in range(n):
            vis, nrm, L = _seen(q[i], q[(i + 1) % n], cxq, cyq, ctx.camdir)
            if vis and L >= MIN_FACE_LEN:
                d = math.hypot(b["c"][0] - core_lot[0], b["c"][1] - core_lot[1])
                key = (round(d, 3), b["key"], i)
                if best is None or key < best[0]:
                    best = (key, q[i], q[(i + 1) % n], nrm, b)
                break
    hx, hy = ctx.hq
    hue = tuple(ctx.district["hue"])
    if best is None:                                  # no eligible building: no sign, label on the HQ lot
        return dict(label=(hx, hy, LABEL_Z), crown=CROWN, hue=hue)
    _, a, c, (nx, ny), b = best
    L = math.hypot(c[0] - a[0], c[1] - a[1])
    ux, uy = (c[0] - a[0]) / L, (c[1] - a[1]) / L
    px, py = a[0] + ux * 0.8, a[1] + uy * 0.8
    z0s, z1s = SIGN_Z
    w_ = SIGN_W
    signs = ctx.station.setdefault("signs", [])
    signs.append(([(px + nx * 0.3, py + ny * 0.3, z0s), (px + nx * (0.3 + w_), py + ny * (0.3 + w_), z0s),
                   (px + nx * (0.3 + w_), py + ny * (0.3 + w_), z1s), (px + nx * 0.3, py + ny * 0.3, z1s)],
                  str(ctx.CP.SCR) + "/" + SIGN_TEX))
    # the red wash of the sign on its shop front
    NEON.face([(a[0] + nx * 0.08, a[1] + ny * 0.08, 0.15), (c[0] + nx * 0.08, c[1] + ny * 0.08, 0.15),
               (c[0] + nx * 0.08, c[1] + ny * 0.08, 1.4), (a[0] + nx * 0.08, a[1] + ny * 0.08, 1.4)], SIGN_RED)
    ctx.spot_at((px, py, 8.0), (px + nx * 6 + ux * 3, py + ny * 6 + uy * 3, 3.0), SPOT_RED, SPOT_POWER, SPOT_CONE)
    ctx.station["mainframe"] = (px + nx * 1.8, py + ny * 1.8, 8.4)
    ctx.station["mainframe_building"] = b["key"]
    return dict(label=(hx, hy, LABEL_Z), crown=CROWN, hue=hue)


# ------------------------------------------------------------------ placing (for the one city), as the Meridian template
class _AccProxy:
    def __init__(self, acc, f):
        self._acc, self._f = acc, f

    def face(self, pts, col, k=0.0):
        self._acc.face([self._f(p) for p in pts], col, k)

    def __getattr__(self, n):
        return getattr(self._acc, n)


def place(K, origin=(0.0, 0.0, 0.0), k=K_UNITS):
    """A copy of K whose accumulators and lights are moved to origin and scaled by k (positions x k, energy x k^2)."""
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


# ------------------------------------------------------------------ the HQ netrun build (option A, non-v3 path)
def build_hq(K, rooms=True, rail=False):
    """Option A section. K as in meridian_landmark.py plus (hq_build_A.py): G (hq_graph_A: ROOM, LANE, KIND, PATH, TY,
    ZL, XS, X0, SHAFT_X, edge_path), obox, oquad, Vector, seg_box, room_shell(id, rec, kind=), ROOM_EMIT, HZ.
    Hooks NOT supplied here and required from the caller (None disables that part):
      K.district_build(K, keep_free, cut_y) -> (accs, SEQ, PULSE, cat)   # rc_district.build
      K.alley_build(K, DIST, cat, hooks, tex_dir, only=False)            # rc_alley.build
      K.new_collection(name) -> collection with .objects.link             # replaces bpy.data.collections.new
      K.seq_lights(hooks, seq, pal)                                       # rc_alley.seq_lights
    `rail` is accepted for the dispatcher signature and ignored (no rail in Rebel Cell)."""
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, obox, tube, box = K.A, K.obox, K.tube, K.box
    Vector = K.Vector
    hooks = {"accs": {}, "beams": [], "mover_lights": {}, "no_cut": ("district",)}
    RED, SOD = pal("red_hot"), pal("sodium")
    ST = CP["stack"]
    CUT = ST["cut"]
    RW, RH, RD = CP["room_w"], CP["room_h"], CP["room_d"]
    log = K.log
    DIST, SEQ, PULSE, cat = None, None, None, (lambda x, y: 0)
    dbuild = getattr(K, "district_build", None)

    def free(x, y):
        xa_, xb_ = K.HZ["v3"]["front_x"] if K.HZ.get("v3") else (K.HZ["alley"]["x_a"], K.HZ["alley"]["x_b"])
        return CUT < y < CUT + 24.0 and xa_ - 6.0 < x < xb_ + 6.0
    if dbuild:
        accs, SEQ, PULSE, cat = dbuild(K, free, CUT)
        hooks["accs"].update(accs)
        DIST = accs["district"]
    if DIST is None or not rooms:
        log("rebel_cell: district hook or rooms missing; section skipped")
        return hooks
    # ---------------------------------------------------------------- the lane buildings (the first row, opened)
    EARTH = (0.045, 0.036, 0.032)
    DARK = (0.08, 0.075, 0.08)
    dzt = ST["dispatch_z"]
    builds = {}
    for i, r in G.ROOM.items():
        if i == "start":
            continue
        x, y, z = r["o"]
        b = builds.setdefault(round(x, 1), dict(x=x, roof=0.0, street=False, srv=False))
        if G.LANE.get(i) == "L":
            b["roof"] = max(b["roof"], z)
        if G.LANE.get(i) == "C":
            b["street"] = True
        if i == "srv":
            b["srv"] = True
            b["roof"] = max(b["roof"], dzt + 26.0)
    for key in sorted(builds):
        b = builds[key]
        x = b["x"]
        roof = b["roof"] or 30.0
        y0, y1 = CUT + 0.6, CUT + 18.0
        c = cat(x, CUT + 9.0)
        if b["street"]:
            box(DIST, x - 10.0, y0, 0.0, x - RW / 2 - 0.4, y1, 9.6, DARK, k=float(c))
            box(DIST, x + RW / 2 + 0.4, y0, 0.0, x + 10.0, y1, 9.6, DARK, k=float(c))
            box(DIST, x - RW / 2 - 0.4, CUT + RD + 0.5, 0.0, x + RW / 2 + 0.4, y1, 9.6, DARK, k=float(c))
            zb = 9.6
        else:
            zb = 0.0
        if b["srv"]:
            box(DIST, x - 12.0, y0, zb, x + 12.0, y1, dzt - 0.4, DARK, k=float(c))
            box(DIST, x - 12.0, y0, dzt - 0.4, x - 9.4, y1, dzt + RH + 2.0, DARK, k=float(c))
            box(DIST, x + 9.4, y0, dzt - 0.4, x + 12.0, y1, dzt + RH + 2.0, DARK, k=float(c))
            box(DIST, x - 12.0, y0, dzt + RH + 2.0, x + 12.0, y1, roof, DARK, k=float(c))
        elif roof > zb + 1.0:
            box(DIST, x - 10.0, y0, zb, x + 10.0, y1, roof, DARK, k=float(c))
    for i in ("L2a", "L2b"):                      # detour huts on a steel frame
        if i not in G.ROOM:
            continue
        x, y, z = G.ROOM[i]["o"]
        for dx in (-6.5, 6.5):
            for dy in (1.0, RD - 1.0):
                tube(A["metal"], (x + dx, y + dy, ST["roofs"]["2"]), (x + dx, y + dy, z - 0.3), 0.3, (0.2, 0.2, 0.2), n=5)
        box(A["rough"], x - RW / 2 - 0.6, y, z - 0.6, x + RW / 2 + 0.6, y + RD + 0.6, z, (0.15, 0.14, 0.13))
    # ---------------------------------------------------------------- the earth, the tunnel, the deeper level
    ze = ST["earth"]
    TY = G.TY
    ztb, ztt = G.ZL["R"] - 3.0, G.ZL["R"] + RH + 4.0
    zdb, zdt = G.ZL["R"] - 12.0 - 3.0, ztb
    xa, xb = G.X0 - 45.0, G.SHAFT_X + 4.0
    dxa, dxb = G.XS["2a"] - 12.0, G.XS["2b"] + 12.0
    yb = TY + 16.0
    E = A["rough"]
    EX0, EX1 = -320.0, 120.0
    box(E, EX0, yb, ze, EX1, TY + 160.0, -0.06, EARTH)
    box(E, EX0, TY, ztt, EX1, yb, -0.06, EARTH)
    box(E, EX0, TY, ztb, xa, yb, ztt, EARTH)
    box(E, xb, TY, ztb, EX1, yb, ztt, EARTH)
    box(E, EX0, TY, ze, dxa, yb, ztb, EARTH)
    box(E, dxb, TY, ze, EX1, yb, ztb, EARTH)
    box(E, dxa, TY, ze, dxb, yb, zdb, EARTH)
    for (x0_, x1_, z0_, z1_) in ((xa, xb, ztb, ztt), (dxa, dxb, zdb, zdt)):
        box(A["metal"], x0_, TY, z0_ - 0.3, x1_, yb, z0_, (0.2, 0.2, 0.21))
        box(A["civic"], x0_, yb - 0.4, z0_, x1_, yb, z1_, (0.16, 0.16, 0.17))
        x = x0_ + 6.0
        while x < x1_ - 4.0:
            box(A["trim"], x - 1.5, TY + 2.0, z1_ - 0.5, x + 1.5, TY + 6.0, z1_ - 0.3, (0.75, 0.9, 1.0), 2.0)
            x += 18.0
        tube(A["metal"], (x0_, yb - 1.2, z1_ - 2.0), (x1_, yb - 1.2, z1_ - 2.0), 0.6, (0.25, 0.2, 0.15), n=6)
        tube(A["metal"], (x0_, yb - 2.6, z1_ - 3.4), (x1_, yb - 2.6, z1_ - 3.4), 0.4, (0.15, 0.25, 0.2), n=6)
    for s_ in (-0.7, 0.7):
        box(A["metal"], xa, TY + 7.0 + s_, ztb, xb, TY + 7.2 + s_, ztb + 0.3, (0.4, 0.38, 0.35))
    # the service shaft: a lit cage up the switch column to DISPATCH's floor and down into the tunnel
    sx = G.SHAFT_X
    box(E, sx - 3.0, TY, ztt, sx + 3.0, TY + 0.01, -0.06, EARTH)
    for dx in (-2.5, 2.5):
        tube(A["metal"], (sx + dx, TY - 1.0, ztb), (sx + dx, TY - 1.0, 1.0), 0.15, (0.4, 0.38, 0.35), n=4)
        tube(A["metal"], (sx + dx, CUT - 1.0, 0.0), (sx + dx, CUT - 1.0, ST["roofs"]["K"] + RH), 0.15, (0.4, 0.38, 0.35), n=4)
    z = ztb
    while z < ST["roofs"]["K"] + RH:
        yy = TY if z < 0 else CUT
        box(A["small"], sx - 2.5, yy - 1.1, z, sx + 2.5, yy - 0.9, z + 0.15, RED, 2.0)
        z += 4.0
    # ---------------------------------------------------------------- rooms: rooftop / street / tunnel / switches / DISPATCH
    emv = K.ROOM_EMIT.setdefault("srv", K.Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"]))
    for i in sorted(G.ROOM):
        r = G.ROOM[i]
        if i == "start":
            continue
        if i == "srv":
            x, y, z = r["o"]
            K.room_shell("srv", dict(r, n=(0.0, -1.0)), kind="router")
            for k in range(6):
                box(emv, x - 7.0 + k * 2.6, y + RD - 0.4, z + 1.0, x - 5.6 + k * 2.6, y + RD - 0.2, z + 7.0, (1.0, 0.12, 0.08), 5.0)
            continue
        K.room_shell(i, r, kind="router" if G.KIND[i] == "switch" else None)
        o = r["o"]
        if G.LANE.get(i) == "L":
            obox(A["rough"], r, -RW / 2 - 1.0, RW / 2 + 1.0, -RD - 1.0, 0.0, o[2] + RH, o[2] + RH + 0.6, (0.12, 0.12, 0.13))
        if G.KIND[i] == "switch":
            obox(A["metal"], r, -1.2, 1.2, -RD + 1.0, -RD + 2.4, o[2], o[2] + 4.5, (0.15, 0.15, 0.16))
            obox(A["trim"], r, -0.8, 0.8, -RD + 2.4, -RD + 2.5, o[2] + 2.5, o[2] + 4.0, RED, 4.0)
    sxy = G.ROOM["start"]["o"]
    box(A["rough"], sxy[0] - 4, sxy[1] + 1, 0, sxy[0] + 4, sxy[1] + 6, 4.0, (0.2, 0.2, 0.21))
    box(A["trim"], sxy[0] - 3.0, sxy[1] + 0.95, 1.4, sxy[0] - 2.0, sxy[1] + 1.0, 2.8, (0.55, 1.0, 0.0), 6.0)
    K.add_light("hack", "POINT", (sxy[0] - 2.5, sxy[1] - 1.0, 2.0), 160.0, (0.55, 1.0, 0.0), size=0.3, group="start")
    for (a, b_) in G.PATH:                         # walkways on the section plane
        pth = G.edge_path(a, b_)
        for p, q in zip(pth, pth[1:]):
            p, q = Vector(p), Vector(q)
            d = q - p
            if math.hypot(d.x, d.y) < 0.3 and abs(d.z) > 0.5:
                for s_ in (-0.5, 0.5):
                    tube(A["metal"], p + Vector((s_, 0.3, -1.6)), q + Vector((s_, 0.3, -0.6)), 0.08, (0.3, 0.28, 0.25), n=4)
                continue
            K.seg_box(A["rough"], p + Vector((0, 0.6, -1.55)), q + Vector((0, 0.6, -1.55)), 1.6, 0.25, (0.16, 0.12, 0.09))
    # ---------------------------------------------------------------- light
    for x in range(int(xa) + 10, int(xb), 30):
        K.add_light("tun_%d" % x, "AREA", (x, G.TY + 5.0, ztt - 1.0), 900.0, (0.75, 0.9, 1.0), aim=(x, G.TY + 5.0, ztb),
                    size=8.0, size_y=4.0, group="corp")
    for x in range(int(xa) + 20, int(xb) + 40, 40):
        K.add_light("sod_%d" % x, "SPOT", (x, CUT - 4.0, 14.0), LH["sod_w"], SOD, aim=(x, CUT + 4.0, 0.0), size=0.6,
                    spot=90, blend=0.9, group="corp")
        K.add_light("roof_%d" % x, "SPOT", (x, CUT - 8.0, 60.0), LH["sod_w"] * 0.8, (0.85, 0.85, 1.0),
                    aim=(x, CUT + 6.0, 34.0), size=0.6, spot=60, blend=0.9, group="corp")
    K.add_light("section_key", "AREA", (-80.0, CUT - 160.0, 40.0), LH["key_w"] * LH["section_key_k"], (0.8, 0.82, 0.95),
                aim=(-80.0, CUT, 12.0), size=260.0, size_y=60.0, group="corp", shadow=False)
    abuild = getattr(K, "alley_build", None)
    if abuild:
        abuild(K, DIST, cat, hooks, K.HZ["out_big"] + "/tex", only=False)
    ncoll = getattr(K, "new_collection", None)
    RIMRX = ncoll("rim_rx") if ncoll else None
    for k, (rx, c_) in enumerate(((-160.0, "neon_a"), (100.0, "neon_b"))):
        K.add_light("rim_%d" % k, "AREA", (rx, CUT + 300.0, 70.0), LH["rim_w"], pal(c_), aim=(rx * 0.5, CUT, 30.0),
                    size=160.0, size_y=80.0, group="corp", shadow=False, receivers=RIMRX)
    log("option A built")

    def post_build(OBJ):
        if RIMRX is None:
            return
        for name, ob in OBJ.items():
            if ob is not None and any(c.name in ("compound", "rooms") for c in ob.users_collection):
                RIMRX.objects.link(ob)
    hooks["post_build"] = post_build

    def apply(fr, ctx):
        me = fr.get("mech") or {}
        SEQ.outputs[0].default_value = float(me.get("seq", 2.0))
        PULSE.outputs[0].default_value = float(me.get("pulse", 0.0))
        sl = getattr(K, "seq_lights", None)
        if sl:
            sl(hooks, float(me.get("seq", 2.0)), pal)
        for ob in hooks.get("tex_objs", []):
            ctx["set_pwo"](ob, ctx["cut"])
    hooks["apply"] = apply
    return hooks


# ------------------------------------------------------------------ dispatcher
def build(K, rooms=True, rail=False):
    """City (landmarks.landmark_ctx): build(ctx) -> dict(label, crown, hue). HQ kit: build(K, rooms, rail) -> hooks."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return build_city(K)
    return build_hq(K, rooms, rail)
