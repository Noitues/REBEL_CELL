"""Round 24 city motion: shared scene + layer renderer.

The approved round 6 restyle (views/restyle_*_full.png) is the static base. Every moving layer is
placed from round6_city_restyle/city_layout.json (street tiles, building prims) so traffic runs on
real avenues and hides behind the real towers (a depth buffer built from the building prims).

Frames are composed at 2x (1920x1080) and reduced to 960x540. All motion is periodic in the loop
length so ambient GIFs loop seamlessly. Randomness is seeded.
"""
import json
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONC = os.path.dirname(ROOT)
R6 = os.path.join(CONC, 'round6_city_restyle')
SCR = os.path.join(ROOT, 'scratch')
BAHN = 'C:/Windows/Fonts/bahnschrift.ttf'

W, H = 960, 540
SS = 2
CROP = (600, 560, 1920, 1302)             # on the 2560 restyle png
Z = 0.633 * 2 / 3                          # city px -> 2560 png px
S = Z * W / (CROP[2] - CROP[0])            # city px -> out px
X0, Y0 = CROP[0] / Z, CROP[1] / Z
TILE_O = (3033.2, 1723.2)                  # street tile (0, 0) centre, city px
LIME = (212, 255, 0)
HAL_V, HAL_A = (140, 123, 255), (255, 176, 40)
RED, BLUE = (255, 34, 56), (42, 107, 255)


def P(x, y):
    """city px -> out px (1x)."""
    return ((x - X0) * S, (y - Y0) * S)


def tile(i, j):
    """Street tile centre (out px, 1x)."""
    return P(TILE_O[0] + (i - j) * 34, TILE_O[1] + (i + j) * 17)


def font(sz, bold=True):
    f = ImageFont.truetype(BAHN, sz)
    try:
        f.set_variation_by_name('Bold' if bold else 'Regular')
    except Exception:
        pass
    return f


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def ss(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Scene:
    def __init__(self, theme, seed=24):
        self.theme = theme
        self.night = theme == 'night'
        self.rng = random.Random(seed)
        self.d = json.load(open(os.path.join(R6, 'city_layout.json')))
        name = 'restyle_%s_full.png' % theme
        big = Image.open(os.path.join(R6, 'views', name)).convert('RGB').crop(CROP)
        self.base1 = big.resize((W, H), Image.LANCZOS)
        self.base2 = big.resize((W * SS, H * SS), Image.LANCZOS)
        self._depth()
        self._avenues()
        self._tops()
        self._highways()
        self._flylanes()
        self._billboards()
        self._vents()
        self._fog_field()
        self._rain()

    # ------------------------------------------------------------------ geometry
    def _depth(self):
        """Depth buffer at 2x: per pixel, the ground depth (out-px y) of the nearest building covering it."""
        prims = []
        for pr in self.d['prims']:
            if pr['t'] != 'ext':
                continue
            b = pr['b']
            cx, cy = sum(b[0::2]) / 4, sum(b[1::2]) / 4
            ox, oy = P(cx, cy)
            if not (-80 < ox < W + 80 and -40 < oy < H + 400):
                continue
            pts = []
            for k in range(4):
                bx, by = b[2 * k], b[2 * k + 1]
                pts.append(P(bx, by - pr['z0']))
                tx = cx + (bx - cx) * pr['ts']
                ty = cy + (by - cy) * pr['ts'] - pr['z0'] - pr['h']
                pts.append(P(tx, ty))
            prims.append((oy + 2.0, pts, pr))
        prims.sort(key=lambda p: p[0])
        img = Image.new('I', (W * SS, H * SS), -100000)
        dr = ImageDraw.Draw(img)
        for dep, pts, pr in prims:
            hp = _hull([(x * SS, y * SS) for x, y in pts])
            dr.polygon(hp, fill=int(dep * 10))
        self.depth = np.asarray(img, dtype=np.int32)
        self.prims = prims

    def vis(self, x, y, gy=None):
        """Is a ground point at out px (x, y) seen (no building in front)?"""
        X, Y = int(x * SS), int(y * SS)
        if not (0 <= X < W * SS and 0 <= Y < H * SS):
            return False
        g = y if gy is None else gy
        return self.depth[Y, X] <= g * 10 + 6

    def _avenues(self):
        T = {(s['i'], s['j']): s for s in self.d['streets']}
        from collections import Counter
        ci = Counter(s['i'] for s in self.d['streets'])
        cj = Counter(s['j'] for s in self.d['streets'])
        self.av_i = sorted(i for i, n in ci.items() if n >= 60)
        self.av_j = sorted(j for j, n in cj.items() if n >= 60)
        lines = []
        for axis, keys in (('i', self.av_i), ('j', self.av_j)):
            for k in keys:
                run = []
                for m in range(-130, 131):
                    key = (k, m) if axis == 'i' else (m, k)
                    if key in T:
                        x, y = tile(*key)
                        if -30 < x < W + 30 and -30 < y < H + 30:
                            run.append((x, y, T[key].get('traffic', 0.3)))
                            continue
                    if len(run) > 3:
                        lines.append((axis, k, run))
                    run = []
                if len(run) > 3:
                    lines.append((axis, k, run))
        self.lines = lines

    def _tops(self):
        tops = []
        for dep, pts, pr in self.prims:
            b = pr['b']
            cx, cy = sum(b[0::2]) / 4, sum(b[1::2]) / 4
            tx, ty = P(cx, cy - pr['z0'] - pr['h'])
            gx, gy = P(cx, cy)
            if 6 < tx < W - 6 and 6 < ty < H - 6:
                tops.append((pr['z0'] + pr['h'], tx, ty, gx, gy))
        tops.sort(key=lambda t: -t[0])
        self.tops = tops
        # aviation lights: tallest, spaced
        av = []
        for h, x, y, gx, gy in tops:
            if all((x - a[0]) ** 2 + (y - a[1]) ** 2 > 40 ** 2 for a in av):
                av.append((x, y, self.rng.randrange(0, 48), h))
            if len(av) >= 26:
                break
        self.avlights = av

    # ------------------------------------------------------------------ highways
    def _highways(self):
        """Elevated decks over real avenues. Each: (name, pts ground (out px), elev(s) per point, lanes)."""
        hw = []
        # A: double-deck along avenue j=4 (screen down-right), ramps down before Halcyon
        a_pts = [tile(i, 4) for i in range(-34, 19)]
        a_pts = [p for p in a_pts if p[1] > -40]
        n = len(a_pts)
        lo = [18.0] * n
        hi = [34.0] * n
        for k in range(n):
            u = (k - (n - 11)) / 10.0
            if u > 0:
                lo[k] = 18.0 * (1 - ss(u))
                hi[k] = 34.0 * (1 - ss(min(1, u * 1.15)))
        hw.append(dict(name='A_low', pts=a_pts, elev=lo, w=11.0, seed=1, rail=(255, 70, 190), cut=n - 1))
        hw.append(dict(name='A_high', pts=a_pts[:n - 8], elev=hi[:n - 8], w=10.0, seed=2, rail=(80, 220, 255), cut=n - 9))
        # B: single high deck along avenue i=6 (screen down-left)
        b_pts = [tile(6, j) for j in range(-60, 60)]
        b_pts = [p for p in b_pts if -40 < p[0] < W + 40 and -40 < p[1] < H + 60]
        b_pts = [p for p in b_pts if p[0] > 300]
        n = len(b_pts)
        el = [52.0] * n
        for k in range(n):
            u = (k - (n - 9)) / 8.0
            if u > 0:
                el[k] = 52.0 * (1 - ss(u))
        hw.append(dict(name='B', pts=b_pts, elev=el, w=12.0, seed=3, rail=(255, 196, 60), cut=n - 1))
        for h in hw:
            h['deck'] = [(x, y - e) for (x, y), e in zip(h['pts'], h['elev'])]
            h['len'] = _plen(h['deck'])
        self.highways = hw

    def _flylanes(self):
        """Upper sky lanes for flying cars (altitude in out px over a ground avenue)."""
        fl = []
        p1 = [tile(i, -9) for i in range(-40, 60)]
        fl.append(dict(pts=[(x, y - 92) for x, y in p1], seed=11, col=(120, 230, 255)))
        p2 = [tile(21, j) for j in range(-70, 60)]
        fl.append(dict(pts=[(x, y - 120) for x, y in p2], seed=12, col=(255, 120, 220)))
        p3 = [tile(i, 20) for i in range(-60, 60)]
        fl.append(dict(pts=[(x, y - 70) for x, y in p3], seed=13, col=(255, 210, 120)))
        for f in fl:
            f['pts'] = [p for p in f['pts'] if -60 < p[0] < W + 60 and -60 < p[1] < H + 60]
            f['len'] = _plen(f['pts'])
        self.flylanes = fl

    def _billboards(self):
        labels = self.label_boxes()
        bb = []
        rng = random.Random(77)
        for h, x, y, gx, gy in self.tops[:400]:
            if h < 110 or y < 40 or y > H - 40 or x < 30 or x > W - 30:
                continue
            if any(l[0] - 30 < x < l[2] + 30 and l[1] - 40 < y < l[3] + 30 for l in labels):
                continue
            if all((x - b['x']) ** 2 + (y - b['y']) ** 2 > 140 ** 2 for b in bb):
                bb.append(dict(x=x, y=y, side=rng.choice((-1, 1)), w=rng.uniform(36, 48), h=rng.uniform(22, 28),
                               hue=len(bb), seed=rng.randrange(1 << 30), ph=rng.randrange(48)))
            if len(bb) >= 8:
                break
        pal = [(255, 60, 200), (60, 230, 255), (255, 170, 40), (170, 110, 255), (255, 80, 110), (90, 255, 210),
               (255, 120, 60), (120, 170, 255)]
        for b in bb:
            b['col'] = pal[b['hue'] % len(pal)]
            b['tex'] = [_billboard_tex(b['seed'] + 31 * k, b['col']) for k in range(3)]
        self.billboards = bb

    def _vents(self):
        rng = random.Random(5)
        v = []
        tries = 0
        while len(v) < 9 and tries < 4000:
            tries += 1
            ax, k, run = rng.choice(self.lines)
            x, y, _ = rng.choice(run)
            if 40 < x < W - 40 and 60 < y < H - 20 and self.vis(x, y) and \
                    all((x - a[0]) ** 2 + (y - a[1]) ** 2 > 90 ** 2 for a in v):
                v.append((x, y, rng.random()))
        # plus three rooftop vents
        for h, x, y, gx, gy in self.tops[200:600:37]:
            if len(v) >= 13:
                break
            v.append((x, y, rng.random()))
        self.vents = v

    def _fog_field(self):
        rng = np.random.default_rng(9)
        self.fog_drift = 140
        fw, fh = W + 2 * self.fog_drift, H
        acc = np.zeros((fh, fw), np.float32)
        for sc, amp in ((110, 1.0), (55, 0.5), (28, 0.25), (14, 0.12)):
            g = rng.random((fh // sc + 3, fw // sc + 3)).astype(np.float32)
            im = Image.fromarray((g * 255).astype(np.uint8)).resize(((fw // sc + 3) * sc, (fh // sc + 3) * sc),
                                                                    Image.BICUBIC)
            acc += np.asarray(im, np.float32)[:fh, :fw] / 255 * amp
        acc /= 1.87
        self.fog_noise = acc
        # keep districts readable: thin the fog round the territory labels / HQs
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        keep = np.ones((H, W), np.float32)
        for t in self.d['territories']:
            x, y = P(*t['screen'])
            y -= 60
            r = np.sqrt(((xx - x) / 150) ** 2 + ((yy - y) / 90) ** 2)
            keep = np.minimum(keep, 0.3 + 0.7 * np.clip(r - 0.4, 0, 1))
        self.fog_keep = keep

    def _rain(self):
        rng = random.Random(3)
        self.drops = [(rng.uniform(0, W * SS), rng.uniform(0, H * SS), rng.choice((3, 4, 5)), rng.uniform(14, 26),
                       rng.randint(55, 105)) for _ in range(1300)]
        self.drops_near = [(rng.uniform(0, W * SS), rng.uniform(0, H * SS), rng.choice((2, 3)), rng.uniform(40, 60),
                            rng.randint(40, 70)) for _ in range(110)]

    def label_boxes(self):
        out = []
        f = font(int(40 * S / 0.633))
        for t in self.d['territories']:
            x, y = P(*t['screen'])
            y -= 120 * S / 0.633
            out.append((x - 80, y - 16, x + 80, y + 16))
        return out

    # ------------------------------------------------------------------ frame
    def frame(self, f, N, extra=None, opts=None):
        """Render frame f of an N-frame loop. extra(scene, layers, f, N) draws event layers."""
        o = dict(traffic=True, highways=True, fly=True, holo=True, steam=True, avl=True, fog=True, rain=self.night,
                 tilt=True, labels=True, fog_drift=True)
        if opts:
            o.update(opts)
        t = (f % N) / N
        img = self.base2.copy()
        over = ImageDraw.Draw(img, 'RGBA')
        add = Image.new('RGB', img.size, (0, 0, 0))
        addd = ImageDraw.Draw(add, 'RGBA')
        L = dict(img=img, over=over, add=add, addd=addd)
        if o['highways']:
            self.draw_highways(over, addd, t, structure=True)
        if o['traffic']:
            self.draw_traffic(over, addd, t)
        if o['highways']:
            self.draw_highways(over, addd, t, structure=False)
        if o['avl']:
            self.draw_avlights(addd, f)
        if o['holo']:
            self.draw_billboards(img, add, addd, f)
        if extra:
            extra(self, L, f, 'ground')
        img = _add_bloom(img, add, 1.0 if self.night else 0.75)
        arr = np.asarray(img, np.float32)
        if o['steam']:
            arr = self.apply_steam(arr, t)
        dens = None
        if o['fog']:
            arr, dens = self.apply_fog(arr, t if o['fog_drift'] else 0.0)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        over = ImageDraw.Draw(img, 'RGBA')
        add = Image.new('RGB', img.size, (0, 0, 0))
        addd = ImageDraw.Draw(add, 'RGBA')
        L = dict(img=img, over=over, add=add, addd=addd)
        if o['fly']:
            self.draw_flyers(over, addd, t)
        if extra:
            extra(self, L, f, 'air')
        img = _add_bloom(img, add, 1.0)
        if o['rain']:
            img = self.apply_rain(img, t)
        img = img.resize((W, H), Image.LANCZOS)
        if o['tilt']:
            img = self.tilt(img, dens)
        if o['labels']:
            img = self.labels(img)
        if extra:
            L1 = dict(img=img, over=ImageDraw.Draw(img, 'RGBA'))
            extra(self, L1, f, 'ui')
        return img

    # ------------------------------------------------------------------ layers
    def draw_traffic(self, over, addd, t):
        rng = random.Random(41)
        for ax, k, run in self.lines:
            pts = [(x, y) for x, y, _ in run]
            Ln = _plen(pts)
            dens = sum(r[2] for r in run) / len(run)
            for lane in (-1, 1):
                gap = rng.uniform(8, 13) / max(0.35, dens)
                m = rng.choice((1, 2, 2, 3))
                n = int(Ln / gap)
                if n < 1:
                    continue
                gap = Ln / n
                s0 = rng.uniform(0, gap)
                speed = m * gap
                for c in range(n):
                    s = (s0 + c * gap + lane * t * speed) % Ln
                    x, y, dx, dy = _at(pts, s)
                    nx, ny = -dy, dx
                    x += nx * lane * 1.1
                    y += ny * lane * 1.1
                    if not self.vis(x, y):
                        continue
                    if self.night:
                        head = (255, 236, 200) if lane > 0 else (255, 46, 60)
                        tl = 5.0
                        bx, by = x - dx * tl * lane, y - dy * tl * lane
                        addd.line([(bx * SS, by * SS), (x * SS, y * SS)], fill=head + (110,), width=2)
                        addd.ellipse([x * SS - 1.6, y * SS - 1.6, x * SS + 1.6, y * SS + 1.6], fill=head + (255,))
                    else:
                        col = rng.choice(((236, 232, 220), (250, 200, 40), (200, 40, 40), (60, 70, 90),
                                          (180, 190, 200)))
                        over.line([((x - dx * 1.4) * SS, (y - dy * 1.4) * SS), ((x + dx * 1.4) * SS,
                                                                                  (y + dy * 1.4) * SS)],
                                  fill=col + (255,), width=3)

    def draw_highways(self, over, addd, t, structure):
        night = self.night
        for h in self.highways:
            deck, pts, el = h['deck'], h['pts'], h['elev']
            w = h['w']
            if structure:
                # pylons, every 3 tiles where the deck is up
                for k in range(0, len(pts), 3):
                    if el[k] < 4:
                        continue
                    gx, gy = pts[k]
                    dx, dy = deck[k]
                    if self.vis(gx, gy):
                        pc = (24, 22, 34) if night else (96, 92, 98)
                        over.polygon([((gx - 1.4) * SS, gy * SS), ((gx + 1.4) * SS, gy * SS),
                                      ((dx + 1.6) * SS, (dy + 2) * SS), ((dx - 1.6) * SS, (dy + 2) * SS)], fill=pc + (255,))
                        over.line([((gx + 1.4) * SS, gy * SS), ((dx + 1.6) * SS, (dy + 2) * SS)],
                                  fill=(8, 8, 12, 255), width=1)
                # shadow on ground (day only)
                if not night:
                    for k in range(len(pts) - 1):
                        a, b = pts[k], pts[k + 1]
                        nx, ny = _norm(b[0] - a[0], b[1] - a[1])
                        px, py = -ny * w * 0.55, nx * w * 0.55
                        sh = [(a[0] + px + 6, a[1] + py + 3), (b[0] + px + 6, b[1] + py + 3),
                              (b[0] - px + 6, b[1] - py + 3), (a[0] - px + 6, a[1] - py + 3)]
                        over.polygon([(x * SS, y * SS) for x, y in sh], fill=(30, 26, 40, 46))
                # deck slabs
                for k in range(len(deck) - 1):
                    a, b = deck[k], deck[k + 1]
                    nx, ny = _norm(b[0] - a[0], b[1] - a[1])
                    px, py = -ny * w * 0.5, nx * w * 0.5
                    if py < 0:
                        px, py = -px, -py
                    th = 4.5
                    top = [(a[0] - px, a[1] - py), (b[0] - px, b[1] - py), (b[0] + px, b[1] + py), (a[0] + px, a[1] + py)]
                    side = [(a[0] + px, a[1] + py), (b[0] + px, b[1] + py), (b[0] + px, b[1] + py + th),
                            (a[0] + px, a[1] + py + th)]
                    if night:
                        over.polygon([(x * SS, y * SS) for x, y in side], fill=(12, 10, 20, 255))
                        over.polygon([(x * SS, y * SS) for x, y in top], fill=(34, 30, 52, 255))
                    else:
                        over.polygon([(x * SS, y * SS) for x, y in side], fill=(70, 66, 74, 255))
                        over.polygon([(x * SS, y * SS) for x, y in top], fill=(128, 124, 120, 255))
                    over.line([(top[3][0] * SS, top[3][1] * SS), (top[2][0] * SS, top[2][1] * SS)],
                              fill=(6, 5, 10, 255), width=2)
                    over.line([(side[3][0] * SS, side[3][1] * SS), (side[2][0] * SS, side[2][1] * SS)],
                              fill=(6, 5, 10, 255), width=2)
                    # lit rails
                    rc = h['rail']
                    a_ = 210 if night else 120
                    addd.line([(top[0][0] * SS, top[0][1] * SS), (top[1][0] * SS, top[1][1] * SS)], fill=rc + (a_ // 2,),
                              width=2)
                    addd.line([(top[3][0] * SS, (top[3][1] + 0.6) * SS), (top[2][0] * SS, (top[2][1] + 0.6) * SS)],
                              fill=rc + (a_,), width=2)
                    # lane divider
                    if night:
                        over.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=(70, 64, 96, 255), width=1)
                    else:
                        over.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=(220, 214, 190, 255), width=1)
            else:
                rng = random.Random(h['seed'] * 101)
                Ln = h['len']
                for lane in (-1.6, -0.6, 0.6, 1.6):
                    d = 1 if lane > 0 else -1
                    n = rng.randint(14, 22)
                    gap = Ln / n
                    m = rng.choice((2, 3, 3, 4))
                    s0 = rng.uniform(0, gap)
                    for c in range(n):
                        if rng.random() < 0.18:
                            continue
                        s = (s0 + c * gap + d * t * m * gap) % Ln
                        x, y, dx, dy = _at(deck, s)
                        nx, ny = -dy, dx
                        if ny < 0:
                            nx, ny = -nx, -ny
                        x += nx * lane * w * 0.22
                        y += ny * lane * w * 0.22
                        if night:
                            col = (255, 240, 210) if d > 0 else (255, 40, 54)
                            tl = 9 if d > 0 else 7
                            bx, by = x - dx * tl * d, y - dy * tl * d
                            addd.line([(bx * SS, by * SS), (x * SS, y * SS)], fill=col + (120,), width=2)
                            addd.ellipse([x * SS - 2, y * SS - 2, x * SS + 2, y * SS + 2], fill=col + (255,))
                        else:
                            col = rng.choice(((240, 236, 226), (250, 196, 30), (210, 50, 44), (50, 60, 84),
                                              (170, 180, 196), (90, 160, 210)))
                            over.line([((x - dx * 2) * SS, (y - dy * 2) * SS), ((x + dx * 2) * SS, (y + dy * 2) * SS)],
                                      fill=(16, 14, 20, 255), width=5)
                            over.line([((x - dx * 1.7) * SS, (y - dy * 1.7) * SS),
                                       ((x + dx * 1.7) * SS, (y + dy * 1.7) * SS)], fill=col + (255,), width=3)

    def draw_flyers(self, over, addd, t):
        night = self.night
        for fl in self.flylanes:
            pts, Ln = fl['pts'], fl['len']
            rng = random.Random(fl['seed'])
            # floating lane markers: chase lights
            nm = int(Ln / 26)
            for k in range(nm):
                s = k * Ln / nm
                x, y, dx, dy = _at(pts, s)
                ph = (k / 6.0 - t * 8) % 1.0
                a = int((60 + 160 * max(0, 1 - ph * 4)) * (1 if night else 0.55))
                addd.ellipse([x * SS - 1.6, y * SS - 1.6, x * SS + 1.6, y * SS + 1.6], fill=fl['col'] + (a,))
            for lane in (-1, 1):
                n = rng.randint(3, 5)
                gap = Ln / n
                s0 = rng.uniform(0, gap)
                m = rng.choice((2, 3))
                for c in range(n):
                    s = (s0 + c * gap + lane * t * m * gap) % Ln
                    x, y, dx, dy = _at(pts, s)
                    y += lane * 4
                    bob = math.sin(2 * math.pi * (t * 2 + c * 0.37)) * 0.8
                    y += bob
                    tl = 26
                    for q in range(6):
                        u0, u1 = q / 6, (q + 1) / 6
                        ax_, ay_ = x - dx * tl * u0 * lane, y - dy * tl * u0 * lane
                        bx_, by_ = x - dx * tl * u1 * lane, y - dy * tl * u1 * lane
                        addd.line([(ax_ * SS, ay_ * SS), (bx_ * SS, by_ * SS)],
                                  fill=fl['col'] + (int((150 if night else 90) * (1 - u0)),), width=3)
                    # body
                    bw = 3.4
                    body = [(x + dx * bw, y + dy * bw), (x - dy * 1.6, y + dx * 1.6 - 1.2), (x - dx * bw, y - dy * bw),
                            (x + dy * 1.6, y - dx * 1.6 - 1.2)]
                    over.polygon([(px * SS, py * SS) for px, py in body], fill=(14, 12, 20, 255) if night else
                                 (40, 38, 50, 255))
                    addd.ellipse([(x + dx * bw * lane) * SS - 2.2, (y + dy * bw * lane) * SS - 2.2,
                                  (x + dx * bw * lane) * SS + 2.2, (y + dy * bw * lane) * SS + 2.2],
                                 fill=(255, 250, 235, 255))
                    # under-glow
                    addd.ellipse([x * SS - 5, (y + 1) * SS - 2.5, x * SS + 5, (y + 1) * SS + 2.5],
                                 fill=fl['col'] + (90,))

    def draw_avlights(self, addd, f):
        for k, (x, y, ph, h) in enumerate(self.avlights):
            per = 24
            on = ((f + ph) % per) < 3
            if k == 0:
                on = ((f + ph) % 16) in (0, 2)
                col = (255, 255, 255)
            else:
                col = (255, 40, 40)
            if on:
                r = 3.2 if k else 4.2
                addd.ellipse([x * SS - r * 3, y * SS - r * 3, x * SS + r * 3, y * SS + r * 3], fill=col + (60,))
                addd.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=col + (255,))
            else:
                addd.ellipse([x * SS - 1.4, y * SS - 1.4, x * SS + 1.4, y * SS + 1.4], fill=col + (70,))

    def draw_billboards(self, img, add, addd, f):
        night = self.night
        for b in self.billboards:
            per = 16
            ff = f + b['ph']
            k = (ff // per) % 3
            u = (ff % per) / per
            tex = b['tex'][k]
            # flicker: occasional dropout and jitter (seeded per frame)
            r = random.Random(b['seed'] + ff * 7)
            alpha = 0.85 if night else 0.62
            if r.random() < 0.08:
                alpha *= 0.25
            jit = (r.random() - 0.5) * 2.0 if r.random() < 0.15 else 0.0
            if u < 0.12:                           # wipe-in of the new panel
                tex = _wipe(tex, u / 0.12)
            x, y, w, h = b['x'] + jit, b['y'] - 5, b['w'], b['h']
            side = b['side']
            ux, uy = w * 0.894, side * w * 0.447
            o = (x - ux / 2, y - uy / 2 - 6)
            v = (0, -h)
            # projector beam
            addd.polygon([(x * SS, (y + 1) * SS), (o[0] * SS, o[1] * SS), ((o[0] + ux) * SS, (o[1] + uy) * SS)],
                         fill=b['col'] + (int(34 * alpha),))
            _paste_affine(add, tex, (o[0] * SS, o[1] * SS), (ux * SS, uy * SS), (v[0] * SS, v[1] * SS), alpha)
            addd.ellipse([x * SS - 2, y * SS - 2, x * SS + 2, y * SS + 2], fill=b['col'] + (255,))

    def apply_steam(self, arr, t):
        m = Image.new('L', (W * SS, H * SS), 0)
        d = ImageDraw.Draw(m)
        for vx, vy, ph in self.vents:
            for q in range(7):
                age = (t * 2 + ph + q / 7.0) % 1.0
                x = vx + age * 16 + math.sin((age + ph) * 9) * 2
                y = vy - age * 34
                r = 2 + age * 9
                a = int(150 * (1 - age) * min(1, age * 6))
                d.ellipse([(x - r) * SS, (y - r * 0.8) * SS, (x + r) * SS, (y + r * 0.8) * SS], fill=a)
        m = m.filter(ImageFilter.GaussianBlur(5))
        a = np.asarray(m, np.float32)[..., None] / 255.0
        col = np.array((176, 160, 220) if self.night else (236, 232, 226), np.float32)
        return arr * (1 - a * 0.8) + col * a * 0.8

    def fog_density(self, t):
        D = self.fog_drift
        n = self.fog_noise
        o1 = int(round(D + D * t))
        o2 = int(round(D + D * (t - 1)))
        g = (1 - t) * n[:, o1:o1 + W] + t * n[:, o2:o2 + W]
        dens = smooth(0.58, 0.80, g) * 0.6 + 0.03
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        dens = dens * (0.8 + 0.3 * (1 - yy))     # thicker far away (top)
        return np.clip(dens * self.fog_keep, 0, 1)

    def apply_fog(self, arr, t):
        dens = self.fog_density(t)
        d2 = np.asarray(Image.fromarray((dens * 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BILINEAR),
                        np.float32)[..., None] / 255
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        bl = np.asarray(img.filter(ImageFilter.GaussianBlur(5)), np.float32)
        glow = np.asarray(img.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
                          .resize((W * SS, H * SS), Image.BILINEAR), np.float32)
        arr = arr * (1 - np.minimum(1, d2 * 1.3)) + bl * np.minimum(1, d2 * 1.3)
        if self.night:
            fc = np.array((40, 34, 84), np.float32) + glow * 0.8
            a = d2 * 0.44
        else:
            fc = np.array((214, 208, 196), np.float32) * 0.8 + glow * 0.25
            a = d2 * 0.44
        return arr * (1 - a) + fc * a, dens

    def apply_rain(self, img, t):
        lay = Image.new('RGB', img.size, (0, 0, 0))
        d = ImageDraw.Draw(lay, 'RGBA')
        HH = H * SS
        for x0, y0, k, ln, a in self.drops:
            y = (y0 + t * k * HH) % HH
            x = (x0 - t * k * HH * 0.18) % (W * SS)
            d.line([(x, y), (x + ln * 0.18, y - ln)], fill=(170, 190, 255, a), width=1)
        for x0, y0, k, ln, a in self.drops_near:
            y = (y0 + t * k * HH) % HH
            x = (x0 - t * k * HH * 0.18) % (W * SS)
            d.line([(x, y), (x + ln * 0.18, y - ln)], fill=(200, 210, 255, a), width=3)
        # splashes on visible ground, re-seeded per frame step
        r = random.Random(int(t * 1000))
        for _ in range(160):
            ax, kk, run = r.choice(self.lines)
            x, y, _ = r.choice(run)
            x += r.uniform(-4, 4)
            if self.vis(x, y):
                d.ellipse([x * SS - 2, y * SS - 1, x * SS + 2, y * SS + 1], fill=(200, 215, 255, 120))
        a = np.asarray(img, np.float32) + np.asarray(lay, np.float32) * 0.9
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    def tilt_mask(self, dens=None):
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32)
        m = np.clip((0.26 - yy) / 0.26, 0, 1) ** 1.3 + 0.7 * np.clip((yy - 0.84) / 0.16, 0, 1) ** 1.5
        if dens is not None:
            m = np.maximum(m, dens * 0.45)
        return np.clip(m, 0, 1)

    def tilt(self, img, dens):
        m = self.tilt_mask(dens)[..., None]
        a = np.asarray(img, np.float32)
        b1 = np.asarray(img.filter(ImageFilter.GaussianBlur(1.4)), np.float32)
        b2 = np.asarray(img.filter(ImageFilter.GaussianBlur(3.2)), np.float32)
        m1 = np.clip(m * 2, 0, 1)
        m2 = np.clip(m * 2 - 1, 0, 1)
        out = a * (1 - m1) + b1 * m1
        out = out * (1 - m2) + b2 * m2
        # gentle haze toward the top (distance), stronger by day
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        hz = np.clip((0.3 - yy) / 0.3, 0, 1) * (0.1 if self.night else 0.2)
        hc = np.array((40, 34, 80) if self.night else (226, 220, 206), np.float32)
        out = out * (1 - hz) + hc * hz
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    def labels(self, img):
        d = ImageDraw.Draw(img)
        k = S / 0.633 * 1.0
        f = font(int(40 * k * 1.0))
        names = {'': 'THE SPRAWL', 'solace': 'SOLACE', 'meridian': 'MERIDIAN', 'halcyon': 'HALCYON',
                 'orbital': 'ORBITAL', 'rebel_cell': 'REBEL_CELL'}
        for t in self.d['territories']:
            x, y = P(*t['screen'])
            y -= 120 * k
            if not (0 < x < W and 0 < y < H):
                continue
            col = tuple(int(round(max(0, min(1, v)) * 255)) for v in t['color'][:3])
            s = names[t['id']]
            tw = d.textlength(s, font=f)
            x0, y0 = x - tw / 2 - 24 * k, y - 30 * k
            x1, y1 = x + tw / 2 + 24 * k, y + 30 * k
            d.polygon([(x0 + 8 * k, y0), (x1, y0), (x1 - 8 * k, y1), (x0, y1)], fill=(10, 9, 16))
            d.polygon([(x0 + 8 * k, y0), (x0 + 20 * k, y0), (x0 + 12 * k, y1), (x0, y1)], fill=col)
            d.text((x + 6 * k, y), s, font=f, fill=col, anchor='mm')
        return img


# ---------------------------------------------------------------------- helpers
def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def _norm(x, y):
    l = math.hypot(x, y) or 1.0
    return x / l, y / l


def _plen(pts):
    return sum(math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1]) for k in range(len(pts) - 1))


def _at(pts, s):
    """Point and unit direction at arc length s along a polyline."""
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        l = math.hypot(b[0] - a[0], b[1] - a[1])
        if s <= l or k == len(pts) - 2:
            u = s / l if l else 0
            dx, dy = _norm(b[0] - a[0], b[1] - a[1])
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, dx, dy
        s -= l
    return pts[-1][0], pts[-1][1], 1.0, 0.0


def _add_bloom(img, add, k):
    a = np.asarray(img, np.float32)
    s = np.asarray(add, np.float32)
    b = np.asarray(add.filter(ImageFilter.GaussianBlur(7)), np.float32)
    out = a + s * 0.9 + b * 1.3 * k
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def _billboard_tex(seed, col):
    """An illegible hologram ad: glyph rows, a pictogram, frame and scanlines."""
    r = random.Random(seed)
    tw, th = 72, 44
    im = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c2 = tuple(min(255, int(v * 0.5 + 128)) for v in col)
    d.rectangle([0, 0, tw - 1, th - 1], fill=col + (60,), outline=col + (230,), width=2)
    kind = r.randint(0, 3)
    if kind == 0:
        d.ellipse([6, 6, 34, 38], outline=c2 + (255,), width=3)
        d.ellipse([14, 14, 26, 30], fill=col + (255,))
    elif kind == 1:
        d.polygon([(20, 6), (36, 38), (4, 38)], outline=c2 + (255,), fill=col + (140,))
    elif kind == 2:
        for q in range(4):
            d.polygon([(6 + q * 7, 8), (12 + q * 7, 22), (6 + q * 7, 36), (9 + q * 7, 22)], fill=c2 + (255,))
    else:
        for q in range(5):
            hh = r.randint(6, 28)
            d.rectangle([5 + q * 6, 38 - hh, 9 + q * 6, 38], fill=c2 + (255,))
    x = 40
    for row in range(5):
        y = 7 + row * 7
        xx = x
        while xx < tw - 6:
            gw = r.randint(2, 5)
            if r.random() < 0.85:
                d.rectangle([xx, y, xx + gw, y + (4 if row == 0 else 3)], fill=(c2 if row == 0 else col) + (240,))
            xx += gw + 2
    px = im.load()
    for yy in range(0, th, 2):
        for xx in range(tw):
            p = px[xx, yy]
            px[xx, yy] = (p[0], p[1], p[2], p[3] // 2)
    return im


def _wipe(tex, u):
    w, h = tex.size
    out = Image.new('RGBA', tex.size, (0, 0, 0, 0))
    cut = int(h * u)
    out.paste(tex.crop((0, h - cut, w, h)), (0, h - cut))
    d = ImageDraw.Draw(out)
    d.line([(0, h - cut), (w, h - cut)], fill=(255, 255, 255, 255), width=2)
    return out


def _paste_affine(dst, tex, o, u, v, alpha):
    """Paste tex onto dst (RGB, light layer) on the parallelogram o + s*u + r*v (s, r in 0..1), r=0 bottom."""
    xs = [o[0], o[0] + u[0], o[0] + v[0], o[0] + u[0] + v[0]]
    ys = [o[1], o[1] + u[1], o[1] + v[1], o[1] + u[1] + v[1]]
    bx0, by0 = int(min(xs)) - 1, int(min(ys)) - 1
    bx1, by1 = int(max(xs)) + 2, int(max(ys)) + 2
    det = u[0] * v[1] - v[0] * u[1]
    if abs(det) < 1e-6:
        return
    i00, i01 = v[1] / det, -v[0] / det
    i10, i11 = -u[1] / det, u[0] / det
    tw, th = tex.size
    # dest (x, y) local to bbox -> X = x + bx0 ; s = i00*(X-ox) + i01*(Y-oy) ; r = i10*... ; src = (s*tw, (1-r)*th)
    cx, cy = bx0 - o[0], by0 - o[1]
    a = tw * i00
    b = tw * i01
    c = tw * (i00 * cx + i01 * cy)
    dd = -th * i10
    e = -th * i11
    f = th - th * (i10 * cx + i11 * cy)
    w, h = bx1 - bx0, by1 - by0
    if w <= 0 or h <= 0:
        return
    t = tex.transform((w, h), Image.AFFINE, (a, b, c, dd, e, f), resample=Image.BILINEAR)
    al = t.getchannel('A').point(lambda q: int(q * alpha))
    dst.paste(t.convert('RGB'), (bx0, by0), al)


def save_gif(frames, path, ms, colors=255, diff=True, tol=14):
    """One shared palette (sampled from all frames), no dither, unchanged pixels transparent."""
    W_, H_ = frames[0].size
    k = max(1, len(frames) // 12)
    sample = Image.new('RGB', (W_, H_ * len(frames[::k])))
    for n, fr in enumerate(frames[::k]):
        sample.paste(fr, (0, n * H_))
    # two palettes merged: a general median cut + accents cut from the most saturated pixels only,
    # so small neon (lime, amber, cyan, police red/blue) keeps its saturation
    n_acc = 72
    base = sample.quantize(colors - 1 - n_acc, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * (colors - 1 - n_acc)]
    arr = np.asarray(sample, np.int16).reshape(-1, 3)
    sat = arr.max(axis=1) - arr.min(axis=1)
    hot = arr[sat >= np.percentile(sat, 93)]
    side = int(math.sqrt(len(hot))) or 1
    hot = hot[:side * side].reshape(side, side, 3).astype(np.uint8)
    acc = Image.fromarray(hot, 'RGB').quantize(n_acc, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * n_acc]
    pal = base + acc
    pal += [0, 0, 0] * (colors - 1 - len(pal) // 3)
    pal_full = pal + [0, 0, 0] * (256 - colors + 1)
    pimg = Image.new('P', (1, 1))
    pimg.putpalette(pal_full)
    TR = 255
    out = []
    prev = None
    shown = None                          # what the viewer currently sees (RGB), to keep tolerance drift-free
    palarr = np.array(pal_full, np.int16).reshape(256, 3)
    for fr in frames:
        q = fr.quantize(palette=pimg, dither=Image.Dither.NONE)
        a = np.asarray(q).copy()
        if diff and prev is not None:
            rgb = np.asarray(fr, np.int16)
            same = (a == prev) | (np.abs(rgb - shown).max(axis=2) < tol)
            b = a.copy()
            b[same] = TR
            im = Image.fromarray(b, 'P')
            a = np.where(same, prev, a)
        else:
            im = Image.fromarray(a, 'P')
        im.putpalette(pal_full)
        out.append(im)
        prev = a
        shown = palarr[a]
    out[0].save(path, save_all=True, append_images=out[1:], duration=ms, loop=0, transparency=TR, disposal=1,
                optimize=False)
    return os.path.getsize(path)
