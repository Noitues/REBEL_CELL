"""R2A LOW-POLY 3D: still 05, the black-market shop. A faceted stall, a hooded fixer, goods with price tags.

blender -b --factory-startup --python still_shop.py -- <out.png> [scale%]
"""
import os
import sys
import math
import random
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp_lib as L
import hud as H
import ui3d as U

CARDS = [("atk", "RAZOR SPIKE", 2, "Deal 7 damage", "blade", "140"),
         ("hack", "GHOST KEY", 1, "Skip enemy slice", "eye", "95"),
         ("def", "MIRROR ICE", 2, "Reflect 3", "shield", "120")]
PARTS = [("SLICE: CRIT x2", "wedge", "#f0b44a", "180"),
         ("POINTER: HOOK", "pointer", "#39e0ff", "150"),
         ("HUB: OVERDRIVE", "hub", "#ff3f7a", "260")]


def main():
    a = L.args()
    out = a[0]
    pct = int(a[1]) if len(a) > 1 else 100
    sc = L.reset()
    L.setup_render(sc, samples=64 if pct == 100 else 16)
    sc.render.resolution_percentage = pct
    L.world(sc, "#3a2838", 0.6)
    L.sun("key", (50, 0, -28), "#ffd9b0", 3.0, angle=10)
    L.sun("rim", (60, 0, 150), "#b86cff", 0.6, angle=20, shadow=False)
    rng = random.Random(505)
    _room(rng)
    _fixer()
    _counter(rng)
    cam = L.camera("cam", (0.0, -16.5, 5.0), (0.0, 0.0, 3.75), lens=34.0)
    bpy.context.view_layer.update()
    _goods(rng)
    _hud(cam)
    L.compositor(sc, bloom=(0.9, 0.5, 7))
    L.render(sc, out)


def _room(rng):
    wall = [L.mat_flat("wall_a", "#7b5a6c"), L.mat_flat("wall_b", "#6a4c60"), L.mat_flat("wall_c", "#8c6a74"),
            L.mat_flat("floor_a", "#4a3848"), L.mat_flat("floor_b", "#3e3040"), L.mat_flat("metal", "#524a58"),
            L.mat_flat("crate_a", "#a88468"), L.mat_flat("crate_b", "#8c6c5a"),
            L.mat_flat("neon_c", "#35e6ff", emit="#35e6ff", emit_str=8.0),
            L.mat_flat("neon_a", "#ffb040", emit="#ffb040", emit_str=6.0)]
    pb = L.PB()
    # corrugated back wall: vertical strips folded in and out -> alternating facet tones
    y = 4.0
    xs = [-13 + k * 0.8 for k in range(34)]
    for k in range(len(xs) - 1):
        x0, x1 = xs[k], xs[k + 1]
        d0 = 0.0 if k % 2 == 0 else 0.22
        d1 = 0.22 if k % 2 == 0 else 0.0
        a = pb.vert((x0, y + d0, 0), 0.0)
        b = pb.vert((x1, y + d1, 0), 0.0)
        c = pb.vert((x1, y + d1, 5.2), 0.03)
        d = pb.vert((x0, y + d0, 5.2), 0.03)
        pb.face([a, b, c, d][::-1], 0 if k % 2 else 1)
        e = pb.vert((x1, y + d1, 11), 0.0)
        f = pb.vert((x0, y + d0, 11), 0.0)
        pb.face([d, c, e, f][::-1], 2 if k % 2 else 0)
    # floor: faceted tiles
    for i in range(-8, 8):
        for j in range(-6, 3):
            x0, y0 = i * 1.6, j * 1.6
            pts = [(x0, y0), (x0 + 1.6, y0), (x0 + 1.6, y0 + 1.6), (x0, y0 + 1.6)]
            ids = [pb.vert((px, py, 0.0), 0.0) for px, py in pts]
            cc = pb.vert((x0 + 0.8, y0 + 0.8, rng.uniform(0.0, 0.05)), 0.0)
            for k in range(4):
                pb.face([ids[k], ids[(k + 1) % 4], cc], 3 + ((i + j + k) % 2))
    # shelves with crates left and right of the fixer
    for sx in (-7.2, 5.2):
        for z in (4.6, 6.6):
            pb.prism(L.rect(3.4, 0.9), z - 0.12, z, 5, 5, cx=sx + 1.0, cy=3.6)
            xx = sx
            while xx < sx + 2.6:
                w = rng.uniform(0.5, 0.9)
                h = rng.uniform(0.4, 0.9)
                pb.prism(L.rect(w, 0.7), z, z + h, 6 + rng.randrange(2), 7, cx=xx + w / 2, cy=3.6, jit=0.03,
                         top_center_dz=rng.choice((0.0, 0.1)))
                xx += w + 0.08
    # neon tubes on the wall
    pb.prism(L.rect(0.12, 0.12), 0.3, 3.8, 8, 8, cx=-9.4, cy=3.8)
    pb.prism(L.rect(0.12, 0.12), 0.3, 3.8, 9, 9, cx=9.4, cy=3.8)
    pb.build("room", wall, seed=21)
    # BLACK MARKET sign: a faceted frame with neon letters
    frame_f = L.mat_flat("sign_face", "#2a2032")
    frame_e = L.mat_flat("sign_edge", "#ff3fa4", emit="#ff3fa4", emit_str=3.0)
    sg = H.plate("sign", 9.2, 1.9, frame_f, frame_e, depth=0.2, bevel=0.35, dome=0.08)
    sg.location = (0, 3.3, 7.6)
    sg.rotation_euler = (math.radians(90), 0, 0)
    t = L.text("sign_t", "BLACK MARKET", (0, 0, 0), 1.3, L.mat_flat("sign_txt", "#ff5fb8", emit="#ff5fb8", emit_str=9.0),
               extrude=0.08, shadow=False)
    t.location = (0, 3.1, 7.62)
    t.rotation_euler = (math.radians(90), 0, 0)
    t2 = L.text("sign_t2", "NO QUESTIONS  //  NO REFUNDS", (0, 0, 0), 0.34,
                L.mat_flat("sign_txt2", "#35e6ff", emit="#35e6ff", emit_str=6.0), extrude=0.03, shadow=False,
                font=L.FONT_BODY)
    t2.location = (0, 3.1, 6.35)
    t2.rotation_euler = (math.radians(90), 0, 0)
    L.point("sign_glow", (0, 2.2, 7.4), "#ff3fa4", 900, radius=2.0)
    L.point("tube_l", (-9.0, 3.0, 2.0), "#35e6ff", 500, radius=0.5)
    L.point("tube_r", (9.0, 3.0, 2.0), "#ffb040", 500, radius=0.5)
    # hanging lamp over the counter
    lamp = L.PB()
    lamp.prism(L.ngon(6, 1.1), 0, 0.7, 0, 1, top_scale=0.25, bottom=True, mi_bot=2)
    lamp.prism(L.ngon(4, 0.03), 0.7, 5.0, 0, 0)
    lmats = [L.mat_flat("lamp_sh", "#2e8a86"), L.mat_flat("lamp_top", "#256e6c"),
             L.mat_flat("lamp_bulb", "#ffe0a8", emit="#ffe0a8", emit_str=8.0)]
    for k, lx_ in enumerate((-3.9, 3.9)):
        lo = lamp.build(f"lamp{k}", lmats, seed=3 + k)
        lo.location = (lx_, -0.1, 6.4)
        L.point(f"lamp_l{k}", (lx_, -0.1, 6.1), "#ffc080", 900, radius=0.6, shadow=True)


def _fixer():
    """A hooded fixer, faceted like a carved toy: coat, hood, visor."""
    coat = L.mat_flat("coat", "#8a5862")
    coat2 = L.mat_flat("coat2", "#653c48")
    hood = L.mat_flat("hood", "#4e3446")
    skin = L.mat_flat("skin", "#c99a82")
    visor = L.mat_flat("visor", "#39e0ff", emit="#39e0ff", emit_str=7.0)
    trim = L.mat_flat("trim", "#e0a24a")
    mats = [coat, coat2, hood, skin, visor, trim]
    pb = L.PB()
    y = 1.5
    # torso: broad sloping shoulders
    pb.prism(L.ngon(8, 1.6, rot=0.2, sx=1.25, sy=0.62), 1.0, 3.35, 0, 1, top_scale=0.5, cy=y + 0.1, jit=0.1,
             top_center_dz=0.2)
    # high collar
    pb.prism(L.ngon(6, 0.62, sy=0.8), 3.1, 3.75, 5, 5, top_scale=1.15, cy=y - 0.1, jit=0.03)
    # hood: a faceted cowl behind and above the head
    pb.prism(L.ngon(8, 1.1, rot=0.1, sy=0.85), 3.35, 5.0, 2, 2, top_scale=0.45, cy=y + 0.45, jit=0.09,
             top_center_dz=0.6)
    # arms: from the shoulders down to the hands on the counter
    for sg in (-1, 1):
        pts = [(-0.38, -0.36), (0.38, -0.36), (0.38, 0.36), (-0.38, 0.36)]
        pb.prism(pts, 1.72, 3.1, 0, 1, cx=sg * 1.45, cy=y - 1.35, top_scale=0.9, jit=0.06,
                 top_off=(sg * 0.35, 1.2))
        pb.prism(L.ngon(5, 0.36), 1.72, 2.0, 3, 3, cx=sg * 1.35, cy=y - 1.55, jit=0.04, top_center_dz=0.1)
    body = pb.build("fixer", mats, seed=31)
    hy, hz = y - 0.2, 4.3
    head = L.ico("fixer_head", (0, hy, hz), 0.7, skin, sub=1, jit=0.06, seed=4, scale=(0.9, 0.85, 1.05))
    vz = L.PB()
    vz.prism([(-0.7, -0.13), (0.7, -0.13), (0.56, 0.14), (-0.56, 0.14)], -0.14, 0.14, 0, 0, top_center_dz=0.05)
    v = vz.build("visor", [visor], seed=2)
    v.location = (0, hy - 0.62, hz + 0.1)
    v.rotation_euler = (math.radians(90), 0, 0)
    L.point("visor_glow", (0, hy - 1.3, hz), "#39e0ff", 60, radius=0.3)
    # a hood rim around the face opening
    rim = L.PB()
    n = 8
    for k in range(n):
        a0 = math.pi * (-0.1 + 1.2 * k / n)
        a1 = math.pi * (-0.1 + 1.2 * (k + 1) / n)
        p = [(math.cos(a0) * 0.95, math.sin(a0) * 1.05), (math.cos(a1) * 0.95, math.sin(a1) * 1.05),
             (math.cos(a1) * 0.74, math.sin(a1) * 0.84), (math.cos(a0) * 0.74, math.sin(a0) * 0.84)]
        ids = [rim.vert((px, py, 0.0), 0.02) for px, py in p]
        ids2 = [rim.vert((px, py, 0.3), 0.02) for px, py in p]
        rim.face([ids2[0], ids2[1], ids2[2], ids2[3]], 0)
        rim.face([ids[0], ids[1], ids2[1], ids2[0]], 0)
    r = rim.build("hood_rim", [hood], seed=5)
    r.location = (0, hy - 0.25, hz - 0.05)
    r.rotation_euler = (math.radians(90), 0, 0)
    # scale the whole bust up a touch around the counter line, so the fixer reads as the stall's centrepiece
    piv = bpy.data.objects.new("fixer_pivot", None)
    bpy.context.scene.collection.objects.link(piv)
    piv.location = (0, y, 1.72)
    bpy.context.view_layer.update()
    for o in (body, head, v, r):
        o.parent = piv
        o.matrix_parent_inverse = piv.matrix_world.inverted()
    piv.scale = (1.22, 1.22, 1.22)


def _counter(rng):
    top = L.mat_flat("ctr_top", "#c8a88c")
    side = L.mat_flat("ctr_side", "#5e4656")
    side2 = L.mat_flat("ctr_side2", "#523c4c")
    strip = L.mat_flat("ctr_strip", "#ff3fa4", emit="#ff3fa4", emit_str=5.0)
    pb = L.PB()
    # front panels, each folded slightly so the face breaks into facets
    x = -8.0
    k = 0
    while x < 8.0:
        w = 1.6
        a = pb.vert((x, -1.1, 0.0))
        b = pb.vert((x + w, -1.1, 0.0))
        c = pb.vert((x + w, -1.25, 1.5), 0.02)
        d = pb.vert((x, -1.25, 1.5), 0.02)
        m = pb.vert((x + w / 2, -1.34, 0.8))
        pb.face([a, b, m], 1 + k % 2)
        pb.face([b, c, m], 1 + (k + 1) % 2)
        pb.face([c, d, m], 1 + k % 2)
        pb.face([d, a, m], 1 + (k + 1) % 2)
        x += w
        k += 1
    pb.prism(L.rect(16.4, 2.6), 1.5, 1.72, 1, 0, cy=-0.05, jit=0.0)
    pb.prism(L.rect(16.0, 0.08), 0.22, 0.34, 3, 3, cy=-1.3)
    pb.build("counter", [top, side, side2, strip], seed=41)


def _goods(rng):
    ztop = 1.72
    xs = [-5.9, -3.9, -1.95, 1.95, 3.9, 5.9]
    tagf = L.mat_flat("tag_f", "#2c2538")
    tage = L.mat_flat("tag_e", "#f0b44a", emit="#f0b44a", emit_str=1.2)
    price = L.mat_flat("tag_p", "#ffd37a", emit="#ffc860", emit_str=2.5)
    name = L.mat_flat("tag_n", "#f3e6d4", emit="#f3e6d4", emit_str=0.6)
    ped = [L.mat_flat("ped_a", "#3b3346"), L.mat_flat("ped_b", "#6a5f74")]
    items = [("card",) + c for c in CARDS] + [("part",) + p for p in PARTS]
    for k, (x, it) in enumerate(zip(xs, items)):
        # pedestal / stand
        pb = L.PB()
        pb.prism(L.ngon(6, 0.62, rot=math.pi / 6), ztop, ztop + 0.28, 0, 1, top_center_dz=0.03)
        pb.build(f"ped{k}", ped, seed=k).location = (x, 0.2, 0)
        if it[0] == "card":
            _, kind, title, cost, desc, icon, pr = it
            cd = U.card(f"scard{k}", 1.32, kind, title, cost, desc, icon, glow=0.0)
            cd.location = (x, 0.25, ztop + 0.3 + 0.96)
            cd.rotation_euler = (math.radians(80), 0, math.radians((k - 1) * -6))
            label = title
        else:
            _, label, shape, col, pr = it
            ob = _part(f"part{k}", shape, col)
            ob.location = (x, 0.2, ztop + 0.3)
            label = label
        # price tag on the counter edge, tilted up to the camera
        tg = H.plate(f"tag{k}", 1.7, 0.62, tagf, tage, depth=0.05, bevel=0.1)
        tg.location = (x, -1.0, ztop + 0.36)
        tg.rotation_euler = (math.radians(62), 0, 0)
        tn = L.text(f"tagn{k}", label, (0, 0.14, 0.06), 0.17, name, extrude=0.01, font=L.FONT_BODY,
                    parent=tg, shadow=False)
        tp = L.text(f"tagp{k}", pr + " CR", (0, -0.12, 0.06), 0.3, price, extrude=0.015, parent=tg,
                    shadow=False)


def _part(name, shape, col):
    m1 = L.mat_flat(name + "_a", col, emit=col, emit_str=0.5)
    m2 = L.mat_flat(name + "_b", U._shade(col, 0.6))
    m3 = L.mat_flat(name + "_c", "#3b3346")
    m4 = L.mat_flat(name + "_d", "#fff4e4", emit="#fff4e4", emit_str=0.5)
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    pb = L.PB()
    if shape == "wedge":
        # a single spinner slice, standing on its point: faceted like the combat wheel
        R = 1.25
        a0, a1 = math.radians(60), math.radians(120)
        segs = 3
        arc = [a0 + (a1 - a0) * k / segs for k in range(segs + 1)]
        top = [pb.vert((math.cos(a) * R, math.sin(a) * R - 0.2, 0.18), 0.01) for a in arc]
        bot = [pb.vert((math.cos(a) * R, math.sin(a) * R - 0.2, -0.18)) for a in arc]
        ap = pb.vert((0, -0.2, 0.22))
        apb = pb.vert((0, -0.2, -0.22))
        mid = [pb.vert((math.cos(a) * R * 0.55, math.sin(a) * R * 0.55 - 0.2, 0.3), 0.01) for a in arc[::3]]
        for k in range(segs):
            pb.face([top[k], top[k + 1], bot[k + 1], bot[k]], 1)
            pb.face([top[k + 1], top[k], mid[0] if k < 2 else mid[1]], 0)
            pb.face([bot[k], bot[k + 1], apb], 1)
        pb.face([mid[0], top[2], mid[1]], 0)
        pb.face([mid[1], ap, mid[0]], 0)
        pb.face([ap, mid[0], top[0]], 0)
        pb.face([ap, top[-1], mid[1]], 0)
        pb.face([ap, bot[0], top[0]], 1)
        pb.face([ap, top[-1], bot[-1]], 1)
        o = pb.build(name + "_m", [m1, m2, m3], seed=1)
        o.parent = root
        o.rotation_euler = (math.radians(90), 0, 0)
        o.location = (0, 0, 0.4)
        t = L.text(name + "_t", "x2", (0, -0.25, 1.45), 0.42, m4, rot=(math.radians(90), 0, 0), extrude=0.03)
        t.parent = root
    elif shape == "pointer":
        pw, ph = 0.8, 1.35
        tip = pb.vert((0, 0, 0.0))
        l = pb.vert((-pw, ph, 0.0))
        r = pb.vert((pw, ph, 0.0))
        c = pb.vert((0, ph * 0.6, 0.45))
        cb = pb.vert((0, ph * 0.6, -0.45))
        pb.face([tip, c, l], 0)
        pb.face([tip, r, c], 1)
        pb.face([l, c, r], 1)
        pb.face([tip, l, cb], 1)
        pb.face([tip, cb, r], 0)
        pb.face([l, r, cb], 1)
        o = pb.build(name + "_m", [m1, m2], seed=2)
        o.parent = root
        o.rotation_euler = (math.radians(90), 0, 0)
        o.location = (0, 0, 0.15)
        # a spindle through it
        pb2 = L.PB()
        pb2.prism(L.ngon(6, 0.12), 0.0, 0.3, 0, 0)
        s = pb2.build(name + "_s", [m3])
        s.parent = root
    else:  # hub
        g = H.gem(name + "_g", 0.75, m1, m2, n=6, h=0.9)
        g.parent = root
        g.rotation_euler = (math.radians(90), 0, 0)
        g.location = (0, 0, 1.1)
        pb.prism(L.ngon(10, 1.05), -0.12, 0.12, 2, 2, bottom=True)
        pb.prism(L.ngon(10, 0.8), 0.12, 0.13, 2, 2)
        ring = pb.build(name + "_r", [m1, m2, m3], seed=3)
        ring.parent = root
        ring.rotation_euler = (math.radians(90), 0, 0)
        ring.location = (0, 0.25, 1.1)
    return root


def _hud(cam):
    hud = L.HUD(cam, depth=5.0)
    u = hud.unit()
    dark = L.mat_flat("hud_dark", "#2b2436", emit="#2b2436", emit_str=0.2)
    edge = L.mat_flat("hud_edge", "#f0b44a", emit="#f0b44a", emit_str=1.2)
    lab = L.mat_flat("hud_lab", "#f3e6d4", emit="#f3e6d4", emit_str=0.8)
    pl = H.plate("cred", 0.44 * u, 0.12 * u, dark, edge, depth=0.012 * u, bevel=0.016 * u)
    hud.adopt(pl, 0.14, 0.905)
    g = H.gem("coin", 0.04 * u, L.mat_flat("coin_a", "#ffd37a", emit="#ffb640", emit_str=1.5),
              L.mat_flat("coin_b", "#c98a2e"), n=6, h=0.03 * u)
    hud.adopt(g, 0.055, 0.905, dz=0.01 * u)
    t = L.text("cred_t", "CREDITS", (0, 0, 0), 0.034 * u, lab, extrude=0.002 * u, align="LEFT")
    hud.adopt(t, 0.085, 0.925, dz=0.01 * u)
    t2 = L.text("cred_v", "340 CR", (0, 0, 0), 0.058 * u, L.mat_flat("cred_vm", "#ffd37a", emit="#ffc860", emit_str=2.0),
                extrude=0.003 * u, align="LEFT")
    hud.adopt(t2, 0.085, 0.885, dz=0.01 * u)
    b = U.button("leave", 0.34 * u, 0.13 * u, "#39e0ff", "LEAVE  >", glow=1.6)
    hud.adopt(b, 0.88, 0.1)


if __name__ == "__main__":
    main()
