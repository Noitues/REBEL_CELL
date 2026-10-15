"""New corps: boss wheels on the LOCKED D4 kit (round 41 d4corp, used read-only), with the two new corp themes and
three motif options per corp. Identical copy in both scripts/ folders.

How: the round 41 renderer is table-driven by theme name. This module registers each option as a theme
(bezel material, accent, slice skin, slice scenes, crest lug, rim language, hub art, emblem glyph) by adding rows to
those tables and wrapping corp_rim / crest / _hub_std for the new themes only. Nothing in round41 is edited.
Option motifs that live outside the rim (tentacles, the air hose, jelly tendrils) are drawn after render() around the
returned centre. All randomness seeded.

python wheel41.py <aurelian|tethys> [options|final] [pick=A|B|C] [backdrop=<png>]
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
R41 = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\round41_wheel_stack\scripts"
sys.path.insert(1, R41)

import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import nc_kit as K  # noqa: E402

_cwd = os.getcwd()
os.chdir(R41)
import crests15 as C41  # noqa: E402  (round 41's own copy: glyph_mask() looks here first)
import d4corp  # noqa: E402
import frames as F  # noqa: E402
import motifs as MO  # noqa: E402
import roster as RS  # noqa: E402
import roster_wheel as RW  # noqa: E402
import scenes as S0  # noqa: E402
import scenes18  # noqa: E402
import skins  # noqa: E402
import slicelib  # noqa: E402
from frames import P  # noqa: E402
os.chdir(_cwd)

U = K.U
SL = K.SL


# ================================================================== shading helpers
def relief(mask, base, hi, lo, k=2.2, blur=6, spec=0.5, shape=None):
    """Shade a silhouette as a bevelled relief lit from the top-left: base colour, highlight, shadow, specular."""
    m = np.asarray(mask, np.float32) / 255
    h = np.asarray(mask.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255
    if shape is not None:
        h = h * 0.6 + shape * 0.4
    gy, gx = np.gradient(h)
    nl = -(gx * -0.6 + gy * -0.8) * k * blur
    lit = np.clip(0.55 + nl, 0, 1.2)
    base, hi, lo = (np.array(c, np.float32) for c in (base, hi, lo))
    col = np.where(lit[..., None] > 0.55, base + (hi - base) * np.clip((lit[..., None] - 0.55) / 0.5, 0, 1),
                   lo + (base - lo) * np.clip(lit[..., None] / 0.55, 0, 1))
    sp = np.clip((lit - 0.95) * 5, 0, 1)[..., None] * spec * 255
    col = np.clip(col + sp, 0, 255)
    out = np.dstack([col, m * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def keyline(img_rgba, w, col=(10, 8, 14)):
    a = img_rgba.split()[3]
    k = a.filter(ImageFilter.MaxFilter(int(w) * 2 + 1))
    lay = Image.new("RGBA", img_rgba.size, col + (0,))
    lay.putalpha(k)
    lay.alpha_composite(img_rgba)
    return lay


def glow_of(img_rgba, col, r, k=1.0):
    a = img_rgba.split()[3].filter(ImageFilter.GaussianBlur(r))
    lay = Image.new("RGBA", img_rgba.size, col + (0,))
    lay.putalpha(a.point(lambda v: int(min(255, v * k))))
    return lay


def pad_img(im, p):
    o = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    o.paste(im, (p, p))
    return o


# ================================================================== slice skins (screen texture space W x H)
def skin_aurelian(ctx, rng):
    W, H, ss = ctx.W, ctx.H, ctx.ss
    im = Image.new("RGB", (W, H), (40, 14, 28))
    d = ImageDraw.Draw(im)
    # porphyry speckle
    for _ in range(int(W * H / (40 * ss * ss))):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(0.6, 1.8) * ss
        c = [(70, 26, 44), (24, 8, 16), (96, 44, 60)][int(rng.integers(0, 3))]
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    # a verdigris meander band along the outer edge, travertine fillet under it
    y0 = 6 * ss
    d.rectangle([0, y0 - 2 * ss, W, y0 + 13 * ss], fill=(214, 196, 156))
    step = 14 * ss
    for x in range(-step, W + step, step):
        pts = [(x, y0 + 10 * ss), (x, y0), (x + 10 * ss, y0), (x + 10 * ss, y0 + 7 * ss), (x + 4 * ss, y0 + 7 * ss), (x + 4 * ss, y0 + 4 * ss)]
        d.line(pts, fill=(28, 168, 128), width=max(1, int(2.2 * ss)))
    # faint arcade arches (the corp motif) low in the screen
    for k in range(-1, int(W / (40 * ss)) + 2):
        x = k * 40 * ss + 20 * ss
        y = H * 0.82
        d.arc([x - 14 * ss, y - 14 * ss, x + 14 * ss, y + 14 * ss], 180, 360, fill=(70, 120, 100), width=max(1, ss))
        d.line([(x - 14 * ss, y), (x - 14 * ss, H)], fill=(70, 120, 100), width=max(1, ss))
    return im


def skin_tethys(ctx, rng):
    W, H, ss = ctx.W, ctx.H, ctx.ss
    a = np.zeros((H, W, 3), np.float32)
    t = np.linspace(0, 1, H)[:, None]
    a[..., 0] = 6 + 6 * t
    a[..., 1] = 30 - 16 * t
    a[..., 2] = 70 - 40 * t
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    # caustic net near the top (light from the surface), bubbles rising
    for _ in range(int(W / (5 * ss))):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.45)
        L = rng.uniform(8, 22) * ss
        ang = rng.uniform(0, math.pi)
        d.line([(x, y), (x + L * math.cos(ang), y + L * math.sin(ang) * 0.5)], fill=(60, 150, 210), width=max(1, ss))
    for _ in range(int(W / (14 * ss))):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(1.0, 3.5) * ss
        d.ellipse([x - r, y - r, x + r, y + r], outline=(120, 190, 255), width=max(1, ss // 2))
    im = im.filter(ImageFilter.GaussianBlur(0.4 * ss))
    return im


# ================================================================== slice scenes (upright, drawn over the skin)
def _sword(d, cx, cy, ang, L, w, col, ink, u):
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    def T(x, y):
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)
    blade = [T(0, -w), T(L * 0.78, -w), T(L, 0), T(L * 0.78, w), T(0, w)]
    d.polygon(blade, fill=col + (255,), outline=ink + (255,))
    d.line([T(0, 0), T(L * 0.8, 0)], fill=tuple(int(c * 0.75) for c in col) + (255,), width=max(1, int(u)))
    d.polygon([T(-4 * u, -w * 2.6), T(4 * u, -w * 2.6), T(4 * u, w * 2.6), T(-4 * u, w * 2.6)], fill=(200, 160, 80, 255), outline=ink + (255,))
    d.polygon([T(-26 * u, -w * 0.8), T(-4 * u, -w * 0.8), T(-4 * u, w * 0.8), T(-26 * u, w * 0.8)], fill=(90, 50, 30, 255), outline=ink + (255,))
    d.ellipse([T(-32 * u, 0)[0] - 6 * u, T(-32 * u, 0)[1] - 6 * u, T(-32 * u, 0)[0] + 6 * u, T(-32 * u, 0)[1] + 6 * u], fill=(200, 160, 80, 255))


def aur_attack(s, t):    # a gladius thrusts across the screen
    u, d, Pp = s.u, s.d, s.P
    k = S0.ease(min(1, t / 0.4))
    x = s.cx - 120 * u + 90 * u * k
    _sword(d, x, s.Y(0.74), -12, 150 * u, 9 * u, (226, 230, 236), Pp["ink"], u)
    for j in range(4):
        y = s.Y(0.66) + j * 8 * u
        d.line([(x - 70 * u - j * 10 * u, y), (x - 30 * u, y)], fill=Pp["a"] + (150,), width=max(1, int(2 * u)))


def aur_crit(s, t):      # the retiarius' trident strikes, sparks
    u, d, Pp = s.u, s.d, s.P
    cx, cy = s.cx + 20 * u, s.Y(0.78)
    d.line([(cx - 120 * u, cy + 40 * u), (cx + 30 * u, cy - 30 * u)], fill=(180, 150, 90, 255), width=int(7 * u))
    for k in (-1, 0, 1):
        a = math.radians(-25 + k * 14)
        d.line([(cx + 30 * u, cy - 30 * u), (cx + 30 * u + 60 * u * math.cos(a), cy - 30 * u + 60 * u * math.sin(a))], fill=(220, 224, 230, 255), width=int(6 * u))
    if t % 1 < 0.6:
        for k in range(10):
            a = math.radians(k * 36 + 15)
            r0, r1 = 20 * u, 46 * u
            px, py = cx + 80 * u, cy - 50 * u
            d.line([(px + r0 * math.cos(a), py + r0 * math.sin(a)), (px + r1 * math.cos(a), py + r1 * math.sin(a))], fill=Pp["gold"] + (255,), width=int(3 * u))


def aur_defend(s, t):    # testudo: a wall of scuta locks shut along the inner edge
    u, d, Pp = s.u, s.d, s.P
    y0 = s.Y(0.66)
    k = S0.ease(min(1, t / 0.5))
    n = 6
    for j in range(n):
        x = s.cx + (j - (n - 1) / 2) * 34 * u * (0.7 + 0.3 * k)
        d.rounded_rectangle([x - 16 * u, y0, x + 16 * u, y0 + 52 * u], radius=int(5 * u), fill=(150, 30, 46, 255), outline=Pp["ink"] + (255,), width=max(1, int(2 * u)))
        d.ellipse([x - 6 * u, y0 + 20 * u, x + 6 * u, y0 + 32 * u], fill=Pp["gold"] + (255,))
        d.line([(x, y0 + 4 * u), (x, y0 + 48 * u)], fill=Pp["gold"] + (200,), width=max(1, int(2 * u)))


def aur_shield(s, t):    # the arena sand: raked lines + a round parma
    u, d, Pp = s.u, s.d, s.P
    for j in range(7):
        y = s.Y(0.6) + j * 9 * u
        d.line([(s.X(-1, y), y), (s.X(1, y), y)], fill=(196, 168, 110, 140), width=max(1, int(2 * u)))
    cx, cy = s.cx + 30 * u, s.Y(0.72)
    r = 26 * u * (1 + 0.04 * math.sin(t * 6.28))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=Pp["a"] + (255,), outline=Pp["ink"] + (255,), width=int(2 * u))
    d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35], fill=Pp["gold"] + (255,))


def aur_miss(s, t):      # an empty arena: sand falling through an hourglass of light
    u, d, Pp = s.u, s.d, s.P
    rng = random.Random(3)
    for _ in range(40):
        x = s.cx + rng.uniform(-60, 60) * u
        y = (rng.uniform(0, 1) + t) % 1 * s.H
        d.ellipse([x - u, y - u, x + u, y + u], fill=(200, 180, 140, 160))


def aur_special(s, t):   # VERDICT: the crowd, thumbs going down along the stands
    u, d, Pp = s.u, s.d, s.P
    for row in range(3):
        y = s.Y(0.62) + row * 20 * u
        n = 9
        for j in range(n):
            x = s.X(-0.95 + 1.9 * j / (n - 1), y)
            d.ellipse([x - 6 * u, y - 6 * u, x + 6 * u, y + 6 * u], fill=(36, 26, 40, 255))
            d.rectangle([x - 8 * u, y + 5 * u, x + 8 * u, y + 18 * u], fill=(36, 26, 40, 255))
            down = ((j + row) % 3 != 0) == (t % 1 > 0.3)
            dy = 10 * u if down else -10 * u
            d.line([(x + 9 * u, y + 2 * u), (x + 9 * u, y + 2 * u + dy)], fill=Pp["a"] + (255,), width=int(3 * u))


def teth_attack(s, t):   # a harpoon bolt on its line
    u, d, Pp = s.u, s.d, s.P
    k = S0.ease(min(1, t / 0.45))
    y = s.Y(0.74)
    x = s.cx - 140 * u + 120 * u * k
    d.line([(s.X(-1, y), y + 6 * u), (x, y)], fill=(170, 180, 190, 255), width=max(1, int(2 * u)))
    d.polygon([(x, y - 4 * u), (x + 60 * u, y - 2 * u), (x + 84 * u, y), (x + 60 * u, y + 2 * u), (x, y + 4 * u)], fill=(220, 228, 236, 255), outline=Pp["ink"] + (255,))
    d.polygon([(x + 60 * u, y - 2 * u), (x + 48 * u, y - 12 * u), (x + 54 * u, y - 2 * u)], fill=(220, 228, 236, 255))
    d.polygon([(x + 60 * u, y + 2 * u), (x + 48 * u, y + 12 * u), (x + 54 * u, y + 2 * u)], fill=(220, 228, 236, 255))
    for j in range(5):
        bx = x - 20 * u - j * 18 * u
        d.ellipse([bx - 3 * u, y - 10 * u - j * 2 * u, bx + 3 * u, y - 4 * u - j * 2 * u], outline=(150, 210, 255, 200), width=max(1, u))


def teth_crit(s, t):     # a torpedo with its bubble trail and the burst
    u, d, Pp = s.u, s.d, s.P
    y = s.Y(0.76)
    x = s.cx + 10 * u
    d.rounded_rectangle([x - 70 * u, y - 10 * u, x + 40 * u, y + 10 * u], radius=int(10 * u), fill=(40, 46, 58, 255), outline=Pp["ink"] + (255,))
    d.rectangle([x - 70 * u, y - 10 * u, x - 56 * u, y + 10 * u], fill=Pp["hot"] + (255,))
    for j in range(8):
        bx = x - 80 * u - j * 14 * u
        r = (2 + j * 0.6) * u
        d.ellipse([bx - r, y - r + math.sin(j) * 4 * u, bx + r, y + r + math.sin(j) * 4 * u], outline=(150, 210, 255, 220), width=max(1, u))
    if t % 1 > 0.5:
        for k in range(12):
            a = math.radians(k * 30)
            d.line([(x + 54 * u, y), (x + 54 * u + 40 * u * math.cos(a), y + 40 * u * math.sin(a))], fill=Pp["gold"] + (220,), width=int(3 * u))


def teth_defend(s, t):   # a riveted bulkhead slides shut
    u, d, Pp = s.u, s.d, s.P
    k = S0.ease(min(1, t / 0.5))
    y0 = s.Y(0.58)
    w = 70 * u * k
    for sx in (-1, 1):
        x0 = s.cx + sx * (110 * u - w)
        d.rectangle([min(x0, s.cx + sx * 110 * u), y0, max(x0, s.cx + sx * 110 * u), s.H], fill=(46, 54, 66, 255), outline=Pp["ink"] + (255,))
        for j in range(4):
            d.ellipse([x0 - sx * 8 * u - 3 * u, y0 + 10 * u + j * 16 * u, x0 - sx * 8 * u + 3 * u, y0 + 16 * u + j * 16 * u], fill=(130, 140, 150, 255))
    d.line([(s.cx - 40 * u, y0 + 4 * u), (s.cx + 40 * u, y0 + 4 * u)], fill=Pp["hot"] + (255,), width=int(3 * u))


def teth_shield(s, t):   # an air pocket: one big bubble, wobbling
    u, d, Pp = s.u, s.d, s.P
    cx, cy = s.cx + 30 * u, s.Y(0.72)
    r = 34 * u * (1 + 0.05 * math.sin(t * 6.28))
    d.ellipse([cx - r, cy - r * 0.94, cx + r, cy + r * 0.94], outline=(170, 220, 255, 255), width=int(3 * u))
    d.arc([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], 200, 260, fill=(255, 255, 255, 255), width=int(4 * u))
    s.g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=Pp["a"] + (90,))


def teth_miss(s, t):     # empty water: marine snow drifting down
    u, d = s.u, s.d
    rng = random.Random(5)
    for _ in range(46):
        x = s.cx + rng.uniform(-70, 70) * u
        y = (rng.uniform(0, 1) + t * 0.5) % 1 * s.H
        d.ellipse([x - u, y - u, x + u, y + u], fill=(200, 230, 240, 150))


def teth_special(s, t):  # TIDE: the water level rises across the screen, swells on top
    u, d, Pp = s.u, s.d, s.P
    lvl = s.Y(0.58 + 0.12 * math.sin(t * 6.28))
    pts = [(x, lvl + 5 * u * math.sin(x / (18 * u) + t * 6.28)) for x in range(0, s.W + 4, max(2, int(3 * u)))]
    d.polygon(pts + [(s.W, s.H), (0, s.H)], fill=(30, 90, 220, 170))
    d.line(pts, fill=(150, 220, 255, 255), width=int(3 * u))


SCENES = {"aurelian": {"ATTACK": aur_attack, "CRITICAL": aur_crit, "DEFEND": aur_defend, "SHIELD": aur_shield,
                       "MISS": aur_miss, "SPECIAL": aur_special},
          "tethys": {"ATTACK": teth_attack, "CRITICAL": teth_crit, "DEFEND": teth_defend, "SHIELD": teth_shield,
                     "MISS": teth_miss, "SPECIAL": teth_special}}


# ================================================================== options (rim language, lug, hub, overlay)
def ring_band(d, gd, ss, R0, R1, col, w=None):
    rm = (R0 + R1) / 2
    bb = [RW.CX * ss - rm * ss, RW.CY * ss - rm * ss, RW.CX * ss + rm * ss, RW.CY * ss + rm * ss]
    d.ellipse(bb, outline=col + (255,), width=int((w or (R1 - R0)) * ss))


def rim_colosseum(img, d, gd, ss, R0, R1, acc, skip, A):
    """Two tiers of arcade arches round the rim: travertine piers, dark openings with a verdigris glow inside."""
    ring_band(d, gd, ss, R0, R1, A["paper"])
    n = 60
    for i in range(n):
        a = i * 360 / n + 3
        for (r0, r1) in ((R0 + 1.5, (R0 + R1) / 2 - 0.5), ((R0 + R1) / 2 + 0.5, R1 - 1.5)):
            h = r1 - r0
            w = 1.9
            rs = r1 - h * 0.38                                      # springline; the arch head rises outward
            poly = [P(r0, a - w, ss), P(r0, a + w, ss)]
            poly += [P(rs + h * 0.36 * math.sin(math.pi * k / 8), a + w - 2 * w * k / 8, ss) for k in range(9)]
            d.polygon(poly, fill=(26, 40, 34, 255))
            gd.polygon(poly, fill=acc + (90,))
    for r in (R0 + 0.5, (R0 + R1) / 2, R1 - 0.5):
        bb = [RW.CX * ss - r * ss, RW.CY * ss - r * ss, RW.CX * ss + r * ss, RW.CY * ss + r * ss]
        d.ellipse(bb, outline=(120, 100, 70, 255), width=max(1, int(1.0 * ss)))


def rim_arena(img, d, gd, ss, R0, R1, acc, skip, A):
    """Sand-coloured band with bronze studs; four portcullis gate plates."""
    ring_band(d, gd, ss, R0, R1, (200, 170, 112))
    for i in range(72):
        a = i * 5
        x, y = P((R0 + R1) / 2, a, ss)
        r = 1.6 * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 84, 40, 255))
    for a in (45, 135, 225, 315):
        pts = RW.arc_poly(R0 - 2, R1 + 2, a - 6, a + 6, ss, 8)
        d.polygon(pts, fill=(30, 22, 18, 255), outline=(180, 140, 70, 255), width=max(1, ss))
        for k in range(-2, 3):
            d.line([P(R0 - 1, a + k * 2.2, ss), P(R1 + 1, a + k * 2.2, ss)], fill=(160, 130, 80, 255), width=max(1, int(1.2 * ss)))


def rim_laurel(img, d, gd, ss, R0, R1, acc, skip, A):
    """A continuous gilded laurel round the rim on porphyry."""
    ring_band(d, gd, ss, R0, R1, (58, 20, 38))
    gold = (226, 186, 96)
    rm = (R0 + R1) / 2
    for i in range(90):
        a = i * 4
        for side in (-1, 1):
            cx, cy = P(rm + side * 2.6, a, ss)
            ang = math.radians(a) + side * 0.5
            L, W = 7 * ss, 2.6 * ss
            tang = (math.cos(math.radians(a)), math.sin(math.radians(a)))
            pts = []
            for k in range(9):
                t = -1 + 2 * k / 8
                pts.append((t * L / 2, (1 - t * t) * W / 2))
            pts += [(x, -y) for x, y in reversed(pts)]
            th = math.radians(a + 60 * side)
            ca, sa = math.cos(th), math.sin(th)
            d.polygon([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts], fill=gold + (255,), outline=(90, 60, 20, 255))
    gd.ellipse([RW.CX * ss - R1 * ss, RW.CY * ss - R1 * ss, RW.CX * ss + R1 * ss, RW.CY * ss + R1 * ss], outline=gold + (120,), width=int(4 * ss))


def rim_brass(img, d, gd, ss, R0, R1, acc, skip, A):
    """Diving-helmet brass: a riveted collar ring, a blue glass seam."""
    ring_band(d, gd, ss, R0, R1, (150, 112, 52))
    for r in (R0 + 1, R1 - 1):
        bb = [RW.CX * ss - r * ss, RW.CY * ss - r * ss, RW.CX * ss + r * ss, RW.CY * ss + r * ss]
        d.ellipse(bb, outline=(232, 196, 120, 255), width=max(1, int(1.4 * ss)))
    for i in range(48):
        x, y = P((R0 + R1) / 2, i * 7.5, ss)
        r = 2.4 * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 206, 140, 255), outline=(70, 50, 20, 255), width=max(1, ss // 2))


def rim_octo(img, d, gd, ss, R0, R1, acc, skip, A):
    """Sucker ring: dark wet hull with rows of pale suckers, an abyss-blue seam."""
    ring_band(d, gd, ss, R0, R1, (40, 22, 40))
    for i in range(60):
        a = i * 6
        for k, rr in enumerate((R0 + 4, R1 - 4)):
            x, y = P(rr, a + (3 if k else 0), ss)
            r = 2.8 * ss
            d.ellipse([x - r, y - r, x + r, y + r], fill=(214, 150, 170, 255), outline=(90, 40, 60, 255), width=max(1, ss // 2))
            d.ellipse([x - r * 0.4, y - r * 0.4, x + r * 0.4, y + r * 0.4], fill=(120, 60, 80, 255))
    bb = [RW.CX * ss - R1 * ss, RW.CY * ss - R1 * ss, RW.CX * ss + R1 * ss, RW.CY * ss + R1 * ss]
    gd.ellipse(bb, outline=acc + (180,), width=int(5 * ss))
    d.ellipse(bb, outline=acc + (255,), width=max(1, int(1.4 * ss)))


def rim_photo(img, d, gd, ss, R0, R1, acc, skip, A):
    """Bioluminescent ring: a dark band, photophore dots in pairs, a coral crust at the bottom quarter."""
    ring_band(d, gd, ss, R0, R1, (10, 24, 44))
    ph = (124, 242, 228)
    for i in range(90):
        x, y = P((R0 + R1) / 2, i * 4, ss)
        r = (1.6 if i % 3 else 2.6) * ss
        gd.ellipse([x - r * 2, y - r * 2, x + r * 2, y + r * 2], fill=ph + (140,))
        d.ellipse([x - r, y - r, x + r, y + r], fill=ph + (255,))
    rng = random.Random(9)
    for i in range(70):                                         # coral growth (bottom)
        a = rng.uniform(140, 220)
        rr = rng.uniform(R0, R1 + 6)
        x, y = P(rr, a, ss)
        r = rng.uniform(1.5, 4.0) * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=rng.choice([(255, 120, 110), (240, 90, 120), (255, 170, 140)]) + (255,))


def lug_round(img, d, gd, ss, x, y, r, corp, acc, emblem, fill=(14, 12, 20), ring=None):
    gd.ellipse([x - r, y - r, x + r, y + r], fill=acc + (150,))
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill + (255,), outline=(ring or acc) + (255,), width=int(3 * ss))
    g = RW.tinted_glyph(emblem, int(r * 1.25), acc)
    img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))


# hub art builders return an RGBA image (side = 2 R) drawn behind the name plate
def hub_emblem(fn, col, R, ss, mat):
    side = int(2 * R * ss)
    m = K.mask(fn, int(side * 0.62))
    if mat == "flat":
        art = K.tint(m, col)
    else:
        base, hi, lo = mat
        art = relief(m, base, hi, lo, blur=max(3, side // 90))
    art = keyline(pad_img(art, 12), max(3, side // 110))
    return art


def hub_sand(R, ss, rng):
    side = int(2 * R * ss)
    a = np.zeros((side, side, 3), np.float32) + np.array([176, 140, 86], np.float32)
    yy, xx = np.mgrid[0:side, 0:side].astype(np.float32)
    rr = np.hypot(xx - side / 2, yy - side / 2)
    a *= (0.85 + 0.15 * np.sin(rr / (5.0 * ss)))[..., None]                 # raked rings
    a += np.asarray(Image.effect_noise((side, side), 18), np.float32)[..., None] * 0.15 - 20
    m = (rr < side / 2 - 2).astype(np.float32) * 255
    return Image.fromarray(np.dstack([np.clip(a, 0, 255), m]).astype(np.uint8), "RGBA")


def hub_bell(R, ss):
    """Translucent jelly bell: radial glass falloff, bright rim, inner gonad ring."""
    side = int(2 * R * ss)
    yy, xx = np.mgrid[0:side, 0:side].astype(np.float32)
    dx, dy = (xx - side / 2) / (side / 2), (yy - side / 2) / (side / 2)
    rr = np.hypot(dx, dy)
    a = np.zeros((side, side, 4), np.float32)
    col = np.array([90, 150, 255], np.float32)
    inner = np.clip(1 - rr, 0, 1)
    a[..., :3] = col * (0.25 + 0.5 * rr ** 3)[..., None] + np.array([200, 240, 255]) * np.exp(-((rr - 0.92) / 0.05) ** 2)[..., None]
    ring = np.exp(-((rr - 0.45) / 0.06) ** 2)
    a[..., :3] += np.array([255, 120, 200]) * ring[..., None] * 0.6
    a[..., 3] = np.clip((rr < 0.98) * (0.55 + 0.45 * rr), 0, 1) * 255
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def make_hub(opt):
    def hub(img, d, gd, spec, ss, hub_r, acc, st, lod, hp_in_hub=False):
        c = (RW.CX * ss, RW.CY * ss)
        R = hub_r
        d.ellipse([c[0] - R * ss, c[1] - R * ss, c[0] + R * ss, c[1] + R * ss], fill=opt["hub_fill"] + (255,), outline=acc + (255,), width=int(3 * ss))
        for rr in range(16, int(R) - 6, 9):
            d.ellipse([c[0] - rr * ss, c[1] - rr * ss, c[0] + rr * ss, c[1] + rr * ss], outline=(255, 255, 255, 10), width=ss)
        art = opt["hub_art"](R, ss)
        if art is not None:
            img.alpha_composite(art, (int(c[0] - art.width / 2), int(c[1] - art.height / 2 - opt.get("art_dy", 0.16) * R * ss)))
        # name plate
        name = spec["hub"]["name"].upper()
        sub = spec["hub"].get("sub", "")
        fb = slicelib.f_num(int(25 * ss))
        fsub = slicelib.f_ui(int(11 * ss))
        w = max(fb.getlength(name), fsub.getlength(sub)) + 22 * ss
        y = c[1] + R * 0.42 * ss
        d.rounded_rectangle([c[0] - w / 2, y - 4 * ss, c[0] + w / 2, y + 44 * ss], radius=int(8 * ss), fill=(8, 8, 12, 230), outline=acc + (255,), width=max(1, int(1.5 * ss)))
        d.text((c[0] - fb.getlength(name) / 2, y - 1 * ss), name, font=fb, fill=(255, 255, 255, 255), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255))
        d.text((c[0] - fsub.getlength(sub) / 2, y + 28 * ss), sub, font=fsub, fill=(205, 205, 215, 255))
    return hub


# ---- overlays drawn on the final wheel image (centre cx, cy in output px; ss scale)
def ov_tentacles(img, cx, cy, ss, acc):
    """Octopus arms curling round the outer ring: tapered, suckered, wet highlight; clear of the pointer (top)."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    R = 476 * ss
    body = (120, 40, 70)
    for k, (a0, sweep, s) in enumerate(((58, 66, 1), (126, 50, -1), (234, -50, 1), (302, -66, -1))):
        pts = []
        n = 80
        for i in range(n + 1):
            t = i / n
            a = math.radians(a0 + sweep * t - 90)
            r = R + 18 * ss * math.sin(t * math.pi * 2.0 + k) + (40 * ss * t if k == 4 else 0)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), 30 * ss * (1 - t) + 7 * ss))
        # curl the tip
        x, y, _ = pts[-1]
        a_end = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
        for i in range(30):
            t = i / 29
            a_end += s * 0.22
            x += math.cos(a_end) * 4 * ss * (1 - t * 0.6)
            y += math.sin(a_end) * 4 * ss * (1 - t * 0.6)
            pts.append((x, y, 7 * ss * (1 - t) + 2 * ss))
        for x, y, w in pts:
            d.ellipse([x - w / 2 - 2 * ss, y - w / 2 - 2 * ss, x + w / 2 + 2 * ss, y + w / 2 + 2 * ss], fill=(14, 6, 12, 255))
        for x, y, w in pts:
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=body + (255,))
        for x, y, w in pts[::1]:
            d.ellipse([x - w * 0.3, y - w * 0.42, x + w * 0.05, y - w * 0.2], fill=(220, 140, 170, 160))
        for i in range(0, len(pts), 5):
            x, y, w = pts[i]
            r = w * 0.18
            d.ellipse([x - r, y + w * 0.12 - r, x + r, y + w * 0.12 + r], fill=(250, 200, 210, 255), outline=(80, 30, 50, 255))
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(8 * ss))
    shl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shl.putalpha(sh.point(lambda v: int(v * 0.6)))
    img.alpha_composite(shl, (int(6 * ss), int(10 * ss)))
    img.alpha_composite(lay)


def ov_hose(img, cx, cy, ss, acc):
    """A ribbed air hose wrapping the outside of the rim, entering from the bottom, clear of the pointer."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pts = []
    n = 220
    for i in range(n + 1):
        t = i / n
        a = math.radians(140 + 260 * t - 90 + 90)
        r = (470 + 16 * math.sin(t * math.pi * 9)) * ss
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    tail = [(cx + (470 * ss) * math.cos(math.radians(140)) - 40 * ss * k, cy + 470 * ss * math.sin(math.radians(140)) + 60 * ss * k) for k in range(6)]
    pts = list(reversed(tail)) + pts
    w = 22 * ss
    for x, y in pts:
        d.ellipse([x - w / 2 - 3 * ss, y - w / 2 - 3 * ss, x + w / 2 + 3 * ss, y + w / 2 + 3 * ss], fill=(14, 10, 8, 255))
    for i, (x, y) in enumerate(pts):
        c = (120, 104, 84) if (i // 2) % 2 else (90, 76, 60)
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=c + (255,))
    for x, y in pts[::3]:
        d.ellipse([x - w * 0.32, y - w * 0.4, x - w * 0.02, y - w * 0.18], fill=(220, 200, 170, 140))
    img.alpha_composite(lay)


def ov_tendrils(img, cx, cy, ss, acc):
    """Jelly tendrils trailing below the wheel, translucent with a photophore glow."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = random.Random(4)
    for k in range(9):
        x0 = cx + (k - 4) * 70 * ss
        y0 = cy + 380 * ss - abs(k - 4) * 24 * ss
        pts = [(x0 + 18 * ss * math.sin(i * 0.35 + k), y0 + i * 9 * ss) for i in range(40)]
        d.line(pts, fill=(150, 220, 255, 150), width=int((8 if k % 2 else 4) * ss))
        for i in range(0, 40, 6):
            x, y = pts[i]
            d.ellipse([x - 3 * ss, y - 3 * ss, x + 3 * ss, y + 3 * ss], fill=(124, 242, 228, 220))
    g = lay.filter(ImageFilter.GaussianBlur(6 * ss))
    img.alpha_composite(g)
    img.alpha_composite(lay)


def ov_none(img, cx, cy, ss, acc):
    pass


def _pp(cx, cy, r, a):
    """Polar to image px around the wheel centre (a = degrees from the top, clockwise)."""
    t = math.radians(a)
    return (cx + r * math.sin(t), cy - r * math.cos(t))


def ov_arcade(img, cx, cy, ss, acc):
    """The Colosseum facade wraps both flanks of the wheel: two tiers of arches outside the threat ring, clear of the
    banner/pointer (top) and the HP arc (bottom). Travertine, verdigris light in the openings, cornice trims."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    gl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(gl)
    r0, r1 = 458 * ss, 512 * ss
    trav, trav_d, ink = (226, 206, 160), (150, 128, 90), (20, 14, 12)
    for (a0, a1) in ((34, 80), (100, 126), (234, 260), (280, 326)):
        n = 60
        outer = [_pp(cx, cy, r1, a0 + (a1 - a0) * k / n) for k in range(n + 1)]
        inner = [_pp(cx, cy, r0, a1 - (a1 - a0) * k / n) for k in range(n + 1)]
        d.polygon(outer + inner, fill=trav + (255,), outline=ink + (255,))
        rm = (r0 + r1) / 2
        for rr in (r0 + 3 * ss, rm, r1 - 3 * ss):                           # cornices
            pts = [_pp(cx, cy, rr, a0 + (a1 - a0) * k / n) for k in range(n + 1)]
            d.line(pts, fill=trav_d + (255,), width=max(1, int(3 * ss)))
        pts = [_pp(cx, cy, r1 + 2 * ss, a0 + (a1 - a0) * k / n) for k in range(n + 1)]
        g.line(pts, fill=acc + (255,), width=int(5 * ss))
        d.line(pts, fill=(200, 255, 236, 255), width=max(1, int(1.5 * ss)))
        bays = max(3, int((a1 - a0) / 5.2))
        for b in range(bays):
            a = a0 + (b + 0.5) * (a1 - a0) / bays
            for (ra, rb) in ((r0 + 5 * ss, rm - 3 * ss), (rm + 3 * ss, r1 - 5 * ss)):
                h = rb - ra
                w = 1.55
                rs = rb - h * 0.42
                poly = [_pp(cx, cy, ra, a - w), _pp(cx, cy, ra, a + w)]
                poly += [_pp(cx, cy, rs + h * 0.4 * math.sin(math.pi * k / 8), a + w - 2 * w * k / 8) for k in range(9)]
                d.polygon(poly, fill=(18, 36, 30, 255))
                g.polygon(poly, fill=acc + (200,))
            for side in (-1, 1):                                            # half-columns between bays
                a2 = a + side * (a1 - a0) / bays / 2
                d.line([_pp(cx, cy, r0 + 4 * ss, a2), _pp(cx, cy, r1 - 4 * ss, a2)], fill=(250, 238, 210, 255), width=max(1, int(2 * ss)))
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(7 * ss))
    shl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shl.putalpha(sh.point(lambda v: int(v * 0.6)))
    img.alpha_composite(shl, (int(5 * ss), int(9 * ss)))
    img.alpha_composite(glow_of(gl, acc, 6 * ss, 1.2))
    img.alpha_composite(lay)
    gi = gl.copy()
    gi.putalpha(gl.split()[3].point(lambda v: int(v * 0.5)))
    img.alpha_composite(gi)


GOLD = (226, 186, 96)
OPTIONS = {
    "aurelian": {
        "A": dict(title="A  COLOSSEUM", rim=rim_colosseum, emblem=K.g_verdict3, hub_fill=(38, 14, 28), lug_fill=(38, 14, 28),
                  hub_art=lambda R, ss: hub_emblem(K.g_verdict3, None, R, ss, ((226, 214, 186), (255, 252, 240), (120, 100, 70))),
                  overlay=ov_arcade, note="Rim + flanks = two tiers of arcade arches (the Circus Aurelius). Hub = the thumb turned down (VERDICT), carved travertine."),
        "B": dict(title="B  ARENA", rim=rim_arena, emblem=K.g_arena_gate, hub_fill=(70, 50, 26), lug_fill=(40, 28, 16),
                  hub_art=lambda R, ss: hub_sand(R * 0.96, ss, None), art_dy=0.0,
                  overlay=ov_none, note="Hub = raked arena sand; rim = sand band with bronze studs and four portcullis gates."),
        "C": dict(title="C  EMPEROR", rim=rim_laurel, emblem=K.g_emperor, hub_fill=(40, 12, 26), lug_fill=(40, 12, 26),
                  hub_art=lambda R, ss: hub_emblem(K.g_emperor, None, R, ss, ((236, 232, 222), (255, 255, 255), (130, 124, 116))),
                  overlay=ov_none, note="Hub = a marble emperor bust in profile; rim = a continuous gilded laurel on porphyry."),
    },
    "tethys": {
        "A": dict(title="A  DIVER", rim=rim_brass, emblem=K.g_helmet, hub_fill=(10, 18, 36), lug_fill=(40, 30, 14),
                  hub_art=lambda R, ss: hub_emblem(K.g_helmet, None, R, ss, ((196, 150, 70), (255, 230, 160), (90, 60, 20))),
                  overlay=ov_hose, note="Hub = the brass diving helmet; rim = riveted brass collar; an air hose wraps the outside."),
        "B": dict(title="B  OCTOPUS", rim=rim_octo, emblem=K.g_octopus, hub_fill=(16, 8, 24), lug_fill=(30, 10, 26),
                  hub_art=lambda R, ss: hub_emblem(K.g_octopus, None, R, ss, ((170, 60, 100), (255, 170, 200), (60, 14, 40))),
                  overlay=ov_tentacles, note="Hub = the octopus (its ink = the black smoke); rim = suckers; four arms curl round the threat ring."),
        "C": dict(title="C  JELLYFISH", rim=rim_photo, emblem=K.g_jelly, hub_fill=(6, 14, 34), lug_fill=(6, 14, 34),
                  hub_art=lambda R, ss: hub_bell(R * 0.9, ss), art_dy=0.05,
                  overlay=ov_tendrils, note="Hub = a translucent bell; rim = photophore dots + a coral crust; tendrils trail below."),
    },
}

CORP_ACC = {"aurelian": dict(a=(41, 219, 166), dim=(20, 100, 76), hot=(255, 60, 70), paper=(233, 213, 170), ink=(30, 10, 22), gold=(201, 163, 90)),
            "tethys": dict(a=(47, 107, 255), dim=(20, 46, 120), hot=(200, 38, 78), paper=(124, 242, 228), ink=(4, 10, 26), gold=(255, 233, 184))}
CORP_BASE = {"aurelian": (0.46, 0.40, 0.30), "tethys": (0.10, 0.16, 0.28)}
CORP_BEZEL = {"aurelian": (0.20, 0.07, 0.13), "tethys": (0.04, 0.08, 0.18)}
SLOTS = {
    "aurelian": [dict(program="ZERO-DAY", value=24, special=None, badge=None, name="Crit 24", id="c"),
                 dict(program="VIRUS", value=3, special="verdict", badge=None, name="Verdict", id="v"),
                 dict(program="FIREWALL", value=12, special=None, badge=None, name="Defend 12", id="d"),
                 dict(program="EXPLOIT", value=14, special=None, badge=None, name="Attack 14", id="a"),
                 dict(program="SANDBOX", value=8, special=None, badge=None, name="Shield 8", id="s"),
                 dict(program="NULL", value=0, special=None, badge=None, name="Miss", id="m")],
    "tethys": [dict(program="ZERO-DAY", value=22, special=None, badge=None, name="Crit 22", id="c"),
               dict(program="VIRUS", value=3, special="tide", badge=None, name="Tide", id="t"),
               dict(program="SANDBOX", value=10, special=None, badge=None, name="Shield 10", id="s"),
               dict(program="EXPLOIT", value=12, special=None, badge=None, name="Attack 12", id="a"),
               dict(program="FIREWALL", value=14, special=None, badge=None, name="Defend 14", id="d"),
               dict(program="NULL", value=0, special=None, badge=None, name="Miss", id="m")],
}
_REG = {}
_orig_rim, _orig_crest, _orig_hub = d4corp.corp_rim, d4corp.crest, F._hub_std


def register(corp, key):
    theme = "%s_%s" % (corp, key)
    if theme in _REG:
        return theme
    o = OPTIONS[corp][key]
    A = dict(CORP_ACC[corp])
    d4corp.CORP_STYLE[theme] = dict(base=CORP_BASE[corp], name=K.CORPS[corp]["name"])
    d4corp.ARMOUR_BASE[theme] = (40, 30, 30)
    MO.ACCENT[theme] = A
    slicelib.CORPS[theme] = dict(name=K.CORPS[corp]["name"], col=A["a"], bezel=CORP_BEZEL[corp])
    skins.SKINS[theme] = skin_aurelian if corp == "aurelian" else skin_tethys
    skins.BOSS[theme] = lambda ctx, mat, phase, rng: mat
    scenes18.SCENES[theme] = SCENES[corp]
    scenes18.PAL[theme] = A
    gname = "NC_EM_" + theme.upper()
    C41.CUSTOM[gname] = o["emblem"]
    RW.CORP_EMBLEM[theme] = gname
    spec_glyph = "NC_SP_" + corp.upper()
    C41.CUSTOM[spec_glyph] = K.g_verdict3 if corp == "aurelian" else _g_tide
    RW.SPECIAL_GLYPH["verdict" if corp == "aurelian" else "tide"] = spec_glyph
    _REG[theme] = dict(corp=corp, key=key, o=o, A=A, hub=make_hub(o))
    return theme


def _g_tide():
    m, d = K.new()
    for k, yb in enumerate((150, 256, 362)):
        K.wave_band(d, 40, 472, yb, 34, 170, 46, phase=k)
    return m


def rim(img, d, gd, ss, corp, R0, R1, acc, skip=()):
    if corp in _REG:
        r = _REG[corp]
        return r["o"]["rim"](img, d, gd, ss, R0, R1, acc, skip, r["A"])
    return _orig_rim(img, d, gd, ss, corp, R0, R1, acc, skip)


def crest(img, d, gd, ss, x, y, r, corp, acc, emblem):
    if corp in _REG:
        o = _REG[corp]["o"]
        return lug_round(img, d, gd, ss, x, y, r, corp, acc, emblem, fill=o["lug_fill"])
    return _orig_crest(img, d, gd, ss, x, y, r, corp, acc, emblem)


def hub_std(img, d, gd, spec, ss, hub_r, acc, st, lod, hp_in_hub=False):
    if spec["theme"] in _REG and not lod:
        return _REG[spec["theme"]]["hub"](img, d, gd, spec, ss, hub_r, acc, st, lod, hp_in_hub)
    return _orig_hub(img, d, gd, spec, ss, hub_r, acc, st, lod, hp_in_hub)


d4corp.corp_rim, d4corp.crest, F._hub_std = rim, crest, hub_std


def spec_for(corp, key):
    theme = register(corp, key)
    p1, p2, m = RS.boss_specs("meridian")
    import copy
    s = copy.deepcopy(p1)
    C = K.CORPS[corp]
    s["theme"] = theme
    s["key"] = theme
    s["slots"] = [dict(x) for x in SLOTS[corp]]
    s["hub"] = dict(emblem=RW.CORP_EMBLEM[theme], name=C["server"].replace("THE ", "The ").title() if False else C["server"],
                    sub=C["hub"].title())
    s["boss"] = dict(phase=1, pips=[0.66, 0.33], title=C["server"], sub="%s  |  BOSS  |  PHASE 1" % C["name"])
    s["seed"] = 31 if corp == "aurelian" else 37
    return s


def render_option(corp, key, ss=1):
    s = spec_for(corp, key)
    cwd = os.getcwd()
    os.chdir(R41)
    try:
        im, c, meta = d4corp.render(s, ss=ss)
    finally:
        os.chdir(cwd)
    im = pad_img(im, int(140 * ss))
    c = (c[0] + int(140 * ss), c[1] + int(140 * ss))
    OPTIONS[corp][key]["overlay"](im, c[0], c[1], ss, CORP_ACC[corp]["a"])
    return im, c


# ================================================================== boards
def emblem_sticker(corp, fn, px=180, seed=3):
    pc = K.col(corp, "primary")
    return K.icon_sticker(fn, (250, 248, 242), K.col(corp, "dark"), px=px, seed=seed, ring_col=pc, gloss_k=0.3)


def options_board(corp):
    C = K.CORPS[corp]
    img = K.board(2560, 1440, top=tuple(int(v * 0.35) + 6 for v in K.col(corp, "dark")), bot=(4, 4, 8), seed=21)
    tt = K.word_sticker(["BOSS WHEEL OPTIONS"], 58, U.FILL_YELLOW, seed=12)
    img = SL.place(img, tt, 300, 70, angle=-2)
    U.text(img, (560, 70), "%s  //  %s  //  locked D4 'lens & rail' kit (round 41), three motifs, one pick" % (C["name"], C["server"]),
           U.F(U.MONO, 21), (210, 214, 226), "lm", 1)
    pick = PICK[corp]
    for i, key in enumerate("ABC"):
        im, c = render_option(corp, key, ss=1)
        im = im.crop(im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox())
        k = min(820 / im.width, 960 / im.height)
        im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
        x0 = 20 + i * 846
        img.alpha_composite(im, (x0 + (820 - im.width) // 2, 120))
        o = OPTIONS[corp][key]
        y = 120 + im.height + 10
        U.text(img, (x0 + 30, min(y, 1190)), o["title"] + ("   << PICK" if key == pick else ""), U.F(U.ANTON, 44),
               K.col(corp, "primary") if key == pick else (230, 230, 236), "la", 1)
        for j, ln in enumerate(K.wrap(o["note"], 62)):
            U.text(img, (x0 + 30, min(y, 1190) + 62 + j * 26), ln, U.F(U.PLEX, 20), (200, 208, 222), "la", 0)
        st = emblem_sticker(corp, o["emblem"], px=120, seed=40 + i)
        img = SL.place(img, st, x0 + 740, min(y, 1190) + 60, angle=4)
    U.text(img, (40, 1410), "Slices, telemetry, blade, banner, threat ring and HP arc are the unchanged round 41 renderer; the new corp adds bezel material, rim language, lugs, hub, slice skin + scenes.",
           U.F(U.MONO, 16), (150, 160, 178), "la", 0.3)
    return img


PICK = {"aurelian": "A", "tethys": "B"}
WHY = {"aurelian": ["WHY A: the rim IS the Circus Aurelius (its HQ), so map,",
                    "HQ and boss read as one place; the thumb turned down in the",
                    "hub carries VERDICT (the house rule) into",
                    "the hub. B's sand hub fights the slice screens; C's",
                    "bust is strong but says 'museum', not 'corporation'."],
       "tethys": ["WHY B: the octopus's ink IS the black smoke, so the",
                  "boss name, the vent and the emblem tell one story; the",
                  "arms are the only option that breaks the circle and",
                  "reads at r = 60. A's helmet is a person, not a corp;",
                  "C's bell is lovely but competes with the slice glass."]}


def final_board(corp, backdrop=None):
    C = K.CORPS[corp]
    pc = K.col(corp, "primary")
    img = K.board(2560, 1440, top=tuple(int(v * 0.4) + 6 for v in K.col(corp, "dark")), bot=(4, 4, 8), seed=17)
    if backdrop and os.path.exists(backdrop):
        bg = U.fit_cover(Image.open(backdrop).convert("RGBA"), 2560, 1440)
        img = U.grade(bg, dim=0.5, blur=2.5, sat=0.9)
        img = U.vignette(img, 0.5)
    key = PICK[corp]
    im, c = render_option(corp, key, ss=2)
    im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    c = (c[0] // 2, c[1] // 2)
    k = 1300 / im.height
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    cx = 1180
    img.alpha_composite(im, (int(cx - c[0] * k), 70))
    tt = K.word_sticker(["BOSS WHEEL"], 58, U.FILL_YELLOW, seed=12)
    img = SL.place(img, tt, 210, 70, angle=-2)
    U.text(img, (60, 140), "%s  //  pick %s" % (C["name"], OPTIONS[corp][key]["title"]), U.F(U.MONO, 20), (210, 214, 226), "la", 1)
    st = emblem_sticker(corp, OPTIONS[corp][key]["emblem"], px=220, seed=9)
    img = SL.place(img, st, 2260, 250, angle=5)
    U.text(img, (2260, 410), "BOSS EMBLEM (same motif)", U.F(U.MONO, 17), pc, "mm", 1)
    for j, px in enumerate((64, 32, 16)):
        g = K.mask(OPTIONS[corp][key]["emblem"], px)
        img.alpha_composite(K.tint(g, pc), (2160 + j * 80, 450))
    notes = {
        "aurelian": ["RIM: two tiers of arcade arches, travertine with", "verdigris light in the openings (the Circus Aurelius)",
                     "LUGS: the laurel-arch crest on porphyry", "HUB: the thumb turned down (the emperor),",
                     "carved travertine (VERDICT) + THE GRAND STAND",
                     "SPECIAL SLICE: VERDICT, the crowd's thumbs", "SCREENS: porphyry, a verdigris meander, arcades",
                     "SCENES: gladius, trident, testudo, sand + parma", "P2 idea: the arcades light gold, the crowd roars"],
        "tethys": ["RIM: a ring of suckers on wet hull, abyss seam", "ARMS: four tentacles curl round the threat ring,",
                   "clear of the blade and the readout rail", "LUGS: the wave crest on trench blue",
                   "HUB: the octopus, wet relief + THE VENT CAP",
                   "SPECIAL SLICE: TIDE, the water rises in the screen", "SCREENS: deep gradient, caustic net, bubbles",
                   "SCENES: harpoon, torpedo, bulkhead, air pocket", "P2 idea: the hub inks: LOCKDOWN water turns black"],
    }[corp]
    img = U.term_panel(img, (1900, 520, 2520, 940), title="WHAT IS CORP-SPECIFIC", accent=pc, seed=8)
    for i, ln in enumerate(notes):
        U.text(img, (1922, 572 + i * 38), ln, U.F(U.PLEX, 20), (214, 224, 236), "la", 0)
    img = U.term_panel(img, (1900, 970, 2520, 1210), title="WHY THIS ONE", accent=pc, seed=9)
    for i, ln in enumerate(WHY[corp]):
        U.text(img, (1922, 1022 + i * 34), ln, U.F(U.PLEX, 19), (214, 224, 236), "la", 0)
    U.text(img, (60, 1410), "Locked D4 kit (round 41 d4corp, unchanged) + the new theme rows. Slice colours stay slice-type colours (bible 2.3).",
           U.F(U.MONO, 16), (150, 160, 178), "la", 0.4)
    return img


def main():
    corp = sys.argv[1]
    what = sys.argv[2] if len(sys.argv) > 2 else "all"
    kw = dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a)
    if "pick" in kw:
        PICK[corp] = kw["pick"]
    out = os.path.join(K.NC, K.CORPS[corp]["folder"])
    if what in ("options", "all"):
        K.save(options_board(corp), os.path.join(out, "boss_wheel_options.png"))
    if what in ("final", "all"):
        K.save(final_board(corp, kw.get("backdrop")), os.path.join(out, "boss_wheel.png"))


if __name__ == "__main__":
    main()
