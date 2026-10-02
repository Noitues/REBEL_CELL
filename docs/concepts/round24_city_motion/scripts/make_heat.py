"""city_heat_levels.gif: the night map cycling NOTICED -> FLAGGED -> HUNTED in the locked Heat language.

NOTICED (31): three rotating alarm beacons on side buildings round the Cell's turf, nothing on the target.
FLAGGED (58): two searchlights sweeping the sky from side blocks + two alarms ON the target.
HUNTED (82): police light clusters on the streets of the turf, two searchlights on the target, two
helicopters circling with jiggling spotlights, a third crossing in and out of frame, six drones with
mini spots. 120 frames at 85 ms, 800x450 (rendered at 960x540, reduced to stay under 4 MB).
"""
import math
import os
import random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cm
import fx
from cm import ss

MS = 85
SEGS = [(0, 36, 31, 'NOTICED', (255, 196, 40), 'ALARM BEACONS ON SIDE BUILDINGS'),
        (36, 72, 58, 'FLAGGED', (255, 128, 32), 'SKY SEARCHLIGHTS  +  ALARMS ON THE TARGET'),
        (72, 120, 82, 'HUNTED', (255, 40, 56), 'POLICE CLUSTERS, SEARCHLIGHTS, CHOPPERS + DRONES')]
TOTAL = 120
OUT_W, OUT_H = 800, 450
CELL_C = (470, 420)


def roof_near(s, x, y, hmin=40, used=()):
    best = None
    for h, tx, ty, gx, gy in s.tops:
        if h < hmin:
            continue
        if any((tx - u[0]) ** 2 + (ty - u[1]) ** 2 < 30 ** 2 for u in used):
            continue
        d = (tx - x) ** 2 + (ty - y) ** 2
        if best is None or d < best[0]:
            best = (d, tx, ty)
    return best[1], best[2]


def street_pts(s, cx, cy, rx, ry, n, seed, mind=34):
    r = random.Random(seed)
    cand = []
    for ax, k, run in s.lines:
        for x, y, _ in run:
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1 and s.vis(x, y):
                cand.append((x, y))
    r.shuffle(cand)
    out = []
    for p in cand:
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > mind ** 2 for q in out):
            out.append(p)
        if len(out) >= n:
            break
    return out


class Heat:
    def __init__(self, s):
        self.s = s
        used = []
        self.side_beacons = []
        for x, y in ((290, 330), (655, 285), (700, 470)):
            p = roof_near(s, x, y, 60, used)
            used.append(p)
            self.side_beacons.append(p)
        self.side_lights = []
        for x, y in ((270, 380), (680, 330)):
            p = roof_near(s, x, y, 60, used)
            used.append(p)
            self.side_lights.append(p)
        self.target_alarms = []
        for x, y in ((430, 360), (530, 410)):
            p = roof_near(s, x, y, 30, used)
            used.append(p)
            self.target_alarms.append(p)
        self.target_lights = []
        for x, y in ((400, 400), (560, 450)):
            p = roof_near(s, x, y, 30, used)
            used.append(p)
            self.target_lights.append(p)
        self.police = street_pts(s, 470, 425, 210, 125, 13, 7)
        self.nodes = [cm.tile(26, 24), cm.tile(30, 31), cm.tile(26, 31)]
        self.links = [[cm.tile(26, 24), cm.tile(26, 31)], [cm.tile(26, 31), cm.tile(30, 31)]]

    def seg(self, f):
        for k, (a, b, v, band, col, sub) in enumerate(SEGS):
            if a <= f < b:
                return k, f - a, b - a
        return 2, f - 72, 48

    def draw(self, s, L, f, phase):
        k, lf, ln = self.seg(f)
        a_in = ss(lf / 6.0)
        if phase == 'ground':
            addd, over = L['addd'], L['over']
            for p, q in self.links:
                fx.link(addd, [p, q], f)
            for n, (x, y) in enumerate(self.nodes):
                fx.node(over, addd, x, y, f)
            if k == 0:
                for n, (x, y) in enumerate(self.side_beacons):
                    fx.beacon(addd, x, y, f, a_in, ph=n * 3)
            if k == 1:
                for n, (x, y) in enumerate(self.target_alarms):
                    fx.beacon(addd, x, y, f, a_in, ph=n * 4)
                for n, (x, y) in enumerate(self.side_lights):
                    ang = 0.42 * math.sin(2 * math.pi * lf / 30 + n * 2.1) + (-0.25 if n == 0 else 0.25)
                    fx.sky_searchlight(addd, x, y, ang, a_in)
            if k == 2:
                for n, (x, y) in enumerate(self.police):
                    fx.police(addd, x, y, f, 100 + n, ss((lf - n * 0.6) / 4.0))
                for n, (x, y) in enumerate(self.target_alarms):
                    fx.beacon(addd, x, y, f, a_in, ph=n * 4)
                for n, (x, y) in enumerate(self.target_lights):
                    ang = 0.5 * math.sin(2 * math.pi * lf / 34 + n * 2.6)
                    fx.sky_searchlight(addd, x, y, ang, a_in)
        elif phase == 'air' and k == 2:
            over, addd = L['over'], L['addd']
            crafts = []
            # two circling helicopters over the turf
            for n, (cx, cy, R, alt, per, dirn, ph) in enumerate(((470, 410, 95, 84, 60, 1, 0.0),
                                                                   (430, 455, 62, 66, 44, -1, 2.0))):
                th = ph + dirn * 2 * math.pi * lf / per
                gx, gy = cx + R * math.cos(th), cy + R * 0.5 * math.sin(th)
                hx, hy = gx, gy - alt
                head = th + dirn * math.pi / 2
                tgt = (cx + 0.35 * R * math.cos(th) + 5 * math.sin(f * 0.9 + n), cy + 0.18 * R * math.sin(th) +
                       3 * math.cos(f * 1.3 + n))
                crafts.append((hy, 'heli', hx, hy, head, tgt, 1.0 * a_in))
            # third chopper enters from the right, sweeps across, leaves top-left
            u = lf / 47.0
            p0, p1, p2 = (1010, 120), (560, 330), (-70, 60)
            hx = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
            hy = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
            dx = 2 * (1 - u) * (p1[0] - p0[0]) + 2 * u * (p2[0] - p1[0])
            dy = 2 * (1 - u) * (p1[1] - p0[1]) + 2 * u * (p2[1] - p1[1])
            head = math.atan2(dy * 2, dx)
            crafts.append((hy, 'heli', hx, hy, head, (hx + 6 * math.sin(f), hy + 90), 1.0))
            # drones
            for n in range(6):
                cx = 400 + (n % 3) * 70
                cy = 380 + (n // 3) * 70
                th = n * 1.3 + 2 * math.pi * lf / (30 + 4 * n) * (1 if n % 2 else -1)
                gx, gy = cx + 26 * math.cos(th), cy + 13 * math.sin(th)
                crafts.append((gy - 38, 'drone', gx, gy - 38, 0, (gx + 2 * math.sin(f * 1.7 + n), gy), ss((lf - 4 - n) / 5)))
            crafts.sort(key=lambda c: c[0])
            for _, kind, x, y, head, tgt, a in crafts:
                if a <= 0:
                    continue
                if kind == 'heli':
                    fx.spot(addd, x, y + 10, tgt[0], tgt[1], 17, a)
                    fx.heli(over, addd, x, y, head, f, 2.3, a=a)
                else:
                    fx.spot(addd, x, y, tgt[0], tgt[1], 6, a * 0.8)
                    fx.drone(over, addd, x, y, f, a, ph=int(x))

    def hud(self, img, f):
        k, lf, ln = self.seg(f)
        if True:
            a, b, v, band, col, sub = SEGS[k]
            if k > 0:
                pv = SEGS[k - 1][2]
                val = int(round(pv + (v - pv) * ss(lf / 8.0)))
            else:
                val = v
            flash = max(0.0, 1 - lf / 5.0) if k > 0 else 0.0
            fx.hud_heat(img, val, band, col, flash=flash, sub=sub)


def main():
    s = cm.Scene('night')
    h = Heat(s)
    frames = []
    for f in range(TOTAL):
        im = s.frame(f, 40, extra=h.draw, opts=dict(rain=False, fog_drift=False))
        im = im.resize((OUT_W, OUT_H), cm.Image.LANCZOS)
        h.hud(im, f)
        frames.append(im)
    out = os.path.join(cm.SCR, 'heat')
    os.makedirs(out, exist_ok=True)
    for k in (20, 50, 60, 80, 100, 116):
        frames[k].save(os.path.join(out, 'f%03d.png' % k))
    size = cm.save_gif(frames, os.path.join(cm.ROOT, 'city_heat_levels.gif'), MS, tol=30)
    print('heat', round(size / 1e6, 2), 'MB')


if __name__ == '__main__':
    main()
