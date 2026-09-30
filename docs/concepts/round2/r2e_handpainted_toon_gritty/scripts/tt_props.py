"""R2E HAND-PAINTED TOON: crafted props shared by the stills.

UI props (spinner, card, button, plaque, bars, price tags) are built flat in a local XY
plane with thickness along +Z (the face looks at +Z) and parented to a group empty.
A UI root parented to the camera maps 1 local unit = 100 px, origin at screen centre.
"""
import bpy
import math
import random
from mathutils import Vector
import tt_lib as T

PAL = {
    "atk": "#cc442e", "def": "#2a9e94", "hack": "#d9a032", "glitch": "#8a50c8",
    "cream": "#fff0cf", "wood": "#9a5f33", "wood_d": "#6b3f22", "brass": "#d9a441",
    "steel": "#8d9ba8", "iron": "#4a4e5a", "ink": "#221614", "lime": "#9ee03a",
    "hp_g": "#6fd64a", "hp_r": "#ef4a3f", "slot": "#3b2a2a", "gem": "#3fd0ff",
}


# ------------------------------------------------------------------ 2D shape helpers
def rrect_poly(w, h, r, n=5):
    pts = []
    cs = [(w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)]
    for cx, cy, a0 in cs:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def sector_poly(r_in, r_out, a0, a1, segs=10):
    outer = [(math.cos(a0 + (a1 - a0) * i / segs) * r_out, math.sin(a0 + (a1 - a0) * i / segs) * r_out) for i in range(segs + 1)]
    if r_in <= 0.001:
        return outer + [(0.0, 0.0)]
    inner = [(math.cos(a1 - (a1 - a0) * i / segs) * r_in, math.sin(a1 - (a1 - a0) * i / segs) * r_in) for i in range(segs + 1)]
    return outer + inner


def ring(r_in, r_out, h, loc, mat, parent, bev=0.04, segs=24, name="ring"):
    objs = []
    for k in range(2):
        a0 = math.pi * k
        o = T.prism(sector_poly(r_in, r_out, a0, a0 + math.pi, segs), h, loc, mat, bev=bev, name=name)
        o.parent = parent
        objs.append(o)
    return objs


def jitter_poly(pts, amt, rng):
    return [(x + rng.uniform(-amt, amt), y + rng.uniform(-amt, amt)) for x, y in pts]


def P(o, parent):
    o.parent = parent
    return o


# ------------------------------------------------------------------ UI root
def ui_root(cam, depth=12.0, name="ui"):
    """Empty parented to the camera; 1 local unit = 100 px, (0,0) = screen centre, +Y up."""
    sc = bpy.context.scene
    w_at = depth * cam.data.sensor_width / cam.data.lens
    s = w_at / (sc.render.resolution_x / 100.0)
    e = T.empty(name)
    e.parent = cam
    e.location = (0, 0, -depth)
    e.scale = (s, s, s)
    return e


def px(x, y):
    """Screen pixel (1920x1080, y down) -> ui_root local coordinates."""
    return ((x - 960) / 100.0, (540 - y) / 100.0)


def sub(parent, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, name="g"):
    e = T.empty(name, loc, rot, scale)
    e.parent = parent
    return e


def label(parent, body, size, loc, col, fnt="title", extrude=0.06, align="CENTER", lined=True, width=None,
          spacing=1.0, fake="ui", thin=None):
    """Extruded painted text. Big text gets the main ink line, small text (< 0.4) a thin one,
    lined=False gives flat unlined ink text (card body copy)."""
    if thin is None:
        thin = size < 0.4
    m = T.paint(col, stroke=0.05, blotch=0.06, grime=0.0, fake=fake) if lined else T.flat_col(col)
    coll = T.noline_coll() if not lined else (T.thin_coll() if thin else None)
    if not lined:
        extrude = 0.0
    o = T.text(body, size, loc, rot=(0, 0, 0), mat=m, fnt=fnt, extrude=extrude, bev=0.0, align=align,
               width=width, spacing=spacing, coll=coll)
    o.parent = parent
    return o


# ------------------------------------------------------------------ plaque / panel
def plaque(parent, w, h, loc, col=PAL["wood"], trim=PAL["brass"], r=0.18, depth=0.22, rng=None, bolts=True,
           fake="ui", inner=None, name="plaque"):
    rng = rng or random.Random(3)
    objs = []
    g = sub(parent, loc, name=name)
    # trim frame behind, face on top
    o = T.prism(jitter_poly(rrect_poly(w + 0.16, h + 0.16, r + 0.06), 0.015, rng), depth * 0.7, (0, 0, -depth * 0.35),
                T.paint(trim, gloss=0.5, fake=fake, streak_axis=0), bev=0.05, name=name + "_trim")
    P(o, g)
    o = T.prism(jitter_poly(rrect_poly(w, h, r), 0.012, rng), depth * 0.55, (0, 0, 0),
                T.paint(col, fake=fake, streak_axis=0, streak=16, stroke=0.22), bev=0.05, name=name)
    P(o, g)
    if inner:
        o = T.prism(rrect_poly(w - 0.28, h - 0.28, max(0.05, r - 0.08)), 0.05, (0, 0, depth * 0.55),
                    T.paint(inner, fake=fake, stroke=0.12), bev=0.02, name=name + "_in")
        P(o, g)
    if bolts:
        for sx in (-1, 1):
            for sy in (-1, 1):
                if w < 1.2 and sy < 0:
                    continue
                b = T.cyl(0.07, 0.07, (sx * (w / 2 - 0.13), sy * (h / 2 - 0.13), depth * 0.55),
                          T.paint(PAL["steel"], gloss=0.8, fake=fake), verts=8, bev=0.02, name="bolt")
                P(b, g)
    return g


def meter(parent, w, frac, loc, fill=PAL["hp_g"], segs=10, label_txt=None, fake="ui", icon=None,
          value_txt=None, frame=PAL["wood_d"], name="meter"):
    """Chunky segmented bar in a wooden frame."""
    g = sub(parent, loc, name=name)
    h = 0.5
    o = T.prism(rrect_poly(w + 0.24, h + 0.24, 0.2), 0.2, (0, 0, -0.1), T.paint(frame, fake=fake, streak_axis=0, streak=18), bev=0.05)
    P(o, g)
    o = T.prism(rrect_poly(w, h, 0.14), 0.08, (0, 0, 0.1), T.paint(PAL["slot"], fake=fake), bev=0.02)
    P(o, g)
    gap = 0.05
    sw = (w - 0.12 - gap * (segs - 1)) / segs
    n_on = frac * segs
    for i in range(segs):
        x = -w / 2 + 0.06 + sw / 2 + i * (sw + gap)
        on = i < int(round(n_on))
        c = fill if on else "#57433f"
        o = T.prism(rrect_poly(sw, h - 0.14, 0.07), 0.1 if on else 0.04, (x, 0, 0.16),
                    T.paint(c, fake=fake, gloss=0.35 if on else 0.0, stroke=0.1), bev=0.025, name="seg")
        P(o, g)
    if value_txt:
        label(g, value_txt, 0.42, (w / 2 + 0.25, -0.02, 0.1), PAL["cream"], fnt="sign", align="LEFT", fake=fake)
    if label_txt:
        label(g, label_txt, 0.3, (-w / 2, 0.42, 0.1), PAL["cream"], fnt="title", align="LEFT", fake=fake)
    return g


# ------------------------------------------------------------------ spinner
def spinner(parent, R, slices, loc, rot=(0, 0, 0), frame=PAL["wood_d"], rim=PAL["brass"], hub=PAL["iron"],
            pointer=PAL["atk"], spin=0.0, rng=None, fake="ui", name="spinner", hub_icon="R", salvaged=True,
            cracked=False, hazard=((3, 7), (17, 20))):
    """Crafted wheel: wooden back disc, brass rim with rivets, raised painted slices with numbers,
    domed hub, chunky pointer at the top."""
    rng = rng or random.Random(4)
    g = sub(parent, loc, rot, name=name)
    F = fake
    o = T.cyl(R + 0.42, 0.34, (0, 0, -0.34), T.paint(frame, fake=F, streak_axis=0, streak=14, stroke=0.24), verts=56,
              bev=0.08, wonk=0.012, rng=rng, name="back")
    P(o, g)
    # planks on the back disc (visible edge) - wood grain via painted streaks is enough
    if not salvaged:
        for o in ring(R + 0.02, R + 0.36, 0.32, (0, 0, -0.04), T.paint(rim, gloss=0.6, fake=F), None, bev=0.05, segs=28):
            P(o, g)
    else:
        # dented, welded rim: 28 plates of slightly different height/width, hazard-striped arcs,
        # a cracked gap (enemy) patched with a bolted plate
        NSEG = 28
        rim_m = T.paint(rim, gloss=0.5, fake=F, stroke=0.3)
        hz_y = T.paint("#e8c030", fake=F, stroke=0.25)
        hz_k = T.paint("#1c1c1c", fake=F)
        gap_i = {9, 10} if cracked else set()
        for k in range(NSEG):
            if k in gap_i:
                continue
            a0 = k / NSEG * math.tau + 0.01
            a1 = (k + 1) / NSEG * math.tau - 0.01
            mat = rim_m
            for (h0, h1) in hazard:
                if h0 <= k <= h1:
                    mat = hz_y if k % 2 else hz_k
            dent = rng.uniform(-0.05, 0.05)
            o = T.prism(sector_poly(R + 0.02 + max(0, dent), R + 0.36 + dent, a0, a1, 3), 0.3 + rng.uniform(-0.04, 0.05),
                        (0, 0, -0.04), mat, bev=0.04, name="rimseg")
            P(o, g)
        # weld beads across three seams
        for k in (5, 14, 23):
            a = k / NSEG * math.tau
            for j in range(5):
                rr = R + 0.06 + j * 0.065
                P(T.rock(0.045, (math.cos(a) * rr, math.sin(a) * rr, 0.28), T.paint("#8a8a80", fake=F, gloss=0.6), rng,
                         flat=0.7), g)
        if cracked:
            a = 9.9 / NSEG * math.tau
            pg_ = sub(g, (math.cos(a) * (R + 0.2), math.sin(a) * (R + 0.2), 0.3), rot=(0, 0, math.degrees(a) + 90))
            P(T.box((0.62, 0.5, 0.08), (0, 0, 0), T.paint("#5a5048", fake=F, gloss=0.3), bev=0.03, wonk=0.08, rng=rng), pg_)
            for sx in (-0.22, 0.22):
                P(T.cyl(0.05, 0.06, (sx, 0.12, 0.08), T.paint(PAL["steel"], gloss=0.9, fake=F), verts=6, bev=0.01), pg_)
            # jagged crack running into the back disc
            crack = [(0.0, 0.0), (0.08, -0.25), (-0.04, -0.45), (0.1, -0.7), (0.02, -0.72), (-0.1, -0.46), (0.0, -0.26)]
            cg = sub(g, (math.cos(a) * (R + 0.02), math.sin(a) * (R + 0.02), 0.01), rot=(0, 0, math.degrees(a) + 90))
            P(T.prism(crack, 0.02, (0, 0.1, 0), T.flat_col("#0c0a0a"), bev=0), cg)
        # exposed wiring looping out from behind the disc
        for j, (a0, a1, c) in enumerate(((0.3, 0.9, "#c0392b"), (3.6, 4.2, "#e8c030"), (2.2, 2.5, "#3a7bd5"))):
            cu = T.bpy.data.curves.new("wire", "CURVE")
            cu.dimensions = "3D"
            cu.bevel_depth = 0.035
            sp = cu.splines.new("POLY")
            sp.points.add(6)
            for t in range(7):
                aa = a0 + (a1 - a0) * t / 6
                rr = R + 0.4 + 0.35 * math.sin(t / 6 * math.pi)
                sp.points[t].co = (math.cos(aa) * rr, math.sin(aa) * rr, -0.15, 1)
            ow = T.bpy.data.objects.new("wire", cu)
            T.link_obj(ow)
            cu.materials.append(T.paint(c, fake=F, gloss=0.4))
            P(ow, g)
    n = len(slices)
    for i in range(18):
        a = i / 18 * math.tau + 0.1
        b = T.cyl(0.075, 0.09, (math.cos(a) * (R + 0.19), math.sin(a) * (R + 0.19), 0.27),
                  T.paint(PAL["steel"], gloss=0.9, fake=F), verts=8, bev=0.025, name="rivet")
        P(b, g)
    gap = 0.035
    for i, (col, num) in enumerate(slices):
        a0 = math.pi / 2 + spin + i / n * math.tau + gap
        a1 = math.pi / 2 + spin + (i + 1) / n * math.tau - gap
        o = T.prism(sector_poly(R * 0.30, R - 0.03, a0, a1, 12), 0.16 + 0.02 * (i % 2), (0, 0, 0),
                    T.paint(col, fake=F, stroke=0.2, blotch=0.22, seed=i, streak_axis=rng.choice((0, 1))), bev=0.045,
                    name="slice")
        P(o, g)
        am = (a0 + a1) / 2
        rr = R * 0.68
        t = label(g, str(num), R * 0.24, (math.cos(am) * rr, math.sin(am) * rr - R * 0.02, 0.18), PAL["cream"],
                  fnt="sign", fake=F)
    o = T.cyl(R * 0.33, 0.28, (0, 0, 0.0), T.paint(hub, gloss=0.6, fake=F), verts=32, bev=0.06, name="hub")
    P(o, g)
    o = T.cyl(R * 0.24, 0.16, (0, 0, 0.26), T.paint(rim, gloss=0.8, fake=F), r2=R * 0.14, verts=32, bev=0.05, name="dome")
    P(o, g)
    label(g, hub_icon, R * 0.2, (0, -0.01, 0.42), PAL["ink"], fnt="title", fake=F)
    # pointer: chunky arrow at 12 o'clock pointing down into the wheel
    pg = sub(g, (0, R + 0.18, 0.36), name="pointer")
    arrow = [(-0.34, 0.55), (0.34, 0.55), (0.3, 0.12), (0.0, -0.42), (-0.3, 0.12)]
    o = T.prism(arrow, 0.22, (0, 0, 0), T.paint(pointer, gloss=0.5, fake=F, stroke=0.2), bev=0.05, name="ptr")
    P(o, pg)
    o = T.cyl(0.13, 0.12, (0, 0.28, 0.2), T.paint(PAL["steel"], gloss=0.9, fake=F), verts=12, bev=0.03, name="ptr_bolt")
    P(o, pg)
    return g


# ------------------------------------------------------------------ card
def card(parent, title, cost, desc, col, loc, rot=(0, 0, 0), icon=None, kind="ATTACK", fake="ui",
         rng=None, name="card", scale=1.0):
    rng = rng or random.Random(9)
    F = fake
    g = sub(parent, loc, rot, scale, name=name)
    W, H = 1.8, 2.55
    o = T.prism(jitter_poly(rrect_poly(W, H, 0.2), 0.012, rng), 0.14, (0, 0, 0),
                T.paint(col, fake=F, stroke=0.22, streak_axis=1), bev=0.05, name="card_frame")
    P(o, g)
    o = T.prism(jitter_poly(rrect_poly(W - 0.22, H - 0.22, 0.14), 0.035, rng), 0.05, (0, 0, 0.14),
                T.paint("#dccb9e", fake=F, stroke=0.3, blotch=0.3), bev=0.02, name="card_paper")
    P(o, g)
    # battered: a strip of tape across a corner, a dog-eared fold
    tg = sub(g, (rng.choice((-1, 1)) * 0.62, H / 2 - 0.12, 0.2), rot=(0, 0, rng.uniform(-50, -30)))
    P(T.box((0.75, 0.24, 0.02), (0, 0, 0), T.paint("#cdbb86", fake=F, stroke=0.4), bev=0.0), tg)
    P(T.prism([(W / 2 - 0.02, -H / 2 + 0.34), (W / 2 - 0.34, -H / 2 + 0.02), (W / 2 - 0.3, -H / 2 + 0.3)], 0.03,
              (0, 0, 0.19), T.paint("#b8a47a", fake=F), bev=0.0), g)
    # art window
    o = T.prism(rrect_poly(W - 0.42, 1.0, 0.12), 0.04, (0, 0.38, 0.19), T.paint(T_dark(col), fake=F, stroke=0.2), bev=0.02,
                name="card_art")
    P(o, g)
    if icon:
        icon(sub(g, (0, 0.38, 0.23)), F)
    # title ribbon
    o = T.prism(jitter_poly(rrect_poly(W + 0.08, 0.36, 0.08), 0.01, rng), 0.08, (0, -0.28, 0.21),
                T.paint(PAL["wood"], fake=F, streak_axis=0, streak=18), bev=0.03, name="ribbon")
    P(o, g)
    label(g, title, 0.24, (0, -0.29, 0.3), PAL["cream"], fnt="title", fake=F)
    # description (small flat ink text, no Freestyle lines so it stays crisp)
    d = label(g, desc, 0.145, (0, -0.72, 0.2), "#3a2418", fnt="body", extrude=0.0, lined=False)
    # cost gem
    o = T.cyl(0.29, 0.14, (-W / 2 + 0.2, H / 2 - 0.2, 0.12), T.paint(PAL["gem"], gloss=0.9, fake=F), verts=6, bev=0.05,
              name="gem")
    P(o, g)
    label(g, str(cost), 0.3, (-W / 2 + 0.2, H / 2 - 0.22, 0.27), PAL["cream"], fnt="sign", fake=F)
    # kind tag
    label(g, kind, 0.12, (0, -1.1, 0.2), "#7a4a2a", fnt="body", extrude=0.0, lined=False)
    return g


def T_dark(h):
    r, g_, b = T.shift(h, dv=0.45, ds=0.8)
    return "#%02x%02x%02x" % (int(r * 255), int(g_ * 255), int(b * 255))


# card icons (little crafted 3D glyphs)
def icon_bolt(g, F):
    pts = [(-0.05, 0.4), (0.25, 0.4), (0.06, 0.06), (0.24, 0.06), (-0.18, -0.42), (-0.02, -0.05), (-0.2, -0.05)]
    P(T.prism(pts, 0.14, (0, 0, 0), T.paint(PAL["hack"], gloss=0.6, fake=F), bev=0.03), g)


def icon_shield(g, F):
    pts = [(-0.3, 0.36), (0.3, 0.36), (0.3, 0.0), (0.0, -0.4), (-0.3, 0.0)]
    P(T.prism(pts, 0.14, (0, 0, 0), T.paint(PAL["def"], gloss=0.5, fake=F), bev=0.04), g)
    P(T.prism([(-0.08, 0.24), (0.08, 0.24), (0.08, -0.18), (-0.08, -0.18)], 0.06, (0, 0, 0.14),
              T.paint(PAL["cream"], fake=F), bev=0.02), g)


def icon_spin(g, F):
    for o in ring(0.2, 0.36, 0.12, (0, 0, 0), T.paint(PAL["brass"], gloss=0.7, fake=F), None, bev=0.03, segs=16):
        P(o, g)
    P(T.prism([(0.3, 0.18), (0.52, 0.02), (0.2, -0.04)], 0.14, (0, 0, 0.02), T.paint(PAL["atk"], fake=F), bev=0.02), g)
    P(T.cyl(0.1, 0.16, (0, 0, 0), T.paint(PAL["iron"], fake=F), verts=10, bev=0.02), g)


def icon_skull(g, F):
    P(T.cyl(0.3, 0.14, (0, 0.06, 0), T.paint("#e8dcc0", fake=F), verts=14, bev=0.04), g)
    P(T.box((0.34, 0.2, 0.14), (0, -0.26, 0), T.paint("#e8dcc0", fake=F), bev=0.03), g)
    for sx in (-1, 1):
        P(T.cyl(0.08, 0.06, (sx * 0.12, 0.06, 0.13), T.paint("#2a1a22", fake=F), verts=10, bev=0.01), g)


def icon_chip(g, F):
    P(T.box((0.5, 0.5, 0.12), (0, 0, 0), T.paint(PAL["glitch"], gloss=0.4, fake=F), bev=0.04), g)
    for i in range(4):
        for sx in (-1, 1):
            P(T.box((0.12, 0.05, 0.05), (sx * 0.31, -0.18 + i * 0.12, 0.03), T.paint(PAL["brass"], fake=F), bev=0.0), g)
            P(T.box((0.05, 0.12, 0.05), (-0.18 + i * 0.12, sx * 0.31, 0.03), T.paint(PAL["brass"], fake=F), bev=0.0), g)
    P(T.box((0.24, 0.24, 0.06), (0, 0, 0.1), T.paint(PAL["gem"], gloss=0.6, fake=F), bev=0.02), g)


# ------------------------------------------------------------------ button
def button(parent, txt, loc, w=2.8, h=1.1, col=PAL["lime"], rot=(0, 0, 0), fake="ui", rng=None,
           size=0.62, txt_col=PAL["cream"], name="btn"):
    rng = rng or random.Random(12)
    F = fake
    g = sub(parent, loc, rot, name=name)
    o = T.prism(jitter_poly(rrect_poly(w + 0.3, h + 0.3, h * 0.5 + 0.12), 0.015, rng), 0.26, (0, -0.06, -0.2),
                T.paint(PAL["iron"], fake=F, gloss=0.4), bev=0.06, name="btn_base")
    P(o, g)
    o = T.prism(jitter_poly(rrect_poly(w, h, h * 0.48), 0.012, rng), 0.3, (0, 0, 0),
                T.paint(col, fake=F, gloss=0.55, stroke=0.18, blotch=0.2), bev=0.1, segs=3, name="btn_top")
    P(o, g)
    label(g, txt, size, (0, -0.02, 0.36), txt_col, fnt="title", fake=F, extrude=0.08)
    return g


# ------------------------------------------------------------------ world props
def ground_base(parent, rx, ry, loc, rng, top="#6aa83c", side="#7a5234", depth=0.45, n=40, fake=None, name="gbase",
                tufts=10, rocks=3):
    """Little painted ground base under a prop (ragged grass disc on an earth slab)."""
    g = sub(parent, loc, name=name)
    poly = []
    for i in range(n):
        a = i / n * math.tau
        k = 1 + rng.uniform(-0.07, 0.07)
        poly.append((math.cos(a) * rx * k, math.sin(a) * ry * k))
    o = T.prism(poly, depth, (0, 0, -depth), T.paint(side, fake=fake, streak_axis=2, streak=6), bev=0.06, name="earth")
    P(o, g)
    poly2 = [(x * 1.03 + rng.uniform(-0.04, 0.04), y * 1.03 + rng.uniform(-0.04, 0.04)) for x, y in poly]
    o = T.prism(poly2, 0.12, (0, 0, -0.06), T.paint(top, fake=fake, stroke=0.25, blotch=0.25), bev=0.04, name="grass")
    P(o, g)
    ga, gb = T.paint("#7fc646", fake=fake), T.paint("#4f8f2e", fake=fake)
    for i in range(tufts):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.75, 0.97)
        for o in T.tuft((math.cos(a) * rx * r, math.sin(a) * ry * r, 0.05), rng, ga, gb, s=rng.uniform(0.9, 1.4)):
            P(o, g)
    for i in range(rocks):
        a = rng.uniform(0, math.tau)
        P(T.rock(rng.uniform(0.12, 0.22), (math.cos(a) * rx * 0.85, math.sin(a) * ry * 0.85, 0.05),
                 T.paint("#a7aeb4", fake=fake), rng), g)
    return g
