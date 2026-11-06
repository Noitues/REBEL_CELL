"""Cached world pieces shared by every beat renderer."""
from fx import *
import os

WORKD = 'D:/rc_scratch/tide_concepts/p1m_work/'
os.makedirs(WORKD, exist_ok=True)

PROGRAMS = {'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}
HAND = [('GUARD', 'D'), ('GUARD', 'N'), ('SHIFT', 'E'), ('JAM', 'N'), ('GUARD', 'E')]


class Stage:
    def __init__(self):
        self.w = World('default')
        self.cv0 = new_canvas(self.w)
        self.base = self.cv0.img.copy()          # graded city + rails
        self.raw = raw_city()
        self._cache = {}
        self.home = self.w.home
        self.hq = self.w.hq
        self.cage_c = np.array([self.hq[0] + 140, self.hq[1] - 170])
        order = sorted(self.w.sites, key=lambda s: float(np.hypot(*(self.w.sites[s]['B'] - self.home))))
        self.site_order = order                  # nearest to HOME first (the grade front reaches them in this order)

    def cv(self):
        return Cv(self.base)

    def cached(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    def world(self, key='idle', states=None, programs=PROGRAMS, home_kw=None, idle=('t1_d',), cage_kw=None, skip_marks=False, extra=None):
        """graded city + towers + programs + HOME deck + Solace cage (cached by key)."""
        def build():
            cv = self.cv()
            draw_world(cv, self.w, states or {}, programs, home_kw=home_kw or dict(hp=44), idle=idle, cage_kw=cage_kw, skip_marks=skip_marks)
            if extra:
                extra(cv)
            return cv.img.copy()
        return Cv(self.cached(('world', key), build))

    def route(self, r):
        return PX(self.w.routes[r]['path'])


S = None


def stage():
    global S
    if S is None:
        S = Stage()
    return S


def hand_slots(n, y=992, spread=108):
    x0 = W / 2 - (n - 1) / 2 * spread
    out = []
    for i in range(n):
        t = i - (n - 1) / 2
        out.append((np.array([x0 + i * spread, y + abs(t) ** 1.6 * 8]), -t * 3.4))
    return out


_CS = {}


def card_spr(verb, typ):
    k = (verb, typ)
    if k not in _CS:
        img, a = hy.vcard_sprite(verb, typ)
        _CS[k] = (img, a)
    return _CS[k]


def put_card(cv, verb, typ, c, angle=0.0, sc=.9, k=1.0, scale_x=1.0, lime=False, back=False):
    img, a = card_spr(verb, typ)
    h, w_ = a.shape
    im = Image.fromarray(to_u8(np.dstack([img, a])), 'RGBA')
    if back:
        # card back: navy with a type-neutral lattice
        arr = np.zeros((h, w_, 3), np.float32) + hexc('0B1236')
        edge = np.clip(blur(a, 1.5) - blur(a, 6) * 0 , 0, 1)
        im = Image.fromarray(to_u8(np.dstack([arr, a])), 'RGBA')
    nw, nh = max(2, int(w_ * sc * scale_x)), max(2, int(h * sc))
    im = im.resize((nw, nh), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    arr = np.asarray(im, np.float32) / 255
    ox, oy = int(c[0] - arr.shape[1] / 2), int(c[1] - arr.shape[0] / 2)
    cv.over(INK, blur(arr[..., 3], 7), .6 * k, (ox + 4, oy + 9))
    if lime:
        big = Image.fromarray((arr[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
        ring = np.clip(np.asarray(big, np.float32) / 255 - arr[..., 3], 0, 1)
        cv.add(LIME, blur(arr[..., 3], 6), .9 * k, (ox, oy))
        cv.add(LIME, ring, 1.0 * k, (ox, oy))
    if back:
        # lattice lines on the back
        ly = Lyr((ox, oy, ox + arr.shape[1], oy + arr.shape[0]), pad=0)
        for i in range(-4, 8):
            ly.line([(ox + i * 14, oy), (ox + i * 14 + 60, oy + arr.shape[0])], 1.6, 255)
        cv.over(arr[..., :3], arr[..., 3], k, (ox, oy))
        cv.add(LATT_D, ly.m * (arr[..., 3][:ly.m.shape[0], :ly.m.shape[1]] > .5), .5 * k, ly.off)
        g = Lyr((ox, oy, ox + arr.shape[1], oy + arr.shape[0]), pad=0)
        g.ell((ox + arr.shape[1] / 2, oy + arr.shape[0] / 2), 15, v=255, outline=True, ow=2.5)
        cv.neonL(g, LATT, core=.9 * k, g1=(2, .5 * k), g2=None)
    else:
        cv.over(arr[..., :3], arr[..., 3], k, (ox, oy))


def hud_sprite():
    return spr(lambda cv: hy.hud(cv, 44, 50, 80, 8, 0), (0, 0, W, 96))
