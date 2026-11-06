"""kind_colour_set: ONE wash table for all six kinds (Packet, Worm, Payload, Jammer, Ring, Adjuster) incl. the unseen Jammer and Ring.
The cell wash, the token disc (kind colour at 26 percent), the landing-arc kind disc (outer_rings arc_glyph_disc) and the bible token table all read TABLES[...] below.
Options: R = optimised mauve ladder (hue AND value separated, passes deutan / protan / tritan), V = the R1 hue ladder with only Ring moved, C(=B) = value ladder.
The search keeps every wash inside the unit-mauve band (hue 290-350, never cyan, never orange / lime / gold) and above the PL10 value rule (cell darker than the red chevrons)."""
import math, json, random, itertools
import numpy as np
from wr2_lib import lab, dE, sim_rgb, _lin, _gam

KINDS = ['Packet', 'Worm', 'Payload', 'Jammer', 'Ring']
TOK_F = 1.40            # token / arc-disc colour = wash x 1.40 (the E10 ratio)

R1_TABLE = {'Packet': (128, 62, 104), 'Worm': (102, 66, 138), 'Jammer': (84, 86, 146), 'Payload': (126, 66, 92), 'Ring': (116, 70, 116)}   # Ring == Payload colour in the E10 token table
BOSS = (255, 196, 40)


def _lch_to_rgb(L_, C_, h):
    a = C_ * math.cos(math.radians(h)); b = C_ * math.sin(math.radians(h))
    fy = (L_ + 16) / 116; fx = fy + a / 500; fz = fy - b / 200
    f = lambda t: t ** 3 if t ** 3 > 0.008856 else (t - 16 / 116) / 7.787
    X, Y, Z = 0.95047 * f(fx), 1.0 * f(fy), 1.08883 * f(fz)
    rgb = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]]) @ np.array([X, Y, Z])
    return tuple(int(v) for v in np.clip(_gam(rgb), 0, 255)), bool(((rgb < -0.002) | (rgb > 1.002)).any())


def _score(tab):
    """minimum pairwise colour distance over normal + deutan + protan + tritan, on the ring-0 wash AND the ring-2 wash"""
    worst = 1e9
    for kind in ('none', 'deutan', 'protan', 'tritan'):
        for ramp in (0.0, 0.38):
            cols = []
            for k in KINDS:
                c = tuple(int(round(v + ((10, 8, 30)[i] - v) * ramp)) for i, v in enumerate(tab[k]))
                cols.append(c if kind == 'none' else sim_rgb(c, kind))
            for a, b in itertools.combinations(cols, 2):
                worst = min(worst, dE(a, b) * (1.0 if kind == 'none' else 1.25))
    return worst


# identity anchors (hue deg, window, L range, C range): rose Packet, violet Worm, indigo Jammer, wine Payload, grey-lilac Ring
ANCH = {'Packet': (340, 14, (34, 42), (30, 46)), 'Worm': (305, 14, (32, 40), (30, 46)), 'Jammer': (282, 8, (36, 44), (28, 38)),
        'Payload': (350, 10, (28, 36), (22, 34)), 'Ring': (322, 30, (40, 48), (10, 24))}


def search(seed=11, n=4000):
    """hill-climb inside the identity windows so each kind keeps its E10 family hue while the set separates in value, chroma and hue"""
    rnd = random.Random(seed)
    cur = {k: [a[0], (a[2][0] + a[2][1]) / 2, (a[3][0] + a[3][1]) / 2] for k, a in ANCH.items()}      # h, L, C

    def to_tab(c):
        return {k: _lch_to_rgb(v[1], v[2], v[0] % 360)[0] for k, v in c.items()}
    bs = _score(to_tab(cur))
    for _ in range(n):
        k = rnd.choice(KINDS)
        a = ANCH[k]
        new = {kk: list(vv) for kk, vv in cur.items()}
        new[k][0] = min(a[0] + a[1], max(a[0] - a[1], new[k][0] + rnd.uniform(-6, 6)))
        new[k][1] = min(a[2][1], max(a[2][0], new[k][1] + rnd.uniform(-2, 2)))
        new[k][2] = min(a[3][1], max(a[3][0], new[k][2] + rnd.uniform(-3, 3)))
        t = to_tab(new)
        if any(_lch_to_rgb(v[1], v[2], v[0] % 360)[1] for v in new.values()):
            continue
        s_ = _score(t)
        if s_ >= bs:
            cur, bs = new, s_
    return to_tab(cur), bs


def tables():
    best, bs = search()
    # ring is the climax unit: keep it the most distinct (largest chroma step); Packet keeps its E10 rose anchor if the search allows it
    return {'R': best, 'V': dict(R1_TABLE, Ring=(98, 84, 120)), 'C': value_ladder()}, bs


def value_ladder():
    """one hue (mauve 320) at five values: kind reads by value, hue is shared"""
    out = {}
    for k, Lv in zip(KINDS, (28, 34, 40, 46, 52)):
        out[k] = _lch_to_rgb(Lv, 36, 318)[0]
    return out


def export(path, tabs):
    d = {}
    for o, t in tabs.items():
        d[o] = {k: dict(wash=list(v), token=[min(255, int(c * TOK_F)) for c in v], token_disc_26=[int(min(255, c * TOK_F) * 0.26) for c in v]) for k, v in t.items()}
        d[o]['Adjuster'] = dict(wash=[70, 52, 14], token=list(BOSS), token_disc_26=[int(c * 0.26) for c in BOSS])
    json.dump(d, open(path, 'w'), indent=1)
    return d


RTAB = {'Packet': (137, 63, 108), 'Worm': (95, 59, 122), 'Jammer': (57, 103, 164), 'Payload': (98, 51, 66), 'Ring': (113, 109, 149)}      # search result (seed 5), frozen
VTAB = dict(R1_TABLE, Ring=(113, 109, 149))
CTAB = None


def table_for(o):
    global CTAB
    if o == 'R':
        return dict(RTAB)
    if o == 'V':
        return dict(VTAB)
    if CTAB is None:
        CTAB = value_ladder()
    return dict(CTAB)
