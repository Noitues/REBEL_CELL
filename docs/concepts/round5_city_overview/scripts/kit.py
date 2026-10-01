"""S1 toolkit: Cv2 triangle facets + E cel shading (3 hard bands, wobbly ink, painted grime), 2D.

Everything is drawn on a 2x canvas (lowpoly.SS) and downsampled once. Shapes are filled by a
triangle fan (poly_fpos) whose triangles each pick one of 3 toon bands from a pseudo-normal
(centroid offset from the shape centre against an upper-left light), keep a small tone jitter
inside the band, then get a wobbly ink outline. Shadows go cool, lit faces warm (toon.tint).
"""
import math
import os
import random
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageChops, ImageFont
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, facet, bil, polar, tri, line2, poly_fpos, text, text_w,
                     font, finalize, NEON, HAND)
from toon import ink_line, ink_poly, hull, tint, BANDS, INK, BEVEL, paint_texture
import city

BG = hexc('#2A2A2E')
LABEL = hexc('#cfcac0')
OUT = os.path.dirname(HERE)

# corporation / material ramps (deep -> pale)
MER = R('#1a0a02', '#4a1c04', '#8a3a08', '#c8600e', '#f08a24', '#f8b45a', '#fcdca0')
SOL = R('#03140f', '#0a3326', '#14604a', '#2a9a78', '#5cc8a4', '#9ae4c8', '#d8f8ea')
HAL = R('#050c1c', '#0c2246', '#1a4080', '#2c66b4', '#5a92d8', '#9cc0ec', '#dcecfc')
ORB = R('#0e061e', '#26104a', '#44207e', '#6a38b0', '#9a68d8', '#c4a4ec', '#ece0fc')
CELL = R('#04161c', '#0a3a48', '#10708a', '#20a8c4', '#5cd8ec', '#a8f0fa', '#e8fcff')
SKIN = R('#1e0e08', '#4a2414', '#7a4026', '#a86440', '#c88a62', '#e0b08a', '#f4d8bc')
METAL = R('#0c0c0e', '#1c1c20', '#302f32', '#4a4846', '#68655e', '#8e897e', '#bab2a2')
RUSTR = R('#140806', '#2e120a', '#4e2010', '#6e3418', '#8e4e28', '#a86c44', '#c89068')
PAPER = R('#2a2620', '#4a443a', '#6e6656', '#948a74', '#b8ac90', '#d4c8aa', '#ece2c8')
RED = R('#1e0406', '#4a0a10', '#8a1418', '#c4242a', '#e8503e', '#f88a6a', '#fcc8b0')
GOLD = R('#1e1404', '#4a3208', '#8a5c10', '#c48a1a', '#e8b438', '#f4d474', '#fcf0c0')
LIME = R('#0c1a04', '#22400a', '#3e7410', '#62a81c', '#8ed03a', '#c0ec7c', '#ecfcd0')
PURP = R('#120418', '#2e0a3a', '#561868', '#82289a', '#ac50c0', '#d08ce0', '#f0d4f8')
STEEL = R('#06080c', '#121822', '#1e2a3a', '#2e425a', '#4a6480', '#7c94ac', '#bccad8')
DARK = R('#060608', '#0e0e12', '#18181e', '#24242c', '#32323c', '#44444e', '#5a5a64')
for k, v in (('mer', MER), ('sol', SOL), ('hal', HAL), ('orb', ORB), ('metal', METAL)):
    city.FAM[k] = v

L2 = (-0.6, -0.8)   # screen-space light direction (toward the light: upper-left)


def band_from(lam):
    return 2 if lam > 0.58 else (1 if lam > 0.26 else 0)


def bcol(stops, band, j=0.0):
    import toon as _T
    return _T.tint(ramp(stops, _T.BANDS[band] + j), band)


# ------------------------------------------------------------------ fills
def cel_fill(d, pts, stops, seed, nu=None, nv=2, c=None, form=1.0, bias=0.0, var=0.035, flat=None, jit=0.28,
             light=L2):
    """Fill a star-shaped polygon with toon-banded triangles."""
    n = len(pts)
    if c is None:
        c = (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
    rx = max(abs(p[0] - c[0]) for p in pts) or 1.0
    ry = max(abs(p[1] - c[1]) for p in pts) or 1.0
    fpos = poly_fpos(pts, c)

    def colfn(u, v, i, j, k, rc):
        if flat is not None:
            b = flat
        else:
            x, y = fpos(u, v)
            ox, oy = (x - c[0]) / rx, (y - c[1]) / ry
            lam = 0.42 + bias + form * 0.6 * (ox * light[0] + oy * light[1])
            b = band_from(lam)
        return bcol(stops, b, rc.uniform(-var, var))
    facet(d, fpos, nu or max(6, n * 2), nv, colfn, seed, jit, wrap_u=True)


def quad_fill(d, q, stops, band, seed, nu=2, nv=2, var=0.035):
    facet(d, bil(q), nu, nv, lambda u, v, i, j, k, rc: bcol(stops, band, rc.uniform(-var, var)), seed, 0.3)


def shape(d, pts, stops, seed, ink=3.4, **kw):
    cel_fill(d, pts, stops, seed, **kw)
    if ink:
        ink_poly(d, pts, ink, (seed, 'ink'))


def circle_pts(cx, cy, rx, ry=None, n=16, a0=0.0):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(a0 + 2 * math.pi * k / n), cy + ry * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def extrude(d, pts, off, stops, seed, ink=3.4, front_kw=None, side_band=0):
    """A flat shape with depth: shadow-band sides toward `off`, banded front, ink on the silhouette."""
    ox, oy = off
    n = len(pts)
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        q = [a, b, (b[0] + ox, b[1] + oy), (a[0] + ox, a[1] + oy)]
        quad_fill(d, q, stops, side_band, (seed, 'side', k), 1, 1)
    cel_fill(d, pts, stops, (seed, 'front'), **(front_kw or {}))
    if ink:
        ink_poly(d, hull(list(pts) + [(p[0] + ox, p[1] + oy) for p in pts]), ink, (seed, 'sil'))
        ink_poly(d, pts, ink * 0.55, (seed, 'fr'))


def bevel(d, a, b, off=2.4, w=1.6, col=BEVEL):
    line2(d, (a[0], a[1] + off), (b[0], b[1] + off), w, col)


def rust_streaks(d, pts, seed, n=4, length=(10, 30), base=None):
    """Painted rust drips running down from the top edge of a shape."""
    rng = random.Random(str(('rust', seed)))
    ys = sorted(p[1] for p in pts)
    top = ys[0]
    xs = [p[0] for p in pts]
    x0, x1 = min(xs), max(xs)
    for _ in range(n):
        x = rng.uniform(x0 + (x1 - x0) * 0.12, x1 - (x1 - x0) * 0.12)
        y = top + rng.uniform(4, 10) + (ys[-1] - top) * rng.uniform(0.0, 0.25)
        L = rng.uniform(*length)
        w = rng.uniform(2, 4.5)
        c = ramp(RUSTR, rng.uniform(0.45, 0.65))
        tri(d, [(x - w, y), (x + w, y), (x + rng.uniform(-1.5, 1.5), y + L)], c)
        tri(d, [(x - w * 0.4, y), (x + w * 0.5, y), (x, y + L * 0.5)], ramp(RUSTR, 0.75))


def chips(d, pts, seed, n=5, col=None):
    """Chipped paint flecks near the edges of a shape."""
    rng = random.Random(str(('chip', seed)))
    col = col or ramp(PAPER, 0.7)
    m = len(pts)
    for _ in range(n):
        k = rng.randrange(m)
        a, b = pts[k], pts[(k + 1) % m]
        t = rng.uniform(0.1, 0.9)
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        cx = sum(p[0] for p in pts) / m
        cy = sum(p[1] for p in pts) / m
        dx, dy = cx - x, cy - y
        L = math.hypot(dx, dy) or 1
        dx, dy = dx / L, dy / L
        s = rng.uniform(2.5, 6)
        tri(d, [(x + dx * 1.5, y + dy * 1.5), (x + dx * s + dy * s * 0.8, y + dy * s - dx * s * 0.8),
                (x + dx * s * 1.3, y + dy * s * 1.3)], col)


def glow_lines(d, a, b, col, w=3):
    line2(d, a, b, w + 3, mix(col, BG, 0.6))
    line2(d, a, b, w, col)


# ------------------------------------------------------------------ text helpers
def ftxt(size, path='C:/Windows/Fonts/bahnschrift.ttf', style='Bold'):
    f = ImageFont.truetype(path, int(size * SS))
    if path.endswith('bahnschrift.ttf') and style:
        try:
            f.set_variation_by_name(style)
        except Exception:
            pass
    return f


def ink_text(d, x, y, s, size, fill, anchor='mm', path='C:/Windows/Fonts/bahnschrift.ttf', style='Bold',
             stroke=None, shadow=(2.5, 3.0)):
    """Lettering with an ink stroke and an offset ink shadow (cel look)."""
    f = ftxt(size, path, style)
    sw = int((stroke if stroke is not None else max(2, size * 0.09)) * SS)
    if shadow:
        d.text(((x + shadow[0]) * SS, (y + shadow[1]) * SS), s, font=f, fill=INK, anchor=anchor, stroke_width=sw,
               stroke_fill=INK)
    d.text((x * SS, y * SS), s, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=INK)


# ------------------------------------------------------------------ sheets
def sheet():
    return Image.new('RGBA', (W * SS, H * SS), BG + (255,))


def header(d, num, title):
    text(d, 40, 36, f'S1  CV2 + CEL', 18, hexc('#8a857a'), anchor='lm')
    text(d, 40, 62, f'{num}  {title}', 26, LABEL, anchor='lm')


def finish(img, name, labels, num, title):
    """Painterly texture on the drawn items only, then crisp labels, then save at 1920x1080."""
    rgb = img.convert('RGB')
    bg = Image.new('RGB', rgb.size, BG)
    mask = ImageChops.difference(rgb, bg).convert('L').point(lambda v: 255 if v > 5 else 0)
    tex = paint_texture(rgb)
    rgb = Image.composite(tex, rgb, mask)
    d = ImageDraw.Draw(rgb)
    header(d, num, title)
    for (x, y, s) in labels:
        text(d, x, y, s, 20, LABEL, anchor='mm', style='SemiBold')
    out = os.path.join(OUT, name)
    finalize(rgb).save(out, optimize=True)
    print('wrote', name)
    return out


def paste_rot(base, im, cx, cy, ang):
    r = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(r, (int(cx * SS - r.width / 2), int(cy * SS - r.height / 2)))


def layer_img(w, h):
    im = Image.new('RGBA', (int(w * SS), int(h * SS)), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)
