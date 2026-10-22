"""Solace HQ as a monumental modern-art sculpture of the DNA helix (exploration). Runs INSIDE Blender, hooked in front of the
render section of hq_scene.py (modernart_blender_hq.py). The base tube / window / office geometry of the landmark is hidden and
replaced by: two broad glossy ribbons (lime, pink) wound on the helix cylinder with a full 360 deg turn, Mondrian / Solace colour-
blocked base-pair slabs, a mirror ball, and a white gallery plinth. City fill = v1's cool teal-black.
Helpers imported read-only from art_deco/deco_restyle.py. Deterministic."""
import math
import random

import bpy
import bmesh
from mathutils import Vector

import deco_restyle as D

LIME = (0.30, 1.0, 0.06)
PINK = (1.0, 0.05, 0.30)
RED = (0.80, 0.015, 0.012)
YEL = (1.0, 0.62, 0.0)
BLUE = (0.015, 0.06, 0.62)
WHITE = (0.80, 0.80, 0.82)
BLACK = (0.012, 0.012, 0.014)
HIDE = ("metal", "porc", "glass", "trim", "office", "win_glass", "office_lamp", "rough", "small", "sign", "plinth_deck",
        "plaza_apron")


def mesh_obj(name, mat, verts, faces, smooth_faces, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    for i in smooth_faces:
        if i < len(me.polygons):
            me.polygons[i].use_smooth = True
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    ob.pass_index = 2
    ob["pwo"] = 1.0
    return ob


class Mesh:
    def __init__(self):
        self.v, self.f, self.sm = [], [], []

    def vert(self, p):
        self.v.append(tuple(p))
        return len(self.v) - 1

    def quad(self, a, b, c, d, smooth=False):
        if smooth:
            self.sm.append(len(self.f))
        self.f.append((a, b, c, d))

    def box(self, c, ax, ay, az, hx, hy, hz):
        """Oriented box: centre c, unit axes, half sizes."""
        c = Vector(c)
        pts = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    pts.append(c + ax * (sx * hx) + ay * (sy * hy) + az * (sz * hz))
        # index = sx*4 + sy*2 + sz with sx,sy,sz in (0,1)
        for fs in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            b = len(self.v)
            for i in fs:
                self.v.append(tuple(pts[i]))
            self.f.append((b, b + 1, b + 2, b + 3))


def ribbon(GR, t, width, thick, bow, zoff=0.0, nz=7, na=216, pack=None):
    """The strand t as a broad ribbon on the helix cylinder: width along z, thickness radial, shallow bow (outer face)."""
    PH, FH, R = GR.PODIUM_H, GR.FH, GR.R
    z_lo, z_hi = PH + 0.0, PH + 27 * FH
    M = Mesh()
    total = 27 * FH
    rows_o, rows_i = [], []
    for j in range(na + 1):
        zc = z_lo + total * j / na + zoff
        c, rv, n = GR.tower_frame(t, (zc - PH) / FH)
        ro, ri = [], []
        for k in range(nz + 1):
            s = k / nz - 0.5
            z = zc + s * width
            # centre line follows azimuth theta(zc) but the strip's rows are at azimuth of their own height (ribbon on the cylinder)
            rv2 = rv
            b = bow * math.cos(math.pi * s)
            ro.append(Vector((rv2[0] * (R + thick / 2 + b), rv2[1] * (R + thick / 2 + b), z)))
            ri.append(Vector((rv2[0] * (R - thick / 2), rv2[1] * (R - thick / 2), z)))
        rows_o.append(ro)
        rows_i.append(ri)
    # shared-vertex smooth outer / inner surfaces
    for rows, flip in ((rows_o, False), (rows_i, True)):
        idx = [[M.vert(p) for p in row] for row in rows]
        for j in range(na):
            for k in range(nz):
                q = (idx[j][k], idx[j + 1][k], idx[j + 1][k + 1], idx[j][k + 1])
                M.quad(*(q[::-1] if flip else q), smooth=True)
    # top and bottom edge faces (flat, own verts)
    for k, flip in ((nz, False), (0, True)):
        for j in range(na):
            a, b_ = rows_o[j][k], rows_o[j + 1][k]
            c_, d_ = rows_i[j + 1][k], rows_i[j][k]
            i0 = M.vert(a)
            i1 = M.vert(b_)
            i2 = M.vert(c_)
            i3 = M.vert(d_)
            M.quad(*((i3, i2, i1, i0) if flip else (i0, i1, i2, i3)))
    return M


def lump(M, c, r, rng, sides=6):
    """A low-poly foliage lump: three rings (narrow / wide / narrow) with hexagon caps, jittered."""
    c = Vector(c)
    lv = [(-0.75, 0.55), (0.0, 1.0), (0.7, 0.6)]
    rings = []
    for dz, rr in lv:
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides + rng.uniform(-0.2, 0.2)
            q = r * rr * rng.uniform(0.8, 1.15)
            ring.append(M.vert((c.x + math.cos(a) * q, c.y + math.sin(a) * q, c.z + dz * r * rng.uniform(0.85, 1.1))))
        rings.append(ring)
    for i in range(2):
        for k in range(sides):
            k2 = (k + 1) % sides
            M.f.append((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
    M.f.append(tuple(reversed(rings[0])))
    M.f.append(tuple(rings[2]))


def rib_pt(GR, t, j, na, s, rad, W):
    PH, FH = GR.PODIUM_H, GR.FH
    zc = PH + 27 * FH * j / na
    c, rv, n = GR.tower_frame(t, (zc - PH) / FH)
    return Vector((rv[0] * rad, rv[1] * rad, zc + s * W)), Vector((rv[0], rv[1], 0)), Vector((-rv[1], rv[0], 0))


PALETTES = {
    "violet": None,
    "warm": dict(
        A=("copper", (0.80, 0.30, 0.12), 1.0, 0.20, 0.45), B=("honey", (0.88, 0.46, 0.06), 0.0, 0.07, 0.6),
        slab={"ochre": (0.55, 0.30, 0.04), "rust": (0.42, 0.09, 0.035), "cream": (0.72, 0.58, 0.40), "olive": (0.11, 0.13, 0.03),
              "umber": (0.06, 0.035, 0.02), "honey": (0.90, 0.50, 0.08), "terra": (0.55, 0.16, 0.06)},
        plinth=(0.88, 0.70, 0.46), ball=(0.95, 0.55, 0.30), edgeA=LIME, edgeB=PINK, edge_k=(5.0, 4.5), edge_w=0.9,
        boxes=((1.0, 0.80, 0.55), (1.0, 0.60, 0.50), (1.0, 0.75, 0.45), (1.0, 0.95, 0.85)),
        key=(1.0, 0.82, 0.6), fill=(1.0, 0.6, 0.5), fog=(0.46, 0.43, 0.42), city_gold=(0.07, 0.055, 0.045), city_dark=0.07,
        city_tint=(1.0, 0.82, 0.6), city_boost=1.15, glow=(1.0, 0.76, 0.55), metal_tint=(0.2, 0.15, 0.1),
        post={"shadow_tint": [0.50, 0.48, 0.47], "sat": 0.9}),
    "solar": None,
}


def apply(g, cfg):
    var = cfg.get("variant", "violet")
    if var == "violet":
        return apply_v1(g, cfg)
    return apply_var(g, cfg, var)


def _city(g, cfg, P):
    OBJ = g["OBJ"]
    D.lacquer_facade(g["M_CITY"], gold=P["city_gold"], dark=P["city_dark"], window_tint=P["city_tint"], band_emit=0.2, win_boost=P["city_boost"])
    D.lacquer_panels(g["M_CIVIC"], gold=P["city_gold"], dark=0.2)
    for k in ("M_METAL", "M_CMETAL"):
        if k in g:
            D.brass_metal(g[k], tint=P["metal_tint"], rough=0.4)
    for k in ("city_sign", "city_neon"):
        if OBJ.get(k) is not None:
            OBJ[k].hide_render = True
    cfg.setdefault("fog_col", P["fog"])
    cfg.setdefault("veil_k", 0.003)
    cfg.setdefault("veil_z", (200.0, 300.0))
    D.tune_fog(g, cfg)
    D.fog_veil(g, cfg)
    for ob, e0, grp in g["LIGHTS"]:
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = P["glow"]
        elif grp in ("civic", "city", "start") and ob.data.type in ("SPOT", "POINT", "AREA") and ob.data.color[2] > ob.data.color[0]:
            ob.data.color = P["glow"]


def _softboxes(coll, P, ks=(14.0, 9.0, 9.0, 8.0)):
    boxes = [((-260, -150, 170), (0, 0, 170)), ((250, 120, 170), (0, 0, 170)), ((60, -330, 150), (0, 0, 150)), ((-120, 280, 260), (0, 0, 200))]
    for i, (loc, aim) in enumerate(boxes):
        me = bpy.data.meshes.new("ma_sb%d" % i)
        w, h = 40.0, 330.0
        me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
        sb = bpy.data.objects.new("ma_sb%d" % i, me)
        sb.location = loc
        sb.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("Y", "Z").to_euler()
        sb.visible_camera = False
        sb.visible_shadow = False
        sb.visible_volume_scatter = False
        coll.objects.link(sb)
        sb.data.materials.append(D.emission("ma_sbm%d" % i, P["boxes"][i], ks[i]))


def _ball(coll, ztop, mat, r=15.0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=r)
    me = bpy.data.meshes.new("ma_ball")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("ma_ball", me)
    ob.location = (0, 0, ztop + 22.0)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    ob.pass_index = 2
    ob["pwo"] = 1.0


def _lights(g, cfg, P):
    add = g["add_light"]
    for nm, loc, col, w in (("ma_key", (-330, -380, 330), P["key"], cfg.get("key_w", 250000.0)), ("ma_fill", (330, -300, 200), P["fill"], cfg.get("fill_w", 120000.0))):
        add(nm, "SPOT", loc, w, col, aim=(0, 0, 170), size=20.0, spot=40.0, blend=0.6, group="deco", shadow=False)


def apply_var(g, cfg, var):
    sc = bpy.context.scene
    GR, CP = g["G"], g["CP"]
    OBJ = g["OBJ"]
    for k in list(OBJ):
        if OBJ[k] is not None and (k in HIDE or k.startswith("room_")):
            OBJ[k].hide_render = True
            OBJ[k].data.clear_geometry()
    coll = bpy.data.collections.new("modernart")
    sc.collection.children.link(coll)
    PH, FH, R = GR.PODIUM_H, GR.FH, GR.R
    ztop = PH + 27 * FH
    PX, PY, PZ = CP["podium"]
    ex = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    W = cfg.get("ribbon_w", 56.0)
    TH = cfg.get("ribbon_t", 2.6)
    rng = random.Random(1953)

    def lac(name, base, rough=0.05, metal=0.0, emit=0.0, coat=1.0, emc=None):
        return D.principled(name, base, metal, rough, coat=coat, coat_rough=0.03, emit=emc or base, emit_k=emit)
    if var == "warm":
        P = PALETTES["warm"]
        (_, cA, mtA, rA, eA_), (_, cB, mtB, rB, eB_) = P["A"], P["B"]
        mA = lac("ma_A", cA, rA, mtA, eA_, coat=0.3 if mtA else 1.0)
        mB = lac("ma_B", cB, rB, mtB, eB_)
        edgeA = D.emission("ma_edge_A", P["edgeA"], P["edge_k"][0])
        edgeB = D.emission("ma_edge_B", P["edgeB"], P["edge_k"][1])
        for t, mat, emat in (("A", mA, edgeA), ("B", mB, edgeB)):
            M = ribbon(GR, t, W, TH, cfg.get("bow", 2.2))
            mesh_obj("ma_ribbon_" + t, mat, M.v, M.f, M.sm, coll)
            for sgn in (1, -1):
                E = ribbon(GR, t, P["edge_w"], TH + 1.0, 0.0, zoff=sgn * (W / 2 - 0.45), nz=1)
                mesh_obj("ma_edge_%s_%d" % (t, sgn), emat, E.v, E.f, E.sm, coll)
        sm = {k: lac("ma_s_" + k, c, 0.1, 0.0, 0.16) for k, c in P["slab"].items()}
        pal = ["ochre", "rust", "cream", "olive", "umber"]
        slabs = {}
        for f in range(1, 27):
            route = f in CP["route_floors"]
            z = PH + f * FH
            _, rvA, _ = GR.tower_frame("A", f)
            ax = Vector((rvA[0], rvA[1], 0))
            ay = Vector((-rvA[1], rvA[0], 0))
            half = R - TH * 0.5 + 0.1
            wd, hh = (7.5, 2.2) if not route else (12.0, 3.8)
            if route:
                ca, cb = "honey", "terra"
            else:
                ca = pal[rng.randrange(5)]
                cb = pal[rng.randrange(5)]
                while cb == ca:
                    cb = pal[rng.randrange(5)]
            sp = rng.uniform(-0.25, 0.25) * half
            for (a0, a1, cname) in ((-half, sp - 0.4, ca), (sp + 0.4, half, cb)):
                slabs.setdefault(cname, Mesh()).box(Vector((0, 0, z)) + ax * ((a0 + a1) / 2), ax, ay, ex[2], (a1 - a0) / 2, wd / 2, hh)
            slabs.setdefault("umber", Mesh()).box(Vector((0, 0, z)) + ax * sp, ax, ay, ex[2], 0.4, wd / 2 + 0.15, hh + 0.15)
            if route:
                fc = rng.choice(("cream", "ochre", "rust"))
                slabs.setdefault(fc, Mesh()).box(Vector((0, 0, z + hh + 3.0)) + ax * (rng.uniform(-0.5, 0.5) * half), ax, ay, ex[2], 6.0, wd / 2 - 0.5, 3.0)
        for cname, M in slabs.items():
            mesh_obj("ma_slab_" + cname, sm[cname], M.v, M.f, M.sm, coll)
        _ball(coll, ztop, D.principled("ma_ball", P["ball"], 1.0, 0.03, emit=P["ball"], emit_k=0.15))
        Pm = Mesh()
        Pm.box((0, 0, 7.0), *ex, PX * 0.98, PY * 0.98, 7.0)
        mesh_obj("ma_plinth", D.principled("ma_plinth", P["plinth"], 0.0, 0.05, coat=1.0, coat_rough=0.02, emit=P["plinth"], emit_k=0.20), Pm.v, Pm.f, Pm.sm, coll)
        S = Mesh()
        S.box((0, 0, 0.9), *ex, PX * 1.1, PY * 1.1, 0.9)
        mesh_obj("ma_plinth_step", D.principled("ma_step", (0.02, 0.012, 0.008), 0.0, 0.2), S.v, S.f, S.sm, coll)
        _softboxes(coll, P)
    else:
        P = SOLAR
        mTim = lac("ma_timber", (0.36, 0.15, 0.05), 0.40, 0.0, 0.30, coat=0.35, emc=(0.9, 0.4, 0.1))
        mCop = lac("ma_copper", (0.80, 0.30, 0.12), 0.24, 1.0, 0.26, coat=0.3, emc=(0.9, 0.35, 0.1))
        mLeaf = lac("ma_leaf", (0.035, 0.15, 0.02), 0.7, 0.0, 0.14, coat=0.0, emc=(0.25, 0.6, 0.06))
        mLeaf2 = lac("ma_leaf2", (0.07, 0.20, 0.03), 0.7, 0.0, 0.16, coat=0.0, emc=(0.4, 0.7, 0.08))
        mStone = lac("ma_stone", (0.74, 0.60, 0.42), 0.5, 0.0, 0.12, coat=0.2)
        mBronze = lac("ma_bronze", (0.14, 0.08, 0.035), 0.3, 1.0, 0.05, coat=0.0)
        mAmber = D.emission("ma_amber", (1.0, 0.52, 0.12), 4.5)
        mWater = D.emission("ma_water", (0.55, 0.95, 0.95), 3.2)
        mSun = D.emission("ma_sun", (1.0, 0.62, 0.18), 7.0)
        for t, mat in (("A", mTim), ("B", mCop)):
            M = ribbon(GR, t, W, TH, cfg.get("bow", 2.2))
            mesh_obj("ma_ribbon_" + t, mat, M.v, M.f, M.sm, coll)
            for sgn in (1, -1):
                E = ribbon(GR, t, 1.0, TH + 0.8, 0.0, zoff=sgn * (W / 2 - 0.5), nz=1)
                mesh_obj("ma_rim_%s_%d" % (t, sgn), mBronze, E.v, E.f, E.sm, coll)
        L1, L2, VN, WT = Mesh(), Mesh(), Mesh(), Mesh()
        na = 216
        lr = random.Random(33)
        for t in ("A", "B"):
            for j in range(0, na, 2):       # hedge spilling over the top edge, and a second row on the lower edge
                for s_, rows in ((0.5, 1), (-0.5, 1)):
                    p, rv, tg = rib_pt(GR, t, j, na, s_, R + TH / 2 + lr.uniform(0.0, 2.2), W)
                    lump(L1 if lr.random() < 0.6 else L2, p + Vector((0, 0, 1.2 if s_ > 0 else -0.5)), lr.uniform(1.8, 3.3), lr)
            for j in range(1, na, 3):       # hanging gardens drape from the lower edge and from the top lip
                p, rv, tg = rib_pt(GR, t, j, na, -0.5, R + TH / 2 + 1.3, W)
                ln_ = lr.uniform(6.0, 17.0)
                VN.box(p - Vector((0, 0, ln_ / 2)), rv, tg, ex[2], 0.18, 0.18, ln_ / 2)
                for q in range(3):
                    lump(L1 if q % 2 else L2, p - Vector((0, 0, ln_ * (0.35 + 0.3 * q))) + rv * lr.uniform(-0.3, 0.8), lr.uniform(1.2, 2.2), lr)
            for j in range(4, na, 9):       # vertical gardens: columns of planting on the ribbon face
                for q in range(5):
                    p, rv, tg = rib_pt(GR, t, j, na, -0.36 + 0.18 * q, R + TH / 2 + 1.6, W)
                    lump(L2 if q % 2 else L1, p, lr.uniform(1.4, 2.0), lr)
        for cname, M in (("L1", L1), ("L2", L2)):
            mesh_obj("ma_foliage_" + cname, mLeaf if cname == "L1" else mLeaf2, M.v, M.f, M.sm, coll)
        mesh_obj("ma_vines", mLeaf, VN.v, VN.f, VN.sm, coll)
        # base pairs: planted terraces and greenhouses glowing amber from inside, water cascades between levels
        T, Gr, GH, FR = Mesh(), Mesh(), Mesh(), Mesh()
        PL1, PL2 = Mesh(), Mesh()
        for f in range(1, 27):
            route = f in CP["route_floors"]
            z = PH + f * FH
            _, rvA, _ = GR.tower_frame("A", f)
            ax = Vector((rvA[0], rvA[1], 0))
            ay = Vector((-rvA[1], rvA[0], 0))
            half = R - TH * 0.5 + 0.1
            wd = 8.0 if not route else 12.0
            T.box(Vector((0, 0, z)), ax, ay, ex[2], half, wd / 2, 1.2)                     # terrace slab
            Gr.box(Vector((0, 0, z + 1.4)), ax, ay, ex[2], half - 1.0, wd / 2 - 0.4, 0.35)  # lawn
            for q in range(5):
                lump(PL1 if q % 2 else PL2, Vector((0, 0, z + 2.2)) + ax * rng.uniform(-half * 0.9, half * 0.9) + ay * rng.uniform(-wd / 2 + 1, wd / 2 - 1), rng.uniform(1.3, 2.3), rng)
            if route or rng.random() < 0.6:                                               # greenhouse
                gl = rng.uniform(16, 24) if not route else 30.0
                gh = 5.5 if not route else 8.0
                c0 = ax * (rng.uniform(-0.45, 0.45) * (half - gl / 2)) if not route else ax * (rng.uniform(-0.3, 0.3) * half)
                GH.box(Vector((0, 0, z + 1.6 + gh / 2)) + c0, ax, ay, ex[2], gl / 2, wd / 2 - 0.9, gh / 2)
                FR.box(Vector((0, 0, z + 1.6 + gh + 0.35)) + c0, ax, ay, ex[2], gl / 2 + 0.5, wd / 2 - 0.5, 0.35)
                for q in range(int(gl // 6) + 1):
                    FR.box(Vector((0, 0, z + 1.6 + gh / 2)) + c0 + ax * (-gl / 2 + q * 6.0), ax, ay, ex[2], 0.2, wd / 2 - 0.8, gh / 2 + 0.2)
            if f % 2 == 0:                                                                # waterfall down to the level below
                for sgn in (-1, 1):
                    xs = ax * (sgn * (half - 4.0 - rng.uniform(0, 8)))
                    WT.box(Vector((0, 0, z - FH / 2 + 0.6)) + xs + ay * (wd / 2 + 0.1), ax, ay, ex[2], 0.8, 0.12, FH / 2 - 0.4)
        mesh_obj("ma_terrace", mStone, T.v, T.f, T.sm, coll)
        mesh_obj("ma_lawn", mLeaf2, Gr.v, Gr.f, Gr.sm, coll)
        mesh_obj("ma_plant1", mLeaf, PL1.v, PL1.f, PL1.sm, coll)
        mesh_obj("ma_plant2", mLeaf2, PL2.v, PL2.f, PL2.sm, coll)
        mesh_obj("ma_glasshouse", mAmber, GH.v, GH.f, GH.sm, coll)
        mesh_obj("ma_gh_frame", mBronze, FR.v, FR.f, FR.sm, coll)
        mesh_obj("ma_water", mWater, WT.v, WT.f, WT.sm, coll)
        # crown: a glowing sun-orb ringed with planting
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=20, radius=13.0)
        me = bpy.data.meshes.new("ma_sun")
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("ma_sun", me)
        ob.location = (0, 0, ztop + 18.0)
        coll.objects.link(ob)
        ob.data.materials.append(mSun)
        ob["pwo"] = 1.0
        C1 = Mesh()
        for q in range(18):
            a = 2 * math.pi * q / 18
            lump(C1, (math.cos(a) * 17.0, math.sin(a) * 17.0, ztop + 4.0), rng.uniform(2.4, 3.6), rng)
        mesh_obj("ma_crown_green", mLeaf2, C1.v, C1.f, C1.sm, coll)
        # plinth: warm stone block with a planted garden rim and a lawn
        Pm = Mesh()
        Pm.box((0, 0, 7.0), *ex, PX * 0.98, PY * 0.98, 7.0)
        mesh_obj("ma_plinth", mStone, Pm.v, Pm.f, Pm.sm, coll)
        S = Mesh()
        S.box((0, 0, 0.9), *ex, PX * 1.1, PY * 1.1, 0.9)
        mesh_obj("ma_plinth_step", mBronze, S.v, S.f, S.sm, coll)
        LW, PR = Mesh(), Mesh()
        LW.box((0, 0, 14.2), *ex, PX * 0.92, PY * 0.9, 0.3)
        for q in range(0, 100):
            a = 2 * math.pi * q / 100
            ca_, sa_ = math.cos(a), math.sin(a)
            x = PX * 0.94 * math.copysign(abs(ca_) ** 0.3, ca_)
            y = PY * 0.92 * math.copysign(abs(sa_) ** 0.3, sa_)
            lump(PR, (x, y, 15.8), rng.uniform(2.0, 3.6), rng)
        mesh_obj("ma_lawn_plinth", mLeaf, LW.v, LW.f, LW.sm, coll)
        mesh_obj("ma_plinth_rim", mLeaf2, PR.v, PR.f, PR.sm, coll)
        _softboxes(coll, P, ks=(8.0, 9.0, 9.0, 6.0))
    _city(g, cfg, P)
    _lights(g, cfg, P)
    print("[modernart] built variant", var, flush=True)


SOLAR = dict(boxes=((1.0, 0.80, 0.55), (1.0, 0.65, 0.45), (0.80, 1.0, 0.60), (1.0, 0.95, 0.85)), key=(1.0, 0.78, 0.5), fill=(0.8, 1.0, 0.6),
             fog=(0.46, 0.43, 0.42), city_gold=(0.07, 0.06, 0.045), city_dark=0.07, city_tint=(1.0, 0.82, 0.6), city_boost=1.15,
             glow=(1.0, 0.76, 0.55), metal_tint=(0.2, 0.15, 0.1), post={"shadow_tint": [0.50, 0.48, 0.46], "sat": 0.95})


def apply_v1(g, cfg):
    sc = bpy.context.scene
    GR, CP = g["G"], g["CP"]
    OBJ = g["OBJ"]
    for k in list(OBJ):
        if OBJ[k] is not None and (k in HIDE or k.startswith("room_")):
            OBJ[k].hide_render = True
            OBJ[k].data.clear_geometry()
    coll = bpy.data.collections.new("modernart")
    sc.collection.children.link(coll)
    PH, FH, R = GR.PODIUM_H, GR.FH, GR.R
    ztop = PH + 27 * FH

    def lac(name, base, rough=0.04, metal=0.0, emit=0.0, coat=1.0):
        m = D.principled(name, base, metal, rough, coat=coat, coat_rough=0.02, emit=base, emit_k=emit)
        return m
    mA = lac("ma_lime", LIME, 0.05, 0.0, emit=0.40)
    mB = lac("ma_pink", PINK, 0.05, 0.0, emit=0.40)
    mats = {"red": lac("ma_red", RED, 0.08, 0.0, 0.18), "yel": lac("ma_yel", YEL, 0.08, 0.0, 0.30), "blue": lac("ma_blue", BLUE, 0.08, 0.0, 0.25),
            "white": lac("ma_white", WHITE, 0.08, 0.0, 0.10), "black": lac("ma_black", BLACK, 0.05, 0.0, 0.0),
            "lime": mA, "pink": mB}
    eA = D.emission("ma_edge_lime", LIME, 9.0)
    eB = D.emission("ma_edge_pink", PINK, 8.0)
    W = cfg.get("ribbon_w", 56.0)
    TH = cfg.get("ribbon_t", 2.6)
    for t, mat, emat in (("A", mA, eA), ("B", mB, eB)):
        M = ribbon(GR, t, W, TH, cfg.get("bow", 2.2))
        mesh_obj("ma_ribbon_" + t, mat, M.v, M.f, M.sm, coll)
        for sgn in (1, -1):
            E = ribbon(GR, t, 1.6, TH + 1.4, 0.0, zoff=sgn * (W / 2 - 0.8), nz=1)
            mesh_obj("ma_edge_%s_%d" % (t, sgn), emat, E.v, E.f, E.sm, coll)
    # base-pair slabs: colour-blocked bars spanning the ribbons, one per floor; route floors are thick, lime / pink blocks
    rng = random.Random(1953)
    pal = ["red", "yel", "blue", "white", "black"]
    slabs = {}
    for f in range(1, 27):
        route = f in CP["route_floors"]
        z = PH + f * FH
        cA, rvA, _ = GR.tower_frame("A", f)
        ax = Vector((rvA[0], rvA[1], 0))
        ay = Vector((-rvA[1], rvA[0], 0))
        az = Vector((0, 0, 1))
        half = R - TH * 0.5 + 0.1
        wd = 7.5 if not route else 12.0
        hh = 2.2 if not route else 3.8
        if route:
            ca, cb = ("lime", "pink")
        else:
            ca = pal[rng.randrange(5)]
            cb = pal[rng.randrange(5)]
            while cb == ca:
                cb = pal[rng.randrange(5)]
        # split at a random point of the span (A-T / G-C style), plus a thin black spacer
        sp = rng.uniform(-0.25, 0.25) * half
        for (a0, a1, cname) in ((-half, sp - 0.4, ca), (sp + 0.4, half, cb)):
            M = slabs.setdefault(cname, Mesh())
            M.box(Vector((0, 0, z)) + ax * ((a0 + a1) / 2), ax, ay, az, (a1 - a0) / 2, wd / 2, hh)
        M = slabs.setdefault("black", Mesh())
        M.box(Vector((0, 0, z)) + ax * sp, ax, ay, az, 0.4, wd / 2 + 0.15, hh + 0.15)
        if route:     # a room block, offset to the front, colour-field
            fc = rng.choice(("red", "yel", "blue", "white"))
            Mb = slabs.setdefault(fc, Mesh())
            Mb.box(Vector((0, 0, z + hh + 3.0)) + ax * (rng.uniform(-0.5, 0.5) * half), ax, ay, az, 6.0, wd / 2 - 0.5, 3.0)
    for cname, M in slabs.items():
        mesh_obj("ma_slab_" + cname, mats[cname], M.v, M.f, M.sm, coll)
    # Kapoor mirror ball on top, with a lime ring light
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=cfg.get("ball_r", 15.0))
    me = bpy.data.meshes.new("ma_ball")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("ma_ball", me)
    ob.location = (0, 0, ztop + 22.0)
    coll.objects.link(ob)
    ob.data.materials.append(D.principled("ma_mirror", (0.9, 0.95, 0.92), 1.0, 0.015))
    ob.pass_index = 2
    ob["pwo"] = 1.0
    # gallery plinth: white glossy block + black reveal + wide low step
    PX, PY, PZ = CP["podium"]
    P = Mesh()
    ex = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    P.box((0, 0, 7.0), *ex, PX * 0.98, PY * 0.98, 7.0)
    mesh_obj("ma_plinth", D.principled("ma_plinth", (0.85, 0.86, 0.88), 0.0, 0.04, coat=1.0, coat_rough=0.02, emit=(0.8, 0.85, 0.9), emit_k=0.22), P.v, P.f, P.sm, coll)
    S = Mesh()
    S.box((0, 0, 0.9), *ex, PX * 1.1, PY * 1.1, 0.9)
    mesh_obj("ma_plinth_step", D.principled("ma_step", (0.01, 0.01, 0.012), 0.0, 0.2), S.v, S.f, S.sm, coll)
    # reflection-only softboxes (invisible to the camera) so mirror and lacquer have long highlights to catch
    boxes = [((-260, -150, 170), (0, 0, 170), (0.80, 0.95, 1.0), 14.0), ((250, 120, 170), (0, 0, 170), (1.0, 0.82, 0.95), 9.0),
             ((60, -330, 150), (0, 0, 150), (0.75, 1.0, 0.75), 9.0), ((-120, 280, 260), (0, 0, 200), (1.0, 1.0, 1.0), 8.0)]
    for i, (loc, aim, col, k) in enumerate(boxes):
        me = bpy.data.meshes.new("ma_sb%d" % i)
        w, h = 40.0, 330.0
        me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
        sb = bpy.data.objects.new("ma_sb%d" % i, me)
        sb.location = loc
        sb.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("Y", "Z").to_euler()
        sb.visible_camera = False
        sb.visible_shadow = False
        sb.visible_volume_scatter = False
        coll.objects.link(sb)
        sb.data.materials.append(D.emission("ma_sbm%d" % i, col, k))
    # city fill: v1 cool teal-black
    D.lacquer_facade(g["M_CITY"], gold=(0.03, 0.20, 0.17), dark=0.14, window_tint=(0.45, 0.85, 1.0), band_emit=0.25, win_boost=2.0)
    D.lacquer_panels(g["M_CIVIC"], gold=(0.05, 0.30, 0.22), dark=0.2)
    for k in ("M_METAL", "M_CMETAL"):
        if k in g:
            D.brass_metal(g[k], tint=(0.18, 0.40, 0.32), rough=0.4)
    if OBJ.get("city_sign") is not None:
        OBJ["city_sign"].hide_render = True
    if OBJ.get("city_neon") is not None:
        OBJ["city_neon"].hide_render = True
    cfg.setdefault("fog_col", (0.30, 0.55, 0.72))
    cfg.setdefault("veil_k", 0.003)
    cfg.setdefault("veil_z", (200.0, 300.0))
    D.tune_fog(g, cfg)
    D.fog_veil(g, cfg)
    for ob, e0, grp in g["LIGHTS"]:
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = (0.45, 0.85, 0.80)
        elif grp in ("civic", "city", "start") and ob.data.type in ("SPOT", "POINT", "AREA") and ob.data.color[0] > ob.data.color[2]:
            ob.data.color = (0.55, 1.0, 0.75)
    add = g["add_light"]
    for nm, loc, col, w in (("ma_key", (-330, -380, 330), (0.85, 0.95, 1.0), cfg.get("key_w", 250000.0)), ("ma_fill", (330, -300, 200), (1.0, 0.75, 0.9), cfg.get("fill_w", 120000.0))):
        add(nm, "SPOT", loc, w, col, aim=(0, 0, 170), size=20.0, spot=40.0, blend=0.6, group="deco", shadow=False)
    print("[modernart] built", flush=True)
