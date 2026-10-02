"""city_incursion.gif: an HQ / raid incursion warning on the night map.

Halcyon Civic's HQ raises the alarm, two threat routes draw along real avenues toward two of the Cell's
claimed Sites, armoured carriers (violet hulls, amber light bars, round 20 livery) roll out in convoy,
and three helicopters lift off the HQ and peel away toward the Cell's turf, spotlights on.
84 frames at 85 ms, 960x540.
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cm
import fx
from cm import ss, HAL_V, HAL_A, RED, SS

MS = 85
TOTAL = 84
WARN = (255, 52, 60)


def route(*legs):
    """legs: ('i', i, j0, j1) runs along constant i; ('j', j, i0, i1) along constant j."""
    pts = []
    for ax, k, a, b in legs:
        st = 1 if b >= a else -1
        for m in range(a, b + st, st):
            p = cm.tile(k, m) if ax == 'i' else cm.tile(m, k)
            if not pts or pts[-1] != p:
                pts.append(p)
    return pts


class Incursion:
    def __init__(self, s):
        self.s = s
        self.nodes = [cm.tile(26, 24), cm.tile(30, 31), cm.tile(26, 31)]
        self.links = [[cm.tile(26, 24), cm.tile(26, 31)], [cm.tile(26, 31), cm.tile(30, 31)]]
        self.routes = [route(('i', 36, 7, 31), ('j', 31, 36, 30)),
                       route(('j', 6, 33, 26), ('i', 26, 6, 24))]
        self.rlen = [cm._plen(r) for r in self.routes]
        hq = cm.tile(36, 2)
        self.hq = (hq[0], hq[1] - 6)
        self.pad = (hq[0], hq[1] - 58)          # helipad near the pyramid's top
        # heli flights: (lift-off frame, ground start offset, control point, target ground, circle dir)
        self.helis = [(22, (-10, 4), (720, 160), cm.tile(26, 24), 1),
                      (28, (10, 2), (820, 470), cm.tile(30, 31), -1),
                      (34, (0, -4), (620, 260), cm.tile(28, 28), 1)]

    def draw(self, s, L, f, phase):
        if phase == 'ground':
            addd, over = L['addd'], L['over']
            warn = ss((f - 58) / 6.0)
            for p, q in self.links:
                fx.link(addd, [p, q], f)
            for n, (x, y) in enumerate(self.nodes):
                fx.node(over, addd, x, y, f, warn=warn if n < 2 else 0.0)
            # HQ alarm: expanding violet rings + amber beacons
            a = ss((f - 4) / 4.0)
            if a > 0:
                hx, hy = self.hq
                for k in range(3):
                    u = ((f + k * 5) % 15) / 15.0
                    r = 40 + u * 110
                    addd.ellipse([(hx - r) * SS, (hy - r * 0.5) * SS, (hx + r) * SS, (hy + r * 0.5) * SS],
                                 outline=HAL_V + (int(200 * a * (1 - u)),), width=4)
                for k, (dx, dy) in enumerate(((-70, 0), (70, 0), (0, 36), (0, -36))):
                    fx.beacon(addd, hx + dx, hy + dy, f, a, col=HAL_A, ph=k * 2)
            # threat routes: grow, then chevrons flow toward the Cell
            for n, (pts, Ln) in enumerate(zip(self.routes, self.rlen)):
                g = ss((f - 12 - n * 4) / 16.0)
                if g <= 0:
                    continue
                cut = Ln * g
                seg = []
                acc = 0.0
                for k in range(len(pts) - 1):
                    l = math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
                    seg.append(pts[k])
                    if acc + l >= cut:
                        x, y, dx, dy = cm._at(pts, cut)
                        seg.append((x, y))
                        break
                    acc += l
                else:
                    seg.append(pts[-1])
                addd.line([(x * SS, y * SS) for x, y in seg], fill=HAL_V + (95,), width=5)
                addd.line([(x * SS, y * SS) for x, y in seg], fill=(220, 210, 255, 110), width=2)
                nc = int(cut / 18)
                for c in range(nc):
                    sc = (c * 18 + f * 3.0) % max(1.0, cut)
                    x, y, dx, dy = cm._at(pts, sc)
                    px, py = -dy, dx
                    tip = (x + dx * 4, y + dy * 4)
                    addd.polygon([((x - dx * 2 + px * 3.5) * SS, (y - dy * 2 + py * 3.5) * SS), (tip[0] * SS, tip[1] * SS),
                                  ((x - dx * 2 - px * 3.5) * SS, (y - dy * 2 - py * 3.5) * SS),
                                  ((x + dx * 0.5) * SS, (y + dy * 0.5) * SS)], fill=HAL_A + (230,))
            # convoys
            for n, (pts, Ln) in enumerate(zip(self.routes, self.rlen)):
                for c in range(3):
                    t0 = 22 + n * 6 + c * 4
                    u = ss((f - t0) / 52.0)
                    if f < t0:
                        continue
                    s_ = (Ln - 22 - c * 14) * u
                    x, y, dx, dy = cm._at(pts, max(0.0, s_))
                    px, py = -dy, dx
                    fx.vehicle(over, addd, x + px * 3, y + py * 3, dx, dy, f, ss((f - t0) / 3.0), ph=c + n,
                               part='light')
        elif phase == 'air':
            over, addd = L['over'], L['addd']
            crafts = []
            for n, (t0, off, ctrl, tgt, dirn) in enumerate(self.helis):
                if f < t0:
                    continue
                lt = f - t0
                gx0, gy0 = self.hq[0] + off[0], self.hq[1] + off[1]
                lift = ss(lt / 10.0)
                alt0 = 58 + 30 * lift                     # starts on the pad (pyramid top), climbs
                u = ss((lt - 6) / 26.0)
                if lt < 6:
                    gx, gy = gx0, gy0
                else:
                    gx = (1 - u) ** 2 * gx0 + 2 * (1 - u) * u * ctrl[0] + u * u * tgt[0]
                    gy = (1 - u) ** 2 * gy0 + 2 * (1 - u) * u * ctrl[1] + u * u * tgt[1]
                if u >= 1:
                    th = dirn * 2 * math.pi * (lt - 32) / 34.0
                    gx += 34 * math.cos(th) - 34
                    gy += 17 * math.sin(th)
                if lt < 6:
                    head = math.pi * 0.85
                else:
                    du = 0.02
                    u2 = min(1.0, u + du)
                    nx = (1 - u2) ** 2 * gx0 + 2 * (1 - u2) * u2 * ctrl[0] + u2 * u2 * tgt[0]
                    ny = (1 - u2) ** 2 * gy0 + 2 * (1 - u2) * u2 * ctrl[1] + u2 * u2 * tgt[1]
                    head = math.atan2((ny - gy) * 2, nx - gx) if u < 1 else th + dirn * math.pi / 2
                hx, hy = gx, gy - alt0
                spot_a = ss((lt - 8) / 5.0)
                crafts.append((hy, hx, hy, head, (gx + 5 * math.sin(f * 0.8 + n), gy + 3 * math.cos(f * 1.1 + n)),
                               spot_a))
            for vx, vy, dx, dy, va, ph in self.convoy(f):
                fx.vehicle(over, addd, vx, vy, dx, dy, f, va, ph=ph, part='body')
            crafts.sort()
            for hy, hx, hy_, head, tgt, sa in crafts:
                if sa > 0:
                    fx.spot(addd, hx, hy + 10, tgt[0], tgt[1], 16, sa, col=(236, 228, 255))
                fx.heli(over, addd, hx, hy, head, f, 2.1, livery=(84, 72, 150))

    def convoy(self, f):
        out = []
        for n, (pts, Ln) in enumerate(zip(self.routes, self.rlen)):
            for c in range(3):
                t0 = 22 + n * 6 + c * 4
                if f < t0:
                    continue
                u = ss((f - t0) / 52.0)
                x, y, dx, dy = cm._at(pts, max(0.0, (Ln - 22 - c * 14) * u))
                px, py = -dy, dx
                out.append((x + px * 3, y + py * 3, dx, dy, ss((f - t0) / 3.0), c + n))
        return out

    def ui(self, img, f):
        a = ss((f - 6) / 5.0)
        if a <= 0:
            return
        sub = None
        if f >= 58:
            sub = 'RAID INBOUND  //  2 ROUTES  -  6 CARRIERS  -  3 AIR  //  TARGET: 2 CELL SITES'
        elif f >= 14:
            sub = 'HALCYON CIVIC MOBILISING ON YOUR TURF'
        fx.banner(img, 'INCURSION WARNING', WARN, a, y=14 - int(20 * (1 - a)), sub=sub)


def main():
    s = cm.Scene('night')
    inc = Incursion(s)
    frames = []
    for f in range(TOTAL):
        im = s.frame(f, 42, extra=inc.draw, opts=dict(rain=False, fog_drift=False))
        inc.ui(im, f)
        frames.append(im)
    out = os.path.join(cm.SCR, 'inc')
    os.makedirs(out, exist_ok=True)
    for k in (4, 10, 20, 30, 44, 60, 72, 83):
        frames[k].save(os.path.join(out, 'f%03d.png' % k))
    size = cm.save_gif(frames, os.path.join(cm.ROOT, 'city_incursion.gif'), MS, tol=30)
    print('incursion', round(size / 1e6, 2), 'MB')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        s = cm.Scene('night')
        inc = Incursion(s)
        from PIL import Image
        ims = []
        for f in (10, 34, 70):
            im = s.frame(f, 42, extra=inc.draw, opts=dict(rain=False, fog_drift=False))
            inc.ui(im, f)
            ims.append(im)
        sh = Image.new('RGB', (960, 1620))
        for n, im in enumerate(ims):
            sh.paste(im, (0, n * 540))
        sh.save(os.path.join(cm.SCR, 'ti.png'))
    else:
        main()
