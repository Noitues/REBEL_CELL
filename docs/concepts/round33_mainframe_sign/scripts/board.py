"""board.py - round 33 v4: a designed circuit board wired to the letters, with more variety.

One coherent style (6 px pitch, 45-degree bends only, round joints, ring pads / filled vias), three trace
weights:
  - POWER  3.4 px: the two rails (left x=34, right x=216);
  - FEED   2.4 px: each letter's two electrode ends -> ring pad -> one 45-degree jog -> rail via;
  - SIGNAL 1.3 px: bus bundles (3-4 parallel traces) fanning from a rail into ICs, test points, LEDs.
Components (seeded, irregular density): SOIC ICs, SOT chips, resistors, ceramic capacitors, crystals,
LEDs (emissive), test points, and a driver-chip row under the last letter.
Every element has an owner (letter key or 'rail'); its light follows that owner: lit + data pulses when the
letter is lit, dark copper when it is dead. dark_boxes() returns the lower box of an A that is lit only as
an 'o' so the caller can black out its legs (tube, glow and wiring) completely.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw

import modem_sign_r4 as M
from lightpen import gblur

PITCH = 6
RAIL_L, RAIL_R = 34, 216
JOG = 12
W_POWER, W_FEED, W_SIG = 3.4, 2.4, 1.3
COPPER = np.array([0.30, 0.17, 0.09], np.float32)


def snap(v):
    return round(v / PITCH) * PITCH


class Trace:
    def __init__(self, owner, pts, width=W_FEED, start='pad', end='via', pulse=True):
        self.owner, self.width, self.start, self.end, self.pulse = owner, width, start, end, pulse
        self.pts = [tuple(map(float, p)) for p in pts]
        seg = [math.dist(a, b) for a, b in zip(self.pts, self.pts[1:])]
        self.L = sum(seg)
        dense = []
        for (a, b), s in zip(zip(self.pts, self.pts[1:]), seg):
            n = max(1, int(s))
            for k in range(n):
                t = k / n
                dense.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        dense.append(self.pts[-1])
        self.dense = dense


def electrode_ends(ch, x, y, w, h, W):
    ends = []
    for st in M.LET[ch]:
        if st[0] == st[-1]:
            continue
        for u, v in (st[0], st[-1]):
            ends.append((u, v))
    left = min(ends, key=lambda e: (e[0], -e[1]))
    right = max(ends, key=lambda e: (e[0], e[1]))

    def P(e):
        return (x + W / 2 + e[0] * (w - W), y + W / 2 + e[1] * (h - W))
    return P(left), P(right), left[1], right[1]


class Board:
    def __init__(self, lets, seed=33):
        rng = random.Random(seed)
        self.lets = lets
        self.traces, self.comps = [], []          # comps: (owner, kind, x, y, w, h)
        ys = []
        for i, (k, ch, x, y, w, h, W, t, col) in enumerate(lets):
            pl, pr, vl, vr = electrode_ends(ch, x, y, w, h, W)
            busy = {-1: [], 1: []}
            for (px, py), v, side in ((pl, vl, -1), (pr, vr, 1)):
                rail = RAIL_L if side < 0 else RAIL_R
                xj = snap(x - 10) if side < 0 else snap(x + w + 10)
                dy = JOG if v < 0.5 else -JOG
                yy = snap(py)
                self.traces.append(Trace(k, [(px, py), (px, yy), (xj, yy), (xj + side * JOG, yy + dy), (rail, yy + dy)]))
                busy[side] += [yy, yy + dy]
            ys.append((k, y, h))
            for side in (-1, 1):                    # side-zone furniture (irregular density)
                lo, hi = y + 2, y + h - 2
                free, cur = [], lo
                for b in sorted(busy[side]):
                    if b - 6 > cur:
                        free.append((cur, b - 6))
                    cur = max(cur, b + 6)
                if hi > cur:
                    free.append((cur, hi))
                a, b = max(free, key=lambda f: f[1] - f[0])
                if b - a < 22:
                    continue
                kind = rng.choice(['ic', 'ic', 'caps', 'tp', 'led', 'xtal', 'none'])
                self._side_item(k, kind, side, a, b, x, w, rng)
        for i in range(len(ys) - 1):                # gap components between letters
            k, y, h = ys[i]
            gy = snap((y + h + ys[i + 1][1]) / 2)
            cx = M.PW / 2
            kind = ['res', 'sot', 'cap2', 'res', 'xtal', 'sot', 'res', 'cap2'][i % 8]
            if kind == 'res':
                self.comps.append((k, 'res', cx - 10, gy - 4, 20, 8))
                pins = (cx - 16, cx + 16)
            elif kind == 'sot':
                self.comps.append((k, 'sot', cx - 12, gy - 6, 24, 12))
                pins = (cx - 16, cx + 16)
            elif kind == 'xtal':
                self.comps.append((k, 'xtal', cx - 11, gy - 4, 22, 8))
                pins = (cx - 16, cx + 16)
            else:
                self.comps.append((k, 'cap', cx - 20, gy - 3, 7, 6))
                self.comps.append((k, 'cap', cx + 13, gy - 3, 7, 6))
                self.traces.append(Trace(k, [(cx - 13, gy), (cx + 13, gy)], W_SIG, start='none', end='none'))
                pins = (cx - 22, cx + 22)
            self.traces.append(Trace(k, [(pins[0], gy), (RAIL_L, gy)], W_FEED, start='none'))
            self.traces.append(Trace(k, [(pins[1], gy), (RAIL_R, gy)], W_FEED, start='none'))
        k, y, h = ys[-1]
        by = snap(y + h + 18)
        ca, cb = M.PW / 2 - 40, M.PW / 2 + 40
        for cx in (ca, cb):
            self.comps.append(('rail', 'ic', cx - 18, by - 7, 36, 14))
        self.traces.append(Trace('rail', [(ca - 22, by), (RAIL_L, by)], W_FEED, start='none'))
        self.traces.append(Trace('rail', [(ca + 22, by), (ca + 30, by), (cb - 30, by), (cb - 22, by)], W_SIG,
                                 start='none', end='none'))
        self.traces.append(Trace('rail', [(cb + 22, by), (RAIL_R, by)], W_FEED, start='none'))
        top, bot = snap(lets[0][3]) - 6, by
        for rx in (RAIL_L, RAIL_R):
            self.traces.append(Trace('rail', [(rx, top), (rx, bot)], W_POWER, start='via', end='via', pulse=False))
        self.owners = sorted({t.owner for t in self.traces} | {c[0] for c in self.comps})
        self._raster()

    def _side_item(self, k, kind, side, a, b, x, w, rng):
        """A small cluster between a rail and the letter, wired with a 45-degree bus bundle."""
        rail = RAIL_L if side < 0 else RAIL_R
        edge = x if side < 0 else x + w
        mid = snap((a + b) / 2)
        cx = (rail + edge) / 2 + side * 2
        if kind == 'ic':                                  # SOIC on a 3-trace bus that jogs 45 degrees
            n = 3 if b - a < 34 else 4
            hgt = n * 6 + 2
            self.comps.append((k, 'soic', cx - 5, mid - hgt / 2, 10, hgt))
            pin_x = cx - 5 if side > 0 else cx + 5         # pins face the rail
            for j in range(n):
                py = mid - hgt / 2 + 4 + j * 6
                ry = py + (6 if (j % 2) else -6) * (1 if rng.random() < 0.5 else 0)
                bend = pin_x - side * 4
                self.traces.append(Trace(k, [(pin_x, py), (bend, py), (bend - side * 4, ry), (rail, ry)],
                                         W_SIG, start='none', end='via' if j == 0 else 'none'))
        elif kind == 'caps':
            for j, dy in enumerate((-6, 6)):
                self.comps.append((k, 'cap', cx - 3, mid + dy - 3, 6, 6))
                self.traces.append(Trace(k, [(cx - side * 3, mid + dy), (rail, mid + dy)], W_SIG, start='none',
                                         end='none'))
        elif kind == 'tp':                                # test points: ring pads on short signal stubs
            for j, dy in enumerate((-8, 0, 8)[:2 + (b - a > 30)]):
                tx = cx + side * (3 + 3 * j)
                self.traces.append(Trace(k, [(tx, mid + dy), (tx - side * 4, mid + dy - 4), (rail, mid + dy - 4)],
                                         W_SIG, start='pad', end='none'))
        elif kind == 'led':
            self.comps.append((k, 'led', cx - 3, mid - 3, 6, 6))
            self.comps.append((k, 'res', cx - 4, mid + 6, 8, 4))
            self.traces.append(Trace(k, [(cx - side * 3, mid), (rail, mid)], W_SIG, start='none', end='via'))
        elif kind == 'xtal':
            self.comps.append((k, 'xtal', cx - 8, mid - 3, 16, 6))
            self.traces.append(Trace(k, [(cx - side * 9, mid), (cx - side * 12, mid - 4), (rail, mid - 4)], W_SIG,
                                     start='none', end='none'))

    # ---------------------------------------------------------------- static masks per owner
    def _raster(self):
        SR = M.SR
        self.tm, self.pm, self.pins, self.led = {}, {}, {}, {}
        body = Image.new('RGB', (M.CW * SR, M.CH * SR), (0, 0, 0))
        am = M._canvas()
        db, da = ImageDraw.Draw(body), ImageDraw.Draw(am)
        for o in self.owners:
            tm, pm, pn, ld = M._canvas(), M._canvas(), M._canvas(), M._canvas()
            dt, dp, dn, dl = ImageDraw.Draw(tm), ImageDraw.Draw(pm), ImageDraw.Draw(pn), ImageDraw.Draw(ld)
            for tr in self.traces:
                if tr.owner != o:
                    continue
                pp = [M._P(*q) for q in tr.pts]
                dt.line(pp, fill=255, width=max(1, int(round(tr.width * SR))), joint='curve')
                r = tr.width * SR / 2
                for q in pp:
                    dt.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
                for kind, q in ((tr.start, pp[0]), (tr.end, pp[-1])):
                    s = 1.0 if tr.width >= W_FEED else 0.7
                    if kind == 'pad':
                        r0, r1 = 4.6 * SR * s, 2.0 * SR * s
                        dp.ellipse([q[0] - r0, q[1] - r0, q[0] + r0, q[1] + r0], fill=255)
                        dp.ellipse([q[0] - r1, q[1] - r1, q[0] + r1, q[1] + r1], fill=0)
                    elif kind == 'via':
                        r0 = (3.4 if tr.width >= W_POWER else 3.0) * SR * s
                        dp.ellipse([q[0] - r0, q[1] - r0, q[0] + r0, q[1] + r0], fill=255)
            for (oo, kind, x, y, w, h) in self.comps:
                if oo != o:
                    continue
                P = M._P
                if kind in ('ic', 'sot', 'soic'):
                    horiz = w >= h
                    n = max(2, int((w if horiz else h) // 6))
                    for kk in range(n):
                        f = (kk + 0.5) / n
                        if horiz:
                            px = x + f * w
                            for yy, sg in ((y, -1), (y + h, 1)):
                                p0, p1 = P(px - 1.2, yy), P(px + 1.2, yy + sg * 3)
                                dn.rectangle([min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])], fill=255)
                        else:
                            py = y + f * h
                            for xx, sg in ((x, -1), (x + w, 1)):
                                p0, p1 = P(xx, py - 1.2), P(xx + sg * 3, py + 1.2)
                                dn.rectangle([min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])], fill=255)
                    a, b, c, e = P(x, y), P(x + w, y), P(x + w, y + h), P(x, y + h)
                    db.polygon([a, b, e], fill=(30, 32, 38))
                    db.polygon([b, c, e], fill=(17, 18, 23))
                    da.polygon([a, b, c, e], fill=255)
                    q = P(x + 2.5, y + 2.5)
                    r = 1.0 * SR
                    db.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(55, 58, 66))   # pin-1 dot
                    if kind == 'ic':
                        q = P(x + w - 4, y + 4)
                        dl.ellipse([q[0] - 1.3 * SR, q[1] - 1.3 * SR, q[0] + 1.3 * SR, q[1] + 1.3 * SR], fill=255)
                elif kind == 'res':
                    a, b = P(x, y), P(x + w, y + h)
                    db.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=min(h, 6) * SR / 2, fill=(74, 60, 44))
                    da.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=min(h, 6) * SR / 2, fill=255)
                    for f, colr in ((0.25, (120, 40, 30)), (0.45, (20, 20, 20)), (0.62, (150, 110, 30)), (0.82, (160, 140, 90))):
                        p0, p1 = P(x + f * w - 0.7, y), P(x + f * w + 0.7, y + h)
                        db.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=colr)
                    for xx in (x - 2, x + w + 2):
                        q = P(xx, y + h / 2)
                        dn.ellipse([q[0] - 1.8 * SR, q[1] - 1.8 * SR, q[0] + 1.8 * SR, q[1] + 1.8 * SR], fill=255)
                elif kind == 'cap':                           # ceramic 0805: tan body, tinned end caps
                    a, b = P(x, y), P(x + w, y + h)
                    db.rectangle([a[0], a[1], b[0], b[1]], fill=(120, 96, 64))
                    da.rectangle([a[0], a[1], b[0], b[1]], fill=255)
                    for xx in (x, x + w - 1.6):
                        p0, p1 = P(xx, y), P(xx + 1.6, y + h)
                        dn.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=255)
                elif kind == 'xtal':                          # HC-49 crystal: silver pill
                    a, b = P(x, y), P(x + w, y + h)
                    db.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=h * SR / 2, fill=(120, 124, 132))
                    da.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=h * SR / 2, fill=255)
                    p0, p1 = P(x + 2, y + 1), P(x + w - 2, y + 2.2)
                    db.rounded_rectangle([p0[0], p0[1], p1[0], p1[1]], radius=SR, fill=(190, 194, 200))
                    for xx in (x - 2, x + w + 2):
                        q = P(xx, y + h / 2)
                        dn.ellipse([q[0] - 1.8 * SR, q[1] - 1.8 * SR, q[0] + 1.8 * SR, q[1] + 1.8 * SR], fill=255)
                elif kind == 'led':
                    a, b = P(x, y), P(x + w, y + h)
                    db.rectangle([a[0], a[1], b[0], b[1]], fill=(60, 60, 64))
                    da.rectangle([a[0], a[1], b[0], b[1]], fill=255)
                    q = P(x + w / 2, y + h / 2)
                    dl.ellipse([q[0] - 2.2 * SR, q[1] - 2.2 * SR, q[0] + 2.2 * SR, q[1] + 2.2 * SR], fill=255)
            self.tm[o], self.pm[o], self.pins[o] = M._arr(tm), M._arr(pm), M._arr(pn)
            self.led[o] = gblur(M._arr(ld), 0.8)
        self.comp_alb = np.asarray(body.reduce(M.SS), np.float32) / 255.0
        self.comp_m = M._arr(am)
        self.copper = sum(self.tm[o] * 0.55 + self.pm[o] * 0.8 for o in self.owners)

    def dark_box(self, key, frac=0.5):
        """Canvas mask (1 inside) of the lower part of a letter: used to black out an A lit only as an o."""
        for (k, ch, x, y, w, h, W, t, col) in self.lets:
            if k == key:
                im = M._canvas()
                a, b = M._P(x - 22, y + h * frac), M._P(x + w + 22, y + h + 8)
                ImageDraw.Draw(im).rectangle([a[0], a[1], b[0], b[1]], fill=255)
                return gblur(M._arr(im), 2.0)
        return None

    # ---------------------------------------------------------------- per frame
    def pulses(self, owner, t):
        im = M._canvas()
        d = ImageDraw.Draw(im)
        for j, tr in enumerate(self.traces):
            if tr.owner != owner or tr.L < 8 or not tr.pulse:
                continue
            speed = 110 if tr.width >= W_FEED else 70
            period = tr.L + 40
            p = (t * speed + j * 37.0) % period
            n = len(tr.dense)
            for dd in np.arange(14, -0.1, -1.0):
                s = p - dd
                if s < 0 or s >= tr.L:
                    continue
                idx = n - 1 - min(n - 1, int(s))
                q = M._P(*tr.dense[idx])
                a = math.exp(-dd / 5.0)
                r = (0.6 * tr.width + 1.4 * a) * M.SR
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=int(255 * a))
        return M._arr(im)

    def light(self, levels, pulse_t=None):
        emis = np.zeros((M.CH, M.CW, 3), np.float32)
        glass = COPPER[None, None] * self.copper[..., None]
        for o in self.owners:
            lv, col = levels.get(o, (0.0, None))
            if lv <= 0 or col is None:
                continue
            m = self.tm[o] * 0.6 + self.pm[o] * 0.9
            emis += col[None, None] * (m * lv)[..., None]
            emis += col[None, None] * (self.pins[o] * 0.5 * lv)[..., None]
            emis += col[None, None] * (self.led[o] * 2.2 * lv)[..., None]
            glass -= COPPER[None, None] * ((self.tm[o] * 0.55 + self.pm[o] * 0.8) * 0.7 * lv)[..., None]
            if pulse_t is not None and lv > 0.5:
                pu = self.pulses(o, pulse_t)
                emis += (0.55 * col + 0.45)[None, None] * (pu * 1.8 * lv)[..., None]
        return emis, glass
