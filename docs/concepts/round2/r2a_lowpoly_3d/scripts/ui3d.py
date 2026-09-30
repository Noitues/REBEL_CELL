"""R2A LOW-POLY 3D: game UI as chunky faceted objects (spinners, health bars, cards, buttons, tags).

Everything is built in a local XY plane facing +Z, so it can be dropped into a camera-space HUD.
"""
import math
import bpy
import lp_lib as L
import hud as H

SLICE_COL = {
    "atk": "#e2645a",   # coral red
    "def": "#3fb3ad",   # teal
    "hack": "#9c6fe0",  # violet
    "heal": "#9fcf62",  # lime
    "crit": "#f0b44a",  # amber
    "miss": "#5a5266",  # dead slice
}


def _mats(prefix, spec):
    return {k: L.mat_flat(f"{prefix}_{k}", c, **kw) for k, (c, kw) in spec.items()}


def spinner(name, R, slices, accent, rot_deg=0.0, ticks=30, label_mat=None, glow=4.0):
    """A faceted wheel. slices = [(ticks, kind, label)], clockwise from 12 o'clock.
    Returns (wheel_root, pointer)."""
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    kinds = sorted(set(k for _, k, _ in slices))
    mats = [L.mat_flat(f"{name}_rim", "#3b3346"), L.mat_flat(f"{name}_rimtop", "#6a5f74"),
            L.mat_flat(f"{name}_tick", accent, emit=accent, emit_str=glow * 0.6)]
    mats += [L.mat_flat(f"{name}_{k}", SLICE_COL[k]) for k in kinds]
    mats += [L.mat_flat(f"{name}_{k}_side", _shade(SLICE_COL[k], 0.6)) for k in kinds]
    kidx = {k: 3 + i for i, k in enumerate(kinds)}
    sidx = {k: 3 + len(kinds) + i for i, k in enumerate(kinds)}
    pb = L.PB()
    # chunky rim ring: 20-gon, bevelled top
    n = 20
    ro, ri = R * 1.12, R * 0.98
    outer_b = [pb.vert((math.cos(a) * ro, math.sin(a) * ro, -0.1 * R)) for a in _angles(n)]
    outer_t = [pb.vert((math.cos(a) * ro * 0.97, math.sin(a) * ro * 0.97, 0.06 * R)) for a in _angles(n)]
    inner_t = [pb.vert((math.cos(a) * ri, math.sin(a) * ri, 0.1 * R)) for a in _angles(n)]
    inner_b = [pb.vert((math.cos(a) * ri, math.sin(a) * ri, -0.05 * R)) for a in _angles(n)]
    for i in range(n):
        a, b = i, (i + 1) % n
        pb.face([outer_b[a], outer_b[b], outer_t[b], outer_t[a]], 0)
        pb.face([outer_t[a], outer_t[b], inner_t[b], inner_t[a]], 1)
        pb.face([inner_t[b], inner_b[b], inner_b[a], inner_t[a]], 0)
    # back plate
    pb.prism(L.ngon(n, ri, rot=0), -0.12 * R, -0.05 * R, 0, 0)
    rim = pb.build(name + "_rim", mats, seed=3, shadow=False)
    rim.parent = root
    # tick studs on the rim: small facet diamonds, every 1/30 turn
    pbt = L.PB()
    for t in range(ticks):
        a = math.pi / 2 - t * 2 * math.pi / ticks
        cx, cy = math.cos(a) * R * 1.05, math.sin(a) * R * 1.05
        big = t % 5 == 0
        s = R * (0.035 if big else 0.02)
        pts = [(math.cos(a) * s * 1.6, math.sin(a) * s * 1.6), (-math.sin(a) * s, math.cos(a) * s),
               (-math.cos(a) * s * 1.6, -math.sin(a) * s * 1.6), (math.sin(a) * s, -math.cos(a) * s)]
        pbt.prism(pts, 0.06 * R, 0.1 * R, 2, 2, cx=cx, cy=cy, top_center_dz=0.02 * R)
    tk = pbt.build(name + "_ticks", mats, shadow=False)
    tk.parent = root
    # the wheel (rotating part): wedges with a raised apex -> every triangle its own tone
    wheel = bpy.data.objects.new(name + "_wheel", None)
    bpy.context.scene.collection.objects.link(wheel)
    wheel.parent = root
    wheel.rotation_euler = (0, 0, math.radians(rot_deg))
    pbw = L.PB()
    t0 = 0
    total = sum(s[0] for s in slices)
    labels = []
    for (tn, kind, lab) in slices:
        a0 = math.pi / 2 - t0 * 2 * math.pi / total
        a1 = math.pi / 2 - (t0 + tn) * 2 * math.pi / total
        t0 += tn
        gap = 0.018
        segs = max(2, int(round(tn / 3)))
        mid = (a0 + a1) / 2
        off = 0.035 * R
        ox, oy = math.cos(mid) * off, math.sin(mid) * off
        rr = R * 0.93
        arc = [a0 - gap + (a1 - a0 + 2 * gap) * k / segs for k in range(segs + 1)]
        top = [pbw.vert((ox + math.cos(a) * rr, oy + math.sin(a) * rr, 0.08 * R), 0.004 * R) for a in arc]
        bot = [pbw.vert((ox + math.cos(a) * rr, oy + math.sin(a) * rr, -0.02 * R)) for a in arc]
        # mid ring gives two tiers of facets per wedge
        mr = rr * 0.55
        midr = [pbw.vert((ox + math.cos(a) * mr, oy + math.sin(a) * mr, 0.16 * R), 0.006 * R)
                for a in arc[::max(1, segs // 2)]]
        apex = pbw.vert((ox, oy, 0.2 * R))
        # outer tier
        m_i = [int(round(k * (len(midr) - 1) / segs)) for k in range(segs + 1)]
        for k in range(segs):
            pbw.face([bot[k + 1], bot[k], top[k], top[k + 1]], sidx[kind])  # rim side (clockwise arc)
            a_, b_ = top[k], top[k + 1]
            ma, mb = midr[m_i[k]], midr[m_i[k + 1]]
            if ma == mb:
                pbw.face([b_, a_, ma], kidx[kind])
            else:
                pbw.face([b_, a_, ma, mb], kidx[kind])
        for k in range(len(midr) - 1):
            pbw.face([midr[k + 1], midr[k], apex], kidx[kind])
        # side walls of the wedge
        pbw.face([bot[0], apex, top[0]], sidx[kind])
        pbw.face([top[-1], apex, bot[-1]], sidx[kind])
        labels.append((mid, lab, kind))
    w = pbw.build(name + "_slices", mats, seed=7, shadow=False)
    w.parent = wheel
    lm = label_mat or L.mat_flat(name + "_lab", "#fff4e4", emit="#fff4e4", emit_str=0.6)
    for k, (mid, lab, kind) in enumerate(labels):
        if not lab:
            continue
        r = R * 0.64
        t = L.text(f"{name}_l{k}", lab, (math.cos(mid) * r, math.sin(mid) * r, 0.2 * R), R * 0.2, lm,
                   extrude=0.012 * R, shadow=False)
        t.parent = wheel
        # keep numbers upright on screen: counter-rotate the wheel angle
        t.rotation_euler = (0, 0, -math.radians(rot_deg))
    # hub gem
    hub = H.gem(name + "_hub", R * 0.2, L.mat_flat(name + "_hubA", accent, emit=accent, emit_str=glow * 0.5),
                L.mat_flat(name + "_hubB", _shade(accent, 0.55), emit=accent, emit_str=glow * 0.15), n=6, h=R * 0.3)
    hub.parent = root
    hub.location = (0, 0, 0.16 * R)
    # pointer: a fat faceted arrowhead above 12 o'clock, pointing down into the rim
    pbp = L.PB()
    pw, ph = R * 0.26, R * 0.4
    tip = pbp.vert((0, R * 0.9, 0.3 * R))
    l = pbp.vert((-pw, R * 0.9 + ph, 0.26 * R))
    r_ = pbp.vert((pw, R * 0.9 + ph, 0.26 * R))
    c = pbp.vert((0, R * 0.9 + ph * 0.62, 0.4 * R))
    lb = pbp.vert((-pw, R * 0.9 + ph, 0.12 * R))
    rb = pbp.vert((pw, R * 0.9 + ph, 0.12 * R))
    tb = pbp.vert((0, R * 0.9, 0.16 * R))
    pbp.face([tip, c, l], 0)
    pbp.face([tip, r_, c], 1)
    pbp.face([l, c, r_], 1)
    pbp.face([l, lb, tb, tip], 2)
    pbp.face([tip, tb, rb, r_], 2)
    pbp.face([r_, rb, lb, l], 2)
    ptr = pbp.build(name + "_ptr", [L.mat_flat(name + "_pa", "#fff0dc", emit=accent, emit_str=0.4),
                                    L.mat_flat(name + "_pb", accent, emit=accent, emit_str=glow * 0.6),
                                    L.mat_flat(name + "_pc", _shade(accent, 0.5))], shadow=False)
    ptr.parent = root
    return root


def _angles(n):
    return [i * 2 * math.pi / n for i in range(n)]


def _shade(hexs, f):
    h = hexs.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


def health_bar(name, w, h, frac, fill_col, label, value, segs=10, glow=3.0):
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    face = L.mat_flat(name + "_face", "#2c2538")
    edge = L.mat_flat(name + "_edge", "#8a7d92")
    pl = H.plate(name + "_pl", w, h, face, edge, depth=h * 0.18, bevel=h * 0.22, dome=h * 0.04)
    pl.parent = root
    on = L.mat_flat(name + "_on", fill_col, emit=fill_col, emit_str=glow * 0.35)
    on2 = L.mat_flat(name + "_on2", _shade(fill_col, 0.7), emit=fill_col, emit_str=glow * 0.12)
    off = L.mat_flat(name + "_off", "#463d52")
    pb = L.PB()
    x0 = -w / 2 + w * 0.3
    x1 = w / 2 - w * 0.19
    sw = (x1 - x0) / segs
    sk = h * 0.18
    for k in range(segs):
        lit = k < round(frac * segs)
        xa = x0 + k * sw + sw * 0.08
        xb = x0 + (k + 1) * sw - sw * 0.08
        hh = h * 0.28
        pts = [(xa, -hh), (xb, -hh), (xb + sk, hh), (xa + sk, hh)]
        # a two-tone facet: raised ridge along the segment
        a = pb.vert((pts[0][0], pts[0][1], h * 0.24))
        b = pb.vert((pts[1][0], pts[1][1], h * 0.24))
        c = pb.vert((pts[2][0], pts[2][1], h * 0.24))
        d = pb.vert((pts[3][0], pts[3][1], h * 0.24))
        m1 = pb.vert(((xa + xb) / 2 + sk * 0.5, 0.0, h * 0.3))
        pb.face([a, b, m1], 0 if lit else 2)
        pb.face([b, c, m1], 1 if lit else 2)
        pb.face([c, d, m1], 0 if lit else 2)
        pb.face([d, a, m1], 1 if lit else 2)
    segs_ob = pb.build(name + "_segs", [on, on2, off], shadow=False)
    segs_ob.parent = root
    lab = L.mat_flat(name + "_lab", "#f3e6d4", emit="#f3e6d4", emit_str=0.5)
    t = L.text(name + "_t", label, (-w / 2 + h * 0.35, -h * 0.02, h * 0.2), h * 0.5, lab, extrude=h * 0.02,
               align="LEFT", shadow=False)
    t.parent = root
    tv = L.text(name + "_v", value, (-w / 2 + w * 0.035, -h * 0.9, h * 0.14), h * 0.5, lab,
                extrude=h * 0.02, align="LEFT", shadow=False, font=L.FONT_BOLD)
    tv.parent = root
    tv.location = (w / 2 - h * 0.35, -h * 0.02, h * 0.2)
    tv.data.align_x = "RIGHT"
    return root


CARD_COL = {"atk": "#d9574f", "def": "#35a8a2", "hack": "#8e62d4", "util": "#e09c42"}


def card(name, w, kind, title, cost, desc, icon, glow=0.0):
    """Chunky card slab: bevelled, a coloured header, a sunken art window with a faceted icon."""
    h = w * 1.4
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    col = CARD_COL[kind]
    face = L.mat_flat(name + "_face", "#eadcc7")
    edge = L.mat_flat(name + "_edge", _shade(col, 0.75), emit=col, emit_str=glow)
    pl = H.plate(name + "_pl", w, h, face, edge, depth=w * 0.05, bevel=w * 0.07, dome=w * 0.015)
    pl.parent = root
    # header band (faceted strip)
    hdr = L.mat_flat(name + "_hdr", col)
    hdr2 = L.mat_flat(name + "_hdr2", _shade(col, 0.82))
    pb = L.PB()
    y0, y1 = h * 0.26, h * 0.43
    xs = [-w * 0.42 + k * (w * 0.84 / 4) for k in range(5)]
    lo = [pb.vert((x, y0, w * 0.058)) for x in xs]
    hi = [pb.vert((x, y1, w * 0.058)) for x in xs]
    for k in range(4):
        pb.face([lo[k], lo[k + 1], hi[k + 1]], k % 2)
        pb.face([lo[k], hi[k + 1], hi[k]], 1 - k % 2)
    hb = pb.build(name + "_hdrb", [hdr, hdr2], shadow=False)
    hb.parent = root
    # art window: dark sunken facets
    win = L.mat_flat(name + "_win", "#2d2638")
    win2 = L.mat_flat(name + "_win2", "#3a3148")
    pbw = L.PB()
    ww, wh = w * 0.84, h * 0.36
    cy = -h * 0.02
    pts = [(-ww / 2, cy - wh / 2), (ww / 2, cy - wh / 2), (ww / 2, cy + wh / 2), (-ww / 2, cy + wh / 2)]
    vv = [pbw.vert((x, y, w * 0.062)) for x, y in pts]
    c = pbw.vert((w * 0.1, cy - wh * 0.1, w * 0.05))
    for k in range(4):
        pbw.face([vv[k], vv[(k + 1) % 4], c], k % 2)
    wb = pbw.build(name + "_winb", [win, win2], shadow=False)
    wb.parent = root
    # icon
    ic = _icon(name + "_icon", icon, w * 0.15, col)
    ic.parent = root
    ic.location = (0, cy, w * 0.1)
    # texts
    ink = L.mat_flat(name + "_ink", "#2b2233")
    white = L.mat_flat(name + "_white", "#fff6e8", emit="#fff6e8", emit_str=0.3)
    t = L.text(name + "_title", title, (0, (y0 + y1) / 2, w * 0.07), w * 0.15, white, extrude=w * 0.006,
               shadow=False)
    t.parent = root
    d = L.text(name + "_desc", desc, (0, -h * 0.33, w * 0.07), w * 0.105, ink, extrude=w * 0.004,
               shadow=False, font=L.FONT_BODY)
    d.parent = root
    # cost gem, top-left corner
    g = H.gem(name + "_cost", w * 0.13, L.mat_flat(name + "_ga", "#ffd37a", emit="#ffb640", emit_str=0.6),
              L.mat_flat(name + "_gb", "#c98a2e"), n=6, h=w * 0.08)
    g.parent = root
    g.location = (-w * 0.4, h * 0.44, w * 0.07)
    ct = L.text(name + "_ct", str(cost), (-w * 0.4, h * 0.44 - w * 0.005, w * 0.2), w * 0.19, ink,
                extrude=w * 0.006, shadow=False)
    ct.parent = root
    return root


def _icon(name, kind, s, col):
    m1 = L.mat_flat(name + "_a", col, emit=col, emit_str=0.8)
    m2 = L.mat_flat(name + "_b", _shade(col, 0.6), emit=col, emit_str=0.2)
    m3 = L.mat_flat(name + "_c", "#fff0dc")
    pb = L.PB()
    if kind == "blade":
        pts = [(-0.25 * s, -s), (0.25 * s, -s), (0.12 * s, 0.9 * s), (0, 1.25 * s), (-0.12 * s, 0.9 * s)]
        pb.prism([(x, y) for x, y in pts], 0, 0.2 * s, 1, 0, top_center_dz=0.15 * s)
        pb.prism([(-0.6 * s, -0.55 * s), (0.6 * s, -0.55 * s), (0.6 * s, -0.4 * s), (-0.6 * s, -0.4 * s)],
                 0, 0.3 * s, 1, 2)
    elif kind == "shield":
        pts = [(0, -1.1 * s), (0.85 * s, -0.3 * s), (0.8 * s, 0.9 * s), (-0.8 * s, 0.9 * s), (-0.85 * s, -0.3 * s)]
        pb.prism(pts, 0, 0.15 * s, 1, 0, top_center_dz=0.3 * s)
    elif kind == "chip":
        pb.prism(L.ngon(4, s, rot=math.pi / 4), 0, 0.15 * s, 1, 0, top_center_dz=0.25 * s)
        for k in range(3):
            y = (-0.5 + 0.5 * k) * s
            pb.prism([(0.72 * s, y - 0.08 * s), (1.1 * s, y - 0.08 * s), (1.1 * s, y + 0.08 * s),
                      (0.72 * s, y + 0.08 * s)], 0, 0.1 * s, 2, 2)
            pb.prism([(-1.1 * s, y - 0.08 * s), (-0.72 * s, y - 0.08 * s), (-0.72 * s, y + 0.08 * s),
                      (-1.1 * s, y + 0.08 * s)], 0, 0.1 * s, 2, 2)
    elif kind == "bolt":
        pts = [(0.2 * s, 1.2 * s), (-0.6 * s, -0.1 * s), (-0.05 * s, -0.1 * s), (-0.3 * s, -1.2 * s),
               (0.6 * s, 0.2 * s), (0.05 * s, 0.2 * s)]
        # non-convex: split into two convex quads
        pb.prism([pts[1], pts[2], pts[5], pts[0]], 0, 0.2 * s, 1, 0, top_center_dz=0.1 * s)
        pb.prism([pts[2], pts[3], pts[4], pts[5]], 0, 0.2 * s, 1, 0, top_center_dz=0.1 * s)
    elif kind == "eye":
        pb.prism(L.ngon(8, s, sy=0.55), 0, 0.12 * s, 1, 2, top_center_dz=0.1 * s)
        pb.prism(L.ngon(6, 0.4 * s), 0.12 * s, 0.25 * s, 1, 0, top_center_dz=0.12 * s)
    elif kind == "gear":
        n = 8
        for k in range(n):
            a = k * 2 * math.pi / n
            pb.prism(L.ngon(4, 0.28 * s), 0, 0.2 * s, 1, 0, cx=math.cos(a) * 0.85 * s, cy=math.sin(a) * 0.85 * s)
        pb.prism(L.ngon(n, 0.85 * s), 0, 0.25 * s, 1, 0, top_center_dz=0.2 * s)
    else:  # crystal
        pb.prism(L.ngon(5, 0.7 * s), -0.4 * s, 0.1 * s, 1, 0, top_center_dz=0.8 * s, bottom=True)
    return pb.build(name, [m1, m2, m3], shadow=False, seed=len(name))


def button(name, w, h, col, label, text_col="#2b1d2c", glow=1.2):
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    face = L.mat_flat(name + "_face", col, emit=col, emit_str=glow * 0.25)
    edge = L.mat_flat(name + "_edge", _shade(col, 0.6), emit=col, emit_str=glow * 0.2)
    pl = H.plate(name + "_pl", w, h, face, edge, depth=h * 0.16, bevel=h * 0.22, dome=h * 0.08)
    pl.parent = root
    tm = L.mat_flat(name + "_tm", text_col)
    t = L.text(name + "_t", label, (0, -h * 0.02, h * 0.16), h * 0.7, tm, extrude=h * 0.04, shadow=False)
    t.parent = root
    return root
