"""World assembly shared by all frames."""
import os, pickle
import numpy as np
from lib import *
import scene as SC
import ui
from daemon import *

WORK = 'D:/rc_scratch/tide_concepts/p2i_work/'
os.makedirs(WORK, exist_ok=True)

LANE_K = 21.0  # lane offset for known beams


class World:
    def __init__(self, scn='default', beat=None, forecast_beat='forecast'):
        self.scn = scn
        self.d = load(scn, forecast_beat if beat is None else beat)
        self.f = load(scn, forecast_beat)
        self.sites = {}
        for s in self.d['sites']:
            self.sites[s['id']] = dict(s, B=SC.site_base(s), crown=T(s['xy']))
        self.home = T(self.d['home']['xy'], SC.BASE_OFF)
        self.hq = T(self.d['solace_hq']['xy'], SC.BASE_OFF)
        self.routes = {}
        bm = {b['name']: b for b in self.f['beams']}
        names = {'K1': 'known0', 'K2': 'known1', 'A': 'cand0', 'B': 'cand1', 'C': 'cand2'}
        for r, n in names.items():
            if n in bm:
                b = bm[n]
                p0 = smooth(clean_poly(b['polyline']), 16)
                lane_ = {'K1': LANE_K, 'K2': -LANE_K}.get(r, 0.0)
                p = lane(extend_back(p0), lane_)
                self.routes[r] = dict(path=p, typ=b['type'], sites=b['site_path'], ext=520.0)
        # pass 2: D, N and E must be co-visible. K2 becomes an N beam; K3 is an authored E beam on real streets
        # (core -> t3_core -> t2_intel -> t1_a -> home, built from the plate's link polylines).
        if 'K2' in self.routes:
            self.routes['K2']['typ'] = 'N'
        try:
            self.routes['K3'] = self._author_k3('E', ['the_genome_core', 't3_core', 't2_intel', 't1_a', 'home'])
        except (IndexError, KeyError):
            pass
        self.hunters = []
        for n in ('hunter0', 'hunter1'):
            if n in bm:
                b = bm[n]
                self.hunters.append(dict(path=smooth(clean_poly(b['polyline']), 10), typ=b['type'], sites=b['site_path']))

    def _author_k3(self, typ, ids):
        raw = []
        for x, y in zip(ids[:-1], ids[1:]):
            lk = [l for l in self.f['links'] if {l['a'], l['b']} == {x, y}][0]
            seg = [np.array(p, float) for p in lk['polyline']]
            if raw:
                if np.hypot(*(seg[0] - raw[-1])) > np.hypot(*(seg[-1] - raw[-1])):
                    seg = seg[::-1]
            else:
                # first link must start at the core end: pick the end nearer the HQ
                hq = np.array(self.d['solace_hq']['xy'], float)
                if np.hypot(*(seg[0] - hq)) > np.hypot(*(seg[-1] - hq)):
                    seg = seg[::-1]
            seg = seg[1:] if raw else seg[1:]      # drop the node stub at the start of each link ...
            if x != ids[-2]:
                seg = seg[:-1]                      # ... and at its end (except the final approach to HOME)
            raw += seg
        p0 = smooth(clean_poly(raw), 16)
        p = lane(extend_back(p0), 0.0)
        return dict(path=p, typ=typ, sites=ids, ext=520.0)

    def visit(self, route, site_id):
        """arclength where a route passes a Site's base node."""
        r = self.routes[route]
        return nearest_s(r['path'], self.sites[site_id]['B'])

    def head_hq(self, route, run=120.0):
        return self.routes[route]['ext'] + run

    def end(self, route):
        return plen(self.routes[route]['path']) - 4


# ------------------------------------------------------------------ static layer cache
def static_layer(scn, w):
    f = WORK + 'hstatic_%s.npy' % scn
    if os.path.exists(f):
        return np.load(f)
    b = base_city(scn)
    cv = Cv(b)
    a = cv.img.astype(np.float32)
    np.save(f, a)
    return a


def new_canvas(w):
    return Cv(static_layer(w.scn, w))


# ------------------------------------------------------------------ route lines (the route a daemon will take)
def route_line(cv, path, typ, s0, s1, k=1.0, dead=False, w=2.6):
    pts = sub(path, s0, s1, 5)
    if len(pts) < 2:
        return
    col = TYPE_COL[typ] if not dead else (TYPE_COL[typ] * .35 + np.array([.2, .2, .25], np.float32))
    bb = pbox(pts, 14)
    ly = Lyr(bb)
    pl = [tuple(p) for p in pts]
    if typ == 'D':
        ly.line(pl, w, 255, dash=(11, 7))
    elif typ == 'N':
        ly.line(pl, w, 255, dash=(2.5, 6))
    else:
        ly.line(pl, w + .6, 255)
    # direction chevrons every ~64 px
    L = plen(pts)
    ch = Lyr(bb)
    s = 30.0
    while s < L - 10:
        p, ang = at(pts, s)
        u = np.array([math.cos(ang), math.sin(ang)])
        n = np.array([-u[1], u[0]])
        a, b, c = p - u * 6 + n * 6, p + u * 4, p - u * 6 - n * 6
        ch.line([tuple(a), tuple(b), tuple(c)], 2.2, 255)
        s += 64
    cv.neonL(ly, col, core=.95 * k, g1=(3, .55 * k), g2=(9, .3 * k))
    cv.neonL(ch, col * .7 + WHITE * .3, core=.9 * k, g1=(2, .4 * k), g2=None)


def draw_world(cv, w, states=None, programs=None, marks=None, home_kw=None, cage_kw=None, tower_alpha=.60, extra_after=None, idle=(), skip_marks=False):
    """states: {site_id: healthy|DOWN|TAKEN}; programs: {site_id: (verb, typ)}; marks drawn after each Site."""
    states = states or {}
    programs = programs or {}
    ck = dict(alpha=.58)
    ck.update(cage_kw or {})
    SC.solace_cage(cv, w.hq, **ck)
    items = [(s['B'][1], 'site', sid) for sid, s in w.sites.items()]
    items.append((w.home[1], 'home', 'home'))
    for _, kind, sid in sorted(items, key=lambda x: x[0]):
        if kind == 'home':
            SC.home_deck(cv, w.home, **(home_kw or {}))
            continue
        s = w.sites[sid]
        st = states.get(sid, 'healthy')
        if st == 'TAKEN':
            pass
        isidle = sid in idle
        SC.tower(cv, s['B'], s['tier'], st, seed=sum(map(ord, sid)) % 97, alpha=tower_alpha * (.5 if isidle else 1), hs=.45 if isidle else 1.0)
        pr = programs.get(sid)
        if pr:
            verb, typ = pr
            if verb == 'GUARD':
                ui.firewall(cv, s['B'], typ)
            elif verb == 'SHIFT':
                ui.decoy(cv, s['B'], typ, s['tier'])
            else:
                ui.tracer(cv, s['B'], typ)
        if skip_marks:
            pass
        elif st == 'DOWN':
            ui.grease_down(cv, (s['B'][0], s['B'][1] - 34), 26, seed=sum(map(ord, sid)) % 50)
        elif st == 'TAKEN':
            ui.grease_taken(cv, (s['B'][0], s['B'][1] - 30), 26, seed=sum(map(ord, sid)) % 50)
        if extra_after:
            extra_after(cv, sid, s)
