"""Art Nouveau restyle of the Solace HQ overview (single-HQ style exploration). Runs INSIDE Blender, hooked in front of the
render section of the base hq_scene.py (nouveau_blender_hq.py). Helpers (accumulators, facade shader, fog) come from the
art-deco pass's deco_restyle.py, imported read-only.

Vocabulary: whiplash vines winding the strands, curled tendril ends, leaded stained-glass rosettes in the oval windows,
dark bronze + verdigris cast iron, Guimard metro lamps round the plaza, dragonfly-wing crown, domed organic tower caps,
cool teal-black city fill with a green-grey mist. All randomness seeded.
"""
import math
import random

import bpy
from mathutils import Vector

import deco_restyle as D

LIME = (0.30, 1.0, 0.06)
PINK = (1.0, 0.05, 0.30)
BRONZE = (0.10, 0.09, 0.04)
VERD = (0.06, 0.40, 0.28)
TEAL = (0.10, 0.80, 0.62)


# ------------------------------------------------------------------------------------------------- geometry helpers
def tube(acc, pts, r, sides=5, r_end=None):
    """A round-ish tube (n-gon section) along a polyline; radius tapers to r_end if given."""
    n = len(pts)
    if n < 2:
        return
    P = [Vector(p) for p in pts]
    rings = []
    prev_n = None
    for i in range(n):
        d = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)])
        if d.length < 1e-6:
            d = Vector((0, 0, 1))
        d.normalize()
        ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        a = d.cross(ref).normalized()
        b = d.cross(a).normalized()
        rr = r if r_end is None else r + (r_end - r) * i / (n - 1)
        rings.append([P[i] + (a * math.cos(2 * math.pi * k / sides) + b * math.sin(2 * math.pi * k / sides)) * rr
                      for k in range(sides)])
    for i in range(n - 1):
        for k in range(sides):
            k2 = (k + 1) % sides
            acc.face([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]])
    acc.face(list(reversed(rings[0])))
    acc.face(rings[-1])


def blob(acc, c, r, sides=6):
    """A small bead / bulb (octahedron-ish ball): two stacked rings."""
    c = Vector(c)
    ring = lambda z, rr: [c + Vector((math.cos(2 * math.pi * k / sides) * rr, math.sin(2 * math.pi * k / sides) * rr, z)) for k in range(sides)]
    zs = [(-r, 0.0), (-r * 0.55, r * 0.85), (r * 0.55, r * 0.85), (r, 0.0)]
    rs = [ring(z, rr) for z, rr in zs]
    for i in range(3):
        for k in range(sides):
            k2 = (k + 1) % sides
            acc.face([rs[i][k], rs[i][k2], rs[i + 1][k2], rs[i + 1][k]])
    acc.face(list(reversed(rs[0])))
    acc.face(rs[3])


def spiral_curl(p0, tan, up, r0, turns=1.25, n=14):
    """Coil: starts at p0 heading along `tan`, curling toward `up` with radius shrinking r0 -> r0*0.15."""
    pts = []
    tan, up = Vector(tan).normalized(), Vector(up).normalized()
    for i in range(n + 1):
        s = i / n
        a = s * turns * 2 * math.pi
        r = r0 * (1.0 - 0.85 * s)
        pts.append(Vector(p0) + tan * (math.sin(a) * r) + up * ((1 - math.cos(a)) * r))
    return pts


def leaf(acc, base, direction, up, length, width, th=0.18):
    """A pointed leaf blade (flat prism) from base along direction, width across `up`... both unit-ish vectors."""
    base, d, u = Vector(base), Vector(direction).normalized(), Vector(up).normalized()
    n = d.cross(u).normalized()
    poly = []
    m = 8
    for i in range(m + 1):
        s = i / m
        w = width * math.sin(math.pi * s ** 0.8) * 0.5
        poly.append((s * length, w))
    for i in range(m, -1, -1):
        s = i / m
        w = width * math.sin(math.pi * s ** 0.8) * 0.5
        poly.append((s * length, -w))
    poly = poly[:m + 1] + poly[m + 2:-1]
    acc.prism(poly, base, d, u, n, th)


# ------------------------------------------------------------------------------------------------- helix
def helix(g, cfg, ctx):
    GR, CP = g["G"], g["CP"]
    RT, FH, PH = GR.RT, GR.FH, GR.PODIUM_H
    floors = CP["floors"]
    ztop = PH + floors * FH
    br, vd, lime, pink, teal = ctx["bronze"], ctx["verd"], ctx["lime"], ctx["pink"], ctx["teal"]
    rng = random.Random(77)
    # wavy floor ribs: each floor a verdigris ring that ripples up and down (whiplash), double on route floors
    for t in ("A", "B"):
        for f in range(1, floors + 1):
            route = f in CP["route_floors"]
            z0 = PH + f * FH - 0.4
            for dz0, rad, acc in ((0.0, 0.85 if not route else 1.4, vd),) + (((2.2, 0.6, br),) if route else ()):
                pts = [GR.tube_pt(t, z0 + dz0 + 0.9 * math.sin(3 * (2 * math.pi * j / 36) + f), 2 * math.pi * j / 36, RT + 0.5)
                       for j in range(37)]
                tube(acc, pts, rad, 5)
        # two whiplash vines wind the strand, opposite phase, with leaf sprays and curled tendril ends
        for vi, (ph0, wd) in enumerate(((0.9, 1.0), (-0.9, -1.0))):
            pts = []
            nz = int((ztop - PH) / 1.6)
            for i in range(nz + 1):
                z = PH + 1.0 + i * 1.6
                ph = ph0 + 0.95 * math.sin(z * 0.115 + vi * 2.4 + (0 if t == "A" else 1.1)) + 0.25 * math.sin(z * 0.43)
                pts.append(GR.tube_pt(t, z, ph, RT + 0.75 + 0.4 * math.sin(z * 0.2)))
            # thick bronze vine, tapering a little at the top
            tube(br, pts, 0.95, 5, 0.6)
            tube(lime if t == "A" else pink, [Vector(p) + Vector((0, 0, 0.5)) for p in pts], 0.22, 4)
            # leaf sprays and curls every ~14 units
            for i in range(6, nz - 4, 9):
                z = PH + 1.0 + i * 1.6
                p = Vector(pts[i])
                tg = (Vector(pts[i + 1]) - Vector(pts[i - 1])).normalized()
                c, rv, n = GR.tower_frame(t, (z - PH) / FH)
                outv = (p - Vector((c[0], c[1], p.z)))
                outv.z = 0
                if outv.length < 1e-3:
                    continue
                outv.normalize()
                side = Vector(tg).cross(outv).normalized() * (1 if rng.random() < 0.5 else -1)
                lp = p + outv * 0.2
                # tendril stem then a coil
                stem = [lp, lp + side * 2.2 + outv * 0.5 + Vector((0, 0, 1.5)), lp + side * 3.8 + outv * 0.9 + Vector((0, 0, 1.0))]
                tube(vd, stem, 0.28, 4)
                coil = spiral_curl(stem[-1], side + Vector((0, 0, 0.3)), Vector((0, 0, 1)) * 1.0 - side * 0.3, 2.0)
                tube(vd, coil, 0.24, 4, 0.1)
                # a leaf pair
                for sg in (1, -1):
                    ld = (tg * (0.8 * sg) + outv * 0.5 + side * 0.3 * sg).normalized()
                    leaf(vd, lp + outv * 0.2, ld, outv.cross(ld).normalized(), 5.0, 2.0, 0.22)
                    leaf(lime, lp + outv * 0.45, ld, outv.cross(ld).normalized(), 3.6, 1.0, 0.1)
                # glowing berry at the coil's heart
                blob(lime if t == "A" else pink, coil[-1], 1.1)
    # window rosettes: leaded stained-glass (bronze ring, came bars, alternate glowing petals) in every route oval
    for f in CP["route_floors"]:
        for t in ("A", "B"):
            for side in ("in", "out"):
                fr = GR.win_frame(t, f, side)
                def P(s, k, n=48, lift=0.45):
                    a = 2 * math.pi * k / n
                    u, dz = GR.WAX * math.cos(a) * s, GR.WB * math.sin(a) * s
                    return GR.win_pt(fr, u, dz, GR.skin_depth(fr, u, dz) + lift)
                n = 48
                for s, rad, acc in ((1.04, 0.9, br), (0.60, 0.35, br), (0.32, 0.28, br)):
                    tube(acc, [P(s, k % n) for k in range(n + 1)], rad, 4)
                # radial came bars
                nr = 12
                for r_ in range(nr):
                    k = int(r_ * n / nr)
                    tube(br, [P(0.30, k, lift=0.5), P(1.0, k, lift=0.5)], 0.14, 4)
                # glowing petals: alternate sectors between rings 0.34..0.58, plus lens at heart
                for r_ in range(nr):
                    if r_ % 2:
                        continue
                    k0, k1 = int(r_ * n / nr) + 1, int((r_ + 1) * n / nr) - 1
                    acc = (lime if t == "A" else pink)
                    for k in range(k0, k1):
                        acc.face([P(0.36, k, lift=0.3), P(0.58, k, lift=0.3), P(0.58, k + 1, lift=0.3), P(0.36, k + 1, lift=0.3)])
                    for k in range(k0, k1):
                        teal.face([P(0.64, k, lift=0.3), P(0.96, k, lift=0.3), P(0.96, k + 1, lift=0.3), P(0.64, k + 1, lift=0.3)])
                # finials: curled whiplash from the oval's top and bottom
                for sg in (1, -1):
                    base = Vector(GR.win_pt(fr, 0.0, sg * GR.WB * 1.06, GR.skin_depth(fr, 0.0, sg * GR.WB) + 0.5))
                    upv = Vector((0, 0, sg))
                    tg_ = Vector((fr["tw"][0], fr["tw"][1], 0))
                    cur = spiral_curl(base + upv * 0.3, tg_, upv, 2.2, turns=1.1)
                    tube(vd, cur, 0.26, 4, 0.1)
                    blob(lime, cur[-1], 0.45)
    # skybridges: Guimard arch hoops over the walkway and two sagging vine rails
    for f in CP["route_floors"]:
        O, e, q, half = GR.bridge_frame(f)
        z0 = GR.deck_z(f)
        ev, qv = Vector((e[0], e[1], 0)), Vector((q[0], q[1], 0))
        for sg in (1, -1):
            rail = []
            for i in range(25):
                s = -half + 2 * half * i / 24
                rail.append(Vector((O[0], O[1], z0)) + ev * s + qv * (sg * 1.6) + Vector((0, 0, 2.6 + 0.8 * math.sin(s * 0.9))))
            tube(vd, rail, 0.22, 4)
        for i in range(1, 8):
            s = -half + 2 * half * i / 8
            hp = []
            for j in range(13):
                a = math.pi * j / 12
                hp.append(Vector((O[0], O[1], z0)) + ev * s + qv * (1.9 * math.cos(a)) + Vector((0, 0, 0.3 + 3.6 * math.sin(a))))
            tube(br, hp, 0.17, 4)
            blob(lime, hp[6] + Vector((0, 0, 0.5)), 0.28)
    # crown: dragonfly wings (four pointed lobes, glowing stained-glass cells) and a bud dome
    cz = ztop - 1.0
    for ai, ang in enumerate((0.0, 90.0)):
        a = math.radians(ang + 20)
        ax = Vector((math.cos(a), math.sin(a), 0))
        for sg in (1, -1):
            outline = []
            Wn = 22
            for j in range(Wn + 1):
                s = j / Wn
                x = sg * (4 + 34 * math.sin(math.pi * s ** 0.85) * 0.5 + 18 * s)
                zz = 3.0 + 32 * s * (1 - 0.15 * s) - 4 * math.sin(math.pi * s)
                x = sg * (3.0 + 30 * math.sin(math.pi * min(1, s * 1.1) ** 1.2) * (1 - 0.4 * s))
                outline.append(Vector((0, 0, cz)) + ax * x + Vector((0, 0, zz)))
            back = [Vector((0, 0, cz)) + ax * (sg * (3.0 + 9 * math.sin(math.pi * (j / Wn)))) + Vector((0, 0, 3.0 + 32 * j / Wn * 0.35)) for j in range(Wn + 1)]
            # wing = lens between the outer curve and the body; veins radiate; glow cells between veins
            body = [Vector((0, 0, cz)) + ax * sg * 2.4 + Vector((0, 0, 2.0 + 26 * j / Wn * 0.75)) for j in range(Wn + 1)]
            tube(br, outline, 0.55, 5)
            tube(vd, body, 0.45, 5)
            for j in range(2, Wn - 1, 3):
                tube(vd, [body[j], outline[min(Wn, j + 2)]], 0.2, 4)
            for j in range(2, Wn - 4, 3):
                pk = lime if ((j // 3) + ai) % 2 == 0 else pink
                pk.face([body[j], outline[j + 2], outline[j + 5], body[j + 3]])
                pk.face(list(reversed([body[j], outline[j + 2], outline[j + 5], body[j + 3]])))
    # bud dome over the genome core: eight arched ribs and a glowing heart
    for k in range(8):
        a = 2 * math.pi * k / 8
        pts = []
        for j in range(13):
            b = math.pi * 0.5 * j / 12
            rr = 11 * math.cos(b)
            pts.append(Vector((math.cos(a) * rr, math.sin(a) * rr, cz + 3.0 + 13 * math.sin(b) ** 1.2)))
        tube(vd, pts, 0.45, 5, 0.25)
    blob(pink, (0, 0, cz + 7.5), 6.0, 8)
    # Mucha halo: concentric leaded rings behind the crown, in the plane facing the overview camera, with iridescent beads
    ha = math.radians(20)
    hx_, hy_ = Vector((math.cos(ha), math.sin(ha), 0)), Vector((0, 0, 1))
    hc = Vector((0, 0, cz + 20))
    for rr, rad, acc in ((30.0, 0.5, br), (27.0, 0.28, vd), (22.0, 0.22, ctx["teal"])):
        tube(acc, [hc + hx_ * (rr * math.cos(2 * math.pi * j / 64)) + hy_ * (rr * math.sin(2 * math.pi * j / 64)) for j in range(65)], rad, 5)
    for j in range(24):
        a = 2 * math.pi * j / 24
        blob(ctx["teal"], hc + hx_ * (28.5 * math.cos(a)) + hy_ * (28.5 * math.sin(a)), 0.8)
    # Sagrada Familia branching: slender twin-twist columns fork from the dome into a canopy of leaf tips
    for k in range(6):
        a = 2 * math.pi * k / 6
        base = Vector((math.cos(a) * 3.0, math.sin(a) * 3.0, cz + 14))
        for sgn in (1, -1):
            pts = []
            for j in range(12):
                s = j / 11
                pts.append(base + Vector((math.cos(a + sgn * s * 1.2) * 12 * s, math.sin(a + sgn * s * 1.2) * 12 * s, 24 * s - 6 * s * s)))
            tube(vd, pts, 0.32, 4, 0.12)
            blob(lime if sgn > 0 else pink, pts[-1], 0.7)
    tube(br, [Vector((0, 0, cz + 17)), Vector((0.8, 0.0, cz + 28)), Vector((-0.8, 0, cz + 38)), Vector((1.5, 0, cz + 46))], 0.35, 5, 0.1)
    blob(lime, (1.5, 0, cz + 47), 0.9)


# ------------------------------------------------------------------------------------------------- plaza
def plaza(g, cfg, ctx):
    GR, CP = g["G"], g["CP"]
    px, py, ph = CP["podium"]
    br, vd, lime, teal = ctx["bronze"], ctx["verd"], ctx["lime"], ctx["teal"]
    # scalloped terraces: three superellipse steps, verdigris with a lime glow lip
    for i in range(3):
        s = 1.0 + 0.045 * (3 - i)
        z0 = ph + i * 0.9
        pts = []
        for j in range(97):
            a = 2 * math.pi * j / 96
            ca, sa = math.cos(a), math.sin(a)
            x = px * s * math.copysign(abs(ca) ** 0.35, ca) * 0.98 + 0
            y = py * s * math.copysign(abs(sa) ** 0.35, sa) * 0.98
            x += 2.5 * math.sin(a * 12)  # scallops
            pts.append((x, y, z0 + 0.5))
        tube(vd, pts, 0.9 + 0.2 * i, 5)
        tube(lime, [(p[0] * 0.99, p[1] * 0.99, p[2] + 0.4) for p in pts], 0.2, 4)
    # Guimard lamps: stalks that arch over and hang a glowing orb, a ring of them
    rng = random.Random(5)
    n = 18
    for k in range(n):
        a = 2 * math.pi * k / n
        ca, sa = math.cos(a), math.sin(a)
        x = px * 1.02 * math.copysign(abs(ca) ** 0.35, ca)
        y = py * 1.02 * math.copysign(abs(sa) ** 0.35, sa)
        ov = Vector((ca, sa, 0)).normalized()
        base = Vector((x, y, ph + 0.5))
        pts = []
        for j in range(17):
            s = j / 16
            pts.append(base + ov * (-6.0 * math.sin(s * 1.6) ** 1.5) + Vector((0, 0, 24 * math.sin(s * 1.45) ** 0.8)))
        tube(vd, pts, 0.7, 5, 0.3)
        # leaf wings under the orb
        tip = pts[-1]
        for sg in (1, -1):
            side = ov.cross(Vector((0, 0, 1))) * sg
            leaf(vd, tip - Vector((0, 0, 0.5)), side + Vector((0, 0, -0.3)), ov, 6.0, 2.2, 0.2)
        blob(lime if k % 3 else ctx["pink"], tip - Vector((0, 0, 3.2)) + ov * 0.3, 2.4, 8)
        tube(br, [tip, tip - Vector((0, 0, 1.0))], 0.25, 4)


# ------------------------------------------------------------------------------------------------- towers
def tower_cap(ctx, x, y, top, hx, hy, rng, big):
    br, vd, lime, teal = ctx["bronze"], ctx["verd"], ctx["lime"], ctx["teal"]
    r = max(hx, hy) * 1.25
    # a squat onion dome of arched ribs on a verdigris collar, a whiplash spire with a lime bud
    tube(vd, [(x + math.cos(2 * math.pi * j / 16) * r, y + math.sin(2 * math.pi * j / 16) * r, top + 0.6) for j in range(17)], 0.55, 5)
    nrib = 6
    for k in range(nrib):
        a = 2 * math.pi * k / nrib + rng.random() * 0.2
        pts = []
        for j in range(11):
            b = math.pi * 0.5 * j / 10
            rr = r * (math.cos(b) * (1 + 0.35 * math.sin(2 * b)))
            pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, top + 0.6 + r * 1.35 * math.sin(b) ** 1.1))
        tube(vd, pts, 0.35, 4, 0.18)
    # glowing core: a lime fan behind the ribs
    blob(ctx["cap"], (x, y, top + r * 0.5), r * 0.3, 6)
    H = r * (2.2 + rng.random())
    sp = [Vector((x, y, top + r * 1.3)), Vector((x + 0.5, y, top + r * 1.3 + H * 0.4)), Vector((x - 0.6, y, top + r * 1.3 + H * 0.75)),
          Vector((x + 0.8, y + 0.3, top + r * 1.3 + H))]
    tube(br, sp, 0.3, 4, 0.1)
    blob(ctx["cap"], sp[-1], 0.7)
    if big:
        # pierced vine ribs down the corners
        for cx_ in (-1, 1):
            for cy_ in (-1, 1):
                pts = [(x + cx_ * hx + 0.5 * cx_ * math.sin(z * 0.5), y + cy_ * hy + 0.5 * cy_ * math.cos(z * 0.5), top - 24 + z) for z in range(0, 25, 2)]
                tube(vd, pts, 0.22, 4)


def towers(g, cfg, ctx):
    fr = g["JOB"]["frames"][0]
    tw = D.select_towers(g, fr["pose"], cfg.get("n_towers", 150), cfg.get("min_top", 30.0), lm_box=cfg.get("lm_box"),
                         max_top=cfg.get("max_top", 380.0), pick="near", min_cam_k=0.8)
    for k, (x, y, top, hx, hy, bi) in enumerate(tw):
        tower_cap(ctx, x, y, top, hx, hy, random.Random(1000 + bi), k < 40)
    ctx["towers"] = tw
    return tw


# ------------------------------------------------------------------------------------------------- entry
def apply(g, cfg):
    if cfg.get("off"):
        return
    sc = bpy.context.scene
    coll = bpy.data.collections.new("nouveau")
    sc.collection.children.link(coll)
    M = D.Mats()
    kk = cfg.get("glow_k", 1.0)
    mats = dict(
        bronze=D.principled("nv_bronze", BRONZE, 1.0, 0.36, emit=(0.5, 0.25, 0.1), emit_k=0.05),
        verd=D.principled("nv_verdigris", VERD, 0.85, 0.42, emit=TEAL, emit_k=0.10),
        lime=D.emission("nv_lime", LIME, 5.0 * kk),
        pink=D.emission("nv_pink", PINK, 4.5 * kk),
        teal=irid("nv_irid", 3.2 * kk),
        cap=irid("nv_cap", 0.9 * kk),
    )
    ctx = {k: D.DAcc("nv_" + k, v, coll) for k, v in mats.items()}
    # city fill: black-teal lacquer, verdigris mullions, cool pale-green windows
    D.lacquer_facade(g["M_CITY"], gold=(0.03, 0.20, 0.17), dark=cfg.get("dark", 0.14), window_tint=cfg.get("win_tint", (0.45, 0.85, 1.0)),
                     band_emit=0.25, win_boost=cfg.get("win_boost", 2.8))
    D.lacquer_panels(g["M_CIVIC"], gold=(0.05, 0.30, 0.22), dark=0.2)
    for k in ("M_METAL", "M_CMETAL"):
        if k in g:
            D.brass_metal(g[k], tint=(0.18, 0.40, 0.32), rough=0.4)
    OBJ = g["OBJ"]
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
            ob.data.color = cfg.get("glow_col", (0.45, 0.85, 0.80))
        elif grp in ("civic", "city", "start") and ob.data.type in ("SPOT", "POINT", "AREA"):
            c = ob.data.color
            if c[0] > c[2]:      # warm -> cool leaf light
                ob.data.color = cfg.get("cool_col", (0.55, 1.0, 0.75))
    towers(g, cfg, ctx)
    helix(g, cfg, ctx)
    plaza(g, cfg, ctx)
    for k, a in ctx.items():
        if isinstance(a, D.DAcc):
            a.build()
    print("[nouveau] faces", {k: len(a.f) for k, a in ctx.items() if isinstance(a, D.DAcc)}, flush=True)


def irid(name, k):
    """Favrile / plique-a-jour glass: emission whose hue drifts teal -> violet -> lime with height and a slow noise."""
    m, nt = D._mat(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = k
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sp.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.08
    nt.links.new(geo.outputs["Position"], nz.inputs["Vector"])
    f = D._math(nt, "ADD", D._math(nt, "MULTIPLY", sp.outputs["Z"], 0.012), D._math(nt, "MULTIPLY", nz.outputs["Fac"], 0.8))
    f = D._math(nt, "PINGPONG", f, 1.0)
    cr = nt.nodes.new("ShaderNodeValToRGB")
    els = cr.color_ramp.elements
    els[0].position, els[0].color = 0.0, (0.05, 0.70, 0.55, 1)
    els[1].position, els[1].color = 1.0, (0.35, 1.0, 0.10, 1)
    mid = els.new(0.5)
    mid.color = (0.45, 0.25, 0.95, 1)
    nt.links.new(f, cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], e.inputs["Color"])
    nt.links.new(e.outputs[0], out.inputs[0])
    return m
