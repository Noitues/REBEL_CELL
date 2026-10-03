"""Round 26: the elevated road network. Highways A + B (round 24, unchanged) plus C, D, E, F and their
interchanges, all on real avenues of city_layout.json:

  A  avenue j=4,  double deck (lower 18, upper 34), ramps to street before the Sprawl centre
  B  avenue i=6,  high deck 52, ramps down by the Cell's turf
  C  avenue j=-5, deck 26: passes UNDER B and UNDER F (flyover crossings at three heights), then
     drops to street level down a 1.75-turn spiral ramp (one-way, down)
  F  avenue i=-10, deck 44: CLOVERLEAF with A (four 270-degree loop ramps between A's lower deck and F)
  D  avenue j=43, deck 20 and E avenue i=17, deck 40: a four-level STACK interchange (four directional
     flyover ramps, two at 58 and two at 74) next to Orbital

Elevations are out px (1x). Every deck is drawn in painter order (low to high, back to front), cars
are drawn with their own deck so upper levels hide lower traffic, and car/rail glow is added only
where that deck is the top one (a coverage buffer of deck elevations)."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw

import cm
from cm import SS, ss, tile


class Road:
    def __init__(self, name, pts, elev, w, rail, oneway=False, seed=0, cars=1.0):
        self.name, self.pts, self.elev, self.w, self.rail = name, pts, elev, w, rail
        self.oneway, self.seed, self.cars = oneway, seed, cars
        self.deck = [(x, y - e) for (x, y), e in zip(pts, elev)]
        self.len = cm._plen(self.deck)


def line_i(i, j0, j1, step=0.5):
    n = int(round(abs(j1 - j0) / step))
    return [tile(i, j0 + (j1 - j0) * k / n) for k in range(n + 1)]


def line_j(j, i0, i1, step=0.5):
    n = int(round(abs(i1 - i0) / step))
    return [tile(i0 + (i1 - i0) * k / n, j) for k in range(n + 1)]


def arc(ci, cj, R, a0, a1, n):
    return [tile(ci + R * math.cos(a0 + (a1 - a0) * k / n), cj + R * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def ramp_ends(n, e, k_in, k_out, lo=0.0):
    """Flat at e, easing to lo over the first k_in and last k_out points."""
    out = []
    for k in range(n):
        v = e
        if k_in and k < k_in:
            v = lo + (e - lo) * ss(k / k_in)
        if k_out and k > n - 1 - k_out:
            v = lo + (e - lo) * ss((n - 1 - k) / k_out)
        out.append(v)
    return out


def bump(n, e0, e1, peak):
    """Ramp elevation from e0 to e1 rising to about peak in the middle."""
    out = []
    for k in range(n):
        u = k / (n - 1)
        base = e0 + (e1 - e0) * ss(u)
        out.append(base + (peak - max(e0, e1)) * math.sin(math.pi * u))
    return out


def quarter_ramp(i0, j0, si, sj, R, e0, e1, peak, n=22):
    """Directional ramp from the j-avenue (j0) to the i-avenue (i0) through quadrant (si, sj)."""
    ci, cj = i0 + si * R, j0 + sj * R
    a0 = math.atan2(-sj, 0)            # tangent point on the j-avenue: (ci, j0)
    a1 = math.atan2(0, -si)            # tangent point on the i-avenue: (i0, cj)
    d = (a1 - a0) % (2 * math.pi)
    if d > math.pi:
        d -= 2 * math.pi
    pts = arc(ci, cj, R, a0, a0 + d, n)
    return pts, bump(len(pts), e0, e1, peak)


def loop_ramp(i0, j0, si, sj, r, e0, e1, n=34):
    """Cloverleaf loop: 270 degrees in quadrant (si, sj), tangent to both avenues."""
    ci, cj = i0 + si * r, j0 + sj * r
    a0 = math.atan2(-sj, 0)
    a1 = math.atan2(0, -si)
    d = (a1 - a0) % (2 * math.pi)
    if d < math.pi:
        d -= 2 * math.pi               # go the long way round
    pts = arc(ci, cj, r, a0, a0 + d, n)
    el = [e0 + (e1 - e0) * ss(k / (len(pts) - 1)) for k in range(len(pts))]
    return pts, el


def clip(pts, el, pad=50):
    keep = [k for k, (x, y) in enumerate(pts) if -pad < x < cm.W + pad and -pad - 80 < y - el[k] and y < cm.H + pad]
    if not keep:
        return [], []
    a, b = keep[0], keep[-1]
    return pts[a:b + 1], el[a:b + 1]


class Network:
    def __init__(self, scene):
        self.s = scene
        R = []
        night = scene.night
        PINK, CYAN, AMBER, VIOL, MINT, ORNG = (255, 70, 190), (80, 220, 255), (255, 196, 60), (170, 120, 255), \
            (90, 255, 200), (255, 120, 60)
        # ---- A (round 24) double deck along j=4
        a_pts = [tile(i, 4) for i in range(-34, 19)]
        a_pts = [p for p in a_pts if p[1] > -40]
        n = len(a_pts)
        lo = ramp_ends(n, 18.0, 0, 10)
        hi = ramp_ends(n - 8, 34.0, 0, 9)
        R.append(Road('A_low', a_pts, lo, 11.0, PINK, seed=1))
        R.append(Road('A_high', a_pts[:n - 8], hi, 10.0, CYAN, seed=2))
        # ---- B (round 24) along i=6
        b_pts = [tile(6, j) for j in range(-60, 60)]
        b_pts = [p for p in b_pts if -40 < p[0] < cm.W + 40 and -40 < p[1] < cm.H + 60 and p[0] > 300]
        R.append(Road('B', b_pts, ramp_ends(len(b_pts), 52.0, 0, 8), 12.0, AMBER, seed=3))
        # ---- C along j=-5 at 26, then the spiral down to street level
        c_pts = line_j(-5, -22, 14)
        c_el = [26.0] * len(c_pts)
        Rs = 2.4
        sp = arc(14, -5 + Rs, Rs, -math.pi / 2, -math.pi / 2 + 3.5 * math.pi, 64)
        sp_el = [26.0 * (1 - k / (len(sp) - 1)) for k in range(len(sp))]
        pts, el = clip(c_pts, c_el)
        R.append(Road('C', pts, el, 10.0, MINT, seed=4))
        R.append(Road('C_spiral', sp, sp_el, 7.0, MINT, oneway=True, seed=5, cars=0.8))
        self.spiral_c = tile(14, -5 + Rs)
        # ---- F along i=-10 at 44, cloverleaf with A's lower deck at (i=-10, j=4)
        f_pts = line_i(-10, -16, 22)
        f_el = ramp_ends(len(f_pts), 44.0, 0, 10)
        pts, el = clip(f_pts, f_el)
        R.append(Road('F', pts, el, 11.0, VIOL, seed=6))
        for q, (si, sj) in enumerate(((1, 1), (-1, -1), (1, -1), (-1, 1))):
            p, e = loop_ramp(-10, 4, si, sj, 2.1, 18.0, 44.0)
            R.append(Road('clover_%d' % q, p, e, 6.0, VIOL, oneway=True, seed=20 + q, cars=0.7))
        self.clover_c = tile(-10, 4)
        # ---- D along j=43 at 20 and E along i=17 at 40: four-level stack at (17, 43)
        d_pts = line_j(43, -8, 29)
        d_el = ramp_ends(len(d_pts), 20.0, 0, 9)
        pts, el = clip(d_pts, d_el)
        R.append(Road('D', pts, el, 11.0, ORNG, seed=7))
        e_pts = line_i(17, 31, 64)
        e_el = ramp_ends(len(e_pts), 40.0, 8, 0)
        pts, el = clip(e_pts, e_el)
        R.append(Road('E', pts, el, 11.0, CYAN, seed=8))
        for q, (si, sj, pk, rad) in enumerate(((1, 1, 84, 7.5), (-1, -1, 84, 7.5), (1, -1, 62, 5.0), (-1, 1, 62, 5.0))):
            p, e = quarter_ramp(17, 43, si, sj, rad, 20.0, 40.0, pk, n=30)
            R.append(Road('stack_%d' % q, p, e, 6.5, PINK if pk > 70 else AMBER, oneway=True, seed=30 + q, cars=0.8))
        self.stack_c = tile(17, 43)
        self.roads = R
        self._segments()
        self._coverage()

    def _segments(self):
        segs = []
        for r in self.roads:
            for k in range(len(r.pts) - 1):
                em = (r.elev[k] + r.elev[k + 1]) / 2
                gy = (r.pts[k][1] + r.pts[k + 1][1]) / 2
                segs.append((round(em / 3.0), gy, r, k))
        segs.sort(key=lambda s: (s[0], s[1]))
        self.segs = segs

    def _quad(self, r, k):
        a, b = r.deck[k], r.deck[k + 1]
        nx, ny = cm._norm(b[0] - a[0], b[1] - a[1])
        px, py = -ny * r.w * 0.5, nx * r.w * 0.5
        if py < 0:
            px, py = -px, -py
        # slight overlap so curved strips have no seams
        ex, ey = (b[0] - a[0]) * 0.08, (b[1] - a[1]) * 0.08
        a = (a[0] - ex, a[1] - ey)
        b = (b[0] + ex, b[1] + ey)
        top = [(a[0] - px, a[1] - py), (b[0] - px, b[1] - py), (b[0] + px, b[1] + py), (a[0] + px, a[1] + py)]
        return top, (px, py)

    def _coverage(self):
        img = Image.new('I', (cm.W * SS, cm.H * SS), -1000)
        d = ImageDraw.Draw(img)
        for _, gy, r, k in self.segs:
            top, _ = self._quad(r, k)
            em = (r.elev[k] + r.elev[k + 1]) / 2
            d.polygon([(x * SS, y * SS) for x, y in top], fill=int(em * 10))
        self.cov = np.asarray(img, np.int32)

    def top_ok(self, x, y, e):
        X, Y = int(x * SS), int(y * SS)
        if not (0 <= X < cm.W * SS and 0 <= Y < cm.H * SS):
            return False
        return self.cov[Y, X] <= e * 10 + 30

    def cars(self, r, t):
        """Cars on road r at loop phase t: list of (segment index, x, y, dx, dy, dir, elev)."""
        rng = random.Random(r.seed * 101)
        out = []
        lanes = (0.5, 1.5) if r.oneway else (-1.6, -0.6, 0.6, 1.6)
        Ln = r.len
        for lane in lanes:
            d = 1 if (lane > 0 or r.oneway) else -1
            gap = rng.uniform(13, 20) / r.cars
            n = max(1, int(Ln / gap))
            gap = Ln / n
            m = rng.choice((2, 3, 3, 4))
            s0 = rng.uniform(0, gap)
            off = (lane - 1.0) if r.oneway else lane
            for c in range(n):
                if rng.random() < 0.15:
                    continue
                s = (s0 + c * gap + d * t * m * gap) % Ln
                x, y, dx, dy, k = _at_k(r.deck, s)
                nx, ny = -dy, dx
                if ny < 0:
                    nx, ny = -nx, -ny
                x += nx * off * r.w * 0.22
                y += ny * off * r.w * 0.22
                el = r.elev[k] + (r.elev[min(k + 1, len(r.elev) - 1)] - r.elev[k]) * 0.5
                out.append((k, x, y, dx, dy, d, el, rng.randrange(6)))
        return out

    def draw(self, img, over, addd, t):
        s = self.s
        night = s.night
        # day shadows on the ground
        if not night:
            for r in self.roads:
                for k in range(len(r.pts) - 1):
                    if r.elev[k] < 3:
                        continue
                    a, b = r.pts[k], r.pts[k + 1]
                    nx, ny = cm._norm(b[0] - a[0], b[1] - a[1])
                    px, py = -ny * r.w * 0.55, nx * r.w * 0.55
                    o = r.elev[k] * 0.18
                    sh = [(a[0] + px + o, a[1] + py + o * 0.5), (b[0] + px + o, b[1] + py + o * 0.5),
                          (b[0] - px + o, b[1] - py + o * 0.5), (a[0] - px + o, a[1] - py + o * 0.5)]
                    over.polygon([(x * SS, y * SS) for x, y in sh], fill=(30, 26, 40, 40))
        # pylons (behind every deck), depth-tested against the buildings
        pc = (24, 22, 34, 255) if night else (96, 92, 98, 255)
        for r in self.roads:
            stepk = 3 if not r.oneway else 4
            for k in range(0, len(r.pts), stepk):
                if r.elev[k] < 5:
                    continue
                gx, gy = r.pts[k]
                dx, dy = r.deck[k]
                if s.vis(gx, gy):
                    wv = 1.5 if r.elev[k] < 50 else 1.9
                    over.polygon([((gx - wv) * SS, gy * SS), ((gx + wv) * SS, gy * SS),
                                  ((dx + wv) * SS, (dy + 2) * SS), ((dx - wv) * SS, (dy + 2) * SS)], fill=pc)
                    over.line([((gx + wv) * SS, gy * SS), ((dx + wv) * SS, (dy + 2) * SS)], fill=(8, 8, 12, 255), width=1)
        # spiral core column
        for cx, cy, h in ((self.spiral_c[0], self.spiral_c[1], 26),):
            if s.vis(cx, cy):
                over.rectangle([(cx - 3) * SS, (cy - h) * SS, (cx + 3) * SS, cy * SS], fill=pc)
        cars = {r.name: {} for r in self.roads}
        for r in self.roads:
            for c in self.cars(r, t):
                cars[r.name].setdefault(c[0], []).append(c)
        th = 4.5
        for _, gy, r, k in self.segs:
            top, (px, py) = self._quad(r, k)
            side = [top[3], top[2], (top[2][0], top[2][1] + th), (top[3][0], top[3][1] + th)]
            if night:
                over.polygon([(x * SS, y * SS) for x, y in side], fill=(12, 10, 20, 255))
                over.polygon([(x * SS, y * SS) for x, y in top], fill=(34, 30, 52, 255))
            else:
                over.polygon([(x * SS, y * SS) for x, y in side], fill=(70, 66, 74, 255))
                over.polygon([(x * SS, y * SS) for x, y in top], fill=(128, 124, 120, 255))
            over.line([(top[3][0] * SS, top[3][1] * SS), (top[2][0] * SS, top[2][1] * SS)], fill=(6, 5, 10, 255), width=2)
            over.line([(side[3][0] * SS, side[3][1] * SS), (side[2][0] * SS, side[2][1] * SS)], fill=(6, 5, 10, 255),
                      width=2)
            em = (r.elev[k] + r.elev[k + 1]) / 2
            rc = r.rail
            if night:
                over.line([(top[3][0] * SS, (top[3][1] + 0.6) * SS), (top[2][0] * SS, (top[2][1] + 0.6) * SS)],
                          fill=rc + (255,), width=2)
                over.line([(top[0][0] * SS, top[0][1] * SS), (top[1][0] * SS, top[1][1] * SS)],
                          fill=tuple(int(v * 0.6) for v in rc) + (255,), width=2)
                mx, my = (top[2][0] + top[3][0]) / 2, (top[2][1] + top[3][1]) / 2
                if self.top_ok(mx, my - 2, em):
                    addd.line([(top[3][0] * SS, (top[3][1] + 0.6) * SS), (top[2][0] * SS, (top[2][1] + 0.6) * SS)],
                              fill=rc + (120,), width=2)
            else:
                over.line([(top[3][0] * SS, (top[3][1] + 0.6) * SS), (top[2][0] * SS, (top[2][1] + 0.6) * SS)],
                          fill=tuple(int(v * 0.75 + 50) for v in rc) + (255,), width=2)
            a, b = r.deck[k], r.deck[k + 1]
            if not r.oneway:
                over.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)],
                          fill=(70, 64, 96, 255) if night else (220, 214, 190, 255), width=1)
            for (_, x, y, dx, dy, d, el, cc) in cars[r.name].get(k, []):
                self._car(over, addd, x, y, dx, dy, d, el, cc, night)

    def _car(self, over, addd, x, y, dx, dy, d, el, cc, night):
        if night:
            col = (255, 240, 210) if d > 0 else (255, 40, 54)
            tl = 8 if d > 0 else 6
            bx, by = x - dx * tl * d, y - dy * tl * d
            over.line([(bx * SS, by * SS), (x * SS, y * SS)], fill=tuple(int(v * 0.55) for v in col) + (255,), width=2)
            over.ellipse([x * SS - 2, y * SS - 2, x * SS + 2, y * SS + 2], fill=col + (255,))
            if self.top_ok(x, y, el):
                addd.line([(bx * SS, by * SS), (x * SS, y * SS)], fill=col + (110,), width=2)
                addd.ellipse([x * SS - 2, y * SS - 2, x * SS + 2, y * SS + 2], fill=col + (255,))
        else:
            col = ((240, 236, 226), (250, 196, 30), (210, 50, 44), (50, 60, 84), (170, 180, 196), (90, 160, 210))[cc]
            over.line([((x - dx * 2) * SS, (y - dy * 2) * SS), ((x + dx * 2) * SS, (y + dy * 2) * SS)],
                      fill=(16, 14, 20, 255), width=5)
            over.line([((x - dx * 1.7) * SS, (y - dy * 1.7) * SS), ((x + dx * 1.7) * SS, (y + dy * 1.7) * SS)],
                      fill=col + (255,), width=3)


def _at_k(pts, s):
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        l = math.hypot(b[0] - a[0], b[1] - a[1])
        if s <= l or k == len(pts) - 2:
            u = s / l if l else 0
            dx, dy = cm._norm(b[0] - a[0], b[1] - a[1])
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, dx, dy, k
        s -= l
    return pts[-1][0], pts[-1][1], 1.0, 0.0, len(pts) - 2
