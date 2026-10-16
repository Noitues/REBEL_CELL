"""CityMap2: CityMap + recording of every drawn feature (for JSON export), proper ramps and
interchanges, dense suburb lots, smoothness checks. Used by design A2."""
import math
import random

import numpy as np

from citymap import (COL, ROAD_CASING, TEXT, U, CityMap, tint)
from geom import (TAU, Noise, catmull, circle_pts, cum, dist, mix, plen, pt_at, rect_pts, resample, rot,
                  seg_intersections)

RAMP_FILL = (255, 232, 168)


class CityMap2(CityMap):
    def __init__(self, seed=1):
        super().__init__(seed)
        self.features = []
        self.rivers = []
        self.lakes = []
        self.interchanges = []
        self.walls = []
        self.dams = []
        self.seawalls = []
        self.station_list = []
        self._last_pts = None
        self.undercity_lines = []
        self.ferries = []
        self.drones = []
        self.undercity_entrances = []

    # ---- recording wrappers -----------------------------------------------------------
    def sub_mask(self, poly, key_parent=None, smooth=True):
        m, pts = super().sub_mask(poly, key_parent, smooth)
        self._last_pts = pts
        return m, pts

    def free_mask(self, poly, smooth=True, mark=True):
        m, pts = super().free_mask(poly, smooth, mark)
        self._last_pts = pts
        return m, pts

    def _feat(self, kind, name, pts, **extra):
        d = dict(kind=kind, name=name, poly=[(round(x, 2), round(y, 2)) for x, y in pts])
        d.update(extra)
        self.features.append(d)

    def park(self, poly, name=None, **kw):
        m = super().park(poly, **kw)
        self._feat('park', name, self._last_pts)
        return m

    def plaza(self, poly, name=None, **kw):
        m = super().plaza(poly, **kw)
        self._feat('plaza', name, self._last_pts)
        return m

    def built(self, poly, col, a=0.5, name=None, kind='built', **kw):
        m = super().built(poly, col, a=a, **kw)
        self._feat(kind, name, self._last_pts)
        return m

    def industry(self, poly, name=None, kind='industry', **kw):
        m = super().industry(poly, **kw)
        self._feat(kind, name, self._last_pts)
        return m

    def undercity(self, poly, color=(190, 130, 255)):
        m = super().undercity(poly, color)
        self._feat('undercity', 'Undercity', self._last_pts)
        return m

    def river(self, pts, w0, w1, name=None, kind='river', **kw):
        dense = super().river(pts, w0, w1, **kw)
        self.rivers.append(dict(name=name, kind=kind, pts=resample(dense, 8.0), w0=w0, w1=w1))
        return dense

    def lake(self, poly, name=None, **kw):
        pts = super().lake(poly, **kw)
        self.lakes.append(dict(name=name, poly=pts))
        return pts

    def wall(self, pts, color, closed=False, clip=True, name=None):
        res = super().wall(pts, color, closed, clip)
        self.walls.append(dict(name=name, pts=resample(res, 6.0)))
        return res

    def dam(self, pts, w=5.0, sluices=True, name=None, kind='dam'):
        dense = catmull(pts, step=3.0) if len(pts) > 2 else resample(pts, 3.0)
        super().dam(dense, w, sluices)
        self.dams.append(dict(name=name, kind=kind, pts=resample(dense, 6.0)))

    def seawall(self, pts, w=3.4, name=None):
        super().seawall(pts, w)
        self.seawalls.append(dict(name=name, pts=resample(pts, 6.0)))

    def station(self, x, y, kind='metro', label=None, ldx=0, ldy=-7, size=10, name=None, lines=()):
        super().station(x, y, kind, label, ldx, ldy, size)
        self.station_list.append(dict(name=name or label, kind=kind, pos=(round(x, 2), round(y, 2)), lines=list(lines)))

    def ferry(self, pts, color=(150, 225, 255), terminals=True):
        super().ferry(pts, color, terminals)
        self.ferries.append(dict(pts=[tuple(p) for p in pts]))

    def drone_corridor(self, pts, **kw):
        super().drone_corridor(pts, **kw)
        self.drones.append(dict(pts=[tuple(p) for p in pts]))

    # ---- roads / rails with closed loops -----------------------------------------------
    def add_road(self, name, pts, cls='motorway', smooth=True, tunnels=(), ramp=False, step=3.0, label=None,
                 closed=False):
        if closed:
            dense = catmull(pts, closed=True, step=step)
            dense = dense + [dense[0]]
        else:
            dense = catmull(pts, step=step) if smooth and len(pts) > 2 else resample(pts, step)
        r = dict(name=name, pts=dense, cls=cls, tunnels=list(tunnels), ramp=ramp, label=label, closed=closed, bridges=[])
        self.roads.append(r)
        return r

    def add_rail(self, name, pts, kind='freight', smooth=True, tunnels=(), step=3.0, closed=False):
        if closed:
            dense = catmull(pts, closed=True, step=step)
            dense = dense + [dense[0]]
        else:
            dense = catmull(pts, step=step) if smooth and len(pts) > 2 else resample(pts, step)
        r = dict(name=name, pts=dense, kind=kind, tunnels=list(tunnels), closed=closed)
        self.rails.append(r)
        return r

    def _bridges(self, r, cw, fw, fc, wet):
        pts = r['pts']
        run, runs = [], []
        for p in pts:
            x, y = int(p[0]), int(p[1])
            w = 0 <= x < U and 0 <= y < U and wet[y, x]
            if w:
                run.append(p)
            else:
                if len(run) > 2:
                    runs.append(run)
                run = []
        if len(run) > 2:
            runs.append(run)
        for rn in runs:
            if plen(rn) >= 6:
                r['bridges'].append(rn)
        super()._bridges(r, cw, fw, fc, wet)

    def _road_style(self, cls):
        if cls == 'collector':
            return (2.7, 1.5, (156, 162, 178))
        return super()._road_style(cls)

    # ---- ramps and interchanges ----------------------------------------------------------
    def _ramp(self, pts, smooth=True):
        d = catmull(pts, step=1.5) if smooth and len(pts) > 2 else pts
        self.line(d, ROAD_CASING, 4.4)
        self.line(d, RAMP_FILL, 2.3)
        return d

    def _cloverleaf(self, p, ua, ub, r):
        ramps = []
        for sa in (1, -1):
            for sb in (1, -1):
                u = (ua[0] * sa, ua[1] * sa)
                v = (ub[0] * sb, ub[1] * sb)
                cosang = max(-0.999, min(0.999, u[0] * v[0] + u[1] * v[1]))
                theta = math.acos(cosang)
                k = r / math.tan(theta / 2)
                bis = (u[0] + v[0], u[1] + v[1])
                bl = math.hypot(*bis)
                bis = (bis[0] / bl, bis[1] / bl)
                cd = r / math.sin(theta / 2)
                c = (p[0] + bis[0] * cd, p[1] + bis[1] * cd)
                TA = (p[0] + u[0] * k, p[1] + u[1] * k)
                TB = (p[0] + v[0] * k, p[1] + v[1] * k)
                aA = math.atan2(TA[1] - c[1], TA[0] - c[0])
                aB = math.atan2(TB[1] - c[1], TB[0] - c[0])
                dd = (aB - aA) % TAU
                sweep = dd if dd > math.pi else dd - TAU
                pts = [(c[0] + r * math.cos(aA + sweep * i / 24), c[1] + r * math.sin(aA + sweep * i / 24))
                       for i in range(25)]
                ramps.append(self._ramp(pts, smooth=False))
        return ramps

    def _stack(self, p, ua, ub, d):
        """Four-level stack drawn as a ring of four sweeping ramps joined to the four arms, plus a flyover pad."""
        ramps = []
        for sa in (1, -1):
            for sb in (1, -1):
                u = (ua[0] * sa, ua[1] * sa)
                v = (ub[0] * sb, ub[1] * sb)
                au, av = math.atan2(u[1], u[0]), math.atan2(v[1], v[0])
                sw = (av - au + math.pi) % TAU - math.pi
                pts = []
                for i in range(21):
                    t = i / 20.0
                    rr = d * (1.0 + 0.18 * math.sin(math.pi * t))
                    pts.append((p[0] + rr * math.cos(au + sw * t), p[1] + rr * math.sin(au + sw * t)))
                ramps.append(self._ramp(pts, smooth=False))
        self.circle(p[0], p[1], 4.2, (10, 12, 18), (255, 255, 255), 1.3)
        return ramps

    def _diamond(self, p, ua, ub):
        """Motorway (ua) with an arterial (ub): four slip ramps that peel off and curve onto the arterial."""
        n = (-ua[1], ua[0])
        ramps = []
        for sa in (1, -1):
            for k in (1, -1):
                side = 1 if (ub[0] * k * n[0] + ub[1] * k * n[1]) > 0 else -1
                M0 = (p[0] + ua[0] * sa * 17, p[1] + ua[1] * sa * 17)
                M1 = (p[0] + ua[0] * sa * 11 + n[0] * side * 2.2, p[1] + ua[1] * sa * 11 + n[1] * side * 2.2)
                M2 = (p[0] + ua[0] * sa * 5.5 + n[0] * side * 4.6, p[1] + ua[1] * sa * 5.5 + n[1] * side * 4.6)
                A0 = (p[0] + ub[0] * k * 8.5, p[1] + ub[1] * k * 8.5)
                A1 = (p[0] + ub[0] * k * 15, p[1] + ub[1] * k * 15)
                ramps.append(self._ramp([M0, M1, M2, A0, A1]))
        return ramps

    def interchange(self, p, a, b, style='stack', size=1.0):
        ua = (math.cos(a), math.sin(a))
        ub = (math.cos(b), math.sin(b))
        if style == 'cloverleaf':
            return self._cloverleaf(p, ua, ub, 7.2 * size)
        if style == 'stack':
            return self._stack(p, ua, ub, 10.0 * size)
        return self._diamond(p, ua, ub)

    def auto_interchanges(self, min_sep=18.0, forced=None, skip=()):
        forced = forced or {}
        mclasses = ('ring', 'motorway', 'truck')
        found, done = [], []
        for i, r1 in enumerate(self.roads):
            for j, r2 in enumerate(self.roads):
                if j <= i:
                    continue
                c1, c2 = r1['cls'], r2['cls']
                if c1 in mclasses and c2 in mclasses:
                    sty = 'auto'
                elif (c1 in mclasses and c2 == 'arterial' and r2['ramp']) or \
                        (c2 in mclasses and c1 == 'arterial' and r1['ramp']):
                    sty = 'diamond'
                else:
                    continue
                for p, aa, bb in seg_intersections(r1['pts'], r2['pts']):
                    ms = min_sep if sty == 'auto' else 14.0
                    if any(dist(p, q) < ms for q in done):
                        continue
                    if any(dist(p, q) < 6 for q in skip):
                        continue
                    if sty == 'auto':
                        d = abs(((aa - bb) + math.pi / 2) % math.pi - math.pi / 2)   # 0..pi/2
                        crossing = math.pi / 2 - d
                        sty2 = 'cloverleaf' if crossing > math.radians(66) else 'stack'
                        sty2 = forced.get((r1['name'], r2['name']), forced.get((r2['name'], r1['name']), sty2))
                    else:
                        sty2 = 'diamond'
                    done.append(p)
                    found.append(dict(pos=p, a=aa, b=bb, type=sty2, roads=(r1['name'], r2['name'])))
        found.sort(key=lambda t: 0 if t['type'] == 'diamond' else 1)
        for f in found:
            # orient the diamond so ua is the motorway
            a, b = f['a'], f['b']
            if f['type'] == 'diamond':
                r1 = next(r for r in self.roads if r['name'] == f['roads'][0])
                if r1['cls'] == 'arterial':
                    a, b = b, a
            ramps = self.interchange(f['pos'], a, b, f['type'])
            f['ramps'] = ramps
            self.interchanges.append(f)
        return found

    # ---- dense low-rise suburb lots ------------------------------------------------------------
    def tex_lots(self, M, angle, sp, lot=(1.9, 1.35), color=(182, 166, 144), a=0.62, seed=0, skip=0.05,
                 margin=1.15, rows=2):
        rng = random.Random(seed + 91)
        bb = self.bbox_u(M, 10)
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        R = math.hypot(bb[2] - bb[0], bb[3] - bb[1]) / 2 + 6
        ang = math.radians(angle)
        mk = self.mnp(M)
        rects = []
        n = int(R / sp) + 1
        nl = max(1, int((sp - 2 * margin) / lot[0]))
        lw = (sp - 2 * margin) / nl
        for i in range(-n, n):
            for j in range(-n, n):
                x0, y0 = cx + i * sp, cy + j * sp
                c = rot((x0 + sp / 2, y0 + sp / 2), ang, (cx, cy))
                xi, yi = int(c[0]), int(c[1])
                if not (0 <= xi < U and 0 <= yi < U and mk[yi, xi]):
                    continue
                for row in range(rows):
                    if rows == 1:
                        yy = y0 + sp / 2
                    else:
                        yy = y0 + margin + lot[1] / 2 + row * (sp - 2 * margin - lot[1])
                    for k in range(nl):
                        if rng.random() < skip:
                            continue
                        xx = x0 + margin + lw * (k + 0.5)
                        cp = rot((xx, yy), ang, (cx, cy))
                        rects.append(rect_pts(cp[0], cp[1], lw * 0.86, lot[1], ang))
        self.polys(rects, color, a, clip=M, bbox_units=bb)

    def tex_suburb_ellipses(self, M, c, rx0, ry0, g0, g1, sp=7.0, color=(200, 190, 175), lot_color=(182, 166, 144),
                            seed=0, lot=(1.9, 1.35), a_street=0.42, a_lot=0.6, spoke_sp=22.0):
        """Low-rise suburb in offset rings of an ellipse: continuous streets, radial connectors, lots on both sides."""
        rng = random.Random(seed + 17)
        bb = self.bbox_u(M, 8)
        mk = self.mnp(M)
        arcs, spokes, rects = [], [], []
        g = g0
        while g < g1:
            rx, ry = rx0 + g, ry0 + g
            n = max(48, int(TAU * max(rx, ry) / 3.0))
            arcs.append([(c[0] + rx * math.cos(TAU * i / n), c[1] + ry * math.sin(TAU * i / n)) for i in range(n + 1)])
            t = rng.uniform(0, 0.01)
            while t < TAU:
                dx, dy = -rx * math.sin(t), ry * math.cos(t)
                sp_ = math.hypot(dx, dy)
                tang = math.atan2(dy, dx)
                for off in (-1, 1):
                    gg = off * (lot[1] / 2 + 0.9)
                    nx_, ny_ = math.cos(tang - math.pi / 2), math.sin(tang - math.pi / 2)
                    x = c[0] + rx * math.cos(t) + nx_ * gg
                    y = c[1] + ry * math.sin(t) + ny_ * gg
                    xi, yi = int(x), int(y)
                    if 0 <= xi < U and 0 <= yi < U and mk[yi, xi] and rng.random() > 0.05:
                        rects.append(rect_pts(x, y, lot[0] * 0.86, lot[1], tang))
                t += lot[0] / sp_
            g += sp * (1 + rng.uniform(-0.08, 0.08))
        t = rng.uniform(0, 0.2)
        while t < TAU:
            pts = [(c[0] + (rx0 + gg) * math.cos(t + 0.012 * math.sin(gg * 0.05)),
                    c[1] + (ry0 + gg) * math.sin(t + 0.012 * math.sin(gg * 0.05))) for gg in np.arange(g0, g1, 3.0)]
            spokes.append(pts)
            t += spoke_sp / (0.5 * (rx0 + ry0 + g0 + g1))
        self.lines(arcs, color, 0.8, a_street, clip=M, bbox_units=bb)
        self.lines(spokes, color, 1.0, a_street + 0.1, clip=M, bbox_units=bb)
        self.polys(rects, lot_color, a_lot, clip=M, bbox_units=bb)

    # ---- undercity network ------------------------------------------------------------------------
    def undercity_net(self, lines, entrances, color=(190, 130, 255)):
        for pts in lines:
            d = catmull(pts, step=3.0) if len(pts) > 2 else resample(pts, 3.0)
            self.line(d, (8, 6, 16), 3.2, 0.8)
            self.line(d, color, 1.5, 0.95, dash=(3, 1.6))
            self.undercity_lines.append(resample(d, 6.0))
        for (x, y, nm) in entrances:
            self.circle(x, y, 3.4, (20, 10, 34), color, 1.5)
            self.circle(x, y, 1.2, color)
            self.undercity_entrances.append(dict(name=nm, pos=(round(x, 2), round(y, 2))))

    # ---- checks ----------------------------------------------------------------------------------------
    def check_turns(self, max_deg=48.0, window=24.0):
        bad = []
        for kind, items in (('road', self.roads), ('rail', self.rails)):
            for r in items:
                p = resample(r['pts'], 3.0)
                k = max(2, int(window / 3.0))
                for i in range(k, len(p) - k):
                    a = math.atan2(p[i][1] - p[i - k][1], p[i][0] - p[i - k][0])
                    b = math.atan2(p[i + k][1] - p[i][1], p[i + k][0] - p[i][0])
                    d = abs((b - a + math.pi) % TAU - math.pi)
                    if math.degrees(d) > max_deg:
                        bad.append((kind, r['name'], round(p[i][0]), round(p[i][1]), round(math.degrees(d))))
                        break
        return bad

    def min_dist_to(self, pts_list, pos):
        best = 1e9
        for p in pts_list:
            for q in resample(p, 4.0):
                best = min(best, dist(q, pos))
        return best
