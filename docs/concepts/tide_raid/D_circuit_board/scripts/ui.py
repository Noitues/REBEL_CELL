"""Wordless UI kit for the Circuit Board direction: sprites, tier badges, HUD counters, component cards,
CRT chips, corp-paper stamp tags, defense components, beams and sealed/hunter marks."""
import math, random
import numpy as np
from lib import *
from PIL import Image, ImageFilter


class Sprite(Frame):
    """small RGBA canvas using the same primitives (local coords)"""

    def __init__(self, w, h):
        self.sw, self.sh = w, h
        self.kind = 'over'
        self.im = Image.new('RGBA', (int(w * SS), int(h * SS)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.bb = [1e9, 1e9, -1e9, -1e9]
        self.a = None


def paste(f, spr, c, angle=0.0, scale=1.0, shadow=0.55, sh_off=(4, 7)):
    """alpha-paste a sprite into the current 'over' layer of frame f, centred on c"""
    if f.kind != "over":
        f.L("over")
    im = spr.im
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    x = int(c[0] * SS - im.width / 2)
    y = int(c[1] * SS - im.height / 2)
    f._m([(x / SS, y / SS), ((x + im.width) / SS, (y + im.height) / SS)], 12)
    if shadow:
        al = im.getchannel('A').point(lambda v: int(v * shadow))
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        sh.putalpha(al)
        sh = sh.filter(ImageFilter.GaussianBlur(4 * SS))
        f.im.alpha_composite(sh, (max(0, x + sh_off[0] * SS), max(0, y + sh_off[1] * SS)))
    f.im.alpha_composite(im, (x, y)) if x >= 0 and y >= 0 else f.im.paste(im, (x, y), im)


# ---------------------------------------------------------------- tier badges (second channel = silhouette + glyph)
def _ngon(c, r, n, rot=-math.pi / 2):
    return [(c[0] + math.cos(rot + i / n * 2 * math.pi) * r, c[1] + math.sin(rot + i / n * 2 * math.pi) * r) for i in range(n)]


def tier_badge(f, c, tier, r=18, num=None):
    col = TIERC[tier]
    dark = (10, 8, 18)
    sil = {'UNTOUCHED': 'circle', 'HOLDS': 'shield', 'SITES_LOST': 'diamond', 'DAMAGED': 'hex', 'BREACHED': 'spike',
           'CITY_LOST': 'circle'}[tier]
    if sil == 'circle':
        pts = _ngon(c, r, 28)
    elif sil == 'shield':
        pts = [(c[0] - r, c[1] - r * .85), (c[0], c[1] - r * 1.05), (c[0] + r, c[1] - r * .85), (c[0] + r * .95, c[1] + r * .1),
               (c[0], c[1] + r * 1.1), (c[0] - r * .95, c[1] + r * .1)]
    elif sil == 'diamond':
        pts = [(c[0], c[1] - r * 1.15), (c[0] + r * 1.1, c[1]), (c[0], c[1] + r * 1.15), (c[0] - r * 1.1, c[1])]
    elif sil == 'hex':
        pts = _ngon(c, r * 1.08, 6, 0)
    else:
        pts = []
        for i in range(16):
            rr = r * 1.25 if i % 2 == 0 else r * .85
            a = -math.pi / 2 + i / 16 * 2 * math.pi
            pts.append((c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr))
    f.poly(pts, dark, WHITE, max(2.2, r * .13))
    gl = {'UNTOUCHED': 'ring', 'HOLDS': 'shield', 'SITES_LOST': 'broken_link', 'DAMAGED': 'crack_heart',
          'BREACHED': 'crack_heart', 'CITY_LOST': 'skull'}[tier]
    if gl in ('shield', 'crack_heart'):
        glyph(f, gl, (c[0], c[1] + (1 if gl == 'shield' else 0)), r * .6, col, max(1.8, r * .12), col)
    elif gl == 'ring':
        glyph(f, 'ring', c, r * .45, col, max(2.2, r * .16))
    else:
        glyph(f, gl, c, r * .58, col, max(1.8, r * .12), col)
    if num is not None:
        f.txt((c[0], c[1] + r * 1.9), str(num), r * 1.05, col, stroke=2.0)


def wave_chip(f, c, t, r=13, ring=True):
    """a type token: dark disc + the type's waveform in its hue (shape + hue)"""
    col = TYPE_COL[t]
    f.ell(c, r, r, (8, 8, 16, 235), col, 2.4 if ring else 1)
    glyph(f, wave_kind(t), c, r * .62, col, 2.2)


# ---------------------------------------------------------------- HUD (counters only)
def hud(f, home=44, heat=80, healthy=8, infected=0, hot=False, home_flash=0.0, tilt=False):
    f.L('over')
    # HOME tile
    def tile(x, w, accent):
        f.rr((x, 18, x + w, 70), 10, (6, 16, 26, 235), accent, 2.2)
        for i in range(0, 52, 4):
            f.line([(x + 4, 18 + i), (x + w - 4, 18 + i)], 1, (255, 255, 255, 8), cap=False)
    tile(24, 128, (110, 226, 255) if not home_flash else TIERC['DAMAGED'])
    glyph(f, 'heart', (52, 45), 14, (255, 255, 255), 2, (255, 255, 255))
    f.txt((104, 45), str(home), 30, (255, 255, 255) if not home_flash else TIERC['DAMAGED'], mono=True)
    tile(164, 150, (255, 150, 90))
    glyph(f, 'flame', (190, 45), 14, (255, 140, 70), 2, (255, 140, 70))
    f.txt((236, 40), str(heat), 26, (255, 200, 150), mono=True)
    f.rr((212, 55, 304, 62), 3, (40, 20, 20), None)
    f.rr((212, 55, 212 + 92 * heat / 100, 62), 3, (255, 130, 60), None)
    # deck tally: healthy cards vs INFECTED cards as a mini-card row (balance, no sentence)
    n = max(healthy, infected)
    wtile = 40 + 22 * (healthy + infected)
    tile(326, wtile, (255, 120, 200) if infected else (110, 226, 255))
    x = 344
    for i in range(healthy):
        f.rr((x, 30, x + 14, 58), 3, (150, 230, 250), (255, 255, 255), 1.2)
        x += 20
    for i in range(infected):
        f.rr((x, 30, x + 14, 58), 3, (60, 14, 62), (255, 120, 200), 1.6)
        f.line([(x + 3, 38), (x + 11, 50)], 1.8, (255, 150, 215), cap=False)
        f.line([(x + 11, 38), (x + 3, 50)], 1.8, (255, 150, 215), cap=False)
        x += 20


# ---------------------------------------------------------------- cards
def card(kind, t, w=112, h=150, picked=False, dim=False):
    """vinyl-sticker component card. kind fuse / jumper / cap; t the beam type it answers (D / N / E)"""
    s = Sprite(w + 24, h + 24)
    o = 12
    s.rr((o - 6, o - 6, o + w + 6, o + h + 6), 16, (246, 242, 232))          # die-cut vinyl edge
    s.rr((o, o, o + w, o + h), 11, (12, 18, 40))
    col = TYPE_COL[t]
    s.rr((o + 5, o + 5, o + w - 5, o + 36), 8, (22, 30, 62))
    wave_chip(s, (o + 24, o + 21), t, 14)
    # PCB footprint motif
    for i in range(4):
        s.line([(o + 54 + i * 12, o + 14), (o + 54 + i * 12, o + 28)], 2.2, A(COPPER, 200), cap=False)
    # illustration
    cx, cy = o + w / 2, o + h * 0.62
    s.ell((cx, cy + 4), 44, 44, (20, 30, 62))
    if kind == 'fuse':
        fuse_flat(s, (cx, cy), 36)
    elif kind == 'jumper':
        jumper_flat(s, (cx, cy + 6), 32)
    else:
        cap_flat(s, (cx, cy), 34)
    s.line([(o + 12, o + h - 14), (o + w - 12, o + h - 14)], 4, col, cap=True)
    if dim:
        s.rr((o - 6, o - 6, o + w + 6, o + h + 6), 16, (6, 6, 14, 150))
    return s


def hand(f, specs, c=(900, 985), spread=104, scale=1.0, lift=None, raise_idx=None):
    """fan of cards along an arc. specs: [(kind, type)]"""
    n = len(specs)
    f.L('over')
    for i, (k, t) in enumerate(specs):
        u = i - (n - 1) / 2
        ang = -u * 4.0
        x = c[0] + u * spread * scale
        y = c[1] + abs(u) ** 1.6 * 4.5 * scale - (26 if raise_idx == i else 0)
        paste(f, card(k, t), (x, y), ang, scale)


def crt_chip(w, h, glyph_name, word, col, picked=False, dots=None, num=None, dim=False):
    s = Sprite(w + 20, h + 20)
    o = 10
    s.rr((o, o, o + w, o + h), 12, (5, 18, 28), col if not dim else (60, 80, 90), 2.8)
    for i in range(0, h, 4):
        s.line([(o + 5, o + i), (o + w - 5, o + i)], 1, (255, 255, 255, 9), cap=False)
    glyph(s, glyph_name, (o + 30, o + h * 0.42), 15, col, 3, col)
    if word:
        s.txt((o + w / 2 + 14, o + h * 0.42), word, 20, (255, 255, 255), mono=True)
    if num is not None:
        s.txt((o + w - 22, o + h * 0.42), str(num), 20, col, mono=True)
    if dots:
        n = len(dots)
        for i, tr in enumerate(dots):
            x = o + w / 2 - (n - 1) * 20 + i * 40
            tier_badge(s, (x, o + h * 0.76), tr, 12)
    return s


def tag(word, col, glyph_name='crack_heart', w=300, h=120):
    """corp-paper hang tag with a rubber stamp"""
    s = Sprite(w + 40, h + 40)
    o = 20
    s.poly([(o, o + 20), (o + 22, o), (o + w, o), (o + w, o + h), (o + 22, o + h), (o, o + h - 20)], PAPER, (60, 55, 50), 2)
    s.ell((o + 20, o + h / 2), 7, 7, (30, 30, 40))
    st = Sprite(w, h)
    st.rr((14, 14, w - 14, h - 14), 10, None, col, 5)
    st.rr((22, 22, w - 22, h - 22), 7, None, col, 2)
    glyph(st, glyph_name, (62, h / 2), 24, col, 4, col)
    st.txt((w / 2 + 30, h / 2 + 2), word, 36, col, mono=False)
    # rubber-stamp wear
    rng = random.Random(4)
    for _ in range(90):
        x, y = rng.uniform(16, w - 16), rng.uniform(16, h - 16)
        st.ell((x, y), rng.uniform(.8, 2.4), rng.uniform(.8, 2.4), (0, 0, 0, 0))
    a = np.asarray(st.im).copy()
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    nz = np.random.RandomState(2).rand(*a.shape[:2])
    a[..., 3] = (a[..., 3] * np.where(nz > 0.18, 1.0, 0.25)).astype(np.uint8)
    st.im = Image.fromarray(a)
    st.d = ImageDraw.Draw(st.im)
    r = st.im.rotate(0, expand=False)
    s.im.alpha_composite(r, (int(o * SS), int(o * SS)))
    return s


# ---------------------------------------------------------------- beams
def beam(f, pts, t, lane=0.0, s0=0.0, s1=None, alpha=1.0, amp=None, wl=None, env=None, casing=True, width=2.8,
         diodes=True, head=False, hot=0.0):
    """oscilloscope pulse on the street: sine (D) / square (N) / sawtooth (E). pts = street polyline (screen px)"""
    base = offset(pts, lane) if lane else list(pts)
    L = plen(base)
    s1 = L if s1 is None else min(L, s1)
    s0 = max(0.0, s0)
    if s1 - s0 < 4:
        return
    seg = sub(base, s0, s1)
    wl = wl or {'D': 38.0, 'N': 42.0, 'E': 36.0}[t]
    amp = amp or {'D': 6.5, 'N': 6.5, 'E': 8.5}[t]
    wv = waveform(seg, wave_kind(t), amp, wl, phase=(s0 / wl) % 1.0, env=env)
    col = TYPE_COL[t]
    core = mix(col, WHITE, 0.62)
    if casing:
        f.L('over')
        f.line(wv, width + 4.4, (5, 3, 12, int(210 * alpha)))
    f.L('add', bloom=1.0 * alpha)
    f.line(wv, width + 1.4, tuple(int(c * 0.75 * alpha) for c in col))
    f.line(wv, width * 0.5, tuple(int(c * alpha) for c in core))
    if hot:
        f.line(wv, width * 0.35, tuple(int(255 * hot) for _ in range(3)))
    if diodes:
        n = max(1, int((s1 - s0) / 170))
        f.L('over')
        for i in range(n):
            q, d = at(base, s0 + (i + 0.5) * (s1 - s0) / n)
            nx, ny = -d[1], d[0]
            tri = [(q[0] + d[0] * 7, q[1] + d[1] * 7), (q[0] - d[0] * 6 + nx * 6, q[1] - d[1] * 6 + ny * 6),
                   (q[0] - d[0] * 6 - nx * 6, q[1] - d[1] * 6 - ny * 6)]
            f.poly(tri, (*col, int(255 * alpha)), (5, 3, 12, int(255 * alpha)), 1.2)
            bar = [(q[0] + d[0] * 9 + nx * 6, q[1] + d[1] * 9 + ny * 6), (q[0] + d[0] * 9 - nx * 6, q[1] + d[1] * 9 - ny * 6)]
            f.line(bar, 2.2, (*col, int(255 * alpha)), cap=False)
    if head:
        q, d = at(base, s1)
        f.L('add', bloom=1.4)
        f.ell(q, 9, 9, tuple(int(c * 0.8) for c in col))
        f.ell(q, 5, 5, (255, 255, 255))
    return wv


def noise_band(f, pts, width=9, dens=2.2, seed=5, alpha=1.0, cols=None):
    """sealed route = ciphertext static hugging the street"""
    rng = random.Random(seed)
    cols = cols or [(255, 255, 255), (170, 150, 255), (110, 120, 150), (255, 200, 255)]
    p = rs(pts, 1.0)
    f.L('add', bloom=0.6)
    for i, q in enumerate(p):
        if i + 1 < len(p):
            dx, dy = p[i + 1][0] - q[0], p[i + 1][1] - q[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        for _ in range(int(dens * 2 + rng.random() * dens)):
            o = rng.gauss(0, width * 0.42)
            if abs(o) > width:
                continue
            x, y = q[0] + nx * o, q[1] + ny * o
            b = rng.random()
            c = rng.choice(cols)
            sz = rng.choice((1.0, 1.0, 1.6, 2.4))
            if rng.random() < 0.06:  # glitch dash
                f.line([(x, y), (x + rng.uniform(-9, 9), y)], 1.4, tuple(int(v * b * alpha) for v in c), cap=False)
            else:
                f.px(x, y, sz, tuple(int(v * b * alpha) for v in c))
    f._m(pts, width + 6)


# ---------------------------------------------------------------- defense components soldered on the board
def component(f, c, kind, t, blown=False, hot=0.0, pad_c=None):
    """iso component standing next to its chip. kind: fuse / jumper / cap. t: beam type it answers"""
    col = TYPE_COL[t]
    f.L('shadow', blur=4)
    f.ell((c[0] + 4, c[1] + 6), 30, 12, (0, 0, 0, 160))
    f.flush()
    f.L('over')
    # solder pads on the trace
    if kind == 'fuse':
        a0, a1 = gpt(c, -1.35, 0), gpt(c, 1.35, 0)
        f.ell(a0, 8, 5, A(COPPER, 255), TIN, 1.6)
        f.ell(a1, 8, 5, A(COPPER, 255), TIN, 1.6)
        y = -13
        s0_, s1_ = (a0[0], a0[1] + y), (a1[0], a1[1] + y)
        f.line([s0_, s1_], 24, (8, 8, 18, 255))
        f.line([s0_, s1_], 20, (170, 220, 245, 255) if not blown else (46, 52, 66, 255))
        f.line([(s0_[0] + 4, s0_[1] - 5), (s1_[0] - 4, s1_[1] - 5)], 3.0, (240, 252, 255, 255) if not blown else (120, 130, 150, 255))
        for q, sg in ((s0_, 1), (s1_, -1)):
            f.line([(q[0] + sg * 1, q[1]), (q[0] + sg * 11, q[1] + sg * 7)], 24, (196, 206, 218, 255), cap=False)
            f.line([(q[0] + sg * 11, q[1] + sg * 7), (q[0] + sg * 13, q[1] + sg * 8)], 24, (110, 120, 135, 255), cap=False)
        m = ((s0_[0] + s1_[0]) / 2, (s0_[1] + s1_[1]) / 2)
        if not blown:
            f.line([(m[0] - 20, m[1] - 8), (m[0] - 10, m[1] + 0), (m[0], m[1] - 8), (m[0] + 10, m[1] + 4), (m[0] + 20, m[1] - 2)],
                   2.4, (255, 200, 110, 255))
        else:
            f.line([(m[0] - 20, m[1] - 8), (m[0] - 8, m[1] - 2)], 2.2, (255, 200, 110, 255))
            f.line([(m[0] + 8, m[1] + 4), (m[0] + 20, m[1] - 2)], 2.2, (255, 200, 110, 255))
            f.line([(m[0] - 6, m[1] - 12), (m[0] + 2, m[1] + 2), (m[0] + 10, m[1] - 10)], 1.6, (10, 8, 14, 255))
        top = (c[0], c[1] - 50)
    elif kind == 'jumper':
        jumper_flat(s, (cx, cy + 6), 32)
    else:
        cap_flat(s, (cx, cy), 34)
    s.line([(o + 12, o + h - 14), (o + w - 12, o + h - 14)], 4, col, cap=True)
    if dim:
        s.rr((o - 6, o - 6, o + w + 6, o + h + 6), 16, (6, 6, 14, 150))
    return s


def hand(f, specs, c=(900, 985), spread=104, scale=1.0, lift=None, raise_idx=None):
    """fan of cards along an arc. specs: [(kind, type)]"""
    n = len(specs)
    f.L('over')
    for i, (k, t) in enumerate(specs):
        u = i - (n - 1) / 2
        ang = -u * 4.0
        x = c[0] + u * spread * scale
        y = c[1] + abs(u) ** 1.6 * 4.5 * scale - (26 if raise_idx == i else 0)
        paste(f, card(k, t), (x, y), ang, scale)


def crt_chip(w, h, glyph_name, word, col, picked=False, dots=None, num=None, dim=False):
    s = Sprite(w + 20, h + 20)
    o = 10
    s.rr((o, o, o + w, o + h), 12, (5, 18, 28), col if not dim else (60, 80, 90), 2.8)
    for i in range(0, h, 4):
        s.line([(o + 5, o + i), (o + w - 5, o + i)], 1, (255, 255, 255, 9), cap=False)
    glyph(s, glyph_name, (o + 30, o + h * 0.42), 15, col, 3, col)
    if word:
        s.txt((o + w / 2 + 14, o + h * 0.42), word, 20, (255, 255, 255), mono=True)
    if num is not None:
        s.txt((o + w - 22, o + h * 0.42), str(num), 20, col, mono=True)
    if dots:
        n = len(dots)
        for i, tr in enumerate(dots):
            x = o + w / 2 - (n - 1) * 20 + i * 40
            tier_badge(s, (x, o + h * 0.76), tr, 12)
    return s


def tag(word, col, glyph_name='crack_heart', w=300, h=120):
    """corp-paper hang tag with a rubber stamp"""
    s = Sprite(w + 40, h + 40)
    o = 20
    s.poly([(o, o + 20), (o + 22, o), (o + w, o), (o + w, o + h), (o + 22, o + h), (o, o + h - 20)], PAPER, (60, 55, 50), 2)
    s.ell((o + 20, o + h / 2), 7, 7, (30, 30, 40))
    st = Sprite(w, h)
    st.rr((14, 14, w - 14, h - 14), 10, None, col, 5)
    st.rr((22, 22, w - 22, h - 22), 7, None, col, 2)
    glyph(st, glyph_name, (62, h / 2), 24, col, 4, col)
    st.txt((w / 2 + 30, h / 2 + 2), word, 36, col, mono=False)
    # rubber-stamp wear
    rng = random.Random(4)
    for _ in range(90):
        x, y = rng.uniform(16, w - 16), rng.uniform(16, h - 16)
        st.ell((x, y), rng.uniform(.8, 2.4), rng.uniform(.8, 2.4), (0, 0, 0, 0))
    a = np.asarray(st.im).copy()
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    nz = np.random.RandomState(2).rand(*a.shape[:2])
    a[..., 3] = (a[..., 3] * np.where(nz > 0.18, 1.0, 0.25)).astype(np.uint8)
    st.im = Image.fromarray(a)
    st.d = ImageDraw.Draw(st.im)
    r = st.im.rotate(0, expand=False)
    s.im.alpha_composite(r, (int(o * SS), int(o * SS)))
    return s


# ---------------------------------------------------------------- beams
def beam(f, pts, t, lane=0.0, s0=0.0, s1=None, alpha=1.0, amp=None, wl=None, env=None, casing=True, width=2.8,
         diodes=True, head=False, hot=0.0):
    """oscilloscope pulse on the street: sine (D) / square (N) / sawtooth (E). pts = street polyline (screen px)"""
    base = offset(pts, lane) if lane else list(pts)
    L = plen(base)
    s1 = L if s1 is None else min(L, s1)
    s0 = max(0.0, s0)
    if s1 - s0 < 4:
        return
    seg = sub(base, s0, s1)
    wl = wl or {'D': 38.0, 'N': 42.0, 'E': 36.0}[t]
    amp = amp or {'D': 6.5, 'N': 6.5, 'E': 8.5}[t]
    wv = waveform(seg, wave_kind(t), amp, wl, phase=(s0 / wl) % 1.0, env=env)
    col = TYPE_COL[t]
    core = mix(col, WHITE, 0.62)
    if casing:
        f.L('over')
        f.line(wv, width + 4.4, (5, 3, 12, int(210 * alpha)))
    f.L('add', bloom=1.0 * alpha)
    f.line(wv, width + 1.4, tuple(int(c * 0.75 * alpha) for c in col))
    f.line(wv, width * 0.5, tuple(int(c * alpha) for c in core))
    if hot:
        f.line(wv, width * 0.35, tuple(int(255 * hot) for _ in range(3)))
    if diodes:
        n = max(1, int((s1 - s0) / 170))
        f.L('over')
        for i in range(n):
            q, d = at(base, s0 + (i + 0.5) * (s1 - s0) / n)
            nx, ny = -d[1], d[0]
            tri = [(q[0] + d[0] * 7, q[1] + d[1] * 7), (q[0] - d[0] * 6 + nx * 6, q[1] - d[1] * 6 + ny * 6),
                   (q[0] - d[0] * 6 - nx * 6, q[1] - d[1] * 6 - ny * 6)]
            f.poly(tri, (*col, int(255 * alpha)), (5, 3, 12, int(255 * alpha)), 1.2)
            bar = [(q[0] + d[0] * 9 + nx * 6, q[1] + d[1] * 9 + ny * 6), (q[0] + d[0] * 9 - nx * 6, q[1] + d[1] * 9 - ny * 6)]
            f.line(bar, 2.2, (*col, int(255 * alpha)), cap=False)
    if head:
        q, d = at(base, s1)
        f.L('add', bloom=1.4)
        f.ell(q, 9, 9, tuple(int(c * 0.8) for c in col))
        f.ell(q, 5, 5, (255, 255, 255))
    return wv


def noise_band(f, pts, width=9, dens=2.2, seed=5, alpha=1.0, cols=None):
    """sealed route = ciphertext static hugging the street"""
    rng = random.Random(seed)
    cols = cols or [(255, 255, 255), (170, 150, 255), (110, 120, 150), (255, 200, 255)]
    p = rs(pts, 1.0)
    f.L('add', bloom=0.6)
    for i, q in enumerate(p):
        if i + 1 < len(p):
            dx, dy = p[i + 1][0] - q[0], p[i + 1][1] - q[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        for _ in range(int(dens * 2 + rng.random() * dens)):
            o = rng.gauss(0, width * 0.42)
            if abs(o) > width:
                continue
            x, y = q[0] + nx * o, q[1] + ny * o
            b = rng.random()
            c = rng.choice(cols)
            sz = rng.choice((1.0, 1.0, 1.6, 2.4))
            if rng.random() < 0.06:  # glitch dash
                f.line([(x, y), (x + rng.uniform(-9, 9), y)], 1.4, tuple(int(v * b * alpha) for v in c), cap=False)
            else:
                f.px(x, y, sz, tuple(int(v * b * alpha) for v in c))
    f._m(pts, width + 6)


# ---------------------------------------------------------------- defense components soldered on the board
def component(f, c, kind, t, blown=False, hot=0.0, pad_c=None):
    """iso component standing next to its chip. kind: fuse / jumper / cap. t: beam type it answers"""
    col = TYPE_COL[t]
    f.L('shadow', blur=4)
    f.ell((c[0] + 4, c[1] + 6), 30, 12, (0, 0, 0, 160))
    f.flush()
    f.L('over')
    # solder pads on the trace
    if kind == 'fuse':
        a0, a1 = gpt(c, -1.0, 0), gpt(c, 1.0, 0)
        f.ell(a0, 7, 4.5, A(COPPER, 255), TIN, 1.6)
        f.ell(a1, 7, 4.5, A(COPPER, 255), TIN, 1.6)
        # glass cartridge lying on the board along +p
        y = -9
        s0_, s1_ = (a0[0], a0[1] + y), (a1[0], a1[1] + y)
        f.line([s0_, s1_], 15, (10, 10, 20, 255))
        f.line([s0_, s1_], 12, (150, 205, 235, 255) if not blown else (60, 70, 85, 255))
        f.line([(s0_[0] + 3, s0_[1] - 3), (s1_[0] - 3, s1_[1] - 3)], 2.4, (235, 250, 255, 255))
        for q in (s0_, s1_):
            f.line([(q[0] - 3, q[1] - 2), (q[0] + 3, q[1] + 2)], 14, (200, 210, 220, 255), cap=False)
        if not blown:
            m = ((s0_[0] + s1_[0]) / 2, (s0_[1] + s1_[1]) / 2)
            f.line([(m[0] - 18, m[1] - 8), (m[0] - 9, m[1] - 3), (m[0], m[1] + 1), (m[0] + 9, m[1] + 6), (m[0] + 18, m[1] + 11)],
                   1.8, (255, 215, 140))
        top = (c[0], c[1] - 40)
    elif kind == 'jumper':
        a0, a1 = gpt(c, -1.1, 0), gpt(c, 1.5, 0)
        for q in (a0, a1):
            f.ell(q, 7, 4.5, A(COPPER, 255), TIN, 1.6)
        arc = []
        for i in range(25):
            u = i / 24
            arc.append((a0[0] + (a1[0] - a0[0]) * u, a0[1] + (a1[1] - a0[1]) * u - math.sin(u * math.pi) * 32))
        f.line(arc, 7.2, (5, 3, 12, 255))
        f.line(arc, 4.2, (255, 255, 255, 255))
        top = (arc[12][0], arc[12][1] - 20)
    else:  # capacitor can
        cyl(f, (c[0], c[1] + 4), 11, 26, (24, 50, 120), (70, 100, 170), (170, 200, 255))
        f.rr((c[0] - 11, c[1] - 22, c[0] - 4, c[1] + 4), 3, (200, 220, 255))
        for dx in (-4, 5):
            f.ell((c[0] + dx, c[1] + 6), 3.2, 2.2, TIN)
        top = (c[0], c[1] - 46)
    # the type token above it
    f.L('over')
    wave_chip(f, top, t, 12)
    f.L('add', bloom=0.9)
    f.ell(top, 14, 14, None, tuple(int(v * 0.8) for v in col), 2.2)
    if hot:
        f.ell(c, 24 * hot, 12 * hot, None, (255, 255, 255), 2)
    return top
