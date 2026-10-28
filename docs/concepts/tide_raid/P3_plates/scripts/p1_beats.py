"""P1 beats: the seven golden plates as Blender specs + UI instructions.
python p1_beats.py <beat> [--border=x0,y0,x1,y1] [--spp=N] [--passes=a,b] [--lo]
beats: plan forecast reveal impact home_hit aftermath city_lost"""
import sys, os, math, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p1lib as L
import p1_spec as S
from p1_spec import Beat, TIERC, BEAMC

RUN = {'K1': 60, 'K2': 400, 'K3': 215}
HERO = {'plan': 'K3', 'forecast': 'K1', 'reveal': 'K3', 'impact': 'K1', 'home_hit': 'K2'}
TARGET = {'K1': ('t1_c', 'HOLDS'), 'K2': ('t1_b', 'SITES_LOST'), 'K3': ('t2_intel', 'UNTOUCHED')}
ON_ROUTE = {'t3_c', 't2_virus', 't1_c', 't3_b', 't2_breach', 't1_b', 't3_core', 't2_intel', 't1_a'}
WARM = 'F6F1E4'
DMG = TIERC['DAMAGED']
RECT = [(-1.0, -0.32), (1.0, -0.32), (1.0, 0.32), (-1.0, 0.32)]
HEX = [(math.cos(math.radians(60 * k)), math.sin(math.radians(60 * k))) for k in range(6)]
TRI = [(1.0, 0.0), (-0.6, 0.7), (-0.6, -0.7)]


# ------------------------------------------------------------------ Beat extensions
def home_deck(B, hp=44, hpmax=50, preview=0, hit=0, k=1.0, fly_seed=3, dmg_col=None, ring_r=19.0, crack=False):
    """P2 HOME: the brightest object in frame. Hex deck + a white ring (ink under-stroke) + a PHYSICAL radial tick gauge (one 3.2 x 1.0 BU tick per HP,
    a longer major tick every 10th) + a warm pool. preview: next `preview` ticks outlined amber. hit: that many ticks fly off."""
    hb = B.home_b()
    B.spec['homes'].append(dict(pos=hb.tolist(), r=8.0, h=9.0, col='FFFFFF', strength=2.6 * k, wire_strength=6.0 * k, pad_strength=1.2 * k, glow='FFF1DC'))
    B.ui['home_b'] = hb.tolist()
    B.ui['home_px'] = [float(B.w.home[0]), float(B.w.home[1])]
    B.spec['glows'].append(dict(pos=hb.tolist(), r=24.0, col='FFD9A8', strength=0.3 * k, power=1.5, z=0.35))
    B.spec['rings'].append(dict(id='home_ink', pos=hb.tolist(), r=24.6, w=5.0, col='06040F', strength=1.0, z=0.46))
    B.spec['rings'].append(dict(id='home_ring', pos=hb.tolist(), r=22.0, w=2.2, col='FFFFFF', strength=(3.6 if not hit else 3.0) * k, z=0.5))
    B.spec['rings'].append(dict(id='home_base', pos=hb.tolist(), r=17.0, w=0.5, col='F6F1E4', strength=6.0 * k, z=0.5))
    rng = np.random.RandomState(fly_seed)
    lit_n = hp
    for i in range(hpmax):
        ang = math.radians(-90 + 360 * i / hpmax)
        out = np.array([math.cos(ang), math.sin(ang)])
        major = (i % 10 == 0)
        sc = 2.1 if major else 1.6
        c = hb + np.array([out[0] * (ring_r + (0.5 if major else 0)), out[1] * (ring_r + (0.5 if major else 0)), 0.0])
        if i < lit_n:
            col, st = WARM, 7.0 * k
            pos, tilt, roll, z = c, 0.0, 0.0, 0.5
        elif i < lit_n + hit:
            col, st = DMG, 14.0 * k
            dist = rng.uniform(5, 22)
            pos = c + np.array([out[0] * dist, out[1] * dist, rng.uniform(5, 20)])
            tilt, roll, z = rng.uniform(-1.2, 1.2), rng.uniform(-1.2, 1.2), 0.0
        elif i < lit_n + hit + preview:
            col, st = DMG, 3.4 * k
            pos, tilt, roll, z = c, 0.0, 0.0, 0.5
        else:
            col, st = '2A3150', 0.9 * k
            pos, tilt, roll, z = c, 0.0, 0.0, 0.45
        B.spec['shards'].append(dict(poly=RECT, scale=sc, thick=0.4, pos=pos.tolist(), dir=[out[0], out[1]], z=z, col=col, strength=st, tilt=tilt, roll=roll))


def fog(B, rid, k=1.0, seed=1.0, s0=None, s1=None):
    R = B.routes[rid]
    s0 = R.ext + 10 if s0 is None else s0
    s1 = R.cs[-1] - 6 if s1 is None else s1
    B.spec['ribbons'].append(dict(id='fog_' + rid, kind='fog', typ='N', pts=R.bw.tolist(), w=17.0, h=0.9, s0=R.w_of_s(s0), s1=R.w_of_s(s1), lenbu=8.0,
                                  col='9C8CFF', strength=8.0 * k, seed=seed))


def burst(B, pos, col, k=1.0, r=14.0, shards=26, seed=1, light=True, core=WARM):
    rng = np.random.RandomState(seed)
    p = np.array(pos, float)
    B.spec['glows'].append(dict(pos=p.tolist(), r=r * 1.9, col=col, strength=2.4 * k, power=1.6, z=0.8))
    B.spec['glows'].append(dict(pos=p.tolist(), r=r * 0.55, col=core, strength=4.5 * k, power=3.0, z=0.9))
    for j in range(18):
        a = 2 * math.pi * j / 18 + rng.uniform(-0.08, 0.08)
        ln = rng.uniform(r * 1.2, r * 2.8)
        B.spec['shards'].append(dict(poly=[(0.0, -0.05), (1.0, -0.012), (1.0, 0.012), (0.0, 0.05)], scale=ln, thick=0.25, pos=[p[0], p[1], p[2] + 0.2], dir=[math.cos(a), math.sin(a)], z=0.9, col=core if j % 3 == 0 else col, strength=9.0 * k, tilt=0.0, roll=0.0))
    B.spec['rings'].append(dict(id='bs_o%d' % seed, pos=p.tolist(), r=r * 1.25, w=1.1, col=col, strength=12.0 * k, z=0.8))
    B.spec['rings'].append(dict(id='bs_i%d' % seed, pos=p.tolist(), r=r * 0.7, w=0.8, col=core, strength=14.0 * k, z=0.9))
    polys_ = [HEX, TRI, RECT]
    for i in range(shards):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(r * 0.3, r * 1.6)
        h = rng.uniform(1.0, r * 1.2)
        q = p + np.array([math.cos(a) * d, math.sin(a) * d, h])
        B.spec['shards'].append(dict(poly=polys_[i % 3], scale=rng.uniform(0.5, 1.7), thick=0.3, pos=q.tolist(), dir=[math.cos(a), math.sin(a)], z=0.0,
                                     col=(core if rng.rand() < 0.3 else col), strength=rng.uniform(8, 18) * k, tilt=rng.uniform(-1.4, 1.4), roll=rng.uniform(-1.4, 1.4)))
    if light:
        B.light((p[0], p[1], p[2] + 8.0), 18000.0 * k, col, size=3.0)


def lime_ring(B, sid, k=1.0):
    b = B.site_b(sid)
    B.spec['rings'].append(dict(id='lime_' + sid, pos=b.tolist(), r=11.5, w=1.3, col='C6FF2E', strength=8.0 * k, z=0.55, fill=1.0, ghost=0.55))


def tier_target(B, rid, s_stop, tier, k=1.0, ring=True, block=True, ghost=0.55):
    sid = TARGET[rid][0]
    if ring:
        B.ring(sid, tier, k=k, ghost=ghost)
    if block:
        B.block(rid, s_stop - 2, tier, k=k, ghost=ghost)


def base(B, down=('t1_a',), taken=(), dim=None, strong=()):
    dim = dim if dim is not None else {sid: 1.0 for sid in B.w.sites}
    B.towers(dim=dim, down=down, taken=taken, strong=strong)
    B.cage()


# ------------------------------------------------------------------ the seven beats
def plan(lo=False):
    B = Beat('plan', lo)
    w = B.w
    base(B)
    for rid in ('K1', 'K2', 'K3'):
        R = B.routes[rid]
        hero = (rid == HERO['plan'])
        B.ribbon(rid, R.ext, None, k=(1.25 if hero else 0.55), wk=(1.15 if hero else 0.72))
        B.head(rid, R.ext + RUN[rid], k=1.0)
        B.ui.setdefault('hero', {})['plan'] = HERO['plan']
    B.wall('t1_c', 'D')
    lime_ring(B, 't2_intel')
    home_deck(B, 44, 50)
    B.ui.update(beat='plan')
    return B


def forecast(lo=False):
    B = Beat('forecast', lo)
    w = B.w
    base(B)
    for rid in ('K1', 'K2', 'K3'):
        R = B.routes[rid]
        sid, tier = TARGET[rid]
        s_stop = w.visit(rid, sid)
        hero = (rid == HERO['forecast'])
        B.ribbon(rid, R.ext, s_stop + 20, k=(1.3 if hero else 0.62), wk=(1.2 if hero else 0.75))
        if hero:
            B.ribbon(rid, s_stop + 40, None, k=0.14, alpha=0.4, wk=0.8)
        tier_target(B, rid, s_stop, tier, ghost=(0.55 if hero else 0.0))
        B.head(rid, R.ext + RUN[rid])
        B.ui.setdefault('stops', {})[rid] = dict(site=sid, tier=tier, s=s_stop)
    B.ui.setdefault('hero', {})['forecast'] = HERO['forecast']
    B.wall('t1_c', 'D')
    home_deck(B, 44, 50, preview=6)
    B.ui.update(beat='forecast')
    return B


def reveal(lo=False):
    B = Beat('reveal', lo)
    w = B.w
    base(B, strong=('t2_intel',))
    for i, rid in enumerate(('A', 'B', 'C')):
        fog(B, rid, k=1.0 if rid != 'A' else 1.3, seed=3.0 + i * 5)
    # the known E beam, full
    R = B.routes['K3']
    sid, tier = TARGET['K3']
    s_stop = w.visit('K3', sid)
    B.ribbon('K3', R.ext, s_stop + 20)
    B.ribbon('K3', s_stop + 40, None, k=0.22, alpha=0.45)
    B.head('K3', R.ext + 300)
    B.ui.setdefault('stops', {})['K3'] = dict(site=sid, tier=tier, s=s_stop)
    # hunter: two candidate streets (white dashes), one E ghost head each
    for i, h in enumerate(w.hunters):
        pth = np.asarray(h['path'], float)
        gw = L.screen_to_ground(pth, lift=0.7)
        bw = L.g2b(gw)
        cs = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(bw[:, :2], axis=0).T))])
        locked = (i == 0)
        B.spec['ribbons'].append(dict(id='hunt%d' % i, typ='E', pts=bw.tolist(), w=2.2 if locked else 1.4, h=0.4, s0=0.0, s1=float(cs[-1]), lenbu=10.0,
                                      tex=L.WORK + 'tex/hunter.png', strength=(7.0 if locked else 1.6), alpha=1.0))
        B.ui.setdefault('hunter_px', []).append(pth.tolist())
    home_deck(B, 44, 50)
    B.ui.update(beat='reveal')
    return B


def impact(lo=False):
    B = Beat('impact', lo)
    w = B.w
    base(B, strong=('t1_c',))
    R = B.routes['K1']
    sid, tier = TARGET['K1']
    s_stop = w.visit('K1', sid)
    B.ribbon('K1', R.ext, s_stop - 4)
    B.ribbon('K1', s_stop + 20, None, k=0.2, alpha=0.4)
    for rid in ('K2', 'K3'):
        R2 = B.routes[rid]
        B.ribbon(rid, R2.ext, None, k=0.35, alpha=0.7)
        B.head(rid, R2.ext + RUN[rid], k=0.45)
    B.head('K1', s_stop - 10, scale=9.5)
    tier_target(B, 'K1', s_stop, 'HOLDS', k=1.3)
    pb = B.site_b(sid)
    B.spec['domes'].append(dict(id=sid, pos=pb.tolist(), r=11.0, col='DDF6FF', strength=7.0))
    B.wall(sid, 'D', k=1.6)
    burst(B, pb + np.array([0, 0, 3.0]), '19C9B4', k=1.0, r=10.0, shards=34, seed=2, core='F2FFFF')
    home_deck(B, 44, 50)
    B.ui.update(beat='impact', site=sid, s_stop=s_stop)
    return B


def home_hit(lo=False):
    B = Beat('home_hit', lo)
    w = B.w
    base(B)
    R = B.routes['K2']
    B.ribbon('K2', R.ext, R.cs[-1] - 8)
    B.head('K2', R.cs[-1] - 14, scale=9.5)
    for rid in ('K1', 'K3'):
        B.ribbon(rid, B.routes[rid].ext, None, k=0.14, alpha=0.4)
    hb = B.home_b()
    home_deck(B, 38, 50, hit=6)
    burst(B, hb + np.array([0, 0, 4.0]), DMG, k=1.0, r=15.0, shards=44, seed=5, core='FFF4D8')
    B.ui.update(beat='home_hit')
    return B


def aftermath(lo=False):
    B = Beat('aftermath', lo)
    base(B, down=('t1_a', 't1_b'))
    for rid in ('K1', 'K2', 'K3'):
        B.ribbon(rid, B.routes[rid].ext, None, k=0.10, alpha=0.35)
    B.ring('t1_b', 'SITES_LOST', k=0.8, ghost=0.0)
    B.ring('t1_c', 'HOLDS', k=0.8, ghost=0.0)
    home_deck(B, 38, 50)
    B.ui.update(beat='aftermath')
    return B


def city_lost(lo=False):
    B = Beat('city_lost', lo)
    w = B.w
    base(B, down=(), taken=('t1_a', 't1_b', 't1_c', 't1_d', 't2_breach', 't2_virus', 't2_intel'), dim={sid: 0.6 for sid in w.sites})
    hb = B.home_b()
    home_deck(B, 0, 50, k=0.5)
    import p1_bloom
    fld = p1_bloom.make_field(B, name='city_lost')
    B.spec['bloom'].append(dict(field=fld, strength=1.1, hair=1.5, lift=0.14))
    B.ui.update(beat='city_lost')
    return B


TIERS_AT = [('t1_a', 'UNTOUCHED'), ('t1_d', 'HOLDS'), ('t2_virus', 'SITES_LOST'), ('t3_c', 'DAMAGED'), ('t3_core', 'BREACHED')]


def tiers(lo=False):
    """test beat (not one of the seven): all five tiers on five real Sites, for the 320 px greyscale tier strip."""
    B = Beat('tiers', lo)
    base(B)
    for sid, tier in TIERS_AT:
        B.ring(sid, tier, ghost=1.0)
    home_deck(B, 44, 50)
    B.ui.update(beat='tiers')
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
        if a.startswith('--device='):
            B.spec['device'] = a.split('=')[1]
        if a.startswith('--passes='):
            B.spec['passes'] = a.split('=')[1].split(',')
    print(B.save())
