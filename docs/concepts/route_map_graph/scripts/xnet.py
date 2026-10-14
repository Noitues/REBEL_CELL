"""Family X, cyberspace: jacking in moves the route into the NET, the data layer of the same city (same camera,
same buildings, same run graph as the A-variants; built from the Blender G-buffer of the round 38 transit camera).

python xnet.py [X1 X2] [rest hover gif] [transition]
  X1 Light grid  black void, a luminous lot grid on the floor, the city as dark data blocks drawn only by their edges;
                 nodes are bright monoliths carrying the type icon; links are light-lanes. Hover: a trace wall (a
                 ribbon of light with a wall standing on it) races down the branch.
  X2 Dense net   facades of scrolling hex, glitch rows, corp ICE shells round every node (Meridian tier-II red),
                 packets of bits on every link. Hover: the branch is DECRYPTED, its shells crack open and the icons
                 inside light white-hot.
  transition     one frame of the jack-in: the 3D city dissolving into X1 with the locked binary-bits dissolve
                 (round 35 bitmask: cells arrive by distance from the operative plus jitter, 0/1 glyphs at the front).
All randomness is seeded.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import frame as FR  # noqa: E402
import rgraph as G  # noqa: E402
import directions as D  # noqa: E402
import avariants as AV  # noqa: E402
import gbuf as GB  # noqa: E402
import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import r32ui as U32  # noqa: E402
import sticker_lib31 as SL  # noqa: E402

W, H = FR.W, FR.H
HOVER = AV.HOVER
ICE = (255, 46, 40)            # Meridian tier-II red (bible 2.4): the corp's ICE, kept off the option orange
GRIDC = (60, 200, 255)
STATE_COL = {"walked": FR.LIME, "current": FR.LIME, "option": FR.ORANGE, "reach": FR.WHITE, "target": (255, 60, 70),
             "grey": FR.GREY}
MONO = SL.MONO


def f_mono(px):
    return K.F(MONO, px)


# ================================================================ the net world
def world_X1(gb):
    """Black void; the lot grid glows on the floor; buildings are dark blocks drawn by their edges."""
    img = np.zeros((H, W, 3), np.float32) + np.array([0.008, 0.01, 0.022], np.float32)
    gx, gy = gb.gpos[..., 0], gb.gpos[..., 1]
    ground = ~gb.bld
    U = 6.0

    def lines(v, pitch, w):
        f = np.abs(((v / pitch) + 0.5) % 1.0 - 0.5) * pitch
        return np.clip(1 - f / w, 0, 1)
    major = np.maximum(lines(gx, U, 0.16), lines(gy, U, 0.16))
    minor = np.maximum(lines(gx, U / 4, 0.05), lines(gy, U / 4, 0.05))
    yfade = (0.35 + 0.65 * (np.arange(H, dtype=np.float32) / H))[:, None]
    g = (major * 0.55 + minor * 0.12) * ground * yfade
    img += g[..., None] * (np.array(GRIDC, np.float32) / 255.0)
    # data blocks: near-black faces, roofs a touch lighter, edges cyan-white
    blk = gb.bld
    img[blk] = np.array([0.018, 0.022, 0.045], np.float32)
    img[gb.roof] = np.array([0.03, 0.04, 0.075], np.float32)
    zf = np.clip(gb.z / 30.0, 0, 1)
    e = gb.edge.astype(np.float32) * (0.35 + 0.4 * zf)
    img += e[..., None] * np.array([0.35, 0.8, 1.0], np.float32)
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    em = Image.fromarray((np.clip(e * 255, 0, 255)).astype(np.uint8))
    out = K.add_glow(out, em, (60, 170, 255), 6, 0.6)
    gm = Image.fromarray((np.clip(major * ground * yfade * 255, 0, 255)).astype(np.uint8))
    out = K.add_glow(out, gm, GRIDC, 5, 0.35)
    return out


_HEX = {}


def hex_tile(seed=3, w=512, h=512):
    if seed not in _HEX:
        rng = random.Random(seed)
        im = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(im)
        f = f_mono(11)
        for y in range(0, h, 12):
            x = 0
            while x < w:
                s = "".join(rng.choice("0123456789ABCDEF") for _ in range(2))
                d.text((x, y), s, font=f, fill=rng.choice((90, 140, 200, 255)))
                x += 18
        _HEX[seed] = np.asarray(im, np.float32) / 255.0
    return _HEX[seed]


def world_X2(gb, t=0.0):
    """Dense net: every facade is scrolling hex (world-mapped), tinted per building; glitch rows; scanlines."""
    img = np.zeros((H, W, 3), np.float32) + np.array([0.02, 0.008, 0.03], np.float32)
    tile = hex_tile()
    th, tw = tile.shape
    x, y, z = gb.pos[..., 0], gb.pos[..., 1], gb.z
    facing_x = np.abs(gb.nrm[..., 0]) > np.abs(gb.nrm[..., 1])
    u = np.where(facing_x, y, x)
    scroll = t * 40.0
    tu = (np.mod(u * 14.0, tw)).astype(int)
    tv = (np.mod(-z * 14.0 + scroll * (1 + (gb.idc % 3)), th)).astype(int)
    hx = tile[tv, tu] * gb.wall
    # roofs: a denser hex
    rv = (np.mod(y * 14.0, th)).astype(int)
    ru = (np.mod(x * 14.0, tw)).astype(int)
    hx = hx + tile[rv, ru] * gb.roof * 0.5
    pal = np.array([[0.36, 0.88, 1.0], [1.0, 0.24, 0.66], [0.70, 0.40, 1.0], [0.36, 0.88, 1.0], [1.0, 0.85, 0.3]],
                   np.float32)
    col = pal[(gb.idc * 7) % len(pal)]
    img += (hx * 0.85)[..., None] * col
    img[gb.bld] += np.array([0.02, 0.012, 0.04], np.float32)
    img += (gb.edge * 0.8)[..., None] * col
    # the ground: a dense bit floor (faint)
    gx, gy = gb.gpos[..., 0], gb.gpos[..., 1]
    gtv = (np.mod(gy * 10.0, th)).astype(int)
    gtu = (np.mod(gx * 10.0, tw)).astype(int)
    img += (tile[gtv, gtu] * (~gb.bld) * 0.12)[..., None] * np.array([0.5, 0.3, 1.0], np.float32)
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    # glitch: seeded row shifts with an RGB split, scanlines
    rng = random.Random(int(t * 10) + 5)
    a = np.asarray(out).copy()
    for _ in range(14):
        y0 = rng.randint(130, H - 80)
        hh = rng.randint(2, 9)
        sh = rng.randint(-24, 24)
        a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], sh, axis=1)
        a[y0:y0 + hh, :, 0] = np.roll(a[y0:y0 + hh, :, 0], 4, axis=1)
    a[::3, :, :3] = (a[::3, :, :3] * 0.72).astype(np.uint8)
    out = Image.fromarray(a)
    em = Image.fromarray((np.clip(hx * 200, 0, 255)).astype(np.uint8))
    return K.add_glow(out, em, (160, 120, 255), 5, 0.35)


# ================================================================ nodes in the net
def icon_img(kind, px):
    return U32.icon("rack" if kind == "target" else kind, px)


def monolith(img, i, x, y, state, hover=False, alpha=1.0):
    """X1 node: a bright standing monolith (iso hex prism) in the state colour, the type icon on its face."""
    col = STATE_COL[state]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    big = state in ("option", "current", "target")
    w = 30 if big else 24
    h = 74 if big else 58
    if hover:
        h += 14
    by = y + 26                                         # base on the floor under the node point
    top = by - h
    L = [(x - w, by - 8), (x, by), (x, top + 8), (x - w, top)]
    R = [(x, by), (x + w, by - 8), (x + w, top), (x, top + 8)]
    T = [(x - w, top), (x, top + 8), (x + w, top), (x, top - 8)]
    k = 1.0 if state != "grey" else 0.6
    d.polygon(L, fill=tuple(int(c * 0.55 * k) for c in col) + (235,))
    d.polygon(R, fill=tuple(int(c * 0.32 * k) for c in col) + (235,))
    d.polygon(T, fill=tuple(int(min(255, c * 1.0)) for c in col) + (255,))
    for poly in (L, R, T):
        d.line(poly + [poly[0]], fill=tuple(min(255, int(c * 0.6 + 110)) for c in col) + (255,), width=2)
    # icon plate on the front edge
    px = 40 if big else 32
    ic = icon_img(G.KIND[i], px) if G.KIND[i] != "start" else FR.start_disc(px)
    if state == "grey":
        ic = Image.merge("RGBA", (*[ic.convert("L")] * 3, ic.split()[3]))
    lay.alpha_composite(ic, (int(x - px / 2), int(top + 14)))
    if alpha < 1:
        lay.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    if state != "grey" and alpha >= 0.99:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon([(x - w, by - 8), (x, by), (x + w, by - 8), (x + w, top), (x, top - 8), (x - w, top)], fill=255)
        img = K.add_glow(img, m, col, 14, 0.55 if big else 0.3)
        # floor halo
        hm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(hm).ellipse([x - 44, by - 12, x + 44, by + 12], fill=255)
        img = K.add_glow(img, hm, col, 10, 0.4)
    img.alpha_composite(lay)
    return img


def ice_shell(img, x, y, cracked=0.0, alpha=1.0, seed=0, r=46):
    """X2: the corp's ICE round a node: a hexagonal shell with a honeycomb skin (Meridian tier-II red).
    cracked 0..1: the shell splits into plates that fly out (decrypted)."""
    rng = random.Random(seed)
    lay = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    S = 2
    hexv = [(x + r * math.cos(math.radians(60 * k + 30)), y + r * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    if cracked <= 0:
        d.polygon([(px * S, py * S) for px, py in hexv], fill=ICE + (int(70 * alpha),))
        # honeycomb skin
        cr = 7
        for gy in range(-6, 7):
            for gx in range(-6, 7):
                cx = x + gx * cr * 1.75 + (gy % 2) * cr * 0.875
                cy = y + gy * cr * 1.5
                if math.hypot(cx - x, cy - y) > r - 6:
                    continue
                hv = [((cx + cr * 0.8 * math.cos(math.radians(60 * k + 30))) * S, (cy + cr * 0.8 * math.sin(math.radians(60 * k + 30))) * S)
                      for k in range(6)]
                d.polygon(hv, outline=ICE + (int(150 * alpha),))
        d.line([(px * S, py * S) for px, py in hexv + [hexv[0]]], fill=ICE + (int(255 * alpha),), width=3 * S)
        d.line([((x + (px - x) * 1.12) * S, (y + (py - y) * 1.12) * S) for px, py in hexv + [hexv[0]]],
               fill=ICE + (int(120 * alpha),), width=S)
    else:
        for k in range(6):                                # six plates, pushed outward and turned
            a0, a1 = hexv[k], hexv[(k + 1) % 6]
            mx, my = (a0[0] + a1[0]) / 2 - x, (a0[1] + a1[1]) / 2 - y
            push = 30 * cracked + rng.uniform(0, 14) * cracked
            ln = math.hypot(mx, my) or 1
            ox, oy = mx / ln * push, my / ln * push
            tri = [(x + ox * 0.6, y + oy * 0.6), (a0[0] + ox, a0[1] + oy), (a1[0] + ox, a1[1] + oy)]
            d.polygon([(px * S, py * S) for px, py in tri], fill=ICE + (int(60 * (1 - 0.6 * cracked)),),
                      outline=(255, 210, 200, int(255 * (1 - 0.3 * cracked))), width=2 * S)
        for k in range(10):                                # crack sparks / bits flying
            ang = rng.uniform(0, math.tau)
            rr = r + 30 * cracked * rng.uniform(0.6, 1.4)
            d.text(((x + rr * math.cos(ang)) * S, (y + rr * math.sin(ang)) * S), rng.choice("01"), font=f_mono(28),
                   fill=(255, 240, 230, int(230 * cracked)))
    lay = lay.resize((W, H), Image.LANCZOS)
    img = K.add_glow(img, lay.split()[3], ICE if cracked <= 0 else (255, 230, 220), 8, 0.35 * alpha)
    img.alpha_composite(lay)
    return img


# ================================================================ links in the net
def light_lanes(img, v, var, t, bedges):
    lay = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    glow = Image.new("L", (W, H), 0)
    dg = ImageDraw.Draw(glow)
    rng = random.Random(21)
    for e in G.EDGES:
        s = v.es[e]
        pts = v.route(*e)
        P2 = [(x * 2, y * 2) for x, y in pts]
        if s == "grey":
            d.line(P2, fill=FR.GREY + (int(255 * FR.GREY_A),), width=4, joint="curve")
            continue
        a = v.edge_alpha(e)
        col = {"walked": FR.LIME, "option": FR.ORANGE, "future": FR.WHITE}[s]
        if var == "X1":
            for off in (-5, 5):                            # a light-lane: two rails and a hot core
                q = FR.offset_poly(pts, off)
                d.line([(x * 2, y * 2) for x, y in q], fill=col + (int(170 * a),), width=3, joint="curve")
            d.line(P2, fill=col + (int(255 * a),), width=4 if s == "future" else 6, joint="curve")
        else:
            d.line(P2, fill=col + (int(200 * a),), width=6, joint="curve")
            L = AV.poly_len(pts)
            s0 = rng.random() * 30 + t * 120
            while s0 < L:                                 # packets of bits riding the link
                px, py = AV.point_at(pts, s0 % L)
                d.text((px * 2 - 8, py * 2 - 16), rng.choice("01"), font=f_mono(26), fill=(255, 255, 255, int(230 * a)))
                s0 += 34
        dg.line(pts, fill=int(200 * a), width=6, joint="curve")
    lay = lay.resize((W, H), Image.LANCZOS)
    img = K.add_glow(img, glow, (255, 220, 170), 8, 0.4)
    img.alpha_composite(lay)
    if t is not None and var == "X1":
        img = trace_wall(img, v, t, bedges)
    return img


def trace_wall(img, v, t, bedges):
    """X1 hover: a light ribbon races each branch link in turn, a translucent wall of light standing on it."""
    wall = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wall)
    core = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    dc = ImageDraw.Draw(core)
    heads = []
    for e in bedges:
        dpt = G.LAYER[e[0]] - G.LAYER[HOVER]
        u = float(np.clip((t - 0.15 * (dpt + 1)) / 0.18, 0, 1))
        if u <= 0:
            continue
        p = v.route(*e)
        L = AV.poly_len(p)
        seg = AV.sub_poly(p, 0, L * u)
        hgt = 16
        for (x0, y0), (x1, y1) in zip(seg, seg[1:]):
            dw.polygon([(x0, y0), (x1, y1), (x1, y1 - hgt), (x0, y0 - hgt)], fill=FR.ORANGE + (70,))
            dw.line([(x0, y0 - hgt), (x1, y1 - hgt)], fill=(255, 200, 140, 160), width=1)
        dc.line([(x * 2, y * 2) for x, y in seg], fill=(255, 245, 225, 255), width=6, joint="curve")
        if u < 1:
            heads.append(AV.point_at(p, L * u))
    img.alpha_composite(wall)
    c = core.resize((W, H), Image.LANCZOS)
    img = K.add_glow(img, c.split()[3], FR.ORANGE, 10, 0.9)
    img.alpha_composite(c)
    for x, y in heads:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([x - 10, y - 10, x + 10, y + 10], fill=255)
        img = K.add_glow(img, m, (255, 240, 220), 18, 1.5)
    return img


# ================================================================ page
def build(var, t, gb=None):
    gb = gb or AV.gbuf()
    v = AV.view(t is not None)
    img = world_X1(gb) if var == "X1" else world_X2(gb, t or 0.0)
    bnodes, bedges = AV.branch(v) if t is not None else ({}, [])
    img = light_lanes(img, v, var, t if t is not None else 0.0, bedges if t is not None else [])
    if var == "X1" and t is None:
        pass
    order = sorted(G.NODES, key=lambda i: (v.pos[i][1], i))
    for i in order:
        x, y = v.pos[i]
        s = v.st[i]
        a = v.node_alpha(i)
        if var == "X1":
            img = monolith(img, i, x, y, s, hover=(i == HOVER and t is not None), alpha=a)
        else:
            cracked = 0.0
            if t is not None and i in bnodes:
                cracked = AV.climb_t(t, bnodes[i], dur=0.2, lead=0.12, step=0.15)
            if s in ("walked", "current", "grey"):
                img = FR.draw_node(img, i, x, y, s, alpha=a)
            elif cracked <= 0:
                img = FR.draw_node(img, i, x, y, s, alpha=a * 0.85, glow=False)
                img = ice_shell(img, x, y, 0.0, alpha=a, seed=sum(map(ord, i)), r=48 if G.KIND[i] != "target" else 58)
            else:                                        # decrypted: the plates fly off, the icon runs white-hot
                img = ice_shell(img, x, y, cracked, alpha=a, seed=sum(map(ord, i)), r=48 if G.KIND[i] != "target" else 58)
                m = Image.new("L", (W, H), 0)
                ImageDraw.Draw(m).ellipse([x - 36, y - 36, x + 36, y + 36], fill=255)
                img = K.add_glow(img, m, (255, 245, 230), 14, 0.6 * cracked)
                img = FR.draw_node(img, i, x, y, s, hover=(i == HOVER), alpha=a)
    img = D.draw_marks(img, v)
    pen = D.target_pen(v)
    if t is not None:
        img = D.draw_tags(img, v)
    img = FR.dossier(img)
    img = FR.chrome_top(img, "You're in their net now. The Rack branch is ICE all the way up." if var == "X2"
                        else "Jacked in. Pick a lane.")
    img = FR.route_panel(img, len(v.opts), None)
    if t is not None:
        img = FR.node_file(img, HOVER, "52 / 60 on arrival")
    img, kbox = FR.legend(img, False)
    img = FR.finish_pencil(img, pen)
    if t is not None:
        hx, hy = v.anchor(HOVER)
        img = FR.cursor(img, hx + 8, hy + 6)
    return img


def bitmask(size, t, seed, origin, cell=16):
    """The locked round 35 binary-bits dissolve mask (transitions.py), unchanged."""
    Wd, Hd = size
    gw, gh = Wd // cell + 1, Hd // cell + 1
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
    d = np.hypot(xx * cell - origin[0], (yy * cell - origin[1]) * 1.6) / 2000.0
    thr = d + rng.random((gh, gw)) * 0.35
    m = (thr < t * 1.35).astype(np.uint8) * 255
    return Image.fromarray(m).resize((gw * cell, gh * cell), Image.NEAREST).crop((0, 0, Wd, Hd))


def transition(t=0.36):
    gb = AV.gbuf()
    v = AV.view(False)
    city = AV.build("A1", None)
    net = build("X1", None, gb)
    cx, cy = v.anchor(v.walked[-1])
    m = bitmask((W, H), t, 5, (cx, cy))
    chrome = Image.new("L", (W, H), 0)
    dc = ImageDraw.Draw(chrome)
    for bx in ((0, 0, W, 128), (0, 128, 272, 460), (1630, 128, W, 410), (470, 1018, 1440, H)):
        dc.rectangle(bx, fill=255)
    m = Image.fromarray(np.minimum(np.asarray(m), 255 - np.asarray(chrome)))
    img = Image.composite(net, city, m)
    # the front: 0/1 glyphs in lime, white-hot just behind the edge (bible: bits white-hot for the first 60-100 ms)
    d = ImageDraw.Draw(img)
    rng = random.Random(10)
    f = f_mono(16)
    edge = np.asarray(m.filter(ImageFilter.FIND_EDGES))
    ys, xs = np.nonzero(edge[::16, ::16])
    for y, x in list(zip(ys, xs))[:: max(1, len(ys) // 320)]:
        px, py = x * 16, y * 16
        if py < 130 or py > 1015 or (px < 275 and py < 460) or (px > 1625 and py < 410):
            continue                                       # the chrome stays put; only the world dissolves
        hot = rng.random() < 0.35
        d.text((x * 16 + 2, y * 16), rng.choice("01"), font=f, fill=((255, 255, 240) if hot else FR.LIME) + (235,))
    return img


def gif(var, n=15, ms=80):
    gb = AV.gbuf()
    frames = []
    for k in range(n):
        t = k / (n - 1)
        im = FR.RL.bloom(build(var, t, gb), 0.10, 0.84, 8).convert("RGB")
        frames.append(im.crop((300, 130, 1620, 1010)).resize((880, 587), Image.LANCZOS))
    frames += [frames[-1]] * 6
    path = os.path.join(FR.OUT, "%s_motion.gif" % var)
    FR.save_gif(frames, [ms] * n + [ms] * 5 + [900], path)


if __name__ == "__main__":
    args = sys.argv[1:]
    vs = [a for a in args if a in ("X1", "X2")] or ["X1", "X2"]
    what = [a for a in args if a in ("rest", "hover", "gif", "transition")] or ["rest", "hover", "gif", "transition"]
    for var in vs:
        if "rest" in what:
            FR.save(build(var, None), "%s_rest.png" % var)
        if "hover" in what:
            FR.save(build(var, 1.0), "%s_hover.png" % var)
        if "gif" in what:
            gif(var)
    if "transition" in what:
        FR.save(transition(), "X_transition.png")
