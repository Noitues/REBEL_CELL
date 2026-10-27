"""P1 spec builder: one Blender spec (JSON) per beat from the H2 world (routes, sites, home, hq) and the raid camera.
python p1_spec.py <beat> [--lo]   -> WORK/<beat>/spec.json
The same RouteW / site objects feed the 2D overlay (p1_comp) so 3D and UI share one set of screen coordinates."""
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p1lib as L
import p1_tex

LEN = {'D': 16.0, 'N': 12.0, 'E': 16.0}
W_BU = {'D': 4.2, 'N': 4.4, 'E': 4.8}
TOW_H = {1: 27.0, 2: 35.0, 3: 44.0}
TOW_A = {1: 4.6, 2: 4.2, 3: 4.8}
TIERC = p1_tex.TIERC
TIER_R = {'UNTOUCHED': 9.5, 'HOLDS': 10.5, 'SITES_LOST': 10.5, 'DAMAGED': 11.5, 'BREACHED': 12.5}
BEAMC = {'D': '4690FF', 'N': 'FF40D6', 'E': 'FFEE3A'}
SLATE = '7C88AE'


def polys(typ):
    sys.path.insert(0, L.H2)
    import glyphs
    return glyphs.type_polys(typ)


class RouteW:
    """a route in screen px + world (Blender coords), with arclength maps."""

    def __init__(self, r, lift=0.7):
        self.typ = r['typ']
        self.sp = np.asarray(r['path'], float)
        self.gw = L.screen_to_ground(self.sp, lift=lift)       # Godot world
        self.bw = L.g2b(self.gw)                                # Blender
        self.cs = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(self.sp, axis=0).T))])
        self.cw = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(self.bw[:, :2], axis=0).T))])
        self.ext = r['ext']
        self.sites = r['sites']

    def w_of_s(self, s):
        """world arclength for screen arclength s"""
        return float(np.interp(s, self.cs, self.cw))

    def pos(self, s):
        sw = self.w_of_s(s)
        return np.array([np.interp(sw, self.cw, self.bw[:, i]) for i in range(3)])

    def tan(self, s, d=2.0):
        a = self.pos(max(s - d * 3, 0)); b = self.pos(min(s + d * 3, self.cs[-1]))
        t = b[:2] - a[:2]
        return t / max(np.hypot(*t), 1e-6)

    def scr(self, s):
        return np.array([np.interp(s, self.cs, self.sp[:, 0]), np.interp(s, self.cs, self.sp[:, 1])])


class Beat:
    def __init__(self, name, lo=False):
        self.name = name
        self.w = L.load_world()
        self.lo = lo
        self.spec = dict(out=L.WORK + name + '/b', res=[960, 540] if lo else [1920, 1080], samples=24 if lo else 64, spill_samples=48 if lo else 128,
                         device='GPU', hf=L.WORK + 'hf15.npz', beauty=L.WORK + 'depth15/window_nonet.png',
                         cam=dict(size=L.SIZE, right=list(L.RIGHT), up=list(L.UP), back=list(L.BACK), pos=list(L.O)),
                         passes=['world_occ', 'world_ghost', 'spill'], moon=dict(sun=1.6, dir=[-0.55, 0.35, -0.62], col='9DB4FF', sky=0.35, sky_col='1C2A5C'),
                         homes=[], ribbons=[], towers=[], cages=[], rings=[], blocks=[], walls=[], domes=[], heads=[], glows=[], shards=[], bloom=[], lights=[])
        os.makedirs(L.WORK + name, exist_ok=True)
        self.routes = {k: RouteW(v) for k, v in self.w.routes.items()}
        self.ui = {}            # 2D overlay instructions (screen px), consumed by p1_comp

    # ------------------------------------------------------------ geometry helpers
    def site_g(self, sid):
        s = self.w.sites[sid]
        return L.screen_to_ground(s['B'].reshape(1, 2))[0]

    def site_b(self, sid):
        return L.g2b(self.site_g(sid))[0]

    def home_b(self):
        return L.g2b(L.screen_to_ground(self.w.home.reshape(1, 2)))[0]

    # ------------------------------------------------------------ elements
    def towers(self, dim=None, down=(), taken=(), strong=(), skip=()):
        dim = dim or {}
        for sid, s in self.w.sites.items():
            if sid in skip:
                continue
            tier = s['tier']
            b = self.site_b(sid)
            k = dim.get(sid, 1.0)
            if sid in strong:
                k = 1.5
            st = 'down' if sid in down else ('taken' if sid in taken else 'healthy')
            self.spec['towers'].append(dict(id=sid, pos=b.tolist(), tier=tier, a=TOW_A[tier], h=TOW_H[tier], state=st, col=SLATE,
                                            strength=3.0 * k, wire_strength=3.2 * k, wire_r=0.085, spine_strength=5.0 * k, pad_strength=2.0 * k))

    def cage(self, k=1.0):
        # the Solace helix foot (screen px 1658,457 on the platform) and its ICE cage
        g = L.screen_to_ground(np.array([[1650.0, 470.0]]))[0]
        g[1] = 13.8
        b = L.g2b(g.reshape(1, 3))[0]
        self.spec['cages'].append(dict(pos=b.tolist(), r=24.0, h=92.0, r_top=22.0, strength=2.0 * k, wire_strength=2.2 * k))
        self.ui['cage_screen'] = [1650, 470]

    def ribbon(self, rid, s0=None, s1=None, k=1.0, w=None, alpha=1.0, grp='world', head=True):
        R = self.routes[rid]
        self.ui.setdefault('route_px', {})[rid] = R.sp[R.cs >= 0].tolist()
        s0 = R.ext if s0 is None else s0
        s1 = R.cs[-1] if s1 is None else s1
        self.spec['ribbons'].append(dict(id=rid + ('_%d' % len(self.spec['ribbons'])), typ=R.typ, pts=R.bw.tolist(), w=w or W_BU[R.typ], h=0.5,
                                         s0=R.w_of_s(s0), s1=R.w_of_s(s1), lenbu=LEN[R.typ], tex=L.WORK + 'tex/ribbon_%s.png' % R.typ,
                                         strength=4.5 * k, alpha=alpha, grp=grp))

    def head(self, rid, s, scale=9.0, k=1.0, col=None, mode='full'):
        R = self.routes[rid]
        p = R.pos(s)
        t = R.tan(s)
        # heads are the H6 sprite layer (p1_heads): screen position + heading only
        a = R.scr(max(s - 6, 0)); b = R.scr(s + 6)
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        sc = R.scr(s)
        self.ui.setdefault('heads', []).append(dict(typ=R.typ, x=float(sc[0]), y=float(sc[1]), ang=float(ang), k=float(min(k, 1.0))))
        return p, t

    def ring(self, sid, tier, k=1.0, r=None, strong=True):
        b = self.site_b(sid)
        r = r or TIER_R[tier]
        c = TIERC[tier]
        self.spec['rings'].append(dict(id=sid + '_o', pos=b.tolist(), r=r, w=1.5, col=c, strength=7.0 * k, z=0.5, fill=1.6 * k, fill_pow=1.2))
        self.spec['rings'].append(dict(id=sid + '_i', pos=b.tolist(), r=r * 0.72, w=0.5, col=c, strength=4.0 * k, z=0.5))

    def block(self, rid, s, tier, k=1.0, length=9.0, across=11.5):
        R = self.routes[rid]
        p = R.pos(s)
        t = R.tan(s)
        n = np.array([-t[1], t[0]])
        self.spec['blocks'].append(dict(id='%s_%s' % (rid, tier), pos=p.tolist(), along=[n[0], n[1], 0], across=[t[0], t[1], 0], len=across, wid=length,
                                        tex=L.WORK + 'tex/block_%s.png' % tier, strength=5.5 * k))

    def wall(self, sid, typ, k=1.0, w=11.0, h=14.0, dirv=(0.7, 0.7)):
        b = self.site_b(sid)
        self.spec['walls'].append(dict(id=sid, pos=b.tolist(), dir=[dirv[0], dirv[1], 0], w=w, h=h, tex=L.WORK + 'tex/wall_%s.png' % typ, strength=4.0 * k))

    def light(self, pos, power, col, size=2.0):
        self.spec['lights'].append(dict(pos=list(pos), power=power, col=col, size=size))

    def save(self):
        json.dump(self.spec, open(L.WORK + self.name + '/spec.json', 'w'))
        json.dump(self.ui, open(L.WORK + self.name + '/ui.json', 'w'), default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
        return L.WORK + self.name + '/spec.json'


RUN = {'K1': 60, 'K2': 400, 'K3': 215}
TARGET = {'K1': ('t1_c', 'HOLDS'), 'K2': ('t1_b', 'SITES_LOST'), 'K3': ('t2_intel', 'UNTOUCHED')}
PROGRAMS = {'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}


def forecast(lo=False):
    B = Beat('forecast', lo)
    w = B.w
    on_route = {'t3_c', 't2_virus', 't1_c', 't3_b', 't2_breach', 't1_b', 't3_core', 't2_intel', 't1_a'}
    dim = {sid: (1.0 if sid in on_route else 0.35) for sid in w.sites}
    B.towers(dim=dim, down=('t1_a',))
    B.cage()
    for rid in ('K1', 'K2', 'K3'):
        R = B.routes[rid]
        sid, tier = TARGET[rid]
        s_stop = w.visit(rid, sid)
        B.ribbon(rid, R.ext, s_stop + 20)
        B.ribbon(rid, s_stop + 40, None, k=0.25, alpha=0.5)      # the dead trail beyond the stop
        B.ring(sid, tier)
        B.block(rid, s_stop - 2, tier)
        B.head(rid, R.ext + RUN[rid])
    B.wall('t1_c', 'D')
    return B


if __name__ == '__main__':
    name = sys.argv[1]
    lo = '--lo' in sys.argv
    B = globals()[name](lo)
    for a in sys.argv:
        if a.startswith('--border='):
            B.spec['border'] = [int(v) for v in a.split('=')[1].split(',')]
        if a.startswith('--spp='):
            B.spec['samples'] = int(a.split('=')[1])
        if a.startswith('--passes='):
            B.spec['passes'] = a.split('=')[1].split(',')
        if a.startswith('--device='):
            B.spec['device'] = a.split('=')[1]
    print(B.save())
