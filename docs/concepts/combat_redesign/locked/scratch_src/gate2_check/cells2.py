"""cells2.py -- independent occupied vs empty cell probe on the published plates.

Cells are rebuilt from radii and angles (ring NOW r 218-267, +1 275-324, +2 332-381; sector s centred on 60*s deg, clockwise from up),
inset 5 px radially and 3 deg angularly.  Glass pixels = cell pixels minus: the token disc (r tok_r + 10), the unit's HP tray band
(t_in - 4 .. t_out + 4), and any pixel that is a mark by colour (chroma ratio > 0.30, L* > 62 or L* < 8).
Reports per cell: whole-cell mean L* (everything, as the reviewer's box read it), glass median L*, glass L* of mean luminance, and the
ratio of glass mean luminance to the brightest empty cell of the same ring (plate cells; ring NOW has none, so its skin probe image is used).
Unit states come from the capture (work/chk_<sfx>.json), only to know which cell is occupied, dying or dimmed."""
import sys, json
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
C = (536, 540)
RINGS = [(218, 267), (275, 324), (332, 381)]
PLATES = [('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p2b_hover', 'p2b'), ('p3_resolve', 'p3'), ('p1_nowords', 'nowords')]
SKINS = [('', ''), ('_solace', '_solace'), ('_meridian', '_meridian')]


def lum(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def lstar(y):
    y = np.asarray(y, float)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


CMAX = 28.0      # Lab C* above this = a coloured mark (HARM, pink hatch, gold, FOCUS), not slate glass


def lab_chroma(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Yy = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    a = 500 * (f(X) - f(Yy))
    b = 200 * (f(Yy) - f(Z))
    return np.hypot(a, b)


yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
ANG = (np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) + 360) % 360


def sector_mask(dep, s, inset_r=5, inset_a=3):
    r0, r1 = RINGS[dep]
    a = (ANG - 60 * s + 180) % 360 - 180
    return (RHO >= r0 + inset_r) & (RHO <= r1 - inset_r) & (np.abs(a) <= 30 - inset_a)


def analyse(png, chk, probe_png):
    rgb = np.asarray(Image.open(png).convert('RGB')).astype(float)
    Y = lum(rgb)
    Ls = lstar(Y)
    chroma = lab_chroma(rgb)
    markish = (chroma > CMAX) | (Ls > 62) | (Ls < 6)
    g = chk['rb']['geometry']
    cut_units = np.zeros((1080, 1920), bool)
    for u in g['units']:
        tx, ty = u['token']
        cut_units |= np.hypot(xx - tx, yy - ty) <= u['tok_r'] + 10
        a = (ANG - u['b0']) % 360
        cut_units |= (RHO >= u['t_in'] - 4) & (RHO <= u['t_out'] + 4) & (a <= (u['b1'] - u['b0']))
    state = {}
    for c in g['cells']:
        state[(c['dep'], c['s'])] = (c['state'], c['kind'], c['uid'])
    pY = None
    if probe_png:
        prgb = np.asarray(Image.open(probe_png).convert('RGB')).astype(float)
        pY = lum(prgb)
        pL = lstar(pY)
        pch = lab_chroma(prgb)
        pmark = (pch > CMAX) | (pL > 62) | (pL < 6)
    out = []
    for dep in range(3):
        empties = []
        for s in range(6):
            st = state.get((dep, s), ('?', None, None))
            m = sector_mask(dep, s)
            whole = float(lstar(Y[m].mean()))
            gm = m & ~cut_units & ~markish
            n = int(gm.sum())
            med = float(np.median(Ls[gm])) if n > 50 else None
            gy = float(Y[gm].mean()) if n > 50 else None
            out.append(dict(dep=dep, s=s, state=st[0], kind=st[1], uid=st[2], whole_L=round(whole, 1), glass_med=None if med is None else round(med, 1),
                            glass_L=None if gy is None else round(float(lstar(gy)), 1), glass_Y=gy, n=n))
            if st[0] == 'empty' and gy is not None:
                empties.append(('plate s%d' % s, gy))
        if pY is not None:
            for s in range(6):
                m = sector_mask(dep, s) & ~pmark
                if m.sum() > 200:
                    empties.append(('probe s%d' % s, float(pY[m].mean())))
        ref = max(empties, key=lambda kv: kv[1]) if empties else (None, None)
        for r in out:
            if r['dep'] == dep:
                r['ref'] = ref[0]
                r['ref_L'] = None if ref[1] is None else round(float(lstar(ref[1])), 1)
                r['ratio'] = None if (ref[1] is None or r['glass_Y'] is None) else round(r['glass_Y'] / ref[1], 2)
    return out


summary = {}
for base, sfx0 in PLATES:
    for sk, ssfx in SKINS:
        name = base + sk
        sfx = sfx0 + ssfx
        chk = json.load(open(WORK + 'chk_%s.json' % sfx))
        probe = WORK + 'probe_%s.png' % sfx
        rows = analyse(FINAL + name + '.png', chk, probe)
        print('==', name)
        for r in rows:
            print('  dep %d s %d %-7s %-8s whole %5.1f glass med %5s glass L %5s n %5d  ref %-8s %5s ratio %s' % (
                r['dep'], r['s'], r['state'], r['kind'], r['whole_L'], r['glass_med'], r['glass_L'], r['n'], r['ref'], r['ref_L'], r['ratio']))
        gated = [r for r in rows if r['state'] in ('live', 'dying') and r['ratio'] is not None]
        summary[name] = dict(min_ratio=min((r['ratio'], r['dep'], r['s']) for r in gated) if gated else None,
                             now_occ=[r['glass_L'] for r in rows if r['dep'] == 0 and r['state'] == 'live'],
                             occ_by_ring={d: [r['glass_L'] for r in rows if r['dep'] == d and r['state'] in ('live', 'dying')] for d in range(3)},
                             ref_by_ring={d: next((r['ref_L'] for r in rows if r['dep'] == d), None) for d in range(3)},
                             whole_occ={d: [r['whole_L'] for r in rows if r['dep'] == d and r['state'] in ('live', 'dying')] for d in range(3)},
                             whole_empty={d: [r['whole_L'] for r in rows if r['dep'] == d and r['state'] == 'empty'] for d in range(3)})
print()
for k, v in summary.items():
    print(k, json.dumps(v))
