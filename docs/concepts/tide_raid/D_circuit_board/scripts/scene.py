"""The circuit-board layer over the real Solace territory: copper traces on the streets, chips for Sites,
a hand-soldered HOME chip, the corp CPU, plum corrosion."""
import math, random
import numpy as np
from scipy.spatial import cKDTree
from lib import *

ORG = (455.8, 519.6)   # lattice origin in plate px (t1_b node)
TIER_SIZE = {1: 0.62, 2: 0.76, 3: 0.70}
TIER_H = {1: 13, 2: 18, 3: 24}


def lat(u, v):
    """plate-px point from lattice (u = p-q, v = p+q) coordinates"""
    return T((ORG[0] + u * LU, ORG[1] + v * LV))


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


class Scene:
    def __init__(self, scn='default', beat='forecast', plate='city_noraid_nonet.png'):
        self.scn = scn
        self.cd = load_coords('default', 'forecast')      # one coordinate set: same camera and street graph
        nodes, links = build_graph(self.cd)
        self.pnodes = nodes
        self.nodes = {k: T(v) for k, v in nodes.items()}
        self.links = {k: [T(p) for p in v] for k, v in links.items()}
        self.f = Frame(grade_base(PLATES + plate))
        self.sites = {s['id']: s for s in self.cd['sites']}
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        c = T((700, 520))
        d2 = ((xx - c[0]) / 760) ** 2 + ((yy - c[1]) / 420) ** 2
        self.bmask = (0.22 + 0.78 * np.exp(-d2 * 1.1)).astype(np.float32)
        self.rng = random.Random(7)

    # ------------------------------------------------------------ secondary board
    def _bus(self, rng):
        if rng.random() < 0.6:
            nid = rng.choice(sorted(self.pnodes))
            px, py = self.pnodes[nid]
            u, v = round((px - ORG[0]) / LU) + rng.randrange(-4, 5), round((py - ORG[1]) / LV) + rng.randrange(-4, 5)
        else:
            u, v = rng.randrange(-24, 62), rng.randrange(-34, 38)
        if (u + v) % 2:
            v += 1
        moves = []
        dirs_axis = [(1, 1, 0), (0, 0, 1)]  # placeholder
        # lattice unit steps in (u,v): +p=(1,1) -p=(-1,-1) +q=(-1,1) -q=(1,-1); vertical=(0,2) horizontal=(2,0)
        axis = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        cham = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        pts = [(u, v)]
        for i in range(rng.choice((3, 3, 5))):
            if i % 2 == 0:
                d = rng.choice(axis)
                n = rng.randrange(3, 10)
            else:
                d = rng.choice(cham)
                n = rng.randrange(2, 7)
            u, v = u + d[0] * n, v + d[1] * n
            pts.append((u, v))
        return [lat(a, b) for a, b in pts]

    def board(self, n_bus=62, alpha=150, seed=11):
        f = self.f
        rng = random.Random(seed)
        strands = []          # polylines
        for _ in range(n_bus):
            pts = self._bus(rng)
            k = rng.choice((1, 2, 3, 3, 4, 5))
            for j in range(k):
                strands.append(offset(pts, (j - (k - 1) / 2) * 6.0))
        for (a, b), pts in sorted(self.links.items()):
            if a < b and len(pts) > 1 and rng.random() < 0.75:
                k = rng.choice((2, 3))
                side = rng.choice((-1, 1))
                for j in range(k):
                    strands.append(offset(pts, side * (17 + 6 * j)))
        f.L('over', mask=self.bmask)
        for p2 in strands:
            f.line(p2, 4.4, (6, 4, 10, 150))
        f.L('over', mask=self.bmask)
        for p2 in strands:
            f.line(p2, 2.3, A(COPPER, alpha))
            f.line(offset(p2, -0.7), 0.9, A(COPPER_HI, alpha * 0.55), cap=False)
            for e in (p2[0], p2[-1]):
                f.ell(e, 3.6, 3.6, A(COPPER, alpha), A(COPPER_HI, alpha), 1)
                f.ell(e, 1.3, 1.3, (8, 6, 12, 255))
            if len(p2) > 4 and rng.random() < 0.18:
                f.ell(p2[len(p2) // 2], 5, 5, None, A(TIN, 150), 1.6)
        # silkscreen dies: outline only, city shows through
        for i in range(22):
            u, v = rng.randrange(-20, 58), rng.randrange(-30, 34)
            if (u + v) % 2:
                v += 1
            c = lat(u, v)
            s = rng.choice((0.8, 1.0, 1.3))
            N, E, S_, Wc = gpt(c, -s, -s), gpt(c, s, -s), gpt(c, s, s), gpt(c, -s, s)
            f.poly([N, E, S_, Wc], None, A(COPPER_HI, 150), 1.4)
            for t in range(4):
                tt = (t + 0.5) / 4
                for (p0, p1, o) in ((Wc, S_, QV), (S_, E, PV)):
                    q = (p0[0] + (p1[0] - p0[0]) * tt, p0[1] + (p1[1] - p0[1]) * tt)
                    f.line([q, (q[0] + o[0] * .3, q[1] + o[1] * .3)], 1.6, A(COPPER, 170), cap=False)
            f.ell(gpt(c, -s * .6, -s * .6), 2, 2, A(COPPER_HI, 170))
        f.L('add', bloom=0.45, mask=self.bmask)
        for p2 in strands[::2]:
            f.line(p2, 1.4, (70, 34, 14))
        # data traffic: bright packets sliding on traces
        f.L('add', bloom=0.9, mask=self.bmask)
        tcol = [(120, 230, 255), (255, 255, 255), (255, 190, 90), (255, 120, 230)]
        for p2 in strands:
            if rng.random() < 0.5:
                p2 = rs(p2, 2)
                L = plen(p2)
                if L < 60:
                    continue
                s0 = rng.uniform(30, L - 10)
                col = rng.choice(tcol)
                for i in range(12):
                    q, _ = at(p2, s0 - i * 2.6)
                    t = 1 - i / 12
                    f.ell(q, 1.7, 1.7, tuple(int(c * t) for c in col))
        return strands

    # ------------------------------------------------------------ primary net on the real streets
    def network(self, dim=1.0):
        f = self.f
        seen = set()
        links = []
        for l in self.cd['links']:
            k = (l['a'], l['b'])
            if not l['polyline'] or k in seen:
                continue
            seen.add(k)
            links.append((self.links[k], l['locked']))
        f.L('over')
        for pts, lk in links:
            f.line(pts, 14 if not lk else 10, (4, 3, 8, 215))
        f.L('over')
        for pts, lk in links:
            w = 9 if not lk else 5
            f.line(pts, w, A(COPPER, 255 * dim))
            f.line(offset(pts, -1.4), 2.4, A(COPPER_HI, 255 * dim), cap=False)
            f.line(offset(pts, 2.2), 1.2, A((120, 58, 28), 255 * dim), cap=False)
        f.L('add', bloom=0.8)
        for pts, lk in links:
            f.line(pts, 3.0, (150, 80, 34) if not lk else (80, 44, 22))
        # via pads at every node
        f.L('over')
        for k, p in self.nodes.items():
            if k in ('burn_the_ledger',):
                continue
            f.ell(p, 8, 5.4, A(COPPER, 255), A(TIN, 255), 1.6)
            f.ell(p, 3, 2, (6, 4, 10, 255))

    # ------------------------------------------------------------ chips
    def chip(self, sid, state='healthy', tier=None, exploit=False, front=False):
        f = self.f
        c = self.nodes[sid]
        t = tier or self.sites[sid]['tier']
        s, h = TIER_SIZE[t], TIER_H[t]
        dead = state in ('DOWN', 'TAKEN', 'INFECTED')
        top = GRAPH_TOP if not dead else (26, 26, 34)
        left = GRAPH if not dead else (14, 14, 20)
        right = (28, 30, 42) if not dead else (18, 18, 26)
        pins = TIN if state == 'healthy' else ((120, 110, 120) if state == 'DOWN' else (70, 40, 70))
        f.L('shadow', blur=6)
        f.poly([gpt(c, -s - .3, -s + .3), gpt(c, s + .5, -s + .3), gpt(c, s + .5, s + .6), gpt(c, -s - .3, s + .6)],
               (0, 0, 0, 170))
        f.flush()
        f.L('over')
        edge = {'healthy': (170, 235, 255), 'DOWN': (130, 100, 110), 'TAKEN': (190, 80, 170), 'INFECTED': (190, 80, 170)}[state]
        tp = box(f, c, s, h, top, left, right, edge=edge, pins=pins, pin_n=5 if t == 1 else 6)
        ctr = (sum(p[0] for p in tp) / 4, sum(p[1] for p in tp) / 4)
        self._chip_top = {sid: (ctr, tp)}
        # die window + pin-1 dot
        f.poly([gpt((ctr[0], ctr[1] + 0), -s * .45, -s * .45), gpt(ctr, s * .45, -s * .45), gpt(ctr, s * .45, s * .45),
                gpt(ctr, -s * .45, s * .45)], (10, 12, 20) if not dead else (8, 8, 12))
        f.ell(gpt(ctr, -s * .72, -s * .72), 1.8, 1.2, (230, 240, 255) if not dead else (70, 60, 80))
        if state == 'healthy':
            f.L('add', bloom=1.0)
            f.poly([gpt(ctr, -s * .45, -s * .45), gpt(ctr, s * .45, -s * .45), gpt(ctr, s * .45, s * .45),
                    gpt(ctr, -s * .45, s * .45)], None, (50, 110, 150), 1.4)
            for i in range(t):
                q = gpt(ctr, -s * .2 + i * s * .2, 0)
                f.ell((q[0], q[1] - 0), 2.2, 1.6, (200, 250, 255))
            if exploit:
                f.poly([(ctr[0], ctr[1] - 6), (ctr[0] + 5, ctr[1]), (ctr[0], ctr[1] + 6), (ctr[0] - 5, ctr[1])],
                       (255, 190, 80))
        return ctr

    def corp_cpu(self):
        f = self.f
        c = self.nodes['the_genome_core']
        # LGA socket rings on the plaza under the helix
        pl = T((1190, 445))
        f.L('over')
        for k, rr in enumerate((120, 92, 64)):
            f.line(ground_ring(pl, rr), 5 - k, (10, 8, 14, 210))
        f.L('add', bloom=0.8)
        for k, rr in enumerate((120, 92, 64)):
            f.line(ground_ring(pl, rr), 2.0, [(130, 70, 34), (160, 90, 40), (190, 110, 60)][k])
            for i in range(0, 72):
                a = i / 72 * 2 * math.pi
                if k == 1:
                    p = (pl[0] + math.cos(a) * rr, pl[1] + math.sin(a) * rr * 0.643)
                    q = (pl[0] + math.cos(a) * (rr + 7), pl[1] + math.sin(a) * (rr + 7) * 0.643)
                    f.line([p, q], 1.2, (180, 120, 70), cap=False)
        # bus from the plaza to the corp CPU
        f.L('over')
        mid = (c[0] + 20, c[1] - 34)
        f.line([pl, (pl[0] - 70, pl[1] + 40), c], 13, (4, 3, 8, 215))
        f.line([pl, (pl[0] - 70, pl[1] + 40), c], 7, A(COPPER, 255))
        # the CPU itself
        f.L('shadow', blur=6)
        f.poly([gpt(c, -1.3, -1.0), gpt(c, 1.7, -1.0), gpt(c, 1.7, 1.7), gpt(c, -1.3, 1.7)], (0, 0, 0, 190))
        f.flush()
        f.L('over')
        tp = box(f, c, 1.05, 24, (60, 66, 76), (28, 32, 40), (40, 46, 58), edge=(210, 225, 240), pins=TIN, pin_n=9, ew=1.6)
        ctr = (sum(p[0] for p in tp) / 4, sum(p[1] for p in tp) / 4)
        f.poly([gpt(ctr, -.62, -.62), gpt(ctr, .62, -.62), gpt(ctr, .62, .62), gpt(ctr, -.62, .62)], (22, 26, 34), (150, 170, 190), 1.4)
        f.L('add', bloom=1.1)
        # the corp's heartbeat: a calm green-white pip array
        for i in range(3):
            for j in range(3):
                q = gpt(ctr, (i - 1) * .32, (j - 1) * .32)
                f.ell(q, 2.6, 1.7, (190, 255, 225))
        return ctr

    def home_chip(self, hp=44, hpmax=50, preview=0, burn=0.0, ring=True):
        """hand-soldered rebel chip patched onto the corp board: skewed board scrap, solder blobs, bodge wires"""
        f = self.f
        c = self.nodes['home']
        k = 1.45
        s = 1.15 * k
        f.L('shadow', blur=6)
        f.poly([gpt(c, -s - .4, -s + .2), gpt(c, s + .8, -s + .2), gpt(c, s + .8, s + .9), gpt(c, -s - .4, s + .9)], (0, 0, 0, 190))
        f.flush()
        f.L('over')
        sc = [gpt(c, -s - .5, -s * .6 - .5), gpt(c, s * .9, -s - .45), gpt(c, s + .6, s * .8), gpt(c, -s * .7, s + .55)]
        f.poly(sc, (14, 40, 34), (200, 215, 220), 2.4)
        for i in range(-5, 6):
            for j in range(-5, 6):
                q = gpt(c, i * .4 * k * .8, j * .4 * k * .8)
                f.ell(q, 1.8, 1.2, (4, 14, 12))
        tp = box(f, c, 0.72 * k, 18, (92, 100, 112), (40, 44, 54), (58, 64, 78), edge=(255, 255, 255), pins=TIN, pin_n=5, ew=2.0)
        ctr = (sum(p[0] for p in tp) / 4, sum(p[1] for p in tp) / 4)
        f.poly([gpt(ctr, -.45 * k, -.45 * k), gpt(ctr, .45 * k, -.45 * k), gpt(ctr, .45 * k, .45 * k), gpt(ctr, -.45 * k, .45 * k)], (30, 34, 44))
        for (a, b, r) in ((-.95, -.9, 5.5), (1.0, -.7, 6), (1.05, .95, 5), (-.9, 1.0, 6.2), (0.1, 1.25, 4.2)):
            q = gpt(c, a * k, b * k)
            f.ell(q, r, r * .75, (200, 210, 222), (255, 255, 255), 1)
        for (a, b, col) in ((-1.0, 0.1, (255, 255, 255)), (0.9, 0.4, (110, 230, 255))):
            p0 = gpt(c, a * k, b * k)
            p1 = (p0[0] + (-34 if a < 0 else 36), p0[1] - 26)
            p2 = (p1[0] + (-22 if a < 0 else 24), p1[1] + 8)
            f.line([p0, (p0[0] + (p1[0] - p0[0]) * .5, p1[1] - 14), p1, p2], 2.6, col)
        f.L('add', bloom=1.0)
        R = 108
        for i in range(hpmax):
            a = -math.pi / 2 + i / hpmax * 2 * math.pi
            p = (c[0] + math.cos(a) * R, c[1] + 6 + math.sin(a) * R * .643)
            q = (c[0] + math.cos(a) * (R + 11), c[1] + 6 + math.sin(a) * (R + 11) * .643)
            if i < hp - preview:
                col = (190, 245, 255)
            elif i < hp:
                col = TIERC['DAMAGED']
            else:
                col = (60, 50, 80)
            f.line([p, q], 3.0, col, cap=False)
        heart = (ctr[0], ctr[1] - 1)
        glyph(f, 'heart', heart, 10, (255, 255, 255), 2, (255, 255, 255))
        return ctr

    # ------------------------------------------------------------ marks
    def grease(self, c, kind='DOWN', r=22):
        f = self.f
        rng = random.Random(int(c[0] * 7 + c[1]))

        def stroke(p0, p1, col, w):
            for k in range(3):
                j = lambda: rng.uniform(-1.6, 1.6)
                f.line([(p0[0] + j(), p0[1] + j()), (p1[0] + j(), p1[1] + j())], w * (0.5 + 0.3 * k), A(col, 215), cap=True)
        if kind == 'DOWN':
            stroke((c[0] - r * .7, c[1] + r * .8), (c[0] + r * .7, c[1] - r * .8), (255, 96, 60), 5.5)
        else:
            stroke((c[0] - r * .8, c[1] - r * .8), (c[0] + r * .8, c[1] + r * .8), (255, 150, 215), 5.5)
            stroke((c[0] + r * .8, c[1] - r * .8), (c[0] - r * .8, c[1] + r * .8), (255, 150, 215), 5.5)

    def decay_clock(self, c, frac=0.75, hot=False):
        """quarter-ring on the ground showing how close a DOWN chip is to turning TAKEN"""
        f = self.f
        R = 40
        f.L('add', bloom=1.0)
        col = (255, 90, 60) if hot else (255, 150, 90)
        f.line(ground_ring(c, R, 40, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac), 3.2, col)
        a = -math.pi / 2 + 2 * math.pi * frac
        f.ell((c[0] + math.cos(a) * R, c[1] + math.sin(a) * R * .643), 3.6, 3.0, (255, 235, 200))

    # ------------------------------------------------------------ plum corrosion
    def infect(self, centers, radius, seed=3, strength=1.0, kill_traces=True):
        """Bloom A necrosis on the board: plum-black body, pink Voronoi veins, hot hairline front.
        centers in screen px; distances measured on the ground plane (y stretched by 1/0.643)."""
        f = self.f
        f.flush()
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        gy = yy / 0.643
        d = np.full((H, W), 9e9, np.float32)
        for (cx, cy), r in zip(centers, radius):
            d = np.minimum(d, np.hypot(xx - cx, gy - cy / 0.643) / r)
        n = fbm((H, W), seed, 5, 5)
        d = d + (n - 0.5) * 1.5 + (fbm((H, W), seed + 9, 3, 14) - 0.5) * 0.5
        inside = (d < 1).astype(np.float32)
        body = smooth(1 - d, 0.0, 0.05) * strength
        # voronoi veins in ground space
        rng = np.random.RandomState(seed)
        cell = 34
        gx = np.arange(0, W + cell, cell)
        gyv = np.arange(0, int(H / 0.643) + cell, cell)
        seeds = np.array([(x + rng.rand() * cell, y + rng.rand() * cell) for x in gx for y in gyv], np.float32)
        tree = cKDTree(seeds)
        sel = body > 0.01
        veins = np.zeros((H, W), np.float32)
        if sel.any():
            pts = np.stack([xx[sel], gy[sel]], 1)
            dd, _ = tree.query(pts, k=2)
            ve = np.clip(1 - (dd[:, 1] - dd[:, 0]) / 3.2, 0, 1)
            veins[sel] = ve
        front = np.exp(-(((d - 1.0) / 0.016) ** 2))
        front *= (d < 1.06)
        plum = np.array(PLUM, np.float32)
        a = f.a
        m = (body * 0.8)[..., None]
        a[:] = a * (1 - m) + (plum * (0.55 + 1.4 * n[..., None]) + np.array((22, 0, 24), np.float32) * np.clip(n[..., None] - 0.5, 0, 1) * 3) * m
        # veins glow (inside only, brightest toward the front)
        vg = (veins * body * (0.35 + 0.65 * np.clip(d, 0, 1) ** 2))[..., None]
        a[:] = a + vg * np.array(VEIN, np.float32) * 0.9
        a[:] = a + (front * strength)[..., None] * np.array(VEIN_HOT, np.float32)
        a[:] = np.clip(a, 0, 255)
        # bloom of the front
        g = Image.fromarray(np.clip((veins * body * 0.5 + front)[..., None] * np.array(VEIN, np.float32), 0, 255).astype(np.uint8))
        for r_, w_ in ((5, 0.6), (16, 0.5)):
            a[:] = 255 - (255 - a) * (255 - np.clip(np.asarray(g.filter(ImageFilter.GaussianBlur(r_)), np.float32) * w_, 0, 255)) / 255
        return body, d
