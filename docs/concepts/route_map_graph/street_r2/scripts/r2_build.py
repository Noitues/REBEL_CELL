"""Street round 2 (exec'd inside r2_scene.py right after the city buildings): rooms, walls, and the planned dressing.

A copy of storyboard/scripts/m44/onecity_build.py. Kept: the room cut, the room interiors and lights, the section rule.
Changed / new (the plan from r2_rules.py, PLAN):
  - route buildings are matched by (ci, key) and cut in every kit accumulator (glass and panel too); the cut pads the
    along-street edge by half a kit cell, and the closed wall over an opening is built by the building's OWN kit rule
    over that padded span (concrete_band: the mainline fgrid; other kits: r2_kits.kit_face);
  - the v3 hero blade + band are replaced by the planned signs (dressing.signs), built per sign as LOD tier objects:
      t1  the neon SHAPE (a dim flat fill in the sign's hue + its rim tubes)      466 >= d > 216 BU
      t2  the full sign (the text / art texture board + a dark frame)             216 >= d (t1 hidden)
      t3  detail (lit tube rim proud of the board, brackets, lamp heads, cable)   70 >= d (added to t2)
    a sign over a room opening belongs to that room's wall (it goes with the wall in the REVEAL);
  - crowns (frontage.silhouette), the megastructure, kerb lamp posts (streets.light).
"""
import bmesh as _bm

OC = JOB_OC
ROOM_TL = {"router": (0.36, 0.88, 1.0), "elite": (1.0, 0.38, 0.16), "terminal": (0.24, 1.0, 0.55),
           "modem": (0.35, 0.59, 1.0), "rack": (1.0, 0.77, 0.24), "target": (1.0, 0.17, 0.24), "start": (0.83, 1.0, 0.0)}
OPEN = []          # (room id, axis, face, u0, u1, z0, z1, nrm)
for _i, _r in sorted(OC["rooms"].items()):
    _f = _r["front"]
    _ax = 0 if abs(_f[0][1] - _f[1][1]) < 1e-6 else 1
    _u = [p[_ax] for p in _f]
    _face = _f[0][1] if _ax == 0 else _f[0][0]
    _b = _r["back"]
    _nrm = 1.0 if ((_b[0][1] if _ax == 0 else _b[0][0]) > _face) else -1.0
    OPEN.append((_i, _ax, _face, min(_u), max(_u), _f[0][2], _f[2][2], _nrm))
UPAD = 0.62        # along-street cut pad (about half a kit cell) - the wall covers the same span


def _in_open(c, pad=0.12, near=0.45, upad=None):
    upad = pad if upad is None else upad
    for (i, ax, face, u0, u1, z0, z1, nrm) in OPEN:
        u = c[ax]
        d = c[1 - ax] - face
        if u0 - upad < u < u1 + upad and z0 - pad < c[2] < z1 + pad and -near < d * nrm < 0.25:
            return i
    return None


def _cut(acc, upad=0.12):
    dead = [f for f in acc.bm.faces if _in_open(f.calc_center_median(), upad=upad) is not None]
    _bm.ops.delete(acc.bm, geom=dead, context="FACES")
    return len(dead)


_RKITS = {KITS.get(u, "concrete_band") for u in OC["route_uids"]}
n1 = _cut(RB, UPAD if _RKITS != {"concrete_band"} else 0.12)
n2, n3, n4, n5 = _cut(RBW, UPAD), _cut(RBN, 0.12), _cut(RBG, UPAD), _cut(RBP, UPAD)
print("R2 cut faces", n1, n2, n3, n4, n5, flush=True)

WALLS = {}
ROOM_LIGHTS = []
RINT = Acc("oc_rooms")          # room interiors (surfaces)
RPAN = Acc("oc_panels")         # lit back panels (emissive)
_bcol = {}
for b in LAY["buildings"]:
    _u_ = "%d_%d" % (b["ci"], b["key"])
    if _u_ in OC["route_uids"]:
        fam = FAMS_C[abs(b["key"]) % len(FAMS_C)]
        tc = TERR.get(b["terr"], (0.8, 0.8, 0.8))
        _bcol[_u_] = mixc(fam, tc, 0.28 if b["terr"] else 0.0)
for (i, ax, face, u0, u1, z0, z1, nrm) in OPEN:
    r = OC["rooms"][i]
    col = _bcol.get(r["bld_uid"], (0.4, 0.38, 0.46))
    rr = random.Random(abs(r["bld"]) * 31 + len(i))
    kit = KITS.get(r["bld_uid"], "concrete_band")

    def P(u, d, z):
        return (u, face + d * nrm, z) if ax == 0 else (face + d * nrm, u, z)
    # the wall over the opening: the building's own kit, its own objects (dissolvable)
    wa, ww = Acc("oc_wall_" + i), Acc("oc_wallw_" + i)
    wg, wp, wn = Acc("oc_wallg_" + i + "_glass"), Acc("oc_wallp_" + i + "_panel"), Acc("oc_walln_" + i)
    if kit == "concrete_band":
        A_, B_, C_, D_ = P(u0 - 0.12, -0.03, z0 - 0.12), P(u1 + 0.12, -0.03, z0 - 0.12), P(u1 + 0.12, -0.03, z1 + 0.12), P(u0 - 0.12, -0.03, z1 + 0.12)
        _keep = CITY
        CITY = wa
        fgrid(A_, B_, C_, D_, col, rid(), rr)
        CITY = _keep
        nxw = int((u1 - u0 - 0.6) / 1.6)
        for uu in range(max(1, nxw)):
            if rr.random() > 0.35:
                continue
            t0 = u0 + 0.3 + uu * 1.6 + 0.4
            zz = z0 + (z1 - z0) * 0.35
            wc = rr.choice(WIN_COLS)
            s = 0.5 + 0.5 * rr.random()
            ww.face([P(t0, -0.08, zz), P(t0 + 0.8, -0.08, zz), P(t0 + 0.8, -0.08, zz + 0.7), P(t0, -0.08, zz + 0.7)],
                    tuple(v * s for v in wc), (0, 0, 0))
    else:
        pa, pc = P(u0 - UPAD, -0.03, 0.0), P(u1 + UPAD, -0.03, 0.0)
        onx, ony = (0.0, -nrm) if ax == 0 else (-nrm, 0.0)
        kit_face(kit, (pa[0], pa[1]), (pc[0], pc[1]), z0 - 0.12, z1 + 0.12, onx, ony, col, rr,
                 dict(conc=wa, glass=wg, panel=wp, win=ww, neon=wn), module=MODS.get(r["bld_uid"], 0))
    if r["bld_uid"] in TRIMS:                    # the lit bands carry across the closed wall
        pa, pc = P(u0 - UPAD, -0.03, 0.0), P(u1 + UPAD, -0.03, 0.0)
        onx, ony = (0.0, -nrm) if ax == 0 else (-nrm, 0.0)
        trim_face((pa[0], pa[1]), (pc[0], pc[1]), 0.0, 999.0, onx, ony, TRIMS[r["bld_uid"]], wn, zr=(z0 - 0.12, z1 + 0.12))
    WALLS[i] = (wa, ww, wg, wp, wn)
    # the room: floor, ceiling, back, sides (dark), a lit back panel in the type colour, a cut frame
    tl = ROOM_TL.get(r["kind"], (0.8, 0.8, 0.9))
    dk = tuple(0.18 + 0.25 * v for v in tl)
    dep = 2.4
    RINT.face([P(u0, 0, z0), P(u1, 0, z0), P(u1, dep, z0), P(u0, dep, z0)], tuple(v * 0.7 for v in dk), rid())
    RINT.face([P(u0, dep, z1), P(u1, dep, z1), P(u1, 0, z1), P(u0, 0, z1)], tuple(v * 0.5 for v in dk), rid())
    RINT.face([P(u0, dep, z0), P(u1, dep, z0), P(u1, dep, z1), P(u0, dep, z1)], dk, rid())
    RINT.face([P(u0, 0, z0), P(u0, dep, z0), P(u0, dep, z1), P(u0, 0, z1)], tuple(v * 0.8 for v in dk), rid())
    RINT.face([P(u1, dep, z0), P(u1, 0, z0), P(u1, 0, z1), P(u1, dep, z1)], tuple(v * 0.8 for v in dk), rid())
    pw = min(u1 - u0 - 0.6, 3.2)
    pc_ = (u0 + u1) / 2
    RPAN.face([P(pc_ - pw / 2, dep - 0.04, z0 + 0.35), P(pc_ + pw / 2, dep - 0.04, z0 + 0.35),
               P(pc_ + pw / 2, dep - 0.04, z1 - 0.3), P(pc_ - pw / 2, dep - 0.04, z1 - 0.3)], tl, (0, 0, 0))
    for (a_, b_) in (((u0, z0), (u1, z0)), ((u1, z0), (u1, z1)), ((u1, z1), (u0, z1)), ((u0, z1), (u0, z0))):
        beam(P(a_[0], -0.02, a_[1]), P(b_[0], -0.02, b_[1]), 0.16, (0.15, 0.13, 0.19), acc=RINT)
    ROOM_LIGHTS.append((i, P(pc_, dep * 0.5, z1 - 0.1), tl, (u1 - u0), dep))

# ------------------------------------------------------------------ crowns (frontage.silhouette)
CROWN_N = Acc("r2_crown_neon")
_bk_h = {}
for c_ in PLAN["crowns"]:
    q = c_["q"]                                   # world coordinates (r2_rules)
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    zt = c_["top"]
    col = tuple(c_["col"])
    rc = random.Random(sum(ord(ch) * (k + 1) for k, ch in enumerate(c_["key"])) + 7919 * int(PLAN["seed"]))
    k = c_["kind"]
    if k == "setback":
        ins = min(x1 - x0, y1 - y0) * rc.uniform(0.18, 0.3)
        hh = c_["floors"] * 1.9
        box(x0 + ins, y0 + ins, zt, x1 - ins, y1 - ins, zt + hh, (0.30, 0.30, 0.36), facet=False)
        for (pa, pb) in (((x0 + ins, y0 + ins), (x1 - ins, y0 + ins)), ((x1 - ins, y0 + ins), (x1 - ins, y1 - ins)),
                         ((x1 - ins, y1 - ins), (x0 + ins, y1 - ins)), ((x0 + ins, y1 - ins), (x0 + ins, y0 + ins))):
            beam((pa[0], pa[1], zt + hh + 0.06), (pb[0], pb[1], zt + hh + 0.06), 0.16, col, acc=CROWN_N)
            beam((pa[0], pa[1], zt + 0.05), (pb[0], pb[1], zt + 0.05), 0.12, tuple(v * 0.7 for v in col), acc=CROWN_N)
        for j in range(c_["floors"]):                          # a lit band per setback floor on the street side
            if rc.random() < 0.5:
                zz = zt + 0.6 + j * 1.9
                CWIN.face([(x0 + ins + 0.3, y0 + ins - 0.04, zz), (x1 - ins - 0.3, y0 + ins - 0.04, zz), (x1 - ins - 0.3, y0 + ins - 0.04, zz + 0.6),
                           (x0 + ins + 0.3, y0 + ins - 0.04, zz + 0.6)], tuple(v * 0.7 for v in rc.choice(WIN_COLS)), (0, 0, 0))
    elif k == "spire":
        hh = c_["h"]
        beam((cx, cy, zt), (cx, cy, zt + hh), 0.32, (0.24, 0.24, 0.3))
        beam((cx, cy, zt + hh), (cx, cy, zt + hh * 1.35), 0.12, (0.24, 0.24, 0.3))
        for f_ in (0.35, 0.7):
            rr_ = 0.7 * (1.1 - f_)
            for m in range(8):
                a0, a1 = 2 * math.pi * m / 8, 2 * math.pi * (m + 1) / 8
                beam((cx + rr_ * math.cos(a0), cy + rr_ * math.sin(a0), zt + hh * f_), (cx + rr_ * math.cos(a1), cy + rr_ * math.sin(a1), zt + hh * f_),
                     0.09, col, acc=CROWN_N)
        CROWN_N.face([(cx - 0.25, cy - 0.02, zt + hh * 1.35), (cx + 0.25, cy - 0.02, zt + hh * 1.35), (cx + 0.25, cy - 0.02, zt + hh * 1.35 + 0.4),
                      (cx - 0.25, cy - 0.02, zt + hh * 1.35 + 0.4)], RED, (0, 0, 0))
        ANTS.append((cx, cy, zt + hh * 1.35 + 0.2))
    elif k == "roof_box":
        w_, d_ = (x1 - x0) * 0.42, (y1 - y0) * 0.42
        bx0, by0 = x0 + (x1 - x0) * rc.uniform(0.08, 0.5), y0 + (y1 - y0) * rc.uniform(0.1, 0.45)
        box(bx0, by0, zt, bx0 + w_, by0 + d_, zt + 2.2, (0.28, 0.28, 0.33), facet=False)
        beam((bx0, by0 - 0.03, zt + 2.25), (bx0 + w_, by0 - 0.03, zt + 2.25), 0.1, col, acc=CROWN_N)
        CWIN.face([(bx0 + 0.3, by0 - 0.04, zt + 0.3), (bx0 + 0.9, by0 - 0.04, zt + 0.3), (bx0 + 0.9, by0 - 0.04, zt + 1.9),
                   (bx0 + 0.3, by0 - 0.04, zt + 1.9)], (1.0, 0.8, 0.5), (0, 0, 0))
        tx, ty = x1 - 1.1, y1 - 1.1
        for dx, dy in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)):
            beam((tx + dx, ty + dy, zt), (tx + dx, ty + dy, zt + 1.0), 0.12, (0.2, 0.2, 0.24))
        cyl36(tx, ty, zt + 1.0, zt + 2.4, 0.85, (0.42, 0.36, 0.32))
    elif k == "sign_frame":
        w_ = min(x1 - x0, 7.0) * 0.85
        hv = w_ * 0.42
        bx0 = cx - w_ / 2
        by_ = y0 + 0.4
        zb = zt + 0.9
        for lx in (bx0 + 0.3, bx0 + w_ - 0.3):
            beam((lx, by_ + 0.2, zt), (lx, by_ + 0.2, zb), 0.16, (0.2, 0.2, 0.24))
        # r2: the board itself is a planned sign (crown_board, dressing.signs); the crown keeps its legs and rim
        for (pa, pb) in (((bx0, zb), (bx0 + w_, zb)), ((bx0 + w_, zb), (bx0 + w_, zb + hv)), ((bx0 + w_, zb + hv), (bx0, zb + hv)), ((bx0, zb + hv), (bx0, zb))):
            beam((pa[0], by_ - 0.05, pa[1]), (pb[0], by_ - 0.05, pb[1]), 0.12, col, acc=CROWN_N)
print("R2 crowns", len(PLAN["crowns"]), flush=True)


# ------------------------------------------------------------------ helpers: UV quads for the signs
def _quad_obj(name, pts, uv=((0, 0), (1, 0), (1, 1), (0, 1))):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(p) for p in pts], [], [(0, 1, 2, 3)])
    lay_ = me.uv_layers.new(name="UVMap")
    for li, l in enumerate(me.loops):
        lay_.data[li].uv = uv[l.vertex_index]
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def _acc_obj(acc, name):
    ob = acc.obj(TOON)
    ob.name = name
    return ob


# ------------------------------------------------------------------ signs (dressing.signs), LOD tiers
SIGN_OBJS = []       # dict(sign, t1=[objs], t2=[objs], t3=[objs], centre)
for s in PLAN["signs"]:
    ax_, d, out = s["axis"], s["d"], s["out"]

    def SP(u, z, dd=0.0):
        return (u, d + out * dd, z) if ax_ == 0 else (d + out * dd, u, z)
    u0, u1, z0, z1 = s["u0"], s["u1"], s["z0"], s["z1"]
    col = tuple(s["col"])
    # the board faces the street (out): order the corners so the normal points out
    flip = (out < 0) == (ax_ == 0)
    pts = [SP(u0, z0), SP(u1, z0), SP(u1, z1), SP(u0, z1)]
    uv = ((0, 0), (1, 0), (1, 1), (0, 1))
    if flip:
        pts = [pts[1], pts[0], pts[3], pts[2]]
        uv = ((1, 0), (0, 0), (0, 1), (1, 1))
    t2 = [_quad_obj("r2s_%s_t2" % s["id"], pts, uv)]
    fr = Acc("r2s_%s_frame" % s["id"])
    for (pa, pb) in (((u0, z0), (u1, z0)), ((u1, z0), (u1, z1)), ((u1, z1), (u0, z1)), ((u0, z1), (u0, z0))):
        beam(SP(pa[0], pa[1], 0.02), SP(pb[0], pb[1], 0.02), 0.07, (0.06, 0.06, 0.08), acc=fr)
    if s.get("roof"):                            # roof boards stand on two legs (always drawn with the board)
        for uu in (u0 + 0.12 * (u1 - u0), u1 - 0.12 * (u1 - u0)):
            beam(SP(uu, z0 - s["legs"], -0.15), SP(uu, z0 + 0.1, -0.15), 0.16, (0.12, 0.12, 0.15), acc=fr)
    t2.append(_acc_obj(fr, "r2s_%s_frame" % s["id"]))
    # t1: the neon shape: a dim flat fill + the rim tubes in the sign's hue
    sh = Acc("r2s_%s_t1" % s["id"])
    sh.face([SP(u0, z0, 0.01), SP(u1, z0, 0.01), SP(u1, z1, 0.01), SP(u0, z1, 0.01)], tuple(v * 0.3 for v in col), (0, 0, 0))
    for (pa, pb) in (((u0, z0), (u1, z0)), ((u1, z0), (u1, z1)), ((u1, z1), (u0, z1)), ((u0, z1), (u0, z0))):
        beam(SP(pa[0], pa[1], 0.04), SP(pb[0], pb[1], 0.04), 0.12, col, acc=sh)
    t1 = [_acc_obj(sh, "r2s_%s_t1" % s["id"])]
    # t3: detail: a lit tube rim proud of the board, brackets to the face, lamp heads over boards, a cable on blades
    dn = Acc("r2s_%s_t3n" % s["id"])
    dd_ = Acc("r2s_%s_t3d" % s["id"])
    e = 0.06
    for (pa, pb) in (((u0 - e, z0 - e), (u1 + e, z0 - e)), ((u1 + e, z0 - e), (u1 + e, z1 + e)), ((u1 + e, z1 + e), (u0 - e, z1 + e)),
                     ((u0 - e, z1 + e), (u0 - e, z0 - e))):
        beam(SP(pa[0], pa[1], 0.09), SP(pb[0], pb[1], 0.09), 0.045, tuple(min(1.0, v * 0.5 + 0.5) for v in col), acc=dn)
    for uu in (u0 + 0.15 * (u1 - u0), u1 - 0.15 * (u1 - u0)):
        for zz in ((z0 + 0.2, z1 - 0.2) if (z1 - z0) > 1.2 else ((z0 + z1) / 2,)):
            beam(SP(uu, zz, 0.0), SP(uu, zz, -s.get("off", 0.12) + 0.0), 0.06, (0.12, 0.12, 0.14), acc=dd_)
    if s["tex"]["style"] in ("box", "wall", "ad") and (u1 - u0) > 1.4:
        for uu in (u0 + 0.25 * (u1 - u0), u1 - 0.25 * (u1 - u0)):
            beam(SP(uu, z1 + 0.05, 0.0), SP(uu, z1 + 0.35, 0.35), 0.05, (0.12, 0.12, 0.14), acc=dd_)
            dn.face([SP(uu - 0.12, z1 + 0.33, 0.33), SP(uu + 0.12, z1 + 0.33, 0.33), SP(uu + 0.12, z1 + 0.42, 0.42),
                     SP(uu - 0.12, z1 + 0.42, 0.42)], (1.0, 0.95, 0.85), (0, 0, 0))
    if s["tex"]["style"] == "blade" and z0 > 1.0:
        beam(SP(u0 + 0.1, z0, 0.03), SP(u0 + 0.1, 0.0, 0.03), 0.03, (0.08, 0.08, 0.1), acc=dd_)
    t3 = [_acc_obj(dn, "r2s_%s_t3n" % s["id"]), _acc_obj(dd_, "r2s_%s_t3d" % s["id"])]
    SIGN_OBJS.append(dict(sign=s, t1=t1, t2=t2, t3=t3, centre=s["centre"]))
print("R2 signs", len(SIGN_OBJS), flush=True)

# ------------------------------------------------------------------ the megastructure (dressing.signs)
MEGA_OBJS = []
_mg = PLAN.get("mega")
if _mg:
    mx, my, mz = _mg["pos"]
    S_ = _mg["size"]
    col = tuple(_mg["col"])
    nrm2 = OC.get("nrm", [0.0, 1.0])
    ox, oy = -nrm2[0], -nrm2[1]                     # toward the street (the camera side)
    rx, ry = -oy, ox                                # along the street
    mg_n = Acc("r2_mega_neon")
    mg_s = Acc("r2_mega_solid")
    if _mg["kind"] == "globe":
        R_ = S_ * 0.5
        cz = mz + R_ * 0.4 + R_
        beam((mx, my, mz), (mx, my, cz - R_ * 0.6), 0.5, (0.22, 0.22, 0.28), acc=mg_s)
        for lat in (-0.66, -0.33, 0.0, 0.33, 0.66):
            rr_ = R_ * math.cos(lat * math.pi / 2)
            zz = cz + R_ * math.sin(lat * math.pi / 2)
            for m in range(24):
                a0, a1 = 2 * math.pi * m / 24, 2 * math.pi * (m + 1) / 24
                beam((mx + rr_ * math.cos(a0), my + rr_ * math.sin(a0), zz), (mx + rr_ * math.cos(a1), my + rr_ * math.sin(a1), zz), 0.14, col, acc=mg_n)
        for mer in range(8):
            ph = math.pi * mer / 8
            for m in range(24):
                a0, a1 = 2 * math.pi * m / 24, 2 * math.pi * (m + 1) / 24
                p0 = (mx + R_ * math.cos(a0) * math.cos(ph), my + R_ * math.cos(a0) * math.sin(ph), cz + R_ * math.sin(a0))
                p1 = (mx + R_ * math.cos(a1) * math.cos(ph), my + R_ * math.cos(a1) * math.sin(ph), cz + R_ * math.sin(a1))
                beam(p0, p1, 0.12, col, acc=mg_n)
        tilt = math.radians(22)
        for m in range(48):                       # the orbit ring
            a0, a1 = 2 * math.pi * m / 48, 2 * math.pi * (m + 1) / 48
            def RP(a):
                x_, y_ = R_ * 1.45 * math.cos(a), R_ * 1.45 * math.sin(a)
                return (mx + x_ * rx + y_ * ox * math.cos(tilt), my + x_ * ry + y_ * oy * math.cos(tilt), cz + y_ * math.sin(tilt) + x_ * 0.18)
            beam(RP(a0), RP(a1), 0.18, tuple(min(1, v * 0.6 + 0.4) for v in col), acc=mg_n)
    else:
        # arch: a curved board on two legs; holo: a flat panel on a frame. Both carry the megastructure texture.
        wv = S_
        hv = wv / (2.4 if _mg["kind"] == "arch" else 1.78)
        zb = mz + 1.6
        for t_ in (-0.42, 0.42):
            lx, ly = mx + rx * wv * t_, my + ry * wv * t_
            beam((lx, ly, mz), (lx, ly, zb + hv * 0.2), 0.35, (0.2, 0.2, 0.25), acc=mg_s)
        nseg = 16 if _mg["kind"] == "arch" else 1
        bulge = wv * 0.10 if _mg["kind"] == "arch" else 0.0
        me = bpy.data.meshes.new("r2_mega_board")
        vs, fs, uvs = [], [], []
        for k_ in range(nseg + 1):
            t_ = k_ / nseg - 0.5
            off = bulge * (1 - (2 * t_) ** 2)
            arc = hv * 0.18 * (1 - (2 * t_) ** 2)
            x_, y_ = mx + rx * wv * t_ + ox * off, my + ry * wv * t_ + oy * off
            vs += [(x_, y_, zb + arc), (x_, y_, zb + hv + arc)]
            uvs += [(k_ / nseg, 0.0), (k_ / nseg, 1.0)]
        for k_ in range(nseg):
            fs.append((2 * k_, 2 * k_ + 2, 2 * k_ + 3, 2 * k_ + 1))
        me.from_pydata(vs, [], fs)
        lay_ = me.uv_layers.new(name="UVMap")
        for li, l in enumerate(me.loops):
            lay_.data[li].uv = uvs[l.vertex_index]
        ob = bpy.data.objects.new("r2_mega_board", me)
        scene.collection.objects.link(ob)
        MEGA_OBJS.append(ob)
        for k_ in range(nseg):                    # lit tube along the top and bottom edges
            for e_ in (0, 1):
                beam(vs[2 * k_ + e_], vs[2 * k_ + 2 + e_], 0.16, col, acc=mg_n)
    MEGA_OBJS += [_acc_obj(mg_n, "r2_mega_neon"), _acc_obj(mg_s, "r2_mega_solid")]
    print("R2 megastructure", _mg["kind"], "size %.1f" % S_, flush=True)

# ------------------------------------------------------------------ kerb lamp posts (streets.light)
LP_S, LP_H = Acc("r2_lamp_post"), Acc("r2_lamp_head")
LAMP_HEADS = []
_lsx = OC.get("nrm", [0.0, 1.0])
for lp in PLAN["lamps"]:
    x_, y_, _z = lp["pos"]
    hh = float(OC.get("lamp_post_h", 4.6))
    # the arm reaches over the road (toward the street centre line)
    cl = PLAN["line"]
    if PLAN["axis"] == 0:
        dy = 1.0 if cl > y_ else -1.0
        hx, hy = x_, y_ + dy * 1.1
    else:
        dx = 1.0 if cl > x_ else -1.0
        hx, hy = x_ + dx * 1.1, y_
    beam((x_, y_, 0.0), (x_, y_, hh), 0.13, (0.08, 0.08, 0.1), acc=LP_S)
    beam((x_, y_, hh), (hx, hy, hh + 0.15), 0.08, (0.08, 0.08, 0.1), acc=LP_S)
    LP_H.face([(hx - 0.28, hy - 0.12, hh + 0.05), (hx + 0.28, hy - 0.12, hh + 0.05), (hx + 0.28, hy + 0.12, hh + 0.05), (hx - 0.28, hy + 0.12, hh + 0.05)],
              tuple(lp["col"]), (0, 0, 0))
    LP_H.face([(hx - 0.28, hy - 0.12, hh + 0.05), (hx + 0.28, hy - 0.12, hh + 0.05), (hx + 0.28, hy - 0.12, hh + 0.2), (hx - 0.28, hy - 0.12, hh + 0.2)],
              tuple(lp["col"]), (0, 0, 0))
    LAMP_HEADS.append(((hx, hy, hh - 0.1), tuple(lp["col"])))
LAMP_OBJS = [_acc_obj(LP_S, "r2_lamp_post"), _acc_obj(LP_H, "r2_lamp_head")]

RB_OBJ = RB.obj(TOON)
RBW_OBJ = RBW.obj(WINM)
RBN_OBJ = RBN.obj(NEONM)
RBG_OBJ = RBG.obj(TOON)
RBP_OBJ = RBP.obj(TOON)
CROWN_OBJ = CROWN_N.obj(NEONM)
RINT_OBJ = RINT.obj(TOON)
RPAN_OBJ = RPAN.obj(NEONM)
WALL_OBJS = {}
for i, (wa, ww, wg, wp, wn) in WALLS.items():
    WALL_OBJS[i] = (wa.obj(TOON), ww.obj(WINM), wg.obj(TOON), wp.obj(TOON), wn.obj(NEONM))
ONECITY_SOLIDS = [RB_OBJ, RBG_OBJ, RBP_OBJ, RINT_OBJ] + [w[0] for w in WALL_OBJS.values()]
print("R2 rooms", len(OPEN), "walls", len(WALL_OBJS), "roof kinds on the frontage",
      sorted({k for u in PLAN["front"] for k in ROOF_KINDS.get(u, set())} | {c_["kind"] for c_ in PLAN["crowns"] if c_["key"] in PLAN["front"]}),
      flush=True)
WALL_STATE = {}


def set_walls(dis):
    """dis: {room: 0 closed .. 1 gone}. A sign over an opening goes with its wall."""
    for i, objs in WALL_OBJS.items():
        h = float(dis.get(i, 0.0)) >= 0.5
        WALL_STATE[i] = h
        for o in objs:
            o.hide_render = h


# ------------------------------------------------------------------ the SECTION rule (a continuous city needs it)
# In a real city the blocks across the street stand between any side-view camera and the netrun street. The rule cuts
# them like a section model: inside the corridor in front of the street (the camera side of the street centre line,
# along the street +- corridor_pad), everything above z_cut is not drawn. z_cut follows the zoom (look preset
# section_by_zoom): far above every roof at the HQ, lowering through the dive to a plinth at the street. Same geometry,
# a clip in the materials (in Godot: a section-plane uniform in the city shaders, as for the wall dissolve).
_SC = OC["street"]
_SA, _SCc = _SC["a"], _SC["c"]
_NRM = OC.get("nrm", [0.0, 1.0])
_PAD = float(OC.get("corridor_pad", 30.0))
_PLINTH_OFF = float(OC.get("plinth_off", 4.2))      # beyond the street's camera-side kerb (half the border street width)
_PLINTH = OC.get("plinth", dict(albedo=0.012, edge=0.05, edge_k=0.0, on=(1.5, 5.0)))
_X0, _X1 = min(_SA[0], _SCc[0]), max(_SA[0], _SCc[0])
_Y0, _Y1 = min(_SA[1], _SCc[1]), max(_SA[1], _SCc[1])
bpy.context.scene["oc_zcut"] = 1.0e4


def section(mat):
    """Insert the section clip in front of a material's surface output (idempotent)."""
    if mat is None or mat.node_tree is None or mat.get("oc_section"):
        return
    nt = mat.node_tree
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None or not out.inputs["Surface"].links:
        return
    src = out.inputs["Surface"].links[0].from_socket
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sp.inputs[0])
    zc = nt.nodes.new("ShaderNodeAttribute")
    zc.attribute_type = "VIEW_LAYER"
    zc.attribute_name = "oc_zcut"

    def M(op, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for k, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[k].default_value = v
            else:
                nt.links.new(v, n.inputs[k])
        return n.outputs[0]
    X, Y, Z = sp.outputs["X"], sp.outputs["Y"], sp.outputs["Z"]
    # the camera side of the street centre line, along the street (+- pad)
    if abs(_NRM[1]) > 0.5:
        side = M("LESS_THAN", M("MULTIPLY", M("SUBTRACT", Y, _SA[1]), _NRM[1]), -0.4)
        along = M("MULTIPLY", M("GREATER_THAN", X, _X0 - _PAD), M("LESS_THAN", X, _X1 + _PAD))
    else:
        side = M("LESS_THAN", M("MULTIPLY", M("SUBTRACT", X, _SA[0]), _NRM[0]), -0.4)
        along = M("MULTIPLY", M("GREATER_THAN", Y, _Y0 - _PAD), M("LESS_THAN", Y, _Y1 + _PAD))
    above = M("GREATER_THAN", Z, zc.outputs["Fac"])
    cut = M("MULTIPLY", M("MULTIPLY", side, along), above)
    # the plinth rule: what stays of the cut blocks (camera side, beyond the kerb, below z_cut) goes near-black,
    # no trims or emissive roofs, only a faint cool top edge just under the cut plane
    if abs(_NRM[1]) > 0.5:
        beyond = M("LESS_THAN", M("MULTIPLY", M("SUBTRACT", Y, _SA[1]), _NRM[1]), -_PLINTH_OFF)
    else:
        beyond = M("LESS_THAN", M("MULTIPLY", M("SUBTRACT", X, _SA[0]), _NRM[0]), -_PLINTH_OFF)
    plinth = M("MULTIPLY", M("MULTIPLY", beyond, along), M("LESS_THAN", Z, zc.outputs["Fac"]))
    # only once the cut is down at plinth height (z_cut under plinth_on[1], full under plinth_on[0]): the HQ and the
    # upper dive keep the corridor's blocks in their own look while the cut is still above (or through) the roofs
    pr = nt.nodes.new("ShaderNodeMapRange")
    pr.interpolation_type = "SMOOTHSTEP"
    pr.inputs["From Min"].default_value, pr.inputs["From Max"].default_value = tuple(_PLINTH.get("on", (1.5, 5.0)))
    pr.inputs["To Min"].default_value, pr.inputs["To Max"].default_value = 1.0, 0.0
    nt.links.new(zc.outputs["Fac"], pr.inputs["Value"])
    plinth = M("MULTIPLY", plinth, pr.outputs[0])
    edge = M("GREATER_THAN", Z, M("SUBTRACT", zc.outputs["Fac"], float(_PLINTH["edge"])))
    a_ = float(_PLINTH["albedo"])
    if _PLINTH.get("wet", True):
        # v3-r3 (art director: the plinths read as a black checkerboard): the plinth tops are WET like the street
        # (the same noise-driven puddle roughness), so they carry the neon reflections and the street-level glows and
        # merge with the wet street instead of cutting black holes in it
        dk = nt.nodes.new("ShaderNodeBsdfPrincipled")
        dk.inputs["Base Color"].default_value = (a_, a_, a_ * 1.2, 1)
        nzp = nt.nodes.new("ShaderNodeTexNoise")
        nzp.inputs["Scale"].default_value = 0.27
        nzp.inputs["Detail"].default_value = 5.0
        nt.links.new(geo.outputs["Position"], nzp.inputs["Vector"])
        mrp = nt.nodes.new("ShaderNodeMapRange")
        mrp.inputs["From Min"].default_value, mrp.inputs["From Max"].default_value = 0.42, 0.6
        mrp.inputs["To Min"].default_value, mrp.inputs["To Max"].default_value = 0.32, 0.03
        nt.links.new(nzp.outputs["Fac"], mrp.inputs["Value"])
        nt.links.new(mrp.outputs[0], dk.inputs["Roughness"])
        try:
            dk.inputs["Specular IOR Level"].default_value = 0.7
        except KeyError:
            pass
    else:
        dk = nt.nodes.new("ShaderNodeBsdfDiffuse")
        dk.inputs["Color"].default_value = (a_, a_, a_ * 1.2, 1)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.45, 0.55, 0.75, 1)
    em.inputs["Strength"].default_value = float(_PLINTH["edge_k"])
    mxe = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(edge, mxe.inputs[0])
    nt.links.new(dk.outputs[0], mxe.inputs[1])
    nt.links.new(em.outputs[0], mxe.inputs[2])
    mxp = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(plinth, mxp.inputs[0])
    nt.links.new(src, mxp.inputs[1])
    nt.links.new(mxe.outputs[0], mxp.inputs[2])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(cut, mx.inputs[0])
    nt.links.new(mxp.outputs[0], mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    mat["oc_section"] = True


def section_all(skip=()):
    for m in bpy.data.materials:
        if m.name in skip:
            continue
        section(m)
