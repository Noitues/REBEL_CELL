"""Builds every frame of the Circuit Board direction. Usage: python build.py [frame ...]  (default: all)"""
import sys, math, random, os
import numpy as np
from lib import *
from scene import Scene
from ui import *

FR = OUT + 'frames/'
_nodes, _links = build_graph(load_coords('default', 'forecast'))
NODES = {k: T(v) for k, v in _nodes.items()}
os.makedirs(FR, exist_ok=True)

ROUTES = {
    'K1': ['the_genome_core', 't3_c', 't2_virus', 't1_c', 't1_b', 'home'],
    'K2': ['the_genome_core', 't3_b', 't2_breach', 't1_b', 't1_c', 'home'],
    'A': ['the_genome_core', 't3_b', 't2_breach', 't1_b', 't1_a', 'home'],
    'H0': ['t2_intel', 't2_breach'],
    'H1': ['t3_core', 't3_b'],
}
TYPES = {'K1': 'D', 'K2': 'D', 'B': 'D', 'C': 'N', 'A': 'E', 'H0': 'E', 'H1': 'E'}
DEF_DEFAULT = [('t1_a', 'N', 'GUARD'), ('t1_b', 'E', 'SHIFT'), ('t1_c', 'D', 'GUARD')]
HAND = [('fuse', 'D'), ('cap', 'N'), ('jumper', 'E'), ('fuse', 'N'), ('fuse', 'E'), ('jumper', 'D'), ('fuse', 'D')]
KIND = {'GUARD': 'fuse', 'SHIFT': 'jumper', 'JAM': 'cap'}


class Stage:
    """one raid-board frame under construction"""

    def __init__(self, states=None, defs=(), hp=44, preview=0, infect=None, blown=(), sec=True, burn=None, marks=True):
        sc = self.sc = Scene()
        self.f = sc.f
        self.defs = list(defs)
        self.states = states if states is not None else {'t1_a': 'DOWN'}
        sc.board() if sec else None
        sc.network()
        KEEP = {'K1': ('t1_c',), 'K2': ('t1_c',), 'A': ('t1_b',)}
        self.paths = {}
        for k, v in ROUTES.items():
            kp = KEEP.get(k, ())
            self.paths[k] = route(v, _nodes, _links, keep_sites=kp)
        for bm in load_coords('default', 'forecast')['beams']:
            if bm['name'] in ('hunter0', 'hunter1'):
                self.paths['H' + bm['name'][-1]] = [T(p) for p in clean_spurs(bm['polyline'])]
        if infect:
            sc.infect(*infect)
        sc.corp_cpu()
        draws = []
        for sid, s in sc.sites.items():
            st = self.states.get(sid, 'healthy')
            draws.append((sc.nodes[sid][1], 'chip', sid, st))
        for sid, t, verb in self.defs:
            c = sc.nodes[sid]
            draws.append((c[1] + 22, 'comp', sid, (t, verb)))
        draws.sort(key=lambda d: d[0])
        self.top = {}
        for _, kind, sid, arg in draws:
            if kind == 'chip':
                sc.chip(sid, arg, exploit=sc.sites[sid]['exploit'])
            else:
                t, verb = arg
                c = gpt(sc.nodes[sid], 0.0, 1.9)
                self.top[sid] = component(sc.f, c, KIND[verb], t, blown=sid in blown)
        sc.home_chip(hp=hp, preview=preview)
        if marks:
            for sid, st in self.states.items():
                if st == 'DOWN':
                    sc.grease(gpt(sc.nodes[sid], 0, 0), 'DOWN')
                elif st in ('TAKEN', 'INFECTED'):
                    sc.grease(gpt(sc.nodes[sid], 0, 0), 'TAKEN')

    def save(self, name):
        self.f.img().save(FR + name + '.png')
        print('saved', name)


def ground_halo(f, c, col, r=34, w=3.4, bloom=1.4):
    f.L('add', bloom=bloom)
    f.line(ground_ring(c, r), w, col)
    f.line(ground_ring(c, r + 7), w * .5, tuple(int(v * .6) for v in col))


def reticle(f, c, r=40, col=(255, 255, 255), w=3.0, lock=0.0):
    """target bracket on the ground plane"""
    f.L('add', bloom=1.3)
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        p0 = (c[0] + math.cos(a - .35) * r, c[1] + math.sin(a - .35) * r * .643)
        pm = (c[0] + math.cos(a) * r, c[1] + math.sin(a) * r * .643)
        p1 = (c[0] + math.cos(a + .35) * r, c[1] + math.sin(a + .35) * r * .643)
        f.line([p0, pm, p1], w, col, cap=False)


def probe(f, c, tier, num=None, up=62, dx=0):
    """oscilloscope probe pinned to a chip: pin, clip and a reading tile (tier badge + number)"""
    f.L('over')
    top = (c[0] + dx, c[1] - up)
    f.line([c, (c[0] + dx * .5, c[1] - up * .45), top], 3.0, (6, 4, 12, 255))
    f.line([c, (c[0] + dx * .5, c[1] - up * .45), top], 1.4, (230, 235, 245, 255))
    f.poly([(c[0] - 5, c[1] + 2), (c[0] + 5, c[1] + 2), (c[0], c[1] - 9)], (230, 235, 245), (6, 4, 12), 1.4)
    f.rr((top[0] - 29, top[1] - 34, top[0] + 29, top[1] + 8), 9, (6, 14, 24, 245), TIERC[tier], 2.6)
    tier_badge(f, (top[0] - (10 if num is not None else 0), top[1] - 13), tier, 12)
    if num is not None:
        f.txt((top[0] + 16, top[1] - 14), str(num), 24, TIERC[tier], mono=True, stroke=1.5)


def sealed_header(st, states, c=None):
    """3-pin keyed header next to the corp CPU: each pin = a lock tile with its letter. states: locked/open/dead per A,B,C"""
    f = st.f
    hq = st.sc.nodes['the_genome_core']
    c = c or (hq[0] - 96, hq[1] + 112)
    f.L('shadow', blur=4)
    f.rr((c[0] - 118, c[1] - 6, c[0] + 118, c[1] + 62), 8, (0, 0, 0, 170))
    f.flush()
    f.L('over')
    f.rr((c[0] - 112, c[1] - 12, c[0] + 112, c[1] + 54), 8, (18, 18, 26, 245), (170, 180, 200), 2)
    for i, (letter, stt, t) in enumerate(states):
        x = c[0] - 74 + i * 74
        col = {'locked': (190, 190, 215), 'open': TYPE_COL.get(t, WHITE), 'dead': (90, 90, 110)}[stt]
        f.rr((x - 30, c[1] - 6, x + 30, c[1] + 48), 8, (8, 10, 20), col, 2.4)
        glyph(f, 'unlock' if stt == 'open' else 'lock', (x - 9, c[1] + 18), 11, col, 2.4)
        f.txt((x + 16, c[1] + 18), letter, 22, col, mono=True)
        for k in range(3):   # gold pins
            f.line([(x - 12 + k * 12, c[1] + 48), (x - 12 + k * 12, c[1] + 58)], 3, (230, 200, 120), cap=False)
        if stt == 'open':
            wave_chip(f, (x, c[1] - 24), t, 11)
    f.L('add', bloom=0.7)
    for i, (letter, stt, t) in enumerate(states):
        x = c[0] - 74 + i * 74
        if stt == 'open':
            f.rr((x - 30, c[1] - 6, x + 30, c[1] + 48), 8, None, TYPE_COL[t], 2.4)


def tally_fly(st, frm, to_c, n=2, t=0.5):
    """INFECTED cards flying from lost chips to the HUD tally"""
    f = st.f
    f.L('add', bloom=1.2)
    for i, a in enumerate(frm):
        q = (a[0] + (to_c[0] + i * 22 - a[0]) * t, a[1] + (to_c[1] - a[1]) * t - math.sin(t * math.pi) * 90)
        for k in range(14):
            tt = max(0, t - k * 0.02)
            qq = (a[0] + (to_c[0] + i * 22 - a[0]) * tt, a[1] + (to_c[1] - a[1]) * tt - math.sin(tt * math.pi) * 90)
            f.ell(qq, 4 - k * .22, 4 - k * .22, (int(255 * (1 - k / 14)), int(90 * (1 - k / 14)), int(190 * (1 - k / 14))))
    f.L('over')
    for i, a in enumerate(frm):
        q = (a[0] + (to_c[0] + i * 22 - a[0]) * t, a[1] + (to_c[1] - a[1]) * t - math.sin(t * math.pi) * 90)
        f.rr((q[0] - 15, q[1] - 21, q[0] + 15, q[1] + 21), 5, (60, 14, 62), (255, 120, 200), 2.4)
        glyph(f, 'x', q, 8, (255, 150, 215), 2.4)


def sparks(f, c, n=40, r0=10, r1=70, seed=1, cols=((255, 255, 255), (255, 220, 120), (255, 150, 60))):
    rng = random.Random(seed)
    f.L('add', bloom=1.2)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        r_a, r_b = rng.uniform(r0, r1 * .6), rng.uniform(r1 * .6, r1)
        p0 = (c[0] + math.cos(a) * r_a, c[1] + math.sin(a) * r_a * .75)
        p1 = (c[0] + math.cos(a) * r_b, c[1] + math.sin(a) * r_b * .75)
        f.line([p0, p1], rng.uniform(1.4, 3.0), rng.choice(cols), cap=False)


def bits(f, c, n=24, r=90, seed=2, col=(120, 230, 255), size=13):
    rng = random.Random(seed)
    f.L('over')
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(r * .25, r)
        q = (c[0] + math.cos(a) * d, c[1] + math.sin(a) * d * .8 - rng.uniform(0, 30))
        f.txt(q, rng.choice('01'), rng.uniform(size * .7, size * 1.3), (*col, int(255 * (1 - d / r * .6))), mono=True)


def smoke(f, c, n=9, seed=3):
    rng = random.Random(seed)
    f.L('shadow', blur=9)
    for i in range(n):
        x = c[0] + rng.uniform(-10, 14) + i * 3
        y = c[1] - 10 - i * 22
        r = 12 + i * 4.5
        f.ell((x, y), r, r * .85, (18, 14, 24, int(205 - i * 11)))
    f.flush()
    f.L('add', bloom=0.8)
    f.ell((c[0], c[1] - 8), 16, 9, (255, 110, 30))


def damage_num(f, c, text, col):
    f.L('over')
    f.txt((c[0] + 3, c[1] + 4), text, 92, (0, 0, 0, 190), stroke=0)
    f.txt(c, text, 92, col, stroke=5, scol=(10, 6, 18))
    f.L('add', bloom=1.2)
    f.txt(c, text, 92, tuple(int(v * .55) for v in col))


def go_button(f, c=(1822, 1000), col=(110, 226, 255), picked=False):
    f.L('over')
    f.ell(c, 42, 42, (6, 16, 26, 245), col, 3.4)
    glyph(f, 'dchev', c, 18, col, 4)


def deck_slot(f, c=(1700, 960)):
    f.L('over')
    for i in range(3):
        paste(f, card('fuse', 'D', 70, 94, dim=True), (c[0] + i * 4, c[1] - i * 4), 0, 1.0, shadow=0.0)


# ====================================================================== frames
def beams_known(st, alpha=1.0, upto=None):
    f = st.f
    beam(f, st.paths['K1'], 'D', lane=-9, alpha=alpha, s1=upto)
    beam(f, st.paths['K2'], 'D', lane=9, alpha=alpha, s1=upto)


def sealed_bands(st, alpha=1.0, which='ABC', hunter=True):
    f = st.f
    if 'A' in which:
        noise_band(f, offset(st.paths['A'], 26), 7, 1.1, 5, alpha * 0.8)
    if 'B' in which:
        noise_band(f, offset(st.paths['K1'], -26), 7, 1.1, 6, alpha * 0.8)
    if 'C' in which:
        noise_band(f, offset(st.paths['K2'], 26), 7, 1.1, 7, alpha * 0.8)


def hunter_ghosts(st, lock=None, alpha=1.0):
    """the HUNTER: two candidate streets as ghost dotted traces with a scanning reticle; lock = 0/1 picks one"""
    f = st.f
    for i, k in enumerate(('H0', 'H1')):
        p = st.paths[k]
        on = lock is None or lock == i
        f.L('add', bloom=0.9)
        if lock is None:
            f.dline(p, 4.2, (255, 245, 150), 9, 8)
        elif on:
            pass
        else:
            f.dline(p, 1.6, (70, 66, 90), 4, 10)
    return


