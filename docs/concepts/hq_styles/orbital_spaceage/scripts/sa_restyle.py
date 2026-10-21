"""Space-age retrofuturism (1955-70) restyle of the Orbital Commons HQ overview. Runs INSIDE Blender, after hq_scene.py has built its
scene and before it renders (sa_blender_hq.py inserts `apply(globals(), cfg)`). Nothing in the base pipeline is edited: base meshes are
culled in memory (rocket, dishes, crest, pad paint) and replaced; shared helpers come from the art-deco restyle module (read only).
Kept: silo crescent (podium, silo, door leaves, 5 dish stations, rocket, service gantry, truss antenna with its two rooms), the camera,
the fog / glow / city pipeline. Added: crossed parabolic launch arches, starburst deck, white needle rocket with fins, octagonal saucer
pods on Y pylons (TWA piers, Chemosphere pod), a Space Needle saucer on the antenna with guy cables, orange / white gantry, rocket
spotlights from the platform edge. Seeded: random.Random(seed)."""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "art_deco", "scripts")))
sys.dont_write_bytecode = True
import deco_restyle as D  # noqa: E402  (read only: DAcc, principled, emission, lacquer_facade, fog, recolor_attr)

ICE = (0.61, 0.87, 1.0)
ORANGE = (1.0, 0.30, 0.02)


class SAcc(D.DAcc):
    def __init__(self, name, mat, coll, smooth=False):
        super().__init__(name, mat, coll)
        self.smooth = smooth

    def build(self):
        ob = super().build()
        if ob is not None and self.smooth:
            try:
                ob.data.shade_smooth()
            except Exception:
                for p in ob.data.polygons:
                    p.use_smooth = True
        return ob


# ------------------------------------------------------------------------------------------------ geometry helpers
def revolve(acc, cx, cy, prof, n=32, a0=0.0):
    """Lathe a (r, z) profile round the vertical axis at (cx, cy)."""
    for i in range(n):
        b0, b1 = a0 + 2 * math.pi * i / n, a0 + 2 * math.pi * (i + 1) / n
        for (r0, z0), (r1, z1) in zip(prof[:-1], prof[1:]):
            acc.face([(cx + r0 * math.cos(b0), cy + r0 * math.sin(b0), z0), (cx + r0 * math.cos(b1), cy + r0 * math.sin(b1), z0),
                      (cx + r1 * math.cos(b1), cy + r1 * math.sin(b1), z1), (cx + r1 * math.cos(b0), cy + r1 * math.sin(b0), z1)])


def annulus(acc, cx, cy, r0, r1, z, n=64, a0=0.0, a1=360.0):
    for i in range(n):
        b0, b1 = math.radians(a0 + (a1 - a0) * i / n), math.radians(a0 + (a1 - a0) * (i + 1) / n)
        acc.face([(cx + r0 * math.sin(b0), cy + r0 * math.cos(b0), z), (cx + r1 * math.sin(b0), cy + r1 * math.cos(b0), z),
                  (cx + r1 * math.sin(b1), cy + r1 * math.cos(b1), z), (cx + r0 * math.sin(b1), cy + r0 * math.cos(b1), z)])


def kite(acc, a, r0, r1, wmax, z, f=0.35):
    """A flat starburst ray (kite) pointing along azimuth a (deg, 0 = +y), widest at f of its length."""
    c, s = math.sin(math.radians(a)), math.cos(math.radians(a))      # (x, y) direction
    t = (s, -c)
    rm = r0 + (r1 - r0) * f
    pts = [(c * r0, s * r0), (c * rm + t[0] * wmax, s * rm + t[1] * wmax), (c * r1, s * r1), (c * rm - t[0] * wmax, s * rm - t[1] * wmax)]
    acc.face([(p[0], p[1], z) for p in pts])


def _perp(d):
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    return u, d.cross(u).normalized()


def cone_along(acc, p0, p1, r0, r1, n=14):
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    u, v = _perp(d)
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        q = [(p0 + (u * math.cos(a) + v * math.sin(a)) * r0) for a in (a0, a1)] + [(p1 + (u * math.cos(a) + v * math.sin(a)) * r1) for a in (a1, a0)]
        acc.face(q)
    return d


def cull(ob, pred):
    if ob is None:
        return 0
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    fs = [f for f in bm.faces if pred(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=fs, context="FACES")
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return len(fs)


def arch(acc_w, acc_n, u, L, H, z0, w0=2.0, w1=4.6, hh=2.8, n=44, ox=0.0, oy=0.0):
    """A parabolic arch in the vertical plane along horizontal direction u: z = z0 + H (1 - t^2), t in [-1, 1]."""
    pts = [(ox + u[0] * L * t, oy + u[1] * L * t, z0 + H * (1 - t * t)) for t in (-1 + 2.0 * i / n for i in range(n + 1))]
    for i in range(n):
        t = abs(-1 + 2.0 * (i + 0.5) / n)
        w = w0 + (w1 - w0) * t * t
        acc_w.bar(pts[i], pts[i + 1], w, hh)
        dz = -(hh * 0.5 + 0.35)
        acc_n.bar((pts[i][0], pts[i][1], pts[i][2] + dz), (pts[i + 1][0], pts[i + 1][1], pts[i + 1][2] + dz), 0.5, 0.3)
    return pts


# ------------------------------------------------------------------------------------------------ components
def saucer(ctx, cx, cy, z, R, th, n=8, band=True, under_orange=True):
    W, A, O, NE = ctx["white"], ctx["alu"], ctx["orange"], ctx["ice"]
    prof = [(0.0, z - 0.62 * th), (0.30 * R, z - 0.55 * th), (0.72 * R, z - 0.26 * th), (R, z - 0.04 * th)]
    revolve(O if under_orange else W, cx, cy, prof[:3], n=n)       # orange underside bowl (Space Needle accent)
    revolve(W, cx, cy, [prof[2], prof[3], (0.86 * R, z + 0.22 * th), (0.50 * R, z + 0.46 * th), (0.2 * R, z + 0.64 * th), (0.0, z + 0.70 * th)], n=n)
    if band:      # the glazed ring: an emissive band standing proud of the rim (framed windows)
        revolve(NE, cx, cy, [(0.985 * R, z - 0.10 * th), (1.035 * R, z - 0.02 * th), (1.035 * R, z + 0.10 * th), (0.97 * R, z + 0.2 * th)], n=n)
    revolve(A, cx, cy, [(R * 1.0, z - 0.10 * th), (R * 1.05, z - 0.04 * th), (R * 1.0, z + 0.0)], n=n)
    top = [(0.97 * R, z + 0.02 * th), (0.86 * R, z + 0.22 * th), (0.50 * R, z + 0.46 * th), (0.2 * R, z + 0.64 * th)]     # TWA skylight ribs
    for k in range(n):
        ak = 2 * math.pi * (k + 0.5) / n
        ca, sa = math.cos(ak), math.sin(ak)
        for (r0_, z0_), (r1_, z1_) in zip(top[:-1], top[1:]):
            ctx["hot"].bar((cx + ca * r0_, cy + sa * r0_, z0_ + 0.18), (cx + ca * r1_, cy + sa * r1_, z1_ + 0.18), 0.32, 0.22)
    revolve(ctx["oneon"], cx, cy, [(0.62 * R, z + 0.40 * th), (0.64 * R, z + 0.42 * th)], n=n * 3)


def pod(ctx, cx, cy, az_vec, z_top=11.0, R=15.5):
    """An octagonal saucer pod on a Y pylon (TWA piers, Chemosphere): a tapering column forking into two blades under the pod; a small
    radar cap replaces the dish."""
    W, A = ctx["white"], ctx["alu"]
    revolve(W, cx, cy, [(4.2, z_top), (2.6, z_top + 5.0), (1.9, z_top + 14.0)], n=10)
    t = Vector((-az_vec[1], az_vec[0], 0.0))
    za = z_top + 14.0
    for s in (-1, 1):
        cone_along(W, (cx, cy, za), (cx + t.x * s * 8.5, cy + t.y * s * 8.5, za + 9.0), 1.7, 0.9, n=6)
    zs = za + 11.0
    saucer(ctx, cx, cy, zs, R, 8.5, n=8)
    A.bar((cx, cy, zs + 5.5), (cx, cy, zs + 12.0), 0.5, 0.5)
    revolve(W, cx, cy, [(0.0, zs + 9.4), (3.3, zs + 10.4), (1.5, zs + 9.0)], n=14)   # radar cap
    ctx["hot"].box(cx - 0.4, cy - 0.4, zs + 12.0, cx + 0.4, cy + 0.4, zs + 13.0)
    return zs


def sputnik(ctx, cx, cy, z):
    A, W, NE = ctx["alu"], ctx["white"], ctx["hot"]
    revolve(W, cx, cy, [(0.0, z - 4.6), (3.2, z - 3.3), (4.6, z), (3.2, z + 3.3), (0.0, z + 4.6)], n=18)
    k = 22
    for i in range(k):
        yv = 1 - 2 * (i + 0.5) / k
        r = math.sqrt(1 - yv * yv)
        th = i * 2.399963
        d = Vector((r * math.cos(th), r * math.sin(th), yv))
        ln = 9.0 + (4.0 if i % 2 == 0 else 0.0)
        p0 = Vector((cx, cy, z)) + d * 4.0
        p1 = Vector((cx, cy, z)) + d * (4.0 + ln)
        A.bar(p0, p1, 0.32, 0.32)
        NE.box(p1.x - 0.5, p1.y - 0.5, p1.z - 0.5, p1.x + 0.5, p1.y + 0.5, p1.z + 0.5)


def rocket(ctx):
    """A classic needle: white body, tangent-ogive nose, black roll band and orange bands, ports, four swept fins, aluminium skirt."""
    W, A, O, B, NE = ctx["white"], ctx["alu"], ctx["orange"], ctx["black"], ctx["ice"]
    r0, zb, zn, L = 5.6, 0.0, 58.0, 42.0
    rho = (r0 * r0 + L * L) / (2 * r0)
    prof = [(0.0, zb), (r0 * 0.92, zb), (r0, zb + 4.0), (r0, zn)]
    for i in range(1, 15):
        x = L * i / 15
        prof.append((max(0.15, math.sqrt(rho * rho - x * x) + r0 - rho), zn + x))
    prof.append((0.0, zn + L))
    revolve(W, 0, 0, prof, n=40)
    revolve(A, 0, 0, [(r0 * 1.04, zb), (r0 * 1.06, zb + 7.0), (r0 * 0.7, zb + 9.5)], n=24)     # engine skirt
    revolve(B, 0, 0, [(r0 + 0.06, 30.0), (r0 + 0.06, 42.0)], n=40)                              # roll band
    revolve(O, 0, 0, [(r0 + 0.1, 43.0), (r0 + 0.1, 46.0)], n=40)
    revolve(O, 0, 0, [(r0 + 0.08, 18.0), (r0 + 0.08, 19.2)], n=40)
    revolve(O, 0, 0, [(r * 1.04, z) for r, z in prof[-4:]], n=40)
    for k in range(8):                                                                         # ports on the black band
        a = math.radians(k * 45.0 + 22.5)
        c, s = math.cos(a), math.sin(a)
        NE.prism([(-0.7, 0.0), (0.7, 0.0), (0.7, 2.2), (-0.7, 2.2)], (c * (r0 + 0.12), s * (r0 + 0.12), 35.0), (-s, c, 0), (0, 0, 1), (c, s, 0), 0.12)
    revolve(NE, 0, 0, [(r0 + 0.14, 48.5), (r0 + 0.14, 48.9)], n=40)
    for k in range(4):                                                                         # swept fins
        a = math.radians(45 + 90 * k)
        c, s = math.cos(a), math.sin(a)
        poly = [(r0 - 0.4, 3.0), (r0 + 11.0, -1.0), (r0 + 11.0, 4.0), (r0 + 1.0, 30.0)]
        W.prism([(p[0], p[1]) for p in poly], (0, 0, 0.0), (c, s, 0), (0, 0, 1), (-s, c, 0), 0.7)
        poly2 = [(r0 + 7.0, -1.0), (r0 + 11.0, -1.0), (r0 + 11.0, 4.0), (r0 + 6.6, 5.0)]
        O.prism([(p[0], p[1]) for p in poly2], (0, 0, 0.0), (c, s, 0), (0, 0, 1), (-s, c, 0), 0.8)


def gantry_arms(ctx, PH, gy):
    """Apollo-style swing arms: white box arms from the gantry to the rocket, orange tips."""
    W, O, NE = ctx["white"], ctx["orange"], ctx["ice"]
    for zz in (PH + 14.0, PH + 33.0, PH + 52.0):
        W.box(-1.3, -6.0, zz, 1.3, gy + 3.5, zz + 2.2)
        O.box(-1.5, -6.6, zz - 0.1, 1.5, -4.5, zz + 2.3)
        NE.box(-0.2, -4.5, zz + 2.2, 0.2, gy + 4.0, zz + 2.4)


def spot_post(ctx, g, name, az_deg, PH, PR, rocket_h, W):
    a = math.radians(az_deg)
    px, py = math.sin(a) * (PR - 2.5), math.cos(a) * (PR - 2.5)
    A, WH, NE = ctx["alu"], ctx["white"], ctx["hot"]
    revolve(WH, px, py, [(2.2, PH), (1.2, PH + 2.5), (0.9, PH + 3.4)], n=10)
    for k, (zt, spot, wat) in enumerate(((rocket_h * 0.28, 30.0, W * 0.8), (rocket_h * 0.78, 24.0, W))):
        lp = Vector((px, py, PH + 3.6 + 1.5 * k))
        aim = Vector((0.0, 0.0, PH + zt))
        d = (aim - lp).normalized()
        cone_along(A, lp, lp + d * 3.2, 1.0, 1.7, n=12)
        l0 = lp + d * 3.25
        u, v = _perp(d)
        NE.prism([(1.3 * math.cos(2 * math.pi * i / 12), 1.3 * math.sin(2 * math.pi * i / 12)) for i in range(12)], l0, u, v, d, 0.05)
        g["add_light"]("sa_spot_%s_%d" % (name, k), "SPOT", tuple(lp + d * 2.6), wat, (0.88, 0.94, 1.0), aim=tuple(aim), size=0.6, spot=spot,
                       blend=0.5, group="deco", shadow=True)


# ------------------------------------------------------------------------------------------------ entry
def apply(g, cfg):
    if cfg.get("off"):
        return
    CP = g["CP"]
    PR, PH, SR, RR = CP["podium_r"], CP["podium_h"], CP["silo_r"], CP["ring_r"]
    AN, RK = CP["antenna"], CP["rocket"]
    OBJ, G = g["OBJ"], g["G"]
    sc = bpy.context.scene
    coll = bpy.data.collections.new("spaceage")
    sc.collection.children.link(coll)

    # ---- materials
    ek = cfg.get("ice_k", 3.2)
    M_W = D.principled("sa_white", (0.82, 0.85, 0.90), 0.0, 0.20, coat=1.0, coat_rough=0.05, emit=(0.80, 0.88, 1.0), emit_k=cfg.get("white_emit", 0.22))
    M_A = D.principled("sa_alu", (0.80, 0.83, 0.88), 1.0, 0.30, emit=(0.8, 0.88, 1.0), emit_k=0.06)
    M_O = D.principled("sa_orange", (0.95, 0.17, 0.01), 0.0, 0.32, coat=0.6, emit=(1.0, 0.25, 0.02), emit_k=0.12)
    M_B = D.principled("sa_black", (0.012, 0.014, 0.02), 0.0, 0.15, coat=1.0)
    M_I = D.emission("sa_ice", ICE, ek)
    M_IH = D.emission("sa_ice_hot", (0.85, 0.95, 1.0), ek * 3.0)
    M_ON = D.emission("sa_orange_neon", ORANGE, 2.4)
    ctx = dict(white=SAcc("sa_white", M_W, coll, True), alu=SAcc("sa_alu", M_A, coll, True), orange=SAcc("sa_orange", M_O, coll, True),
               black=SAcc("sa_black", M_B, coll, True), ice=SAcc("sa_ice", M_I, coll), hot=SAcc("sa_hot", M_IH, coll),
               oneon=SAcc("sa_oneon", M_ON, coll), flat_w=SAcc("sa_flatw", M_W, coll), flat_o=SAcc("sa_flato", M_O, coll))

    # ---- city fill: dark, cool, steel-blue (the HQ wins)
    D.lacquer_facade(g["M_CITY"], gold=cfg.get("grid", (0.20, 0.30, 0.42)), dark=0.14, window_tint=cfg.get("win_tint", (0.62, 0.82, 1.0)),
                     win_boost=cfg.get("win_boost", 0.9), band_emit=0.15)
    D.brass_metal(g["M_CMETAL"], tint=(0.40, 0.50, 0.64), metal=0.8, rough=0.38)
    for k in ("city_sign", "city_neon"):
        if OBJ.get(k) is not None:
            OBJ[k].hide_render = True
    # civic (bunker walls, podium drum): white fibreglass; metal: brushed aluminium, red -> international orange
    for b in D.find_nodes(g["M_CIVIC"], "ShaderNodeBsdfPrincipled"):
        for lk in list(b.inputs["Base Color"].links):
            g["M_CIVIC"].node_tree.links.remove(lk)
        b.inputs["Base Color"].default_value = (0.80, 0.83, 0.88, 1.0)
        b.inputs["Roughness"].default_value = 0.22
        b.inputs["Coat Weight"].default_value = 1.0
        b.inputs["Coat Roughness"].default_value = 0.05
        b.inputs["Emission Color"].default_value = (0.8, 0.88, 1.0, 1.0)
        b.inputs["Emission Strength"].default_value = cfg.get("white_emit", 0.22)
    D.brass_metal(g["M_METAL"], tint=(0.85, 0.88, 0.95), metal=0.9, rough=0.34)

    def orangeify(c):
        if c[0] > 0.35 and c[1] < 0.15:
            return (1.0, 0.25, 0.02)
        return c
    D.recolor_attr(OBJ.get("metal"), orangeify)
    D.tune_fog(g, dict(fog_col=cfg.get("fog_col", (0.46, 0.60, 0.80))))
    D.fog_veil(g, dict(veil_k=cfg.get("veil_k", 0.0025), veil_z=(110.0, 300.0)))
    for ob, e0, grp in g["LIGHTS"]:
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = cfg.get("glow_col", (0.62, 0.80, 1.0))
    for ob, e0, grp in g["LIGHTS"]:
        print("[sa light]", ob.name, ob.data.type, round(e0), grp, tuple(round(x) for x in ob.location), flush=True)

    # ---- cull the base pieces being replaced
    for k, ob in list(OBJ.items()):
        if k.startswith("mv_rocket_") or k.startswith("band_"):
            cull(ob, lambda c: True)
    for k in ("mv_door_e_rough", "mv_door_w_rough"):
        cull(OBJ.get(k), lambda c: True)
    D.recolor_attr(OBJ.get("city_small"), lambda c: (0.55, 0.80, 1.0) if c[0] > c[2] * 1.3 else c)
    cull(OBJ.get("pad_paint"), lambda c: math.hypot(c.x, c.y) > SR + 3.0)
    for nid, a in G.STATION.items():
        v = G.az_vec(a)
        cx, cy = v[0] * (RR + 3.0), v[1] * (RR + 3.0)
        for k in ("civic", "metal", "trim", "small"):
            cull(OBJ.get(k), lambda c, cx=cx, cy=cy: c.z > 11.4 and math.hypot(c.x - cx, c.y - cy) < 17.0)
    # ---- the base lights that overlit the pad
    pk = cfg.get("pad_k", 0.35)
    for i, (ob, e0, grp) in enumerate(g["LIGHTS"]):
        if ob.name == "ant_red":
            g["LIGHTS"][i] = (ob, e0 * 0.2, grp)
            ob.data.energy = e0 * 0.2
        if ob.name.startswith(("pad_flood", "rocket_svc")):
            k_ = pk if ob.name.startswith("pad_flood") else 0.2
            g["LIGHTS"][i] = (ob, e0 * k_, grp)
            ob.data.energy = e0 * k_

    W, A, O, B, NE, HOT, ON = ctx["white"], ctx["alu"], ctx["orange"], ctx["black"], ctx["ice"], ctx["hot"], ctx["oneon"]
    FW, FO = ctx["flat_w"], ctx["flat_o"]

    # ---- the platform: starburst deck (kite rays, atomic nodes), rings
    z = PH + 0.12
    nr = 24
    for i in range(nr):
        a = i * 360.0 / nr
        if i % 2 == 0:
            kite(NE, a, SR + 4.5, PR - 4.0, 1.5, z, 0.22)
            kite(FW, a, SR + 4.5, PR - 14.0, 3.6, z - 0.04, 0.22)
        else:
            kite(FO, a, SR + 5.0, PR - 24.0, 2.6, z - 0.03, 0.30)
            kite(NE, a, SR + 8.0, PR - 27.0, 0.7, z + 0.01, 0.4)
    for i in range(12):                                  # atomic star nodes on the rim
        a = math.radians(i * 30.0 + 15.0)
        x, y = math.sin(a) * (PR - 6.5), math.cos(a) * (PR - 6.5)
        for q in range(8):
            ln = 2.6 if q % 2 == 0 else 1.5
            cs, sn = math.cos(math.radians(q * 45.0)), math.sin(math.radians(q * 45.0))
            tx_, ty_ = -sn, cs
            HOT.face([(x, y, z + 0.03), (x + cs * ln * 0.3 + tx_ * 0.22, y + sn * ln * 0.3 + ty_ * 0.22, z + 0.03),
                      (x + cs * ln, y + sn * ln, z + 0.03), (x + cs * ln * 0.3 - tx_ * 0.22, y + sn * ln * 0.3 - ty_ * 0.22, z + 0.03)])
    annulus(NE, 0, 0, SR + 3.0, SR + 3.5, z + 0.02, n=96)
    annulus(NE, 0, 0, PR - 3.6, PR - 3.0, z + 0.02, n=120)
    annulus(ON, 0, 0, PR - 15.0, PR - 14.5, z + 0.02, n=120)
    revolve(A, 0, 0, [(SR + 0.2, PH), (SR + 1.4, PH + 0.1), (SR + 1.4, PH + 1.1), (SR + 0.2, PH + 1.1)], n=48)
    revolve(W, 0, 0, [(PR + 0.2, PH - 1.8), (PR + 1.8, PH - 0.9), (PR + 1.8, PH + 0.5), (PR - 0.2, PH + 0.5)], n=120)
    annulus(NE, 0, 0, PR + 1.5, PR + 1.9, PH + 0.55, n=120)

    # ---- crossed parabolic launch arches (LAX Theme Building, Saarinen) with footings
    Harch = cfg.get("arch_h", 94.0)
    cam_az = math.radians(cfg.get("arch_az", 150.0))
    u = (math.sin(cam_az), math.cos(cam_az))
    nrm = (u[1], -u[0])
    La, off = cfg.get("arch_L", 50.0), cfg.get("arch_off", 31.0)
    for sd in (-1, 1):
        ox, oy = nrm[0] * off * sd, nrm[1] * off * sd
        arch(W, NE, u, La, Harch, PH, w0=cfg.get("arch_w0", 2.6), w1=cfg.get("arch_w1", 5.6), hh=3.2, ox=ox, oy=oy)
        for s in (-1, 1):
            fx, fy = ox + u[0] * s * La, oy + u[1] * s * La
            revolve(W, fx, fy, [(6.5, PH), (5.0, PH + 3.0), (3.4, PH + 6.5)], n=8)
            revolve(A, fx, fy, [(7.0, PH), (7.0, PH + 0.8)], n=8)

    # ---- the rocket (white needle) + swing arms; the silo stays open under it
    rocket(ctx)
    for k in range(8):                                   # LC-39 mobile-launcher pedestals: white posts with orange caps round the silo mouth
        a_ = math.radians(22.5 + 45.0 * k)
        px_, py_ = math.sin(a_) * (SR + 5.0), math.cos(a_) * (SR + 5.0)
        revolve(W, px_, py_, [(2.0, PH), (1.4, PH + 3.2)], n=6)
        revolve(O, px_, py_, [(1.6, PH + 3.2), (1.6, PH + 4.0)], n=6)
    gantry_arms(ctx, PH, CP["control"]["y"])

    # ---- rocket spotlights from the platform edge
    rh = RK["h"] + 36.0
    for i, az in enumerate((0.0, 90.0, 180.0, 270.0)):
        spot_post(ctx, g, "p%d" % i, az, PH, PR, rh, cfg.get("spot_w", 1.2e6))

    # ---- stations: octagonal saucer pods on Y pylons (the PAD bunker gets the atomic starburst)
    for nid, a in sorted(G.STATION.items()):
        v = G.az_vec(a)
        cx, cy = v[0] * (RR + 3.0), v[1] * (RR + 3.0)
        if nid == "start":
            revolve(W, cx, cy, [(3.6, 11.0), (2.0, 16.0), (1.6, 22.0)], n=10)
            sputnik(ctx, cx, cy, 30.0)
        else:
            pod(ctx, cx, cy, v)
        annulus(NE, cx, cy, 14.0, 14.7, 0.35, n=48)

    # ---- the antenna: Space Needle saucer + guy cables (Ostankino)
    av = G.az_vec(AN["az"])
    tx, ty = av[0] * AN["r"], av[1] * AN["r"]
    saucer(ctx, tx, ty, 94.0, 19.0, 6.5, n=24)
    revolve(W, tx, ty, [(6.5, 78.0), (9.0, 82.0), (13.0, 88.5)], n=12)             # the hourglass flare under the saucer
    for k in range(3):
        a = math.radians(30 + 120 * k)
        p = (tx + math.cos(a) * 42.0, ty + math.sin(a) * 42.0, 0.2)
        A.bar(p, (tx, ty, AN["h"] + 12.0), 0.35, 0.35)
        revolve(W, p[0], p[1], [(2.4, 0.0), (1.5, 1.6)], n=8)
    HOT.box(tx - 0.7, ty - 0.7, AN["h"] + 26.0, tx + 0.7, ty + 0.7, AN["h"] + 27.4)

    for k in ctx:
        ctx[k].build()
    print("[sa] faces", {k: len(ctx[k].f) for k in ctx}, flush=True)
