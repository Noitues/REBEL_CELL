"""F Rebel Tag: glyphs, beams, pins, paint effects, HUD, cards.  Everything wordless (numbers and 1-2 word verbs only)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, distance_transform_edt
from ft_lib import *


def rot(p, ang, c=(0, 0)):
    ca, sa = math.cos(ang), math.sin(ang)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


# ------------------------------------------------------------------------- glyphs (centre c, size s ~ half height)
def g_shield(L, c, s, fill, line=None, a=255, lw=2):
    x, y = c
    pts = [(x - s * .85, y - s * .8), (x, y - s), (x + s * .85, y - s * .8), (x + s * .8, y + s * .1), (x, y + s), (x - s * .8, y + s * .1)]
    L.poly(pts, fill=fill, outline=line, w=lw, a=a)


def g_arrow(L, c, s, fill, ang=0.0, line=None, a=255):
    pts = [(-s, -s * .32), (s * .25, -s * .32), (s * .25, -s * .75), (s, 0), (s * .25, s * .75), (s * .25, s * .32), (-s, s * .32)]
    pts = [rot((c[0] + p[0], c[1] + p[1]), ang, c) for p in pts]
    L.poly(pts, fill=fill, outline=line, w=2, a=a)


def g_hex(L, c, r, fill=None, line=None, w=2, a=255, ang=math.pi / 6):
    pts = [(c[0] + r * math.cos(ang + k * math.pi / 3), c[1] + r * math.sin(ang + k * math.pi / 3)) for k in range(6)]
    L.poly(pts, fill=fill, outline=line, w=w, a=a)


def g_drone(L, c, s, col, line=INK):
    x, y = c
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        L.line([c, (x + dx * s * .78, y + dy * s * .6)], line, s * .26 + 3)
        L.line([c, (x + dx * s * .78, y + dy * s * .6)], col, s * .26)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        p = (x + dx * s * .78, y + dy * s * .6)
        L.ellipse(p, s * .36, s * .2, fill=line)
        L.ellipse(p, s * .27, s * .13, fill=col)
    L.circle(c, s * .32, fill=line)
    L.circle(c, s * .22, fill=col)


def g_diamond_eye(L, c, s, col, line=INK):
    x, y = c
    pts = [(x, y - s), (x + s * .8, y), (x, y + s), (x - s * .8, y)]
    L.poly(pts, fill=line)
    pts2 = [(x, y - s * .78), (x + s * .62, y), (x, y + s * .78), (x - s * .62, y)]
    L.poly(pts2, fill=col)
    L.circle(c, s * .26, fill=line)
    L.circle(c, s * .1, fill=(255, 255, 255))


def g_enf(L, c, s, col, line=INK):
    x, y = c
    L.rrect((x - s * .85, y - s * .85, x + s * .85, y + s * .85), s * .2, fill=line)
    L.rrect((x - s * .7, y - s * .7, x + s * .7, y + s * .7), s * .14, fill=col)
    for dy in (-.28, .26):
        L.line([(x - s * .38, y + s * (dy + .26)), (x, y + s * (dy - .1)), (x + s * .38, y + s * (dy + .26))], line, s * .2, joints=True)


def g_type(L, t, c, s, line=INK):
    {"D": g_drone, "N": g_diamond_eye, "E": g_enf}[t](L, c, s, BEAM[t], line)


def g_heart(L, c, s, fill, line=None, a=255):
    x, y = c
    pts = []
    for k in range(40):
        t = k / 40 * 2 * math.pi
        px = 16 * math.sin(t) ** 3
        py = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x + px * s / 16, y + py * s / 16 - s * .05))
    L.poly(pts, fill=fill, outline=line, w=2, a=a)


def g_heart_broken(L, c, s, fill, line=INK, a=255):
    g_heart(L, c, s, fill, line, a)
    x, y = c
    zz = [(x + s * .1, y - s * .95), (x - s * .2, y - s * .35), (x + s * .25, y - s * .05), (x - s * .1, y + s * .45), (x + s * .05, y + s * .95)]
    L.line(zz, INK, s * .22, a=a)


def g_x(L, c, s, col, w=4, a=255):
    x, y = c
    L.line([(x - s, y - s), (x + s, y + s)], col, w, a=a)
    L.line([(x - s, y + s), (x + s, y - s)], col, w, a=a)


def g_ring(L, c, s, col, w=3, a=255):
    L.circle(c, s, outline=col, w=w, a=a)


def g_square_slash(L, c, s, fill, line=INK):
    x, y = c
    L.rrect((x - s * .8, y - s * .8, x + s * .8, y + s * .8), s * .12, fill=fill, outline=line, w=2)
    L.line([(x - s * .8, y + s * .5), (x + s * .8, y - s * .5)], line, s * .26)


def g_octx(L, c, s, fill, line=INK):
    x, y = c
    pts = [(x + s * math.cos(math.pi / 8 + k * math.pi / 4), y + s * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    L.poly(pts, fill=fill, outline=line, w=2)
    g_x(L, c, s * .5, line, w=s * .3)


def g_skull(L, c, s, fill, hole=None, a=255):
    x, y = c
    L.circle((x, y - s * .15), s * .85, fill=fill, a=a)
    L.rrect((x - s * .5, y + s * .25, x + s * .5, y + s * .95), s * .12, fill=fill, a=a)
    Z = (0, 0, 0, 0)
    for dx in (-.34, .34):
        L.d.ellipse([(x + dx * s - s * .24) * SS, (y - s * .2 - s * .26) * SS, (x + dx * s + s * .24) * SS, (y - s * .2 + s * .26) * SS], fill=Z)
    L.d.polygon([((x) * SS, (y + s * .02) * SS), ((x - s * .1) * SS, (y + s * .24) * SS), ((x + s * .1) * SS, (y + s * .24) * SS)], fill=Z)
    for k in (-.3, -.1, .1, .3):
        L.d.rectangle([(x + k * s - s * .035) * SS, (y + s * .5) * SS, (x + k * s + s * .035) * SS, (y + s * .95) * SS], fill=Z)


def g_bio(L, c, s, col, a=255):
    """biohazard trefoil (stencil-ish)"""
    x, y = c
    for k in range(3):
        ang = -math.pi / 2 + k * 2 * math.pi / 3
        cx, cy = x + math.cos(ang) * s * .52, y + math.sin(ang) * s * .52
        L.circle((cx, cy), s * .5, fill=col, a=a)
    Z = (0, 0, 0, 0)
    for k in range(3):
        ang = -math.pi / 2 + k * 2 * math.pi / 3
        cx, cy = x + math.cos(ang) * s * .62, y + math.sin(ang) * s * .62
        L.d.ellipse([(cx - s * .3) * SS, (cy - s * .3) * SS, (cx + s * .3) * SS, (cy + s * .3) * SS], fill=Z)
        cx2, cy2 = x + math.cos(ang) * s * .92, y + math.sin(ang) * s * .92
        L.d.ellipse([(cx2 - s * .36) * SS, (cy2 - s * .36) * SS, (cx2 + s * .36) * SS, (cy2 + s * .36) * SS], fill=Z)
    L.d.ellipse([(x - s * .3) * SS, (y - s * .3) * SS, (x + s * .3) * SS, (y + s * .3) * SS], fill=Z)
    L.circle(c, s * .17, fill=col, a=a)
    for k in range(3):
        ang = -math.pi / 2 + k * 2 * math.pi / 3 + math.pi / 3
        L.d.line([(x * SS, y * SS), ((x + math.cos(ang) * s * 1.1) * SS, (y + math.sin(ang) * s * 1.1) * SS)], fill=Z, width=int(s * .12 * SS))


def g_wrench(L, c, s, col, a=255):
    x, y = c
    L.line([(x - s * .7, y + s * .7), (x + s * .35, y - s * .35)], col, s * .32, a=a)
    L.circle((x + s * .5, y - s * .5), s * .46, fill=col, a=a)
    L.d.polygon([((x + s * .5) * SS, (y - s * .5) * SS), ((x + s * .95) * SS, (y - s * .95) * SS), ((x + s * 1.05) * SS, (y - s * .2) * SS)], fill=(0, 0, 0, 0))


def g_lock(L, c, s, col, line=INK):
    x, y = c
    L.d.arc([(x - s * .48) * SS, (y - s * 1.0) * SS, (x + s * .48) * SS, (y + s * .1) * SS], 180, 360, fill=line + (255,), width=int(s * .3 * SS) + 4)
    L.d.arc([(x - s * .48) * SS, (y - s * 1.0) * SS, (x + s * .48) * SS, (y + s * .1) * SS], 180, 360, fill=col + (255,), width=int(s * .3 * SS))
    L.line([(x - s * .48, y - s * .45), (x - s * .48, y)], col, s * .3)
    L.line([(x + s * .48, y - s * .45), (x + s * .48, y)], col, s * .3)
    L.rrect((x - s * .82, y - s * .05, x + s * .82, y + s * .85), s * .12, fill=line)
    L.rrect((x - s * .7, y + s * .05, x + s * .7, y + s * .75), s * .1, fill=col)
    L.circle((x, y + s * .38), s * .13, fill=line)


def g_lock_open(L, c, s, col, line=INK):
    x, y = c
    L.d.arc([(x - s * .48 + s * .55) * SS, (y - s * 1.35) * SS, (x + s * .48 + s * .55) * SS, (y - s * .25) * SS], 180, 360, fill=line + (255,), width=int(s * .3 * SS) + 4)
    L.d.arc([(x - s * .48 + s * .55) * SS, (y - s * 1.35) * SS, (x + s * .48 + s * .55) * SS, (y - s * .25) * SS], 180, 360, fill=col + (255,), width=int(s * .3 * SS))
    L.line([(x + s * .07 + s * .55 * 1.0, y - s * .8), (x + s * .07 + s * .55, y - s * .3)], col, s * .3)
    L.rrect((x - s * .82, y - s * .05, x + s * .82, y + s * .85), s * .12, fill=line)
    L.rrect((x - s * .7, y + s * .05, x + s * .7, y + s * .75), s * .1, fill=col)
    L.circle((x, y + s * .38), s * .13, fill=line)


def g_eye(L, c, s, col, line=INK):
    x, y = c
    top = [(x - s * 1.1 + s * 2.2 * k / 16, y - math.sin(k / 16 * math.pi) * s * .62) for k in range(17)]
    bot = [(x - s * 1.1 + s * 2.2 * k / 16, y + math.sin(k / 16 * math.pi) * s * .62) for k in range(17)]
    L.poly(top + bot[::-1], fill=line)
    sh = [(x - s * 1.0 + s * 2.0 * k / 16, y - math.sin(k / 16 * math.pi) * s * .5) for k in range(17)]
    sb = [(x - s * 1.0 + s * 2.0 * k / 16, y + math.sin(k / 16 * math.pi) * s * .5) for k in range(17)]
    L.poly(sh + sb[::-1], fill=col)
    L.circle(c, s * .3, fill=line)
    L.circle(c, s * .12, fill=col)


def g_flame(L, c, s, col, line=None):
    x, y = c
    pts = [(x, y - s), (x + s * .5, y - s * .2), (x + s * .62, y + s * .35), (x + s * .3, y + s * .85), (x - s * .3, y + s * .85), (x - s * .62, y + s * .35), (x - s * .4, y - s * .1), (x - s * .1, y + s * .15), (x - s * .05, y - s * .45)]
    L.poly(pts, fill=col, outline=line, w=2)


def g_bolt(L, c, s, col):
    x, y = c
    L.poly([(x + s * .2, y - s), (x - s * .6, y + s * .15), (x - s * .05, y + s * .15), (x - s * .25, y + s), (x + s * .6, y - s * .2), (x + s * .05, y - s * .2)], fill=col)


def tier_glyph(L, tier, c, s):
    if tier == "untouched":
        L.circle(c, s * .85, fill=INK, a=200)
        L.circle(c, s * .85, outline=UNTOUCHED, w=s * .28)
    elif tier == "holds":
        g_shield(L, c, s, HOLDS, INK, lw=2)
    elif tier == "lost":
        g_square_slash(L, c, s, LOST)
    elif tier == "damaged":
        g_heart_broken(L, c, s, DAMAGED)
    elif tier == "breach":
        g_octx(L, c, s, BREACH)


# ------------------------------------------------------------------------------------------- iso helpers
ISO = 0.62


def ground_ring(L, c, r, col, w=2, a=255, dash=False):
    if not dash:
        L.ellipse(c, r, r * ISO, outline=col, w=w, a=a)
    else:
        n = 28
        for k in range(n):
            if k % 2:
                continue
            t0, t1 = k / n * 2 * math.pi, (k + 1) / n * 2 * math.pi
            pts = [(c[0] + r * math.cos(t), c[1] + r * ISO * math.sin(t)) for t in np.linspace(t0, t1, 4)]
            L.line(pts, col, w, a=a)


# --------------------------------------------------------------------------------- corp AR: HQ & site pins
def corp_hq(L, c, t=0.0, a=255):
    """sterile AR crown around the Solace helix base"""
    for i, r in enumerate((64, 104, 150)):
        ground_ring(L, c, r, CORP, w=2 if i else 3, a=int(a * (0.9 - i * .2)), dash=bool(i % 2))
    for k in range(24):
        ang = k / 24 * 2 * math.pi + t
        p0 = (c[0] + 150 * math.cos(ang), c[1] + 150 * ISO * math.sin(ang))
        p1 = (c[0] + 160 * math.cos(ang), c[1] + 160 * ISO * math.sin(ang))
        L.line([p0, p1], CORP, 2, a=a)
    # origin hex badge floating up the helix
    top = (c[0], c[1] - 120)
    L.line([c, top], CORP, 2, a=int(a * .6))
    g_hex(L, top, 24, fill=(8, 18, 36), line=CORP, w=3, a=a)
    g_hex(L, top, 13, fill=None, line=CORP, w=2, a=a)
    L.circle(top, 3.5, fill=CORP, a=a)


def site_pin(L, c, state="healthy", tier=1, focus=False, big=1.0, dim=False, lift=50):
    """corp AR pin: ground hex pad + stalk + floating hex badge with tier pips."""
    a = 120 if dim else 255
    ground_ring(L, c, 17 * big, CORP, w=2, a=a)
    top = (c[0], c[1] - lift * big)
    body = (8, 18, 36)
    edge = CORP
    if state == "TAKEN":
        body, edge = PLUM, VEIN
    elif state == "DOWN":
        edge = (150, 165, 190)
    L.line([c, top], edge, 2, a=int(a * .8))
    if focus:
        L.circle(top, 29 * big, outline=INK, w=7)
        L.circle(top, 29 * big, outline=LIME, w=4)
    g_hex(L, top, 19 * big, fill=body, line=INK, w=7 * big, a=a)
    g_hex(L, top, 19 * big, fill=body, line=edge, w=3 * big, a=a)
    n = int(tier)
    for k in range(n):
        px = top[0] + (k - (n - 1) / 2) * 8 * big
        L.circle((px, top[1]), 2.8 * big, fill=edge, a=a)
    return top


def grease_rgba(pts, col, w=5, seed=1, alpha=0.95):
    """D28 grease pencil: waxy rough stroke (frame px)"""
    rng = np.random.default_rng(seed)
    m = stroke_mask(wobble(pts, rng, 1.2, 8), w)
    mm = mask_np(m)
    streak = gaussian_filter(rng.random(mm.shape).astype(np.float32), (0.6, 2.2))
    mm = mm * (0.9 + 0.35 * streak)
    return spray_rgba(np.clip(mm, 0, 1), col, seed, over_r=1.5, over_k=0.0, rough=0.9, alpha=alpha, grain=0.25)


def mark_down(base, top, seed=1, big=1.0):
    """D28: DOWN = one grease slash through the badge, plus a quarter decay clock ring."""
    r = 28 * big
    base = over(base, grease_rgba([(top[0] - r, top[1] + r * .85), (top[0] + r, top[1] - r * .9)], GREASE, 10 * big, seed))
    return base


def decay_ring(L, top, frac, big=1.0, col=GREASE):
    r = 30 * big
    L.d.arc([(top[0] - r) * SS, (top[1] - r) * SS, (top[0] + r) * SS, (top[1] + r) * SS], -90, -90 + 360 * frac, fill=INK + (255,), width=int(9 * SS))
    L.d.arc([(top[0] - r) * SS, (top[1] - r) * SS, (top[0] + r) * SS, (top[1] + r) * SS], -90, -90 + 360 * frac, fill=col + (255,), width=int(5 * SS))


def mark_taken(base, top, seed=1, big=1.0):
    r = 23 * big
    base = over(base, grease_rgba([(top[0] - r, top[1] - r), (top[0] + r, top[1] + r)], GREASE, 10 * big, seed))
    base = over(base, grease_rgba([(top[0] - r, top[1] + r), (top[0] + r, top[1] - r)], GREASE, 10 * big, seed + 1))
    return base


# ------------------------------------------------------------------------------------------- beams
def beam_style_path(pts, t, step=9):
    """returns the drawn centre polyline for type t (N is a zigzag)"""
    if t != "N":
        return pts
    rp = resample(pts, step)
    out = []
    for i, p in enumerate(rp):
        j = min(i + 1, len(rp) - 1)
        k = max(i - 1, 0)
        dx, dy = rp[j][0] - rp[k][0], rp[j][1] - rp[k][1]
        L_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / L_, dx / L_
        a = 10 * (1 if i % 2 == 0 else -1)
        out.append((p[0] + nx * a, p[1] + ny * a))
    return out


def draw_beam(L, pts, t, s0=0.0, s1=None, alpha=255, w=1.3, chev=True, dim_after=None, casing=True):
    """one corp AR beam.  pts: screen px polyline (already lane-offset), from HQ to HOME.
    Drawn from s0..s1 along arclength; shape by type: D beads, N zigzag, E chevron band."""
    tot = path_len(pts)
    s1 = tot if s1 is None else s1
    seg = sub_path(pts, s0, s1)
    if len(seg) < 2:
        return
    col = BEAM[t]
    if t == "D":
        L.line(seg, INK, 7 * w, a=int(alpha * .75))
        L.line(seg, col, 2.2 * w, a=int(alpha * .65))
        rs = resample(seg, 19)
        for p in rs:
            L.circle(p, 6.2 * w, fill=INK, a=alpha)
        for p in rs:
            L.circle(p, 4.4 * w, fill=col, a=alpha)
            L.circle((p[0] - 1, p[1] - 1.2), 1.3 * w, fill=(255, 255, 255), a=int(alpha * .8))
    elif t == "N":
        zz = beam_style_path(seg, "N")
        L.line(zz, INK, 10 * w, a=int(alpha * .85))
        L.line(zz, col, 5.6 * w, a=alpha)
        L.line(zz, (255, 235, 252), 1.8 * w, a=int(alpha * .95))
    else:
        L.line(seg, INK, 13 * w, a=int(alpha * .85))
        L.line(seg, col, 8.6 * w, a=alpha)
        if chev:
            cl = cum(seg)
            k = 0
            s = 10
            while s < cl[-1] - 6:
                p, ang = point_at(seg, s, cl)
                d = (math.cos(ang), math.sin(ang))
                n = (-d[1], d[0])
                a_ = (p[0] - d[0] * 4 + n[0] * 3.4, p[1] - d[1] * 4 + n[1] * 3.4)
                b_ = (p[0] + d[0] * 2.5, p[1] + d[1] * 2.5)
                c_ = (p[0] - d[0] * 4 - n[0] * 3.4, p[1] - d[1] * 4 - n[1] * 3.4)
                L.line([a_, b_, c_], INK, 2.4 * w, a=alpha)
                s += 28


def dead_beam(L, pts, s0, t, alpha=150):
    """what a stopped beam would have done: grey dotted, sterile"""
    seg = sub_path(pts, s0, path_len(pts))
    if len(seg) < 2:
        return
    for p in resample(seg, 14):
        L.circle(p, 2.2, fill=(150, 160, 185), a=alpha)


def flat_end(L, p, ang, col=HOLDS, s=18):
    """ITB flat-ended stop bar across the path"""
    d = (math.cos(ang), math.sin(ang))
    n = (-d[1], d[0])
    a = (p[0] + n[0] * s, p[1] + n[1] * s)
    b = (p[0] - n[0] * s, p[1] - n[1] * s)
    L.line([a, b], INK, 11)
    L.line([a, b], col, 6)


def intent_tile(L, c, tier, num=None, s=25):
    """corp AR result tile: tier glyph (second channel) on a hex plate in tier colour + number"""
    col = TIER[tier]
    g_hex(L, c, s + 7, fill=INK, line=INK, w=1)
    g_hex(L, c, s + 3, fill=(8, 18, 36), line=col, w=3)
    tier_glyph(L, tier, c, s * .62)
    if num is not None:
        L.text((c[0] + s + 14, c[1] + 2), str(num), f2(F_MONO, 32), col, anchor="lm", stroke=3, stroke_fill=INK)


# ----------------------------------------------------------------------------------------- paint effects
def splat(base, c, r, col, seed=1, n=26, outline=None):
    rng = np.random.default_rng(seed)
    m = new_mask()
    d = ImageDraw.Draw(m)
    d.ellipse((c[0] - r * .55, c[1] - r * .55 * ISO * 1.5, c[0] + r * .55, c[1] + r * .55 * ISO * 1.5), fill=255)
    for _ in range(n):
        ang = rng.uniform(0, 6.283)
        dist = r * rng.uniform(.5, 1.25) ** 1.3
        ln = rng.uniform(r * .1, r * .35)
        w = rng.uniform(2, 6) * (1.2 - dist / (r * 1.6))
        x0, y0 = c[0] + math.cos(ang) * dist * .6, c[1] + math.sin(ang) * dist * .6 * .8
        x1, y1 = c[0] + math.cos(ang) * dist, c[1] + math.sin(ang) * dist * .8
        d.line([(x0, y0), (x1, y1)], fill=255, width=max(2, int(w)))
        d.ellipse((x1 - w, y1 - w, x1 + w, y1 + w), fill=255)
    for _ in range(n * 2):
        ang = rng.uniform(0, 6.283)
        dist = r * rng.uniform(.8, 1.9)
        x1, y1 = c[0] + math.cos(ang) * dist, c[1] + math.sin(ang) * dist * .8
        rr = rng.uniform(1.2, 3.6)
        d.ellipse((x1 - rr, y1 - rr, x1 + rr, y1 + rr), fill=255)
    out = base
    if outline is not None:
        out = over(out, spray_rgba(np.clip(gaussian_filter(mask_np(m), 3) * 3, 0, 1), outline, seed + 3, over_r=2, over_k=0.1, alpha=.8))
    return over(out, spray_rgba(mask_np(m), col, seed, over_r=9, rough=0.7))


def shatter(base, c, r, seed=1, tint=(180, 225, 255), bits=True, shard_a=1.0):
    """AR glass shatter: radial cracks, ringed fractures, displaced translucent shards, binary bits"""
    rng = np.random.default_rng(seed)
    L = Layer()
    n = 13
    angs = sorted(rng.uniform(0, 2 * math.pi, n))
    # shard polygons between neighbouring cracks, in rings
    ring_r = [0, r * .35, r * .7, r * 1.05]
    for i in range(n):
        a0, a1 = angs[i], angs[(i + 1) % n] + (2 * math.pi if i == n - 1 else 0)
        for j in range(3):
            if rng.random() < .25:
                continue
            r0, r1 = ring_r[j] * rng.uniform(.9, 1.1), ring_r[j + 1] * rng.uniform(.85, 1.1)
            jit = rng.uniform(-6, 6, 2) * (j + 1) / 2
            poly = [(c[0] + math.cos(a0) * r0 + jit[0], c[1] + math.sin(a0) * r0 * .78 + jit[1]),
                    (c[0] + math.cos(a0) * r1 + jit[0], c[1] + math.sin(a0) * r1 * .78 + jit[1]),
                    (c[0] + math.cos(a1) * r1 + jit[0], c[1] + math.sin(a1) * r1 * .78 + jit[1]),
                    (c[0] + math.cos(a1) * r0 + jit[0], c[1] + math.sin(a1) * r0 * .78 + jit[1])]
            L.poly(poly, fill=tint, outline=(255, 255, 255), w=1.4, a=int(min(255, rng.uniform(38, 95) * shard_a)))
    for a in angs:
        pts = [c]
        rr_ = 0
        ang = a
        while rr_ < r * 1.15:
            rr_ += rng.uniform(12, 26)
            ang += rng.normal(0, .08)
            pts.append((c[0] + math.cos(ang) * rr_, c[1] + math.sin(ang) * rr_ * .78))
        L.line(pts, (255, 255, 255), 2.0, a=235)
        L.line(pts, tint, 5.0, a=70)
    for rr_ in (r * .35, r * .7):
        pts = [(c[0] + math.cos(t) * rr_ * rng.uniform(.93, 1.07), c[1] + math.sin(t) * rr_ * .78 * rng.uniform(.93, 1.07)) for t in np.linspace(0, 2 * math.pi, 22)]
        L.line(pts, (255, 255, 255), 1.4, a=160)
    L.circle(c, min(r * .06, 8), fill=(255, 255, 255), a=255)
    out = commit(base, L, glow=0.9, glow_r=8)
    if bits:
        out = bitburst(out, c, r * 1.2, seed + 9, col=(215, 245, 255))
    return out


def bitburst(base, c, r, seed=1, col=(200, 245, 255), n=34):
    rng = np.random.default_rng(seed)
    L = Layer()
    f = f2(F_MONO, 15)
    for _ in range(n):
        ang = rng.uniform(0, 6.283)
        d = r * rng.uniform(.25, 1.3)
        p = (c[0] + math.cos(ang) * d, c[1] + math.sin(ang) * d * .8)
        L.text(p, str(int(rng.integers(0, 2))), f, col, a=int(rng.uniform(130, 255)), stroke=1, stroke_fill=INK)
    return commit(base, L, glow=0.5, glow_r=4)


def hex_flash(base, c, r, col=(120, 200, 255), seed=1):
    """hex shield flash"""
    L = Layer()
    rng = np.random.default_rng(seed)
    for q in range(-3, 4):
        for p in range(-3, 4):
            x = c[0] + (q * 1.5) * r * .3
            y = c[1] + (p * 1.732 + q * .866) * r * .3 * .78
            d = math.hypot(x - c[0], (y - c[1]) / .78)
            if d > r:
                continue
            a = int(255 * (1 - d / r) ** 1.2)
            g_hex(L, (x, y), r * .17, fill=col, line=(255, 255, 255), w=1.6, a=int(a * .35))
            g_hex(L, (x, y), r * .17, fill=None, line=(255, 255, 255), w=1.8, a=a)
    L.ellipse(c, r, r * .78, outline=(255, 255, 255), w=3, a=230)
    return commit(base, L, glow=1.0, glow_r=12)


# ------------------------------------------------------------------------------------------ infection ("Bloom A")
def _noise(shape, sigma, seed):
    rng = np.random.default_rng(seed)
    n = gaussian_filter(rng.random(shape).astype(np.float32), sigma)
    return (n - n.mean()) / (n.std() + 1e-6)


def bloom_mask(centers, radii, seed=5, squash=0.72, wob=0.42):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = _noise((H, W), 22, seed)
    n2 = _noise((H, W), 7, seed + 1)
    field = np.full((H, W), -1e9, np.float32)
    for (cx, cy), r in zip(centers, radii):
        d = np.sqrt((xx - cx) ** 2 + ((yy - cy) / squash) ** 2)
        field = np.maximum(field, r * (1 + wob * n * .55 + .12 * n2) - d)
    return field  # >0 inside


def bloom(base, centers, radii, seed=5, glyph=True, veins=True):
    """Bloom A necrosis: plum-black body, pink Voronoi veins, hot hairline front, windows dying behind the front."""
    field = bloom_mask(centers, radii, seed)
    inside = (field > 0).astype(np.float32)
    soft = gaussian_filter(inside, 1.2)
    a = np.asarray(base.convert("RGB")).astype(np.float32) / 255
    lum = (a * np.array([.3, .59, .11], np.float32)).sum(-1, keepdims=True)
    # body: crush the city to plum-black; dying windows keep a rotten dim pink-violet
    plum = np.array(PLUM, np.float32) / 255
    body = plum[None, None, :] * (0.7 + 0.5 * lum) + np.clip(lum - .3, 0, 1) * np.array([.35, .08, .22], np.float32)
    k = (soft * 0.93)[..., None]
    a = a * (1 - k) + body * k
    # Voronoi veins
    if veins:
        rng = np.random.default_rng(seed + 11)
        ys, xs = np.where(inside > 0)
        if len(xs) > 60:
            sel = rng.choice(len(xs), min(150, len(xs) // 40 + 12), replace=False)
            pts = np.stack([xs[sel], ys[sel]], 1).astype(np.float32)
            from scipy.spatial import cKDTree
            tr = cKDTree(pts)
            sub = 2
            gy, gx = np.mgrid[0:H:sub, 0:W:sub]
            q = np.stack([gx.ravel(), gy.ravel()], 1).astype(np.float32)
            d, _ = tr.query(q, k=2)
            edge = (d[:, 1] - d[:, 0]).reshape(gx.shape)
            vm = np.clip(1 - edge / 3.4, 0, 1)
            vm = np.asarray(Image.fromarray((vm * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
            depth = np.clip(field / 60.0, 0, 1)
            vm = vm * soft * (0.35 + 0.65 * depth)
            vc = np.array(VEIN, np.float32) / 255
            a = a + vm[..., None] * vc[None, None, :] * 0.85
    # hot hairline front + hot rim glow
    edge = np.exp(-(field / 2.6) ** 2)
    edge2 = np.exp(-((field + 6) / 14.0) ** 2) * (field < 6)
    hc = np.array(HOT, np.float32) / 255
    vc = np.array(VEIN, np.float32) / 255
    a = a + edge[..., None] * hc[None, None, :] * 1.0 + edge2[..., None] * vc[None, None, :] * 0.35
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    # plum paint drips off the lower edge
    rng = np.random.default_rng(seed + 21)
    m = new_mask()
    d = ImageDraw.Draw(m)
    ey, ex = np.where((field > -2) & (field < 3))
    if len(ex):
        for _ in range(16):
            i = rng.integers(0, len(ex))
            x, y = ex[i], ey[i]
            ln = rng.uniform(16, 52)
            d.line([(x, y), (x, y + ln)], fill=255, width=3)
            d.ellipse((x - 3.4, y + ln - 3, x + 3.4, y + ln + 4), fill=255)
    out = over(out, spray_rgba(mask_np(m), (70, 20, 70), seed + 2, over_r=2, over_k=.1))
    if glyph:
        for c, r in zip(centers, radii):
            if r < 50:
                continue
            L = Layer()
            g_bio(L, (c[0], c[1]), min(r * .42, 62), (255, 120, 205))
            out = spray_layer(out, L, (255, 105, 200), seed + 31, outline=PLUM, glow=0.35)
    return out.convert("RGB")


# ------------------------------------------------------------------------------------------- vinyl cards & chips
def vinyl_card(L, c, w, h, ang, col, glyph, shadow=True, line=INK):
    """die-cut vinyl sticker: white border, coloured face, glyph"""
    def box(m):
        return [rot((c[0] + x * (w / 2 - m), c[1] + y * (h / 2 - m)), ang, c) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    if shadow:
        L.poly([(p[0] + 4, p[1] + 6) for p in box(0)], fill=(0, 0, 0), a=120)
    L.poly(box(0), fill=(250, 248, 240), outline=line, w=2.5)
    L.poly(box(7), fill=col, outline=line, w=2)
    # glossy diagonal highlight
    p = box(7)
    L.poly([p[0], (p[0][0] + (p[1][0] - p[0][0]) * .55, p[0][1] + (p[1][1] - p[0][1]) * .55),
            (p[0][0] + (p[3][0] - p[0][0]) * .5, p[0][1] + (p[3][1] - p[0][1]) * .5)], fill=(255, 255, 255), a=45)
    glyph(L, c, min(w, h) * .26)


def chip(L, box, fill=CRT_BG, edge=CRT_EDGE, a=235):
    L.rrect(box, 9, fill=fill, outline=INK, w=6, a=a)
    L.rrect(box, 9, fill=fill, outline=edge, w=2.2, a=a)


def hud(base, home=44, heat=80, inf=0, healthy=8, home_col=None, home_delta=None, flash=0.0, tip=None):
    """HUD (kept from the game's vocabulary): HOME / HEAT chips top-left, INFECTED vs healthy balance top-right."""
    L = Layer()
    chip(L, (24, 20, 236, 76))
    g_heart(L, (54, 48), 15, (255, 80, 110), INK)
    L.text((84, 48), str(home), f2(F_MONO, 34), home_col or (230, 250, 255), anchor="lm")
    L.text((158, 50), "/50", f2(F_MONO, 20), (130, 160, 185), anchor="lm")
    chip(L, (246, 20, 420, 76))
    g_flame(L, (276, 48), 16, (255, 150, 40), INK)
    L.text((304, 48), str(heat), f2(F_MONO, 34), (255, 225, 190), anchor="lm")
    # balance: INFECTED (plum biohazard) vs healthy
    chip(L, (1540, 20, 1896, 76))
    # infected side
    L.circle((1580, 48), 20, fill=PLUM, outline=VEIN, w=2.6)
    g_bio(L, (1580, 48), 12, VEIN)
    L.text((1616, 49), str(inf), f2(F_MONO, 34), (255, 150, 215), anchor="lm")
    # healthy side
    n = healthy
    L.text((1716, 49), str(n), f2(F_MONO, 34), UNTOUCHED, anchor="rm")
    L.rrect((1728, 30, 1750, 66), 4, fill=(10, 30, 44), outline=UNTOUCHED, w=2.2)
    L.rrect((1735, 38, 1743, 58), 2, fill=UNTOUCHED)
    # balance beam glyph
    tilt = 0 if inf == healthy else (-1 if inf < healthy else 1)
    L.line([(1650, 48 + 7 * tilt * -1), (1690, 48 + 7 * tilt)], (240, 250, 255), 3)
    L.circle((1670, 48), 3.5, fill=(240, 250, 255))
    return commit(base, L)


# --------------------------------------------------------------------------------------------- wheatpaste poster
def poster(base, box, ang, paper, ink_col, draw_fn, seed=1, shadow=True):
    """Wheatpaste poster (Obey): torn edges, wrinkles, halftone.  draw_fn(Layer, rect) draws content in 1x frame px at box."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rng = np.random.default_rng(seed)
    # paper silhouette with torn edge
    L = Layer()
    corners = [rot(p, ang, (cx, cy)) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    L.poly(corners, fill=paper)
    sil = layer_to_mask(L)
    n = _noise((H, W), 2.2, seed)
    sil_t = ((gaussian_filter(sil, 1.2) + n * 0.1) > 0.5).astype(np.float32)
    # content layer
    C = Layer()
    draw_fn(C, (x0, y0, x1, y1), ang, (cx, cy))
    content = np.asarray(C.down()).astype(np.float32) / 255
    # paper colour w/ wrinkle shading
    wr = _noise((H, W), 9, seed + 2) * 0.05 + _noise((H, W), 2, seed + 3) * 0.02
    pc = np.array(paper, np.float32) / 255
    img = np.ones((H, W, 3), np.float32) * pc
    img = img * (1 + wr[..., None])
    a_c = content[..., 3:4]
    img = img * (1 - a_c) + content[..., :3] * a_c
    img *= (1 + 0.04 * wr[..., None])
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    rgba[..., 3] = (sil_t * 255).astype(np.uint8)
    out = base.convert("RGBA")
    if shadow:
        sh = gaussian_filter(np.roll(np.roll(sil_t, 8, 0), 6, 1), 7) * 0.55
        shl = np.zeros((H, W, 4), np.uint8)
        shl[..., 3] = (sh * 255).astype(np.uint8)
        out = Image.alpha_composite(out, Image.fromarray(shl, "RGBA"))
    out = Image.alpha_composite(out, Image.fromarray(rgba, "RGBA"))
    return out


def halftone(L, rect, col, ang=0.5, step=9, grad=None):
    """halftone dot field; grad(x,y)->0..1 dot radius factor"""
    x0, y0, x1, y1 = rect
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(-60, 120):
        for j in range(-60, 120):
            px = x0 + (i * ca - j * sa) * step
            py = y0 + (i * sa + j * ca) * step
            if not (x0 <= px <= x1 and y0 <= py <= y1):
                continue
            k = grad(px, py) if grad else 1.0
            if k > 0.05:
                L.circle((px, py), step * .5 * k, fill=col)
