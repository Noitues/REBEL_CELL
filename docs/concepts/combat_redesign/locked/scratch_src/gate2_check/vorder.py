"""vorder.py -- value order re-measure on the published plates.

1. Recomputes the check-b family and mark p95 / p99 / median from the published PNG and the capture masks (verifies checks.json).
2. Independent HOT read: ring NOW annulus pixels that are HARM-like red (R > 200, G < 130, B < 120) or the white-hot core (R > 240,
   G > 215, B > 200, lying within 3 px of a HARM pixel), outside the tower radius; p95 L*.
3. Per-token-disc p95 / p99 (tokens mask inside each unit's token circle).
4. Unclassed board pixels: pixels at r < 480 that are in NO capture mask (and not within 2 px of one); L* p99 / p99.9 / max and the count
   above the HOT p95.  Plus the thin structure lines: the ring NOW outer gutter (r 267-275) and the band r 389-400 at the tape end.
Writes vorder_out.json."""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
C = (536, 540)
PLATES = [('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p2b_hover', 'p2b'), ('p3_resolve', 'p3'), ('p1_nowords', 'nowords')]
SKINS = [('', ''), ('_solace', '_solace'), ('_meridian', '_meridian')]


def lum(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def lstar(y):
    y = np.asarray(y, float)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def load_masks(sfx):
    z = np.load(WORK + 'masks_%s.npz' % sfx)
    return {k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) for k in z.files}


def st(v):
    if v.size < 30:
        return None
    return dict(p95=round(float(np.percentile(v, 95)), 1), p99=round(float(np.percentile(v, 99)), 1), median=round(float(np.median(v)), 1), px=int(v.size))


yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
ANG = (np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) + 360) % 360
checks = json.load(open(FINAL + 'checks.json', encoding='utf-8'))
res = {}
for base, s0 in PLATES:
    for sk, ss in SKINS:
        name, sfx = base + sk, s0 + ss
        rgb = np.asarray(Image.open(FINAL + name + '.png').convert('RGB')).astype(float)
        Ls = lstar(lum(rgb))
        M = load_masks(sfx)
        get = lambda k: M.get(k, np.zeros((1080, 1920), bool))
        out = {}
        # 1. families straight from masks (no cut) and the mark rows as rb_checks defines them
        fam = {'SEND IT': get('send'), 'T HOT marks': get('chev0') | get('arcT0'), 'P tower': get('tower'), 'P hand (rest)': get('hand_rest'),
               'P lifted card': get('hand_lift'), 'K clock': get('tape') | get('plates'), 'S HUD': get('hud')}
        out['fam'] = {k: st(Ls[m]) for k, m in fam.items() if m.any()}
        over = ndi.binary_dilation(get('plan') | get('leader') | get('twist_badge') | get('guns'), iterations=1)
        rows = {'hp': ('hp',), 'adj_hp': ('adj_hp',), 'adj': ('adj',), 'digits': ('digits',), 'ring_tags': ('ring_tags',), 'labels': ('labels',),
                'tickets': ('tickets',), 'tokens': ('tokens',), 'COLD': ('chev1', 'arcT1'), 'FAR': ('chev2', 'arcT2'), 'guns': ('guns',), 'plan': ('plan', 'twist_badge')}
        out['marks'] = {}
        for k, cls in rows.items():
            m = np.zeros((1080, 1920), bool)
            for c in cls:
                m |= get(c)
            if k not in ('guns', 'plan'):
                m &= ~over
            r = st(Ls[m])
            if r:
                out['marks'][k] = r
        # 2. independent HOT read by colour on ring NOW (r 200-270) and the landing arcs inside the bezel
        R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        harm = (R > 200) & (G < 130) & (B < 120)
        core = (R > 240) & (G > 215) & (B > 200) & ndi.binary_dilation(harm, iterations=3)
        ringnow = (RHO >= 214) & (RHO <= 268)
        hot_mask_i = (harm | core) & ringnow & ~get('hand_rest') & ~get('hud')
        out['hot_colour_ringnow'] = st(Ls[hot_mask_i])
        hot_core_only = core & ringnow
        out['hot_core_px'] = int(hot_core_only.sum())
        # 3. per token disc
        toks = []
        g = json.load(open(WORK + 'chk_%s.json' % sfx))['rb']['geometry']
        tm = get('tokens') & ~over
        for u in g['units']:
            tx, ty = u['token']
            m = tm & (np.hypot(xx - tx, yy - ty) <= u['tok_r'] + 4)
            r = st(Ls[m])
            if r:
                toks.append(dict(uid=u['id'], dep=u['dep'], s=u['s'], **r))
        out['tokens_each'] = toks
        # 4. unclassed board pixels
        allm = np.zeros((1080, 1920), bool)
        for k, m in M.items():
            if k in ('scrim',):
                continue
            allm |= m
        allm = ndi.binary_dilation(allm, iterations=2)
        hot95 = out['fam'].get('T HOT marks', {}).get('p95') if out['fam'].get('T HOT marks') else None
        un = (RHO < 480) & ~allm
        v = Ls[un]
        out['unclassed'] = dict(px=int(un.sum()), p99=round(float(np.percentile(v, 99)), 1), p999=round(float(np.percentile(v, 99.9)), 1), max=round(float(v.max()), 1),
                                n_above_hot95=None if hot95 is None else int((v > hot95).sum()), n_above_90=int((v > 90).sum()))
        # where are they: top clusters of unclassed pixels above 90
        hi = un & (Ls > 90)
        lab, n = ndi.label(ndi.binary_dilation(hi, iterations=2))
        cl = []
        for i in range(1, n + 1):
            ys, xs = np.nonzero((lab == i) & hi)
            if len(xs) == 0:
                continue
            rr = RHO[ys, xs]
            cl.append(dict(n=int(len(xs)), box=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], r=[round(float(rr.min()), 1), round(float(rr.max()), 1)],
                           maxL=round(float(Ls[ys, xs].max()), 1)))
        cl.sort(key=lambda d: -d['n'])
        out['unclassed_hi_clusters'] = cl[:12]
        out['n_unclassed_hi_clusters'] = len(cl)
        # thin line bands
        gut = (RHO >= 266) & (RHO <= 276) & ~ndi.binary_dilation(get('tokens') | get('chev0') | get('chev1') | get('tags') | get('ring_tags') | get('guns') | get('plan') | get('leader') | get('adj') | get('adj_hp'), iterations=2)
        out['ringNOW_outer_line'] = st(Ls[gut])
        out['ringNOW_outer_line_max'] = round(float(Ls[gut].max()), 1)
        # 5. compare with checks.json
        rbb = checks['rb_checks'][name]['b_value_order']
        cj = {r['family']: r for r in rbb['sorted']}
        out['checks_json_HOT_p95'] = cj.get('T HOT marks', {}).get('p95')
        out['checks_json_tower_p95'] = cj.get('P tower', {}).get('p95')
        out['checks_json_marks'] = {k: (v['p95'], v['p99']) for k, v in rbb['marks'].items()}
        res[name] = out
        f = out['fam']
        print('==', name, 'HOT', f.get('T HOT marks'), '| cj', out['checks_json_HOT_p95'], '| tower', f.get('P tower', {}).get('p95'), 'cj', out['checks_json_tower_p95'])
        print('   HOT by colour (ring NOW):', out['hot_colour_ringnow'], 'core px', out['hot_core_px'])
        print('   K clock', f.get('K clock'), 'SEND', f.get('SEND IT', {}).get('p95'), 'lift', (f.get('P lifted card') or {}).get('p95'), 'hand', f.get('P hand (rest)', {}).get('p95'))
        print('   marks', {k: (v['p95'], v['p99']) for k, v in out['marks'].items()})
        print('   cj marks', out['checks_json_marks'])
        print('   tokens each', [(t['uid'], t['p95'], t['p99']) for t in toks])
        print('   unclassed', out['unclassed'], 'clusters', out['n_unclassed_hi_clusters'])
        for c in out['unclassed_hi_clusters'][:8]:
            print('      ', c)
        print('   ring NOW outer line', out['ringNOW_outer_line'], 'max', out['ringNOW_outer_line_max'])
json.dump(res, open('D:/rc_scratch/combat_redesign/locked/gate2_check/vorder_out.json', 'w'), indent=1)
