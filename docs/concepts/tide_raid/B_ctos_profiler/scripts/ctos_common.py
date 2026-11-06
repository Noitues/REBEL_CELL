"""Shared helpers for direction B "ctOS Profiler": camera, geometry, layers, glyphs, grade.
Plates live in D:/rc_scratch/tide_concepts/plates; output is written next to this scripts/ folder."""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

PLATES = 'D:/rc_scratch/tide_concepts/plates'
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FONTS = 'D:/rc_art/art-pass/assets/fonts'
W, H = 1920, 1080
SS = 2                      # supersample for vector overlays
ZOOM, CEN, ORG = 1.7, (700.0, 500.0), (930.0, 560.0)   # plate crop-zoom onto the Solace territory
ISO = 0.643                 # sin(40 deg): ground circle -> ellipse ratio at the raid camera


def hx(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


# ---- palette (hex) ----
GRID = hx('#7FD8E8')        # the Grid itself: cool teal-white, thin
CYAN = hx('#5CE1FF')        # CRT chrome / ctOS brackets (NET_CYAN)
NAVY = hx('#06122B')
BEAM = {'D': hx('#3DB4FF'), 'N': hx('#FF40D6'), 'E': hx('#B58CFF')}
TIER = {'UNTOUCHED': hx('#BFFFEF'), 'HOLDS': hx('#19D3C5'), 'LOST': hx('#FFB000'),
        'DAMAGED': hx('#FF7A1A'), 'BREACHED': hx('#FF4433')}
PENCIL_RED = hx('#FF1C2C')
PENCIL_YEL = hx('#FFE200')
LIME = hx('#D4FF00')
PLUM = hx('#1A0A1E')
VEIN = hx('#E8458F')
HOT = hx('#FF9AD2')
WHITE = (255, 255, 255)
SOLACE = hx('#3DFF8B')

_f = {}


def font(name, size):
    k = (name, size)
    if k not in _f:
        p = {'anton': 'Anton-Regular.ttf', 'mono': 'ShareTechMono-Regular.ttf', 'plex': 'IBMPlexSansCondensed-Medium.ttf'}[name]
        _f[k] = ImageFont.truetype(os.path.join(FONTS, p), int(size * SS))
    return _f[k]


# ---- camera ----
def T(p):
    return ((p[0] - CEN[0]) * ZOOM + ORG[0], (p[1] - CEN[1]) * ZOOM + ORG[1])


def TP(poly):
    return [T(p) for p in poly]


def load_coords(scn, beat):
    return json.load(open(f'{PLATES}/coords/{scn}_{beat}.json'))


# ---- geometry ----
def clean_path(poly):
    p = [tuple(q) for q in poly]
    ch = True
    while ch:
        ch = False
        for i in range(1, len(p) - 1):
            if math.dist(p[i - 1], p[i + 1]) < 1.5:
                del p[i:i + 2]
                ch = True
                break
    out = [p[0]]
    for q in p[1:]:
        if math.dist(q, out[-1]) > 0.5:
            out.append(q)
    return out


def offset_path(p, d):
    if abs(d) < 1e-6 or len(p) < 2:
        return list(p)
    out = []
    for i, q in enumerate(p):
        ns = []
        if i > 0:
            a = p[i - 1]
            dx, dy = q[0] - a[0], q[1] - a[1]
            L = math.hypot(dx, dy) or 1
            ns.append((-dy / L, dx / L))
        if i < len(p) - 1:
            b = p[i + 1]
            dx, dy = b[0] - q[0], b[1] - q[1]
            L = math.hypot(dx, dy) or 1
            ns.append((-dy / L, dx / L))
        nx = sum(n[0] for n in ns) / len(ns)
        ny = sum(n[1] for n in ns) / len(ns)
        L = math.hypot(nx, ny) or 1
        nx /= L
        ny /= L
        k = 1.0
        if len(ns) == 2:
            c = ns[0][0] * ns[1][0] + ns[0][1] * ns[1][1]
            k = min(1.6, 1 / max(0.62, math.sqrt((1 + c) / 2)))
        out.append((q[0] + nx * d * k, q[1] + ny * d * k))
    return out


def seg_lengths(p):
    return [math.dist(a, b) for a, b in zip(p, p[1:])]


def plen(p):
    return sum(seg_lengths(p))


def sample(p, s):
    """point + tangent angle at arc length s."""
    L = seg_lengths(p)
    s = max(0, min(sum(L), s))
    acc = 0
    for i, l in enumerate(L):
        if acc + l >= s or i == len(L) - 1:
            a, b = p[i], p[i + 1]
            t = 0 if l == 0 else (s - acc) / l
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), math.atan2(b[1] - a[1], b[0] - a[0])
        acc += l
    return p[-1], 0


def sub_path(p, s0, s1, step=6):
    pts = []
    s = s0
    while s < s1:
        pts.append(sample(p, s)[0])
        s += step
    pts.append(sample(p, s1)[0])
    return pts


def nearest_on(polys, q):
    best = (1e9, None)
    for poly in polys:
        for a, b in zip(poly, poly[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = dx * dx + dy * dy
            t = 0 if L == 0 else max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L))
            pt = (a[0] + t * dx, a[1] + t * dy)
            d = math.dist(q, pt)
            if d < best[0]:
                best = (d, pt)
    return best[1]


def site_anchors(j):
    """street anchor (plate px) of every raid site = the pole-base 'tip' where its link polyline ends
    (link a->b: polyline[0] is a's tip, polyline[-1] is b's tip). Falls back to the nearest street point."""
    tips = {}
    for l in j['links']:
        pl = l['polyline']
        if len(pl) > 1:
            tips.setdefault(l['b'], tuple(pl[-1]))
            tips.setdefault(l['a'], tuple(pl[0]))
    polys = [clean_path(l['polyline']) for l in j['links'] if len(l['polyline']) > 1]
    out = {}
    for s in j['sites']:
        out[s['id']] = tips.get(s['id']) or nearest_on(polys, (s['xy'][0], s['xy'][1] + 30))
    out['home'] = tips.get('home') or (318.1, j['home']['xy'][1] + 57.5)
    out['hq'] = tips.get('the_genome_core') or (1088.8, j['solace_hq']['xy'][1] + 54.2)
    return out


# ---- layers ----
class Layer:
    def __init__(s):
        s.solid = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
        s.glow = Image.new('RGB', (W * SS, H * SS), (0, 0, 0))
        s.d = ImageDraw.Draw(s.solid)
        s.g = ImageDraw.Draw(s.glow)

    def _p(s, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def _blit(s, P, fn, a):
        xs = [p[0] for p in P]
        ys = [p[1] for p in P]
        x0, y0, x1, y1 = int(min(xs)) - 2, int(min(ys)) - 2, int(max(xs)) + 3, int(max(ys)) + 3
        cx0, cy0 = max(0, x0), max(0, y0)
        cx1, cy1 = min(W * SS, x1), min(H * SS, y1)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        t = Image.new('RGBA', (cx1 - cx0, cy1 - cy0), (0, 0, 0, 0))
        fn(ImageDraw.Draw(t), cx0, cy0)
        s.solid.alpha_composite(t, (cx0, cy0))

    def line(s, pts, col, w=2, a=255, glow=0.0, gw=None, joint='curve'):
        if len(pts) < 2:
            return
        P = s._p(pts)
        if a > 0:
            if a >= 255:
                s.d.line(P, fill=col + (255,), width=max(1, int(w * SS)), joint=joint)
            else:
                s._blit(P, lambda d, ox, oy: d.line([(x - ox, y - oy) for x, y in P], fill=col + (int(a),), width=max(1, int(w * SS)), joint=joint), a)
        if glow > 0:
            s.g.line(P, fill=tuple(int(c * glow) for c in col), width=max(1, int((gw or w) * SS)), joint=joint)

    def poly(s, pts, fill=None, outline=None, w=1.5, a=255, glow=0.0, ow=None):
        P = s._p(pts)
        if fill is not None:
            if a >= 255:
                s.d.polygon(P, fill=fill + (255,))
            else:
                s._blit(P, lambda d, ox, oy: d.polygon([(x - ox, y - oy) for x, y in P], fill=fill + (int(a),)), a)
        if outline is not None:
            s.d.line(P + [P[0]], fill=outline + (255,), width=max(1, int(w * SS)), joint='curve')
        if glow > 0:
            col = outline or fill
            s.g.line(P + [P[0]], fill=tuple(int(c * glow) for c in col), width=max(1, int((ow or w * 2) * SS)), joint='curve')

    def ellipse(s, cx, cy, rx, ry, fill=None, outline=None, w=1.5, a=255, glow=0.0, gw=None):
        box = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        if fill is not None:
            if a >= 255:
                s.d.ellipse(box, fill=fill + (255,))
            else:
                P = [(box[0], box[1]), (box[2], box[3])]
                s._blit(P, lambda d, ox, oy: d.ellipse([box[0] - ox, box[1] - oy, box[2] - ox, box[3] - oy], fill=fill + (int(a),)), a)
        if outline is not None:
            s.d.ellipse(box, outline=outline + (255,), width=max(1, int(w * SS)))
        if glow > 0:
            col = outline or fill
            s.g.ellipse(box, outline=tuple(int(c * glow) for c in col), width=max(1, int((gw or w * 2) * SS)))

    def arc(s, cx, cy, rx, ry, a0, a1, col, w=2, a=255, glow=0.0, gw=None, step=4):
        pts = [(cx + rx * math.cos(math.radians(t)), cy + ry * math.sin(math.radians(t))) for t in np.arange(a0, a1 + 0.01, step)]
        s.line(pts, col, w, a, glow, gw)

    def text(s, xy, txt, fnt, col, anchor='mm', a=255, glow=0.0, stroke=0, stroke_col=(0, 0, 0)):
        x, y = xy[0] * SS, xy[1] * SS
        s.d.text((x, y), txt, font=fnt, fill=col + (int(a),), anchor=anchor, stroke_width=int(stroke * SS), stroke_fill=stroke_col + (255,))
        if glow > 0:
            s.g.text((x, y), txt, font=fnt, fill=tuple(int(c * glow) for c in col), anchor=anchor)


def blend_layer(img, L, glow_gain=1.0, radii=(2.5, 9, 26), wts=(0.55, 0.5, 0.45)):
    """img float32 HxWx3 0..1. Adds blurred glow, then alpha-composites the solid layer."""
    g = L.glow.resize((W, H), Image.LANCZOS)
    gn = np.asarray(g, dtype=np.float32) / 255.0
    acc = gn * 0.5
    for r, wt in zip(radii, wts):
        acc += np.asarray(g.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0 * wt * 2.2
    img = 1 - (1 - np.clip(img, 0, 1)) * (1 - np.clip(acc * glow_gain, 0, 1))
    s = L.solid.resize((W, H), Image.LANCZOS)
    sa = np.asarray(s, dtype=np.float32) / 255.0
    a = sa[..., 3:4]
    return img * (1 - a) + sa[..., :3] * a


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


# ---- glyph shapes ----
def ngon(cx, cy, r, n, rot=0):
    return [(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def hexg(cx, cy, r, rot=0):
    return ngon(cx, cy, r, 6, rot)


def tri(cx, cy, r, ang=0):
    """arrow-wedge pointing along ang."""
    return [(cx + r * math.cos(ang), cy + r * math.sin(ang)),
            (cx + r * 0.8 * math.cos(ang + 2.5), cy + r * 0.8 * math.sin(ang + 2.5)),
            (cx + r * 0.25 * math.cos(ang + math.pi), cy + r * 0.25 * math.sin(ang + math.pi)),
            (cx + r * 0.8 * math.cos(ang - 2.5), cy + r * 0.8 * math.sin(ang - 2.5))]


def rot_sq(cx, cy, r, ang=0):
    return ngon(cx, cy, r * 1.25, 4, ang + math.pi / 4)


def chamfer(x, y, w, h, c):
    return [(x + c, y), (x + w, y), (x + w, y + h - c), (x + w - c, y + h), (x, y + h), (x, y + c)]


def shield_pts(cx, cy, r):
    return [(cx - r, cy - r * 0.8), (cx + r, cy - r * 0.8), (cx + r, cy + r * 0.1), (cx, cy + r), (cx - r, cy + r * 0.1)]


def star_pts(cx, cy, r, n=5):
    return [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + math.pi * i / n),
             cy + (r if i % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + math.pi * i / n)) for i in range(2 * n)]


def type_glyph(L, t, x, y, r, col=None, fill=True, ang=0.0, glow=0.9, a=255):
    """Beam-type head. D = drone orb with rotor ticks, N = packet square, E = wedge arrow. Shapes differ as well as hue."""
    col = col or BEAM[t]
    dark = tuple(int(c * 0.28) for c in col)
    w = max(1.6, r * 0.28)
    if t == 'D':
        L.ellipse(x, y, r, r, fill=dark if fill else None, outline=col, w=w, glow=glow)
        for k in range(4):
            q = ang + k * math.pi / 2 + math.pi / 4
            L.line([(x + math.cos(q) * r * 0.95, y + math.sin(q) * r * 0.95), (x + math.cos(q) * r * 1.55, y + math.sin(q) * r * 1.55)], col, w, glow=glow)
        L.ellipse(x, y, r * 0.32, r * 0.32, fill=WHITE)
    elif t == 'N':
        L.poly(rot_sq(x, y, r * 0.95, 0), fill=dark if fill else None, outline=col, w=w, glow=glow, ow=r * .8)
        L.poly(rot_sq(x, y, r * 0.38, 0), fill=WHITE)
    else:
        L.poly(tri(x, y, r * 1.35, ang), fill=dark if fill else None, outline=col, w=w, glow=glow, ow=r * .8)
        L.poly(tri(x, y, r * 0.5, ang), fill=WHITE)


def site_glyph(L, x, y, r, col, exploit=False, fill=None, w=1.8, glow=0.6):
    L.poly(hexg(x, y, r, math.pi / 6), fill=fill, outline=col, w=w, glow=glow)
    if exploit:
        L.poly(star_pts(x, y, r * 0.6), fill=col)
    else:
        L.poly(hexg(x, y, r * 0.38, math.pi / 6), fill=col)


def skull(L, x, y, r, col=WHITE, eye=(10, 6, 16)):
    L.ellipse(x, y - r * .1, r, r * .95, fill=col)
    L.poly([(x - r * .55, y + r * .5), (x + r * .55, y + r * .5), (x + r * .45, y + r * 1.15), (x - r * .45, y + r * 1.15)], fill=col)
    for dx in (-.42, .42):
        L.ellipse(x + dx * r, y - r * .05, r * .26, r * .3, fill=eye)
    L.poly([(x, y + r * .22), (x - r * .1, y + r * .45), (x + r * .1, y + r * .45)], fill=eye)
    for dx in (-.2, 0, .2):
        L.line([(x + dx * r, y + r * .72), (x + dx * r, y + r * 1.1)], eye, max(1, r * .1))


def house(L, x, y, r, col):
    L.poly([(x - r, y), (x, y - r * .95), (x + r, y), (x + r * .72, y), (x + r * .72, y + r * .85), (x - r * .72, y + r * .85), (x - r * .72, y)], fill=col)
    L.poly([(x - r * .2, y + r * .85), (x - r * .2, y + r * .3), (x + r * .2, y + r * .3), (x + r * .2, y + r * .85)], fill=(20, 14, 0))


def flame(L, x, y, r, col):
    L.poly([(x, y - r * 1.2), (x + r * .55, y - r * .3), (x + r * .8, y + r * .2), (x + r * .45, y + r * .95), (x - r * .45, y + r * .95), (x - r * .8, y + r * .2), (x - r * .5, y - r * .3), (x - r * .12, y - r * .5)], fill=col)


def grease(L, pts, col, w=5, seed=1, a=245):
    """D28 grease pencil: rough wax stroke, dark under-shadow, dropouts, sheen line."""
    rnd = random.Random(seed)

    def jit(pp, amp):
        return [(x + rnd.uniform(-amp, amp), y + rnd.uniform(-amp, amp)) for x, y in pp]
    L.line([(x + 1.5, y + 2) for x, y in pts], (6, 4, 12), w + 3, 170)
    for k in range(3):
        L.line(jit(pts, w * .18), col, w * (1.0 - k * .22), a)
    L.line(jit(pts, w * .3), tuple(min(255, int(c * 1.25 + 40)) for c in col), max(1, w * .22), 150)
    for _ in range(int(plen(pts) / 14)):
        p, _a = sample(pts, rnd.uniform(0, plen(pts)))
        L.ellipse(p[0] + rnd.uniform(-w * .3, w * .3), p[1] + rnd.uniform(-w * .3, w * .3), w * .12, w * .12, fill=(24, 10, 24), a=130)


def iso_ring(L, cx, cy, rx, col, w=2, a=255, glow=0.7, dash=None):
    ry = rx * ISO
    if not dash:
        L.ellipse(cx, cy, rx, ry, outline=col, w=w, glow=glow)
    else:
        n = int(360 / dash[0])
        for k in range(n):
            if k % 2 == 0:
                L.arc(cx, cy, rx, ry, k * dash[0] + dash[1], (k + 1) * dash[0] + dash[1], col, w, a, glow, step=3)


def iso_hex(L, cx, cy, r, col, w=2, glow=0.7, fill=None, fa=90):
    pts = [(cx + r * math.cos(math.pi / 6 + k * math.pi / 3), cy + r * ISO * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
    L.poly(pts, fill=fill, outline=col, w=w, glow=glow, a=fa)
    return pts


def bracket_box(L, x, y, w, h, col, c=7, th=2, a=255, glow=0.6):
    for sx, sy, ox, oy in ((1, 1, x, y), (-1, 1, x + w, y), (1, -1, x, y + h), (-1, -1, x + w, y + h)):
        L.line([(ox + sx * c, oy), (ox, oy), (ox, oy + sy * c)], col, th, a, glow)


# ---- grading ----
def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def load_city(dy=0):
    """plate city, zoomed; dy = vertical plate offset for scenarios whose camera is shifted (decay: +22)."""
    im = Image.open(f'{PLATES}/city_noraid_nonet.png').convert('RGB')
    big = im.resize((int(im.width * ZOOM), int(im.height * ZOOM)), Image.LANCZOS)
    ox, oy = int(CEN[0] * ZOOM - ORG[0]), int(CEN[1] * ZOOM - ORG[1] + dy * ZOOM)
    big = big.crop((ox, oy, ox + W, oy + H)).filter(ImageFilter.UnsharpMask(1.6, 90, 2))
    return np.asarray(big, dtype=np.float32) / 255.0


def lum(a):
    return a[..., 0] * .2126 + a[..., 1] * .7152 + a[..., 2] * .0722


def territory_mask(j):
    """soft mask of the profiled Solace territory (network hull + HQ), in screen space."""
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    for l in j['links']:
        for p in l['polyline']:
            x, y = T(p)
            d.ellipse([x - 150, y - 100, x + 150, y + 100], fill=255)
    for k in ('solace_hq', 'home'):
        x, y = T(j[k]['xy'])
        d.ellipse([x - 160, y - 110, x + 160, y + 110], fill=255)
    hx_, hy_ = T((1190, 410))
    d.ellipse([hx_ - 230, hy_ - 230, hx_ + 230, hy_ + 200], fill=255)
    return np.asarray(im.filter(ImageFilter.GaussianBlur(70)), dtype=np.float32) / 255.0


def grade(city, mask, sweep=None, wire=0.55):
    """night-noir, rich and lit: dim outside the profiled territory, lifted and cooled inside, cyan wire edges on buildings."""
    a = city.copy()
    L = lum(a)[..., None]
    a = L + (a - L) * 0.82
    a = np.clip(a * np.array([0.86, 0.92, 1.02]), 0, 1)
    a = a ** 1.05 * 1.28
    m = mask[..., None]
    out = a * (0.40 + 0.90 * m)
    lit = smoothstep(0.42, 0.8, lum(a))[..., None]
    out = out + a * lit * m * 0.55
    g = ndi.gaussian_filter(lum(a), 1.1)
    gx, gy = ndi.sobel(g, 1), ndi.sobel(g, 0)
    e = np.hypot(gx, gy)
    e = np.clip((e - 0.10) / 0.55, 0, 1) ** 0.8
    wm = mask ** 1.2
    if sweep is not None:
        wm = np.clip(wm * (0.35 + 1.6 * sweep), 0, 1.6)
    out = out + e[..., None] * np.array(GRID, np.float32) / 255.0 * wire * wm[..., None]
    return np.clip(out, 0, 1.2)


def finish(img, seed=3, vignette=0.38, scan=0.035, ca=1.5):
    """vignette, faint scanlines, RGB split at the frame edge, grain."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    img = img * (1 - vignette * np.clip(r - 0.55, 0, 1)[..., None] ** 1.6)
    img = img * (1 - scan * (0.5 + 0.5 * np.sin(yy * math.pi * 2 / 3))[..., None])
    sh = int(round(ca))
    edge = np.clip(r - 0.92, 0, 1) * 5
    sr = np.roll(img[..., 0], sh, 1)
    sb = np.roll(img[..., 2], -sh, 1)
    img[..., 0] = img[..., 0] * (1 - edge) + sr * edge
    img[..., 2] = img[..., 2] * (1 - edge) + sb * edge
    rng = np.random.default_rng(seed)
    img = img + rng.normal(0, 0.012, img.shape[:2])[..., None]
    return np.clip(img, 0, 1)
