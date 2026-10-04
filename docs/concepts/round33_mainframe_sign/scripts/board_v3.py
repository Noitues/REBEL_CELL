"""board.py - round 33 v3: a designed circuit board that is wired to the letters.

One trace style on one 6 px pitch:
  - two power rails (left x=34, right x=216) running the height of the plate;
  - every letter's two electrode ends (leftmost / rightmost open stroke end) get a solder pad, and a
    trace leaves the pad horizontally, makes one 45-degree jog (toward the letter's middle), and lands on
    its rail with a junction via;
  - in each gap between letters a component (alternating resistor / SOT chip) bridges the rails, wired
    to both, owned by the letter above it;
  - a small driver-chip row under the last letter, wired to both rails.
Every trace / pad / component pin has an owner (a letter key, or 'rail'), so its light follows that
letter: lit and pulsing with it, dark copper when the letter is dead.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import modem_sign_r4 as M
from lightpen import gblur

PITCH = 6
RAIL_L, RAIL_R = 34, 216
JOG = 12
TW = 2.2           # trace width
COPPER = np.array([0.30, 0.17, 0.09], np.float32)


def snap(v):
    return round(v / PITCH) * PITCH


class Trace:
    def __init__(self, owner, pts, start_pad=True, end_via=True):
        self.owner = owner
        self.pts = [tuple(map(float, p)) for p in pts]
        self.start_pad, self.end_via = start_pad, end_via
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
    def __init__(self, lets, plate_h=M.PH):
        self.traces, self.resistors, self.chips = [], [], []
        ys = []
        for i, (k, ch, x, y, w, h, W, t, col) in enumerate(lets):
            pl, pr, vl, vr = electrode_ends(ch, x, y, w, h, W)
            for (px, py), v, side in ((pl, vl, -1), (pr, vr, 1)):
                rail = RAIL_L if side < 0 else RAIL_R
                xj = snap(x - 10) if side < 0 else snap(x + w + 10)
                dy = JOG if v < 0.5 else -JOG
                yy = snap(py)
                pts = [(px, py), (px, yy), (xj, yy), (xj + side * JOG, yy + dy), (rail, yy + dy)]
                self.traces.append(Trace(k, pts))
            ys.append((k, y, h))
        for i in range(len(ys) - 1):           # gap components, owned by the letter above
            k, y, h = ys[i]
            gy = snap((y + h + ys[i + 1][1]) / 2)
            cx = M.PW / 2
            if i % 2 == 0:
                self.resistors.append((k, cx, gy))
                a, b = cx - 16, cx + 16
            else:
                self.chips.append((k, cx - 12, gy - 6, 24, 12))
                a, b = cx - 16, cx + 16
            self.traces.append(Trace(k, [(a, gy), (RAIL_L, gy)], start_pad=False))
            self.traces.append(Trace(k, [(b, gy), (RAIL_R, gy)], start_pad=False))
        k, y, h = ys[-1]
        by = snap(y + h + 18)
        ca, cb = M.PW / 2 - 40, M.PW / 2 + 40           # driver-chip row: rail - chip - chip - rail
        for cx in (ca, cb):
            self.chips.append(('rail', cx - 18, by - 7, 36, 14))
        self.traces.append(Trace('rail', [(ca - 22, by), (RAIL_L, by)], start_pad=False))
        self.traces.append(Trace('rail', [(ca + 22, by), (cb - 22, by)], start_pad=False, end_via=False))
        self.traces.append(Trace('rail', [(cb + 22, by), (RAIL_R, by)], start_pad=False))
        top, bot = snap(lets[0][3]) - 6, by
        for rx in (RAIL_L, RAIL_R):
            self.traces.append(Trace('rail', [(rx, top), (rx, bot)], start_pad=True, end_via=True))
        self.owners = sorted({t.owner for t in self.traces} | {r[0] for r in self.resistors} | {c[0] for c in self.chips})
        self._raster()

    # ---------------------------------------------------------------- static masks per owner
    def _raster(self):
        SR = M.SR
        self.tm, self.pm, self.pins = {}, {}, {}
        for o in self.owners:
            tm, pm, pn = M._canvas(), M._canvas(), M._canvas()
            dt, dp, dn = ImageDraw.Draw(tm), ImageDraw.Draw(pm), ImageDraw.Draw(pn)
            for tr in self.traces:
                if tr.owner != o:
                    continue
                pp = [M._P(*q) for q in tr.pts]
                dt.line(pp, fill=255, width=int(TW * SR), joint='curve')
                for q in pp[1:-1]:
                    r = TW * SR / 2
                    dt.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
                if tr.start_pad:      # tube mount: ring pad
                    q = pp[0]
                    r0, r1 = 4.6 * SR, 2.0 * SR
                    dp.ellipse([q[0] - r0, q[1] - r0, q[0] + r0, q[1] + r0], fill=255)
                    dp.ellipse([q[0] - r1, q[1] - r1, q[0] + r1, q[1] + r1], fill=0)
                if tr.end_via:        # junction via on the rail
                    q = pp[-1]
                    r0 = 3.0 * SR
                    dp.ellipse([q[0] - r0, q[1] - r0, q[0] + r0, q[1] + r0], fill=255)
            for (oo, cx, cy) in self.resistors:
                if oo != o:
                    continue
                for sx in (-16, 16):
                    q = M._P(cx + sx, cy)
                    r = 2.6 * SR
                    dn.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
                p0, p1 = M._P(cx - 16, cy), M._P(cx - 10, cy)
                dn.line([p0, p1], fill=255, width=int(1.6 * SR))
                p0, p1 = M._P(cx + 10, cy), M._P(cx + 16, cy)
                dn.line([p0, p1], fill=255, width=int(1.6 * SR))
            for (oo, x, y, w, h) in self.chips:
                if oo != o:
                    continue
                n = max(2, int(w // 8))
                for kk in range(n):
                    px = x + (kk + 0.5) * w / n
                    for yy, sg in ((y, -1), (y + h, 1)):
                        a, b = M._P(px - 1.4, yy), M._P(px + 1.4, yy + sg * 3.5)
                        dn.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=255)
                for yy, sg, xx in ((y + h / 2, 1, x), (y + h / 2, 1, x + w)):
                    a, b = M._P(xx - 4 if xx == x else xx, yy - 1), M._P(xx if xx == x else xx + 4, yy + 1)
                    dn.rectangle([a[0], a[1], b[0], b[1]], fill=255)
            self.tm[o], self.pm[o], self.pins[o] = M._arr(tm), M._arr(pm), M._arr(pn)
        # component bodies (albedo) + small status LED per chip
        body = Image.new('RGB', (M.CW * SR, M.CH * SR), (0, 0, 0))
        am = M._canvas()
        led = {o: M._canvas() for o in self.owners}
        db, da = ImageDraw.Draw(body), ImageDraw.Draw(am)
        for (o, cx, cy) in self.resistors:
            a, b = M._P(cx - 10, cy - 4), M._P(cx + 10, cy + 4)
            db.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=3 * SR, fill=(70, 58, 44))
            da.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=3 * SR, fill=255)
            for bx, col in ((-5, (120, 40, 30)), (-1, (20, 20, 20)), (3, (150, 110, 30)), (7, (160, 140, 90))):
                p0, p1 = M._P(cx + bx, cy - 4), M._P(cx + bx + 1.6, cy + 4)
                db.rectangle([p0[0], p0[1], p1[0], p1[1]], fill=col)
        for (o, x, y, w, h) in self.chips:
            a, b, c, e = M._P(x, y), M._P(x + w, y), M._P(x + w, y + h), M._P(x, y + h)
            db.polygon([a, b, e], fill=(30, 32, 38))
            db.polygon([b, c, e], fill=(18, 19, 24))
            da.polygon([a, b, c, e], fill=255)
            q = M._P(x + 4, y + 4)
            r = 1.4 * SR
            ImageDraw.Draw(led[o]).ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
        self.comp_alb = np.asarray(body.reduce(M.SS), np.float32) / 255.0
        self.comp_m = M._arr(am)
        self.led = {o: gblur(M._arr(m), 0.7) for o, m in led.items()}
        self.copper = sum(self.tm[o] * 0.55 + self.pm[o] * 0.8 for o in self.owners)

    # ---------------------------------------------------------------- per frame
    def pulses(self, owner, t):
        """Data packets running from the rail into the letter (reverse along each trace)."""
        im = M._canvas()
        d = ImageDraw.Draw(im)
        for j, tr in enumerate(self.traces):
            if tr.owner != owner or tr.L < 8:
                continue
            period = tr.L + 40
            p = (t * 110 + j * 37.0) % period
            n = len(tr.dense)
            for dd in np.arange(14, -0.1, -1.0):
                s = p - dd
                if s < 0 or s >= tr.L:
                    continue
                idx = n - 1 - min(n - 1, int(s))
                q = M._P(*tr.dense[idx])
                a = math.exp(-dd / 5.0)
                r = (1.2 + 1.6 * a) * M.SR
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=int(255 * a))
        return M._arr(im)

    def light(self, levels, pulse_t=None):
        """levels: owner -> (level 0..1, rgb colour). Returns (emission, copper glass, component albedo/mask)."""
        emis = np.zeros((M.CH, M.CW, 3), np.float32)
        glass = COPPER[None, None] * self.copper[..., None]
        for o in self.owners:
            lv, col = levels.get(o, (0.0, None))
            if lv <= 0 or col is None:
                continue
            m = self.tm[o] * 0.6 + self.pm[o] * 0.9
            emis += col[None, None] * (m * lv)[..., None]
            emis += col[None, None] * (self.pins[o] * 0.5 * lv)[..., None]
            emis += col[None, None] * (self.led[o] * 2.0 * lv)[..., None]
            glass -= COPPER[None, None] * ((self.tm[o] * 0.55 + self.pm[o] * 0.8) * 0.7 * lv)[..., None]
            if pulse_t is not None and lv > 0.5:
                pu = self.pulses(o, pulse_t)
                emis += (0.55 * col + 0.45)[None, None] * (pu * 1.8 * lv)[..., None]
        return emis, glass
