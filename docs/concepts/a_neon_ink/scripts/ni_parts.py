"""NEON INK parts: layered spinners, sticker cards, binary shards, the inked city."""
import math, random
from ni_lib import *

# ================================================================ spinners
SLICE = {"atk": "pink", "def": "cyan", "evd": "gain", "crit": "pink_hot", "afl": "#C85AFF", "miss": "#6A6A6A"}


def wproj(cx, cy, r, th, h, k=0.80, s=1.0):
    """Wheel-space -> screen. The wheel lies on a disc tilted toward the viewer:
    th around the disc, h = height above the disc (px, pushes up the screen)."""
    return (cx + r * math.cos(th), cy + r * math.sin(th) * k - h * s)


def ring(cx, cy, r, h, k=0.80, a0=0.0, a1=2 * math.pi, n=96):
    return [wproj(cx, cy, r, a0 + (a1 - a0) * i / n, h, k) for i in range(n + 1)]


def glyph(pl, layer, kind, x, y, s, color, hand, w=2.4):
    """Slice glyphs, inked (read without colour: shape per type)."""
    if kind == "atk":
        ink(pl, layer, [(x - s * .5, y + s * .5), (x + s * .5, y - s * .5)], color, w, 1, hand, .3)
        ink(pl, layer, [(x - s * .45, y + s * .05), (x - s * .05, y + s * .45)], color, w, 1, hand, .3)
    elif kind == "def":
        ink(pl, layer, [(x - s * .45, y - s * .45), (x + s * .45, y - s * .45), (x + s * .4, y + s * .05), (x, y + s * .5),
                        (x - s * .4, y + s * .05)], color, w, 1, hand, .3, closed=True)
    elif kind == "evd":
        for dx in (-s * .25, s * .15):
            ink(pl, layer, [(x + dx - s * .2, y - s * .4), (x + dx + s * .15, y), (x + dx - s * .2, y + s * .4)], color, w, 1, hand, .3)
    elif kind == "crit":
        for i in range(8):
            a = i * math.pi / 4; rr = s * (.55 if i % 2 == 0 else .3)
            ink(pl, layer, [(x, y), (x + rr * math.cos(a), y + rr * math.sin(a))], color, w, 1, hand, .2)
    elif kind == "afl":
        ink(pl, layer, [(x, y - s * .5), (x + s * .32, y + s * .1), (x, y + s * .45), (x - s * .32, y + s * .1)], color, w, 1, hand, .3,
            closed=True, smooth=True)
    else:
        ink(pl, layer, [(x - s * .4, y), (x + s * .4, y)], color, w, .7, hand, .3)


def spinner(back, pl, cx, cy, r, slices, owner, hand, needle=0.0, hp=(60, 60), label="",
            accent="pink", k=0.80, hit=None, spin=0.0):
    """A stack of inked rings at different heights: shadow, bezel wall, bezel face,
    recessed glass, slice inlays, raised hub, needle, glass sheen, HP arc.
    back: plane under (shadow, halo); pl: the wheel plane."""
    bez_h = 34; glass_h = 12; hub_h = 30; needle_h = 40
    edge = accent
    # 1 cast shadow on the table/UI (offset, soft, separate blurred plane)
    fill_poly(back, "shadow", ellipse(cx + 14, cy + 34, r * 1.06, r * k * 1.06, 72), "#000000", 0.75)
    # light spill: the wheel's neon throws a pool onto whatever is under it
    fill_poly(back, "spill", ellipse(cx, cy + 10, r * 1.45, r * k * 1.35, 72), edge, 0.10)
    fill_poly(back, "spill", ellipse(cx, cy + 10, r * 1.2, r * k * 1.15, 72), edge, 0.10)
    # 2 bezel outer wall: bottom ellipse front half + top ellipse, filled dark metal
    front = ring(cx, cy, r, 0, k, 0, math.pi, 48)
    top_back = ring(cx, cy, r, bez_h, k, math.pi, 2 * math.pi, 48)
    wall = front + [wproj(cx, cy, r, math.pi, bez_h, k)] + top_back[1:] + [wproj(cx, cy, r, 0, bez_h, k)]
    fill_poly(pl, "body", wall, "#0C0F17", 1.0)
    fill_poly(pl, "body", ring(cx, cy, r, bez_h, k, n=72), "#161A24", 1.0)
    # wall hatching (value: the side wall is darker, hatch gives it form)
    for i in range(0, 60):
        th = i / 60 * math.pi
        a = wproj(cx, cy, r, th, 2, k); b = wproj(cx, cy, r, th, bez_h - 3, k)
        shade = 0.35 + 0.5 * abs(math.cos(th))
        ink(pl, "body", [a, b], "#2A3346", 1.0, shade, hand, 0.2, taper=0.3)
    # bottom rim + top rim silhouettes
    ink(pl, "line", front, edge, 3.2, 1, hand, 0.5, taper=0.6)
    ink(pl, "line", [wproj(cx, cy, r, 0, 0, k), wproj(cx, cy, r, 0, bez_h, k)], edge, 2.2, 1, hand, .3)
    ink(pl, "line", [wproj(cx, cy, r, math.pi, 0, k), wproj(cx, cy, r, math.pi, bez_h, k)], edge, 2.2, 1, hand, .3)
    ink(pl, "line", ring(cx, cy, r, bez_h, k, n=96), edge, 3.6, 1, hand, 0.5, closed=True)
    # owner hardware
    if owner == "op":
        # scratched paper-stickered bezel: tape strips + scratches
        for a in (0.6, 2.3, 4.1):
            p1 = wproj(cx, cy, r * 0.97, a, bez_h, k); p2 = wproj(cx, cy, r * 0.97, a + 0.22, bez_h, k)
            ink(pl, "line", [p1, p2], "paper2", 9, 0.85, hand, 0.4, taper=0.9)
        for i in range(14):
            a = hand.r.uniform(0, 6.28)
            p1 = wproj(cx, cy, r * 0.93, a, bez_h, k); p2 = wproj(cx, cy, r * 0.93, a + 0.05, bez_h, k)
            ink(pl, "line", [p1, p2], "white", 0.8, 0.5, hand, 0.2)
    else:
        # machined hostile bezel: notches + corp concentric rings (Halcyon pattern)
        for i in range(24):
            a = i / 24 * 2 * math.pi
            p1 = wproj(cx, cy, r * 1.0, a, bez_h, k); p2 = wproj(cx, cy, r * 1.09, a + 0.06, bez_h, k)
            p3 = wproj(cx, cy, r * 1.0, a + 0.12, bez_h, k)
            ink(pl, "line", [p1, p2, p3], edge, 2.0, 1, hand, 0.2, taper=0.8)
        ink(pl, "line", ring(cx, cy, r * 0.955, bez_h, k), edge, 1.0, 0.6, hand, 0.3, closed=True)
    # 3 bezel face ticks (30-tick wheel)
    for i in range(30):
        a = i / 30 * 2 * math.pi + spin
        maj = i % 5 == 0
        p1 = wproj(cx, cy, r * 0.90, a, bez_h, k); p2 = wproj(cx, cy, r * (0.97 if maj else 0.94), a, bez_h, k)
        ink(pl, "line", [p1, p2], "white" if maj else edge, 2.0 if maj else 1.0, 0.9 if maj else 0.6, hand, 0.1, taper=0.7)
    # 4 recess: the glass sits lower; inner wall visible on the far side
    ri = r * 0.86
    inner_top = ring(cx, cy, ri, bez_h, k, math.pi, 2 * math.pi, 48)
    inner_bot = ring(cx, cy, ri, glass_h, k, math.pi, 2 * math.pi, 48)
    fill_poly(pl, "body", ring(cx, cy, ri, glass_h, k), "#070A12", 1.0)
    fill_poly(pl, "body", inner_top + inner_bot[::-1], "#1E2433", 1.0)
    for i in range(1, 40):
        th = math.pi + i / 40 * math.pi
        ink(pl, "body", [wproj(cx, cy, ri, th, bez_h - 2, k), wproj(cx, cy, ri, th, glass_h + 2, k)], "#35405A", 0.9, 0.7, hand, 0.1)
    ink(pl, "line", ring(cx, cy, ri, bez_h, k), edge, 2.0, 0.9, hand, 0.4, closed=True)
    # 5 slice inlays (translucent wedges, bright rims, bold glyphs) on the glass plane
    tot = sum(s[1] for s in slices)
    a = -math.pi / 2 + spin
    r_out, r_in = ri * 0.97, ri * 0.50
    for kind, span in slices:
        a1 = a + span / tot * 2 * math.pi
        c = SLICE[kind]
        outer = [wproj(cx, cy, r_out, a + (a1 - a) * i / 24, glass_h, k) for i in range(25)]
        inner = [wproj(cx, cy, r_in, a1 - (a1 - a) * i / 24, glass_h, k) for i in range(25)]
        wedge = outer + inner
        fill_poly(pl, "slice", wedge, c, 0.30 if kind != "miss" else 0.12)
        # inner lit edge (value toward the rim = depth in the glass)
        ink(pl, "slice", outer, c, 3.0, 0.95, hand, 0.3, taper=0.7)
        ink(pl, "slice", [outer[0], inner[-1]], "#05070C", 3.0, 1, hand, 0.2)
        ink(pl, "slice", [outer[0], inner[-1]], c, 1.0, 0.8, hand, 0.2)
        am = (a + a1) / 2
        gx, gy = wproj(cx, cy, (r_out + r_in) / 2, am, glass_h, k)
        glyph(pl, "glyph", kind, gx, gy, r * 0.13, mix_hex(c, "#FFFFFF", 0.35), hand, 2.6)
        a = a1
    ink(pl, "slice", ring(cx, cy, r_in, glass_h, k), "#3A4660", 1.2, 1, hand, 0.3, closed=True)
    # 6 raised hub: its own wall + face (it sits proud of the glass)
    rh = ri * 0.44
    hfront = ring(cx, cy, rh, glass_h, k, 0, math.pi, 36)
    htop = ring(cx, cy, rh, hub_h, k, math.pi, 2 * math.pi, 36)
    fill_poly(pl, "hub", ring(cx, cy, rh * 1.06, glass_h - 4, k), "#000000", 0.6)
    fill_poly(pl, "hub", hfront + htop, "#10141E", 1.0)
    fill_poly(pl, "hub", ring(cx, cy, rh, hub_h, k), "#0A0D16", 1.0)
    ink(pl, "hub", hfront, edge, 2.0, 1, hand, 0.3)
    ink(pl, "hub", ring(cx, cy, rh, hub_h, k), edge, 2.4, 1, hand, 0.4, closed=True)
    ink(pl, "hub", ring(cx, cy, rh * 0.84, hub_h, k), edge, 0.8, 0.5, hand, 0.2, closed=True)
    # 7 needle above the glass, with its cast shadow on the glass (offset = height)
    tip = wproj(cx, cy, r_out * 0.98, needle, needle_h, k)
    base = wproj(cx, cy, rh * 0.2, needle, needle_h, k)
    cw = wproj(cx, cy, rh * 0.7, needle + math.pi, needle_h, k)
    stip = wproj(cx + 10, cy + 18, r_out * 0.98, needle, glass_h, k)
    sbase = wproj(cx + 10, cy + 18, rh * 0.2, needle, glass_h, k)
    ink(pl, "needle", [sbase, stip], "#000000", 7, 0.55, None, 0, taper=0.4)
    ink(pl, "needle", [cw, base, tip], "acid", 4.2, 1, hand, 0.2, taper=0.25)
    ink(pl, "needle", [base, tip], "#FFFFFF", 1.2, 0.9, hand, 0.1)
    fill_poly(pl, "needle", ellipse(cw[0], cw[1], 9, 9 * k, 16), "acid", 1.0)
    fill_poly(pl, "needle", ellipse(base[0], base[1], 7, 7 * k, 16), "#FFFFFF", 1.0)
    # 8 glass sheen: two arcs floating above everything (the dome)
    ink(pl, "sheen", ring(cx - r * 0.05, cy, r * 0.78, needle_h + 12, k, math.pi * 1.12, math.pi * 1.42, 20), "#FFFFFF", 4.0, 0.35, hand, 0.3, taper=0.1)
    ink(pl, "sheen", ring(cx - r * 0.05, cy, r * 0.70, needle_h + 12, k, math.pi * 1.15, math.pi * 1.28, 12), "#FFFFFF", 1.4, 0.55, hand, 0.2, taper=0.1)
    # 9 HP arc under the wheel (segmented, thick)
    frac = hp[0] / hp[1]
    segs = 24
    hpcol = "gain" if frac >= 0.5 else ("amber" if frac >= 0.25 else "harm")
    for i in range(segs):
        t0 = math.pi * 0.18 + (math.pi * 0.64) * i / segs
        t1 = t0 + math.pi * 0.64 / segs * 0.72
        on = i < int(round(frac * segs))
        pts = ring(cx, cy, r * 1.14, -4, k, t0, t1, 4)
        ink(pl, "line", pts, hpcol if on else "#1C2433", 11, 1 if on else 0.9, None, 0, taper=0)
    return dict(tip=tip, hub=wproj(cx, cy, 0, 0, hub_h, k))


# ================================================================ stickers
def sticker_card(pl, x, y, w, h, rot, title, cost, tcolor, hand, art="spin", lift=0.0, sub=""):
    """A card printed as a die-cut sticker: white kiss-cut border, paper face, ink art,
    coloured title band, tape-free (it sticks). lift>0 = mid-slap (bigger, far shadow)."""
    cx, cy = x + w / 2, y + h / 2
    s = 1 + lift * 0.22
    def T(pts):
        return rot_pts([(cx + (px - cx) * s, cy + (py - cy) * s - lift * 40) for px, py in pts], cx, cy, rot)
    b = 7
    # hard shadow (further + softer with lift)
    sh = rot_pts([(px + 7 + lift * 26, py + 9 + lift * 44) for px, py in rect(x - b, y - b, w + 2 * b, h + 2 * b)], cx, cy, rot)
    fill_poly(pl, "shadow", sh, "#000000", 0.55 - lift * 0.2)
    # die-cut border (rounded feel from overshooting ink)
    fill_poly(pl, "paper", T(rect(x - b, y - b, w + 2 * b, h + 2 * b)), "#FBFAF6", 1.0)
    fill_poly(pl, "paper", T(rect(x, y, w, h)), "paper", 1.0)
    # title band
    fill_poly(pl, "paper", T(rect(x, y, w, h * 0.2)), tcolor, 1.0)
    # art window with halftone dots and an inked motif
    ax, ay, aw, ah = x + w * 0.1, y + h * 0.27, w * 0.8, h * 0.44
    fill_poly(pl, "paper", T(rect(ax, ay, aw, ah)), "paper2", 1.0)
    r = hand.r
    for i in range(10):
        for j in range(7):
            px, py = ax + aw * (i + .5) / 10, ay + ah * (j + .5) / 7
            d = math.hypot(px - (ax + aw * .7), py - (ay + ah * .3)) / aw
            rr = max(0.6, 3.2 - d * 4)
            fill_poly(pl, "art", T(ellipse(px, py, rr, rr, 8)), tcolor, 0.55)
    mx, my = ax + aw / 2, ay + ah / 2
    if art == "spin":
        ink(pl, "art", T(ellipse(mx, my, ah * .36, ah * .36, 40)), "ink", 2.6, 1, hand, 0.6, closed=True)
        ink(pl, "art", T(ellipse(mx, my, ah * .36, ah * .36, 30, -2.4, -0.6)), "ink", 1.4, 1, hand, .6)
        ink(pl, "art", T([(mx, my), (mx + ah * .3, my - ah * .2)]), "ink", 3, 1, hand, .4)
        ink(pl, "art", T([(mx + ah * .42, my - ah * .02), (mx + ah * .5, my - ah * .2), (mx + ah * .3, my - ah * .14)]), "ink", 2.2, 1, hand, .3)
    elif art == "fist":
        pts = [(mx - ah * .2, my + ah * .45), (mx - ah * .22, my - ah * .05), (mx - ah * .28, my - ah * .3), (mx - ah * .1, my - ah * .42),
               (mx + ah * .22, my - ah * .38), (mx + ah * .26, my - ah * .1), (mx + ah * .18, my + ah * .45)]
        ink(pl, "art", T(pts), "ink", 2.6, 1, hand, .6, smooth=True)
        for i in range(3):
            ink(pl, "art", T([(mx - ah * .18 + i * ah * .13, my - ah * .4), (mx - ah * .16 + i * ah * .13, my - ah * .2)]), "ink", 1.4, 1, hand, .3)
    elif art == "bolt":
        ink(pl, "art", T([(mx + ah * .1, my - ah * .45), (mx - ah * .18, my + ah * .04), (mx + ah * .06, my + ah * .04), (mx - ah * .1, my + ah * .45),
                          (mx + ah * .22, my - ah * .08), (mx - ah * .02, my - ah * .08)]), "ink", 2.6, 1, hand, .5, closed=True)
    elif art == "shield":
        ink(pl, "art", T([(mx - ah * .3, my - ah * .38), (mx + ah * .3, my - ah * .38), (mx + ah * .26, my + ah * .05), (mx, my + ah * .42),
                          (mx - ah * .26, my + ah * .05)]), "ink", 2.6, 1, hand, .5, closed=True)
        ink(pl, "art", T([(mx - ah * .15, my - ah * .2), (mx + ah * .15, my - ah * .2)]), "ink", 1.4, 1, hand, .3)
    else:
        for i in range(3):
            ink(pl, "art", T([(mx - ah * .4, my - ah * .2 + i * ah * .2), (mx + ah * .4, my - ah * .25 + i * ah * .2)]), "ink", 2.2, 1, hand, .8)
    # rules and outline in ink (sketchy)
    ink(pl, "art", T(rect(ax, ay, aw, ah)), "ink", 1.6, 1, hand, 0.5, closed=True)
    ink(pl, "art", T(rect(x, y, w, h)), "ink", 2.4, 1, hand, 0.6, closed=True, passes=2)
    for i in range(3):
        yy = y + h * (0.78 + i * 0.06)
        ink(pl, "art", T([(x + w * .1, yy), (x + w * (0.85 - i * .2), yy)]), "#555049", 1.2, 0.8, hand, 0.4)
    # cost coin
    ccx, ccy = x + w * 0.86, y + h * 0.1
    fill_poly(pl, "art", T(ellipse(ccx, ccy, w * .11, w * .11, 20)), "acid", 1.0)
    ink(pl, "art", T(ellipse(ccx, ccy, w * .11, w * .11, 20)), "ink", 2, 1, hand, .4, closed=True)
    # peel: a lifted corner catching light (sticker, not paper)
    if lift > 0:
        c1 = (x + w, y + h); pts = [(x + w - 34, y + h), (x + w, y + h - 34), (x + w - 22, y + h - 22)]
        fill_poly(pl, "art", T(pts), "#D9D5CB", 1.0)
        ink(pl, "art", T(pts), "ink", 1.4, 1, hand, .3, closed=True)
    # title text (mesh), rotated with the card
    tx, ty = T([(x + w * 0.08, y + h * 0.16)])[0]
    pl.text(title, tx, ty, h * 0.14 * s, "ink", FONT_ANTON, rot=-rot, emissive=True)
    cxx, cyy = T([(ccx, ccy + w * 0.06)])[0]
    pl.text(str(cost), cxx, cyy, w * 0.15 * s, "ink", FONT_ANTON, align="CENTER", rot=-rot)
    if sub:
        sx, sy = T([(x + w * .1, y + h * .77)])[0]
        pl.text(sub, sx, sy, h * 0.06 * s, "#2A2622", FONT_PLEX, rot=-rot)


def slap_marks(pl, layer, x, y, w, h, hand, color="white"):
    """Impact ticks around a sticker being slapped on (motion cue)."""
    r = hand.r
    for i in range(14):
        side = i % 4
        if side == 0:
            px, py, dx, dy = x + r.uniform(0, w), y - 14, 0, -1
        elif side == 1:
            px, py, dx, dy = x + w + 14, y + r.uniform(0, h), 1, 0
        elif side == 2:
            px, py, dx, dy = x + r.uniform(0, w), y + h + 14, 0, 1
        else:
            px, py, dx, dy = x - 14, y + r.uniform(0, h), -1, 0
        L = r.uniform(12, 30)
        ink(pl, layer, [(px, py), (px + dx * L, py + dy * L)], color, 2.2, 0.9, hand, 0.3, taper=0.3)


# ================================================================ binary shards
def binary_shards(pl, layer, x, y, hand, n=40, spread=(-2.6, 0.4), speed=(60, 260), color="harm", core="#FFFFFF"):
    """0/1 glyph shards thrown from a hit point, each with a short motion streak."""
    r = hand.r
    for i in range(n):
        a = r.uniform(*spread); d = r.uniform(*speed)
        px, py = x + math.cos(a) * d, y + math.sin(a) * d
        sz = r.uniform(9, 22) * (1.2 - d / speed[1] * 0.5)
        tr = r.uniform(18, 60)
        ink(pl, layer, [(px - math.cos(a) * tr, py - math.sin(a) * tr), (px - math.cos(a) * 4, py - math.sin(a) * 4)],
            color, sz * 0.18, 0.5, None, 0, taper=0.05)
        rot = r.uniform(-0.6, 0.6)
        c = color if r.random() < 0.6 else core
        if r.random() < 0.5:
            pts = rot_pts(ellipse(px, py, sz * 0.32, sz * 0.5, 14), px, py, rot)
            ink(pl, layer, pts, c, max(1.4, sz * 0.14), 1, hand, 0.2, closed=True)
        else:
            pts = rot_pts([(px - sz * .2, py - sz * .3), (px, py - sz * .5), (px, py + sz * .5)], px, py, rot)
            ink(pl, layer, pts, c, max(1.4, sz * 0.14), 1, hand, 0.2)
        if r.random() < 0.35:  # a glass chip
            t = [(px + r.uniform(-8, 8), py + r.uniform(-8, 8)) for _ in range(3)]
            fill_poly(pl, layer, t, color, 0.7)
    # impact star
    for i in range(12):
        a = i / 12 * 2 * math.pi + r.uniform(-.1, .1); L = r.uniform(26, 70)
        ink(pl, layer, [(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], core, 2.4, 0.9, hand, 0.2, taper=0.1)
    fill_poly(pl, layer, ellipse(x, y, 18, 18, 20), "#FFFFFF", 0.95)


# ================================================================ city
class City:
    """Inked isometric city. Buildings/highways are bucketed into depth bands so each
    band can live on its own blurred plane (tilt-shift + receding)."""

    def __init__(self, seed, u=44.0, ox=960.0, oy=540.0, mode="night", hq=None, extent=34):
        self.r = random.Random(seed); self.hand = Hand(seed + 7)
        self.u = u; self.ox = ox; self.oy = oy; self.mode = mode; self.hq = hq
        self.buildings = []; self.highways = []; self.extent = extent
        self._layout()

    # iso projection (gx, gy grid, gz height in tiles)
    def P(self, gx, gy, gz=0.0):
        u = self.u
        return (self.ox + (gx - gy) * u * 0.866, self.oy + (gx + gy) * u * 0.5 - gz * u)

    def _layout(self):
        r = self.r; E = self.extent
        blk = 5
        for bx in range(-E, E, blk):
            for by in range(-E, E, blk):
                # cull whole blocks off-screen (with height margin)
                cx, cy = self.P(bx + 2, by + 2)
                if cx < -300 or cx > W + 300 or cy < -200 or cy > H + 900:
                    continue
                # split a 4x4 block into lots
                lots = []
                if r.random() < 0.3:
                    lots = [(bx, by, 4, 4)]
                else:
                    sx = r.choice([2, 2, 1, 3])
                    for (lx, lw) in ((bx, sx), (bx + sx, 4 - sx)):
                        sy = r.choice([2, 1, 3])
                        lots += [(lx, by, lw, sy), (lx, by + sy, lw, 4 - sy)]
                for (lx, ly, lw, ld) in lots:
                    if self.hq and abs(lx + lw / 2 - self.hq[0]) < 3.5 and abs(ly + ld / 2 - self.hq[1]) < 3.5:
                        continue
                    h = r.choice([0.6, 1, 1.4, 2, 2.5, 3, 4]) * r.uniform(0.8, 1.3)
                    if r.random() < 0.07:
                        h *= 2.0
                    if self.hq and abs(lx - self.hq[0]) + abs(ly - self.hq[1]) < 9:
                        h = min(h, 2.4)  # clear the skyline around the HQ
                    inset = 0.12
                    self.buildings.append(dict(x=lx + inset, y=ly + inset, w=lw - 2 * inset, d=ld - 2 * inset, h=h,
                                               kind="bld", seed=r.randint(0, 99999)))
        if self.hq:
            hx, hy = self.hq
            self.buildings.append(dict(x=hx - 1.8, y=hy - 1.8, w=3.8, d=3.8, h=13.0, kind="hq", seed=4242))
        self.buildings.sort(key=lambda b: (b["x"] + b["w"] + b["y"] + b["d"], b["x"] - b["y"]))

    def depth_y(self, b):
        return self.P(b["x"] + b["w"], b["y"] + b["d"])[1]

    # ---------------------------------------------------------- building
    def draw_building(self, pl, b, pal, detail=1.0, lit=True):
        P = self.P; h = b["h"]; hand = self.hand
        rr = random.Random(b["seed"])
        x0, y0, x1, y1 = b["x"], b["y"], b["x"] + b["w"], b["y"] + b["d"]
        b0, b1, b2, b3 = P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)
        t0, t1, t2, t3 = P(x0, y0, h), P(x1, y0, h), P(x1, y1, h), P(x0, y1, h)
        line = pal["line"]
        if b["kind"] == "bld" and rr.random() < pal.get("alt_p", 0):
            line = rr.choice(pal["alt"])
        # faces: value steps give form without texture
        fill_poly(pl, "ink", [b1, b2, t2, t1], pal["right"], 1.0)
        fill_poly(pl, "ink", [b3, b2, t2, t3], pal["left"], 1.0)
        fill_poly(pl, "ink", [t0, t1, t2, t3], pal["top"], 1.0)
        # windows (hairlines on the faces)
        if detail > 0.3:
            fl = max(1, int(h / 0.32))
            for face, (A, B) in (("r", ((x1, y0), (x1, y1))), ("l", ((x0, y1), (x1, y1)))):
                cols = max(1, int(math.hypot(B[0] - A[0], B[1] - A[1]) / 0.28))
                for f in range(fl):
                    z = (f + 0.45) * h / fl
                    if z > h - 0.15:
                        continue
                    for c in range(cols):
                        v = rr.random()
                        t = (c + 0.3) / cols; t2_ = (c + 0.7) / cols
                        pa = P(A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t, z)
                        pb = P(A[0] + (B[0] - A[0]) * t2_, A[1] + (B[1] - A[1]) * t2_, z)
                        if lit and v < pal["win_p"]:
                            wc = rr.choice(pal["win"])
                            ink(pl, "ink", [pa, pb], wc, 2.2, rr.uniform(0.55, 1.0), None, 0, taper=0.9)
                        elif v < pal["win_p"] + 0.25 and detail > 0.6:
                            ink(pl, "ink", [pa, pb], line, 0.7, 0.22, None, 0, taper=0.9)
        # silhouette thick, inner edges hairline, construction overshoot
        lw = pal["lw"]; lo = 1.0 if b["kind"] == "hq" else pal.get("line_op", 1.0)
        ink(pl, "ink", [t0, t1, b1, b2, b3, t3, t0], line, lw, lo, hand, 0.5, taper=0.7)
        ink(pl, "ink", [t1, t2, t3], line, lw * 0.5, 0.85 * lo, hand, 0.4, taper=0.7)
        ink(pl, "ink", [t2, b2], line, lw * 0.45, 0.8 * lo, hand, 0.3, overshoot=5, taper=0.5)
        # rooftop kit
        if detail > 0.5 and b["kind"] == "bld":
            k = rr.random()
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if k < 0.35:
                bw = min(b["w"], b["d"]) * 0.35
                bb = dict(x=cx - bw / 2, y=cy - bw / 2, w=bw, d=bw, h=0.35, seed=rr.randint(0, 999), kind="kit")
                self._box(pl, bb, h, pal, line)
            elif k < 0.55:
                a = P(cx, cy, h); c = P(cx, cy, h + rr.uniform(0.8, 1.8))
                ink(pl, "ink", [a, c], line, 1.2, 0.9, hand, 0.2)
                fill_poly(pl, "fx", ellipse(c[0], c[1], 3, 3, 8), "harm", 1.0)
            elif k < 0.7 and pal.get("signs"):
                # vertical neon blade sign on the left face
                sc = rr.choice(pal["signs"])
                sx = x0 + b["w"] * rr.uniform(0.2, 0.8)
                zb = h * rr.uniform(0.3, 0.55); zt = min(h + 0.3, zb + rr.uniform(0.8, 1.6))
                pa, pb = P(sx, y1 + 0.02, zb), P(sx, y1 + 0.02, zt)
                ink(pl, "fx", [pa, pb], sc, 7, 0.9, hand, 0.2, taper=0.9)
                ink(pl, "fx", [pa, pb], "#FFFFFF", 1.6, 0.8, hand, 0.1, taper=0.9)
        if b["kind"] == "hq":
            self._hq_details(pl, b, pal)

    def _box(self, pl, b, base, pal, line):
        P = self.P
        x0, y0, x1, y1, h = b["x"], b["y"], b["x"] + b["w"], b["y"] + b["d"], base + b["h"]
        b1, b2, b3 = P(x1, y0, base), P(x1, y1, base), P(x0, y1, base)
        t0, t1, t2, t3 = P(x0, y0, h), P(x1, y0, h), P(x1, y1, h), P(x0, y1, h)
        fill_poly(pl, "ink", [b1, b2, t2, t1], pal["right"], 1.0)
        fill_poly(pl, "ink", [b3, b2, t2, t3], pal["left"], 1.0)
        fill_poly(pl, "ink", [t0, t1, t2, t3], pal["top"], 1.0)
        ink(pl, "ink", [t0, t1, b1, b2, b3, t3, t0], line, 1.0, 0.9, self.hand, 0.3)

    def _hq_details(self, pl, b, pal):
        """The Cell's HQ: stacked setbacks, a mast, a marker banner, pink cables."""
        P = self.P; hand = self.hand
        x0, y0 = b["x"], b["y"]; h = b["h"]
        x1, y1 = x0 + b["w"], y0 + b["d"]
        # hero silhouette: re-inked heavier, with a pink rim light on the lit edges
        sil = [P(x0, y0, h), P(x1, y0, h), P(x1, y0, 0), P(x1, y1, 0), P(x0, y1, 0), P(x0, y1, h), P(x0, y0, h)]
        ink(pl, "ink", sil, pal["line"], pal["lw"] * 1.8, 1, hand, 0.7, passes=2)
        neon_line(pl, "fx", [P(x1, y0, 0.2), P(x1, y0, h)], "pink", 3.0, hand)
        neon_line(pl, "fx", [P(x0, y1, 0.2), P(x0, y1, h)], "pink", 2.0, hand)
        # warm home windows (amber) in irregular rows: people live here
        rr = random.Random(77)
        for f in range(int(h / 0.45)):
            z = 0.5 + f * 0.45
            for c in range(7):
                if rr.random() < 0.45:
                    t = (c + 0.3) / 7
                    pa = P(x1, y0 + b["d"] * t, z); pb = P(x1, y0 + b["d"] * (t + 0.07), z)
                    ink(pl, "fx", [pa, pb], rr.choice(["amber", "amber", "pink", "#FFFFFF"]), 2.6, 0.9, None, 0)
        # setback tiers
        tiers = [(0.35, 2.5, 2.0), (0.8, 1.6, 1.6)]
        base = h
        for ins, th, _ in tiers:
            bb = dict(x=x0 + ins, y=y0 + ins, w=b["w"] - 2 * ins, d=b["d"] - 2 * ins, h=th, seed=1, kind="kit")
            self._box(pl, bb, base, pal, pal["line"])
            # windows band
            for i in range(6):
                t = (i + .5) / 6
                pa = P(bb["x"] + bb["w"] * t, bb["y"] + bb["d"], base + th * 0.5)
                ink(pl, "ink", [pa, (pa[0] + 6, pa[1] - 3)], "amber", 2.4, 0.9, None, 0)
            base += th
        # mast
        mx, my = x0 + b["w"] / 2, y0 + b["d"] / 2
        a, c = P(mx, my, base), P(mx, my, base + 3.2)
        ink(pl, "ink", [a, c], pal["line"], 2.6, 1, hand, 0.3)
        for i in range(5):
            z = base + 0.4 + i * 0.6
            ink(pl, "ink", [P(mx - .25, my, z), P(mx, my - .25, z + .3), P(mx + .25, my, z)], pal["line"], 1, 0.8, hand, 0.2)
        fill_poly(pl, "fx", ellipse(c[0], c[1], 6, 6, 10), "pink", 1.0)
        glow_halo(pl, "fx", ellipse(c[0], c[1], 10, 10, 12), "pink", 12, 0.3, closed=True)
        # dish
        d = P(mx + 0.5, my - 0.3, base + 0.9)
        ink(pl, "ink", ellipse(d[0], d[1], 16, 9, 20, math.pi * 0.9, math.pi * 2.1, 0.5), "pink", 2.2, 1, hand, 0.3)
        # pink neon crown ring + tube sign down the face (Cell brand)
        crown = [P(x0, y0 + b["d"], h), P(x0 + b["w"], y0 + b["d"], h), P(x0 + b["w"], y0, h)]
        neon_line(pl, "fx", crown, "pink", 4, hand)
        fx = x0 + b["w"] * 0.5
        top, bot = P(fx, y0 + b["d"] + 0.02, h - 0.4), P(fx, y0 + b["d"] + 0.02, h - 6.6)
        fill_poly(pl, "fx", [(top[0] - 22, top[1]), (top[0] + 22, top[1] - 12), (bot[0] + 22, bot[1] - 12), (bot[0] - 22, bot[1])], "#0A0610", 0.9)
        # stacked letters C E L L (single-stroke neon)
        yy = top[1] + 46
        for ch in "CELL":
            st, _ = marker_word_strokes(ch, top[0] - 13, yy, 36, slant=0.0, hand=hand, jit=0.0)
            for _, s in st:
                neon_line(pl, "fx", s, "pink", 3.6, hand, jit=0.2, smooth=True)
            yy += 48
        # cables from the HQ to neighbours (pink catenaries)
        return

    # ---------------------------------------------------------- highways
    def add_highway(self, path, z, width=1.2, lanes=2, seed=0, color_hi="#FFF3D6", color_tail="#FF3D5A"):
        self.highways.append(dict(path=path, z=z, w=width, lanes=lanes, seed=seed, hi=color_hi, tail=color_tail))

    def highway_runs(self, hw, step=0.35):
        pts = catmull(hw["path"], 10)
        # resample by distance
        out = [pts[0]]
        for p in pts[1:]:
            if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) >= step:
                out.append(p)
        return out

    def draw_highway_segment(self, pl, hw, gpts, pal, detail=1.0):
        """gpts: consecutive grid points (a run inside one depth band)."""
        if len(gpts) < 2:
            return
        P = self.P; z = hw["z"]; w = hw["w"]; hand = self.hand
        rr = random.Random(hw["seed"] + int(gpts[0][0] * 100))
        L, R, C = [], [], []
        for i, (gx, gy) in enumerate(gpts):
            a = gpts[max(i - 1, 0)]; b = gpts[min(i + 1, len(gpts) - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]; dl = math.hypot(dx, dy) or 1
            nx, ny = -dy / dl * w / 2, dx / dl * w / 2
            L.append((gx + nx, gy + ny)); R.append((gx - nx, gy - ny)); C.append((gx, gy))
        # pillars
        for i in range(0, len(gpts), 6):
            gx, gy = gpts[i]
            top, bot = P(gx, gy, z - 0.25), P(gx, gy, 0)
            fill_poly(pl, "ink", [(top[0] - 6, top[1]), (top[0] + 6, top[1]), (bot[0] + 6, bot[1]), (bot[0] - 6, bot[1])], pal["right"], 1)
            ink(pl, "ink", [top, bot], pal["line"], 1.0, 0.6, hand, 0.3)
        # fascia (the deck's thickness) then deck
        Ls = [P(x, y, z) for x, y in L]; Rs = [P(x, y, z) for x, y in R]
        Lb = [P(x, y, z - 0.28) for x, y in L]; Rb = [P(x, y, z - 0.28) for x, y in R]
        # choose the edge that faces the viewer (larger screen y)
        front, frontb = (Ls, Lb) if sum(p[1] for p in Ls) > sum(p[1] for p in Rs) else (Rs, Rb)
        fill_poly(pl, "ink", front + frontb[::-1], pal["left"], 1.0)
        fill_poly(pl, "ink", Ls + Rs[::-1], pal["deck"], 1.0)
        # underglow + rails
        ink(pl, "ink", frontb, pal.get("under", "pink"), 2.0, 0.7, hand, 0.3)
        ink(pl, "ink", Ls, pal["line"], pal["lw"] * 0.8, 1, hand, 0.4)
        ink(pl, "ink", Rs, pal["line"], pal["lw"] * 0.8, 1, hand, 0.4)
        # traffic: headlights one lane, tail-lights the other
        if detail > 0.2:
            for lane, colr in ((0.25, hw["hi"]), (-0.25, hw["tail"])):
                i = rr.randint(0, 3)
                while i < len(C) - 2:
                    gx, gy = C[i]; hx, hy = C[i + 1]
                    dx, dy = hx - gx, hy - gy; dl = math.hypot(dx, dy) or 1
                    nx, ny = -dy / dl * w * lane, dx / dl * w * lane
                    pa = P(gx + nx, gy + ny, z + 0.05); pb = P(hx + nx, hy + ny, z + 0.05)
                    ink(pl, "traffic", [pa, pb], colr, 3.2, 0.95, None, 0, taper=0.2)
                    i += rr.randint(2, 5)

    # ---------------------------------------------------------- misc
    def cable(self, pl, layer, a, b, sag, color="pink", w=1.4, op=0.9, hand=None):
        pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)) for t in [i / 20 for i in range(21)]]
        ink(pl, layer, pts, color, w, op, hand, 0.3, taper=0.8)

    def roof_point(self, b, fx=0.5, fy=0.5):
        return self.P(b["x"] + b["w"] * fx, b["y"] + b["d"] * fy, b["h"])


PAL_NIGHT = dict(line="cyan", right="#04060C", left="#090D18", top="#0D1322", deck="#0B1020", lw=1.9, line_op=0.55,
                 win=["cyan", "amber", "pink", "#FFFFFF", "violet"], win_p=0.18, signs=["pink", "violet", "cyan", "acid"],
                 alt=["violet", "#7FA8FF"], alt_p=0.12, under="pink")
PAL_DESAT = dict(line="#3E5670", right="#0B0E15", left="#10141D", top="#151A25", deck="#131822", lw=1.8,
                 win=["#46607A", "#5A6A7A"], win_p=0.10, signs=["#4A5A70"], alt=[], alt_p=0, under="#3A4658")
PAL_HEAT = dict(line="#5CC8FF", right="#07050C", left="#100A14", top="#160D1B", deck="#120B16", lw=1.9, line_op=0.5,
                win=["#FF6A3A", "amber", "#FFFFFF", "cyan"], win_p=0.14, signs=["harm", "violet", "pink"],
                alt=["harm", "#FF7A1A"], alt_p=0.18, under="harm")
