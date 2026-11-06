"""CV (converged Shifting Waves) helpers: supersampled screen layer, geometry, chips, arc text, glyphs.
Reuses the bible kit (bb_lib: fonts, bible glyph set, round41 slice renderer)."""
import sys, os, math, json, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bb_lib as B
from bb_lib import *          # np, Image, ImageDraw, ImageFilter, anton, mono, plex, glyph_rgba, colours, SL, RW, CW
ROOT = os.path.dirname(HERE) + '/'
W, H = 1920, 1080
NOW = {'words': True}
K = 0.76 * 0.84                      # master -> screen scale of the board
C = (536, 540)                # board centre on screen
# screen radii (px)
RS = dict(hub=42, s0=44, s1=143, hp0=146, hp1=158, c0=161, T=64, bz0=355, bz1=389)
WHITE = (242, 246, 255)
TXT_MID = (175, 192, 214)
CRT_TXT = (207, 246, 255)
AMBER = (255, 176, 0)
PURP = (200, 90, 255)
KIND = {'Packet': ('EXPLOIT', 'U_PACKET'), 'Worm': ('VIRUS', 'U_WORM'), 'Jammer': ('TROJAN', 'U_JAMMER'),
        'Payload': ('ZERO-DAY', 'U_PAYLOAD'), 'Adjuster': ('NULL', 'X_SKULL')}
KCOL = {'Packet': (255, 61, 168), 'Worm': (200, 90, 255), 'Jammer': (176, 140, 255), 'Payload': (255, 120, 215), 'Adjuster': (210, 210, 220)}
KNAME = {'Packet': 'PACKET', 'Worm': 'WORM', 'Jammer': 'JAMMER', 'Payload': 'PAYLOAD', 'Adjuster': 'ADJUSTER'}
LANE = [dict(col=RED, dash=None, w=4, name='NOW'), dict(col=(120, 170, 255), dash=None, w=3, name='+1'), dict(col=(236, 240, 255), dash=(10, 7), w=3, name='+2')]


def ppx(c, r, ang):
    a = math.radians(ang)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


class L2:
    """transparent screen layer drawn at 2x and downscaled on done(); every coordinate is a 1080p pixel."""

    def __init__(self, k=2):
        self.k = k
        self.im = Image.new('RGBA', (W * k, H * k), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * self.k, y * self.k) for x, y in pts]

    def poly(self, pts, fill=None, outline=None, w=1):
        f = None if fill is None else tuple(fill) + ((255,) if len(fill) == 3 else ())
        o = None if outline is None else tuple(outline) + ((255,) if len(outline) == 3 else ())
        self.d.polygon(self.P(pts), fill=f)
        if o is not None:
            pp = self.P(pts)
            self.d.line(pp + [pp[0]], fill=o, width=max(1, int(w * self.k)), joint='curve')

    def line(self, pts, col, w=2, dash=None):
        col = tuple(col) + ((255,) if len(col) == 3 else ())
        if dash is None:
            self.d.line(self.P(pts), fill=col, width=max(1, int(w * self.k)), joint='curve')
        else:
            dashed_k(self.d, self.P(pts), col, max(1, int(w * self.k)), dash[0] * self.k, dash[1] * self.k)

    def text(self, xy, s, font_px, kind='anton', fill=(255, 255, 255), anchor='mm', stroke=0, sf=INK):
        if not NOW['words']:
            t = s.strip().lstrip('-(+')
            if kind == 'anton' and t.isdigit():
                n = int(t)
                w = max(10, n * 1.2)
                x0 = xy[0] - (w / 2 if anchor[0] == 'm' else 0)
                hh = font_px * 0.30
                self.rect([x0, xy[1] - hh / 2, x0 + w, xy[1] + hh / 2], fill=tuple(fill), outline=INK, w=1.5, r=2)
            return
        f = {'anton': anton, 'mono': mono, 'plex': plex}[kind](int(font_px * self.k))
        fill = tuple(fill) + ((255,) if len(fill) == 3 else ())
        self.d.text((xy[0] * self.k, xy[1] * self.k), s, font=f, fill=fill, anchor=anchor,
                    stroke_width=int(stroke * self.k), stroke_fill=tuple(sf) + (255,))

    def tw(self, s, font_px, kind='anton'):
        f = {'anton': anton, 'mono': mono, 'plex': plex}[kind](int(font_px * self.k))
        return f.getlength(s) / self.k

    def rect(self, box, fill=None, outline=None, w=2, r=8):
        b = [v * self.k for v in box]
        self.d.rounded_rectangle(b, radius=r * self.k, fill=None if fill is None else tuple(fill) + ((255,) if len(fill) == 3 else ()),
                                 outline=None if outline is None else tuple(outline) + ((255,) if len(outline) == 3 else ()), width=int(w * self.k))

    def ellipse(self, box, fill=None, outline=None, w=2):
        b = [v * self.k for v in box]
        self.d.ellipse(b, fill=None if fill is None else tuple(fill) + ((255,) if len(fill) == 3 else ()),
                       outline=None if outline is None else tuple(outline) + ((255,) if len(outline) == 3 else ()), width=int(w * self.k))

    def glyph(self, name, px, xy, col=(255, 255, 255)):
        g = glyph_rgba(name, int(px * self.k), max(2, int(px * self.k * 0.075)), fill=col)
        self.im.alpha_composite(g, (int(xy[0] * self.k - g.width / 2), int(xy[1] * self.k - g.height / 2)))
        return g.width / self.k

    def paste(self, img, xy, scale=1.0):
        """paste a 1x RGBA at screen centre xy (rendered at 1x -> upscaled k)."""
        im = img.resize((int(img.width * self.k * scale), int(img.height * self.k * scale)), Image.LANCZOS)
        self.im.alpha_composite(im, (int(xy[0] * self.k - im.width / 2), int(xy[1] * self.k - im.height / 2)))

    def glow(self, fn, blur=6, strength=1.0):
        """fn(draw) draws in 2x px on a temp layer, blurred and added."""
        t = Image.new('RGBA', self.im.size, (0, 0, 0, 0))
        fn(ImageDraw.Draw(t))
        t = t.filter(ImageFilter.GaussianBlur(blur * self.k))
        if strength != 1.0:
            t.putalpha(t.split()[3].point(lambda v: int(v * strength)))
        self.im.alpha_composite(t)

    def arc_pts(self, c, r, a0, a1, n=None):
        n = n or max(6, int(abs(a1 - a0) / 3))
        return [ppx(c, r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]

    def band(self, c, r0, r1, a0, a1):
        n = max(6, int(abs(a1 - a0) / 3))
        return [ppx(c, r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [ppx(c, r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]

    def arc_text(self, c, r, a_mid, s, px, col, kind='mono', spread=None, flip=False):
        """text laid along a circle (clockwise reading), centred on angle a_mid."""
        f = {'anton': anton, 'mono': mono, 'plex': plex}[kind](int(px * self.k))
        advs = [f.getlength(ch) / self.k for ch in s]
        tot = sum(advs)
        if not NOW['words']:
            return
        bottom = 90 < (a_mid % 360) < 270
        if bottom:
            s, advs, flip = s[::-1], advs[::-1], True
        a = a_mid - math.degrees(tot / 2 / r)
        for ch, adv in zip(s, advs):
            am = a + math.degrees(adv / 2 / r)
            if ch != ' ':
                x, y = ppx(c, r, am)
                tmp = Image.new('RGBA', (int(adv * self.k * 2 + 8), int(px * self.k * 1.8)), (0, 0, 0, 0))
                ImageDraw.Draw(tmp).text((tmp.width / 2, tmp.height / 2), ch, font=f, fill=tuple(col) + (255,), anchor='mm')
                tmp = tmp.rotate(-am + (180 if flip else 0), resample=Image.BICUBIC, expand=True)
                self.im.alpha_composite(tmp, (int(x * self.k - tmp.width / 2), int(y * self.k - tmp.height / 2)))
            a += math.degrees(adv / r)

    def done(self):
        return self.im.resize((W, H), Image.LANCZOS)


def dashed_k(d, pts, col, w, dash, gap):
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0:
            continue
        t = 0
        while t < L:
            t2 = min(L, t + dash)
            d.line([(x0 + (x1 - x0) * t / L, y0 + (y1 - y0) * t / L), (x0 + (x1 - x0) * t2 / L, y0 + (y1 - y0) * t2 / L)], fill=col, width=w)
            t += dash + gap


def chip(L, x, y, s, col, px=26, h=34, icon=None, box=True, pad=8, anchor='l', fill=(10, 9, 16), kind='anton', dash=None, w=2, icon_after=True, tcol=None):
    """CRT/HUD chip (bible 3.1 result chips). returns bbox. x,y = top-left (anchor l) or top-right (anchor r)."""
    tw = L.tw(s, px, kind)
    ig = (h - 14) if icon else 0
    w_ = tw + 2 * pad + (ig + 3 if icon else 0)
    x0 = x if anchor == 'l' else x - w_
    if box:
        L.rect([x0, y, x0 + w_, y + h], fill=fill + (240,), outline=col, w=w, r=7)
        if dash:
            pass
    xx = x0 + pad
    if icon and not icon_after:
        L.glyph(icon, ig, (xx + ig / 2, y + h / 2), col)
        xx += ig + 3
    L.text((xx, y + h / 2 + 1), s, px, kind, fill=tcol or col, anchor='lm')
    if icon and icon_after:
        L.glyph(icon, ig, (xx + tw + 3 + ig / 2, y + h / 2), col)
    return (x0, y, x0 + w_, y + h)


def vinyl(text, size, col, ink=(14, 12, 20), tilt=2, pad=(22, 10)):
    if not NOW['words']:
        text = ' ' * max(2, len(text) // 2)
    f = anton(size)
    tw = f.getlength(text)
    w, h = int(tw + 2 * pad[0]), int(size * 1.25 + 2 * pad[1])
    b = 12
    im = Image.new('RGBA', (w + 2 * b, h + 2 * b), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w + 2 * b - 1, h + 2 * b - 1], radius=16, fill=(250, 250, 248, 255))
    d.rounded_rectangle([b, b, b + w, b + h], radius=10, fill=col + (255,), outline=ink + (255,), width=3)
    d.text((b + w / 2, b + h / 2 + 2), text, font=f, fill=ink + (255,), anchor='mm')
    return im.rotate(tilt, resample=Image.BICUBIC, expand=True)


def shadow_paste(base, im, xy, k=0.5, blur=8, off=(5, 9)):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    sh.putalpha(im.split()[3].point(lambda v: int(v * k)).filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(sh, (int(xy[0] + off[0]), int(xy[1] + off[1])))
    base.alpha_composite(im, (int(xy[0]), int(xy[1])))


def terminal(L, box, col=CYAN, fill=(5, 13, 28)):
    """CRT terminal plate (bible 1.2): navy glass, cyan edge, scanlines."""
    L.rect(box, fill=fill + (238,), outline=col + (210,), w=2, r=8)
    x0, y0, x1, y1 = box
    for y in range(int(y0) + 5, int(y1) - 3, 4):
        L.line([(x0 + 5, y), (x1 - 5, y)], (0, 0, 0, 38), 1)


def load_state():
    return json.load(open(ROOT + 'state_cv.json'))


def backdrop(centres_r=None, dim=0.80):
    """bible 3.14: close-up of the attacked place, board softened; round31 Meridian HQ close-up (same frame as the strict bible plates)."""
    g = Image.open(ROOT + 'round31_meridian_combat/meridian_backdrop_motion.gif')
    g.seek(6)
    bd = g.convert('RGB').resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
    a = np.asarray(bd, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    q = np.hypot(xx - C[0], yy - C[1]) / (RS['bz1'] * 1.22)
    pool = np.exp(-q ** 4)
    d_ = dim * (1 - 0.55 * pool)
    return Image.fromarray(np.clip(a * d_[..., None], 0, 255).astype(np.uint8)).convert('RGBA')


def _g_pull(d, m):
    d.rectangle([226, 40, 286, 280], fill=255)
    d.polygon([(110, 250), (402, 250), (256, 420)], fill=255)
    d.rectangle([90, 440, 422, 480], fill=255)


import crests15 as _c15
_c15.CUSTOM['C_PULL'] = B._mk(_g_pull)
