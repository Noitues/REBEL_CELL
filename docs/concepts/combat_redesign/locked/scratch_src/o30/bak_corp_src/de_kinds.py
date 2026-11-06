"""de_kinds: dE2000 between the unit kind washes, per skin, as the real cell painter draws them (f1_board.screen gradient + the skin cell material).
python de_kinds.py [out.json]"""
import sys, os, json, math
sys.dont_write_bytecode = True
os.environ['LW_SKIN'] = '0'
import numpy as np
from PIL import Image, ImageDraw
import lw_render as LW
import f1_board as FB
import cs_skin as CS
import corp_kinds as CK
from cs_skin import region_apply
from lw_skin import NeutralSkin
from wr_geo import cell_poly, unit_bounds
from cv_lib import L2

KINDS = ['Packet', 'Worm', 'Jammer', 'Payload']


def rgb2lab(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def de2000(l1, l2):
    L1, a1, b1 = l1; L2_, a2, b2 = l2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cm = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1 = math.degrees(math.atan2(b1, a1p)) % 360
    h2 = math.degrees(math.atan2(b2, a2p)) % 360
    dL, dC = L2_ - L1, C2p - C1p
    dh = h2 - h1
    if C1p * C2p == 0: dh = 0
    elif dh > 180: dh -= 360
    elif dh < -180: dh += 360
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lm, Cmp = (L1 + L2_) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0: hm = h1 + h2
    elif abs(h1 - h2) <= 180: hm = (h1 + h2) / 2
    else: hm = (h1 + h2 + 360) / 2 if h1 + h2 < 360 else (h1 + h2 - 360) / 2
    T = 1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm)) + 0.32 * math.cos(math.radians(3 * hm + 6)) - 0.20 * math.cos(math.radians(4 * hm - 63))
    dth = 30 * math.exp(-(((hm - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cmp ** 7 / (Cmp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lm - 50) ** 2 / math.sqrt(20 + (Lm - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cmp, 1 + 0.015 * Cmp * T
    Rt = -math.sin(math.radians(2 * dth)) * Rc
    return math.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))


def swatch(skin, kind, dep, s=3):
    u = dict(id=1, kind=kind, dep=dep, s=s, w=2, hp=3, mx=6)
    L = L2()
    restore = CK.use(getattr(skin, 'kind_gain', None) if skin is not None else None)
    FB.screen(L, u)
    restore()
    b0, b1 = unit_bounds(u)
    poly = cell_poly(dep, b0, b1, kind='unit')
    if skin is not None:
        region_apply(L, [poly], skin.cell)
    im = np.asarray(L.im).astype(np.float64)
    k = im.shape[1] / 1920.0
    m = Image.new('L', (im.shape[1], im.shape[0]), 0)
    ImageDraw.Draw(m).polygon([(x * k, y * k) for x, y in poly], fill=255)
    m = np.asarray(m) > 0
    px = im[m][:, :3]
    return px.mean(0)


def measure(skin_name, skin):
    out = {}
    for dep in range(3):
        cols = {k: swatch(skin, k, dep) for k in KINDS}
        labs = {k: rgb2lab(c) for k, c in cols.items()}
        pairs = {}
        for i, a in enumerate(KINDS):
            for b in KINDS[i + 1:]:
                pairs['%s-%s' % (a, b)] = round(de2000(labs[a], labs[b]), 2)
        out['ring%d' % dep] = dict(rgb={k: [int(round(v)) for v in cols[k]] for k in KINDS}, pairs=pairs,
                                   min=min(pairs.values()), mean=round(sum(pairs.values()) / len(pairs), 2))
    return out


def solve(skin, base_min, cap=3.0):
    """smallest gain per ring (steps of 0.05) with skinned min dE >= base_min[ring]"""
    gains = [1.0, 1.0, 1.0]
    for dep in range(3):
        g = 1.0
        while g <= cap:
            skin.kind_gain = tuple(gains[:dep] + [g] + [1.0] * (2 - dep))
            r = measure_ring(skin, dep)
            if r['min'] >= base_min[dep]:
                break
            g = round(g + 0.1, 2)
        gains[dep] = min(g, cap)
    skin.kind_gain = tuple(gains)
    return tuple(gains)


def measure_ring(skin, dep):
    cols = {k: swatch(skin, k, dep) for k in KINDS}
    labs = {k: rgb2lab(c) for k, c in cols.items()}
    pr = [de2000(labs[a], labs[b]) for i, a in enumerate(KINDS) for b in KINDS[i + 1:]]
    return dict(min=min(pr), mean=sum(pr) / len(pr))


if __name__ == '__main__':
    skins = {'unskinned': None, 'neutral': NeutralSkin(), 'solace': CS.SKINS['solace'], 'meridian': CS.SKINS['meridian']}
    extra = sys.argv[2:]
    res = {}
    res['unskinned'] = measure('unskinned', None)
    base_min = [6.8, 4.3, 2.3]  # target: the neutral skin's own min dE per ring (O-27 follow-up: corp tint must not collapse kinds more than neutral)
    for n in ('neutral', 'solace', 'meridian'):
        sk = skins[n]
        res[n + '_before'] = measure(n, sk)
        if n != 'neutral' and 'nosolve' not in extra:
            res[n + '_gain'] = list(solve(sk, base_min))
        res[n] = measure(n, sk)
    out = sys.argv[1] if len(sys.argv) > 1 else '../work/de_kinds.json'
    json.dump(res, open(out, 'w'), indent=1)
    for n, r in res.items():
        if isinstance(r, list):
            print(n, r); continue
        print(n, ' '.join('r%d min %.1f mean %.1f' % (d, r['ring%d' % d]['min'], r['ring%d' % d]['mean']) for d in range(3)))
