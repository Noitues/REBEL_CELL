"""skins.py -- corp skin probes on p1 (neutral / solace / meridian) and the other beats.

1. Cell glass colour per ring (median sRGB of glass pixels, Lab C*), occupied and empty: are the fills neutral slate?
2. COLD marks vs their own cell: COLD fill (chev1 + arcT1 mask, L* > 45) median colour vs the glass of the cell under it (ring +1 cells), dE76
   and luminance ratio; per skin.
3. Corp hue pixel census: pixels within dE76 18 of the skin inks, split by where they sit (tickets, bezel rim r >= 440, cells r 214-385,
   token discs, tower r < 212, other).
4. Wave ticket edges: L* median of the outer 3 px of each ticket (W6, W5, W4) -- time is carried by edge value (W6 50, W5 70, W4 100 %)."""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
C = (536, 540)
hx = lambda s: np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float)
SKIN = {'solace': {'leaf': hx('96FF46'), 'leaf_deep': hx('4FA83A'), 'porcelain': hx('B8DCCC')},
        'meridian': {'rust': hx('B0602C'), 'rust_hi': hx('D88A4E')}}
RINGS = [(218, 267), (275, 324), (332, 381)]


def to_lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.stack([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))], -1), Y


def load_masks(sfx):
    z = np.load(WORK + 'masks_%s.npz' % sfx)
    return {k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) for k in z.files}


yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
ANG = (np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) + 360) % 360
for beat, s0 in (('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p3_resolve', 'p3'), ('p1_nowords', 'nowords'), ('p2b_hover', 'p2b')):
    for corp in ('', 'solace', 'meridian'):
        name = beat + ('_' + corp if corp else '')
        sfx = s0 + ('_' + corp if corp else '')
        rgb = np.asarray(Image.open(FINAL + name + '.png').convert('RGB')).astype(float)
        lab, Y = to_lab(rgb)
        Ls = lab[..., 0]
        Cs = np.hypot(lab[..., 1], lab[..., 2])
        M = load_masks(sfx)
        get = lambda k: M.get(k, np.zeros((1080, 1920), bool))
        chk = json.load(open(WORK + 'chk_%s.json' % sfx))
        g = chk['rb']['geometry']
        marks = np.zeros((1080, 1920), bool)
        for k, m in M.items():
            if k not in ('scrim', 'hud', 'hand', 'hand_rest', 'card_0', 'card_1', 'card_2', 'card_3'):
                marks |= m
        marks = ndi.binary_dilation(marks, iterations=3)
        for u in g['units']:
            marks |= np.hypot(xx - u['token'][0], yy - u['token'][1]) <= u['tok_r'] + 10
            a = (ANG - u['b0']) % 360
            marks |= (RHO >= u['t_in'] - 4) & (RHO <= u['t_out'] + 4) & (a <= (u['b1'] - u['b0']))
        st = {(c['dep'], c['s']): c['state'] for c in g['cells']}
        print('==', name)
        glass_cols = {}
        for dep in range(3):
            for kind in ('live', 'empty'):
                m = np.zeros((1080, 1920), bool)
                for s in range(6):
                    if st.get((dep, s)) == kind:
                        a = (ANG - 60 * s + 180) % 360 - 180
                        m |= (RHO >= RINGS[dep][0] + 5) & (RHO <= RINGS[dep][1] - 5) & (np.abs(a) <= 27)
                m &= ~marks & (Cs < 28) & (Ls > 6) & (Ls < 62)
                if m.sum() > 300:
                    med = np.median(rgb[m], 0)
                    lm, _ = to_lab(med)
                    glass_cols[(dep, kind)] = med
                    print('  glass ring %d %-5s median #%02X%02X%02X  L* %.1f  C* %.1f  (px %d)' % (dep, kind, *[int(v) for v in med], lm[0], np.hypot(lm[1], lm[2]), m.sum()))
        # COLD vs its cell (ring +1 occupied)
        cm = (get('chev1') | get('arcT1')) & (Ls > 45)
        cm &= (RHO >= RINGS[1][0]) & (RHO <= RINGS[1][1])
        if cm.sum() > 30 and (1, 'live') in glass_cols:
            mc = np.median(rgb[cm], 0)
            lc, yc = to_lab(mc)
            lg, yg = to_lab(glass_cols[(1, 'live')])
            print('  COLD fill in ring +1 #%02X%02X%02X L* %.1f vs ring +1 glass L* %.1f: dE76 %.1f, lum ratio %.2f, WCAG %.2f  (px %d)' % (
                *[int(v) for v in mc], lc[0], lg[0], float(np.linalg.norm(lc - lg)), float(yc / yg), float((yc + 0.05) / (yg + 0.05)), cm.sum()))
            # also the keyline: darkest 10 % of pixels within 3 px around the COLD fill
            ring_ = ndi.binary_dilation(cm, iterations=3) & ~cm
            print('     COLD keyline: L* p10 of the 3 px ring around the fill %.1f' % float(np.percentile(Ls[ring_], 10)))
        # corp hue census
        if corp:
            near = np.zeros((1080, 1920), bool)
            for k, v in SKIN[corp].items():
                lv, _ = to_lab(v)
                near |= np.linalg.norm(lab - lv, axis=-1) < 18
            near &= (xx < 1060)
            where = {'tickets (x<300,y<100)': (xx < 300) & (yy < 100), 'bezel rim r>=440': RHO >= 440, 'bezel r 385-440': (RHO >= 385) & (RHO < 440),
                     'cells r 212-385': (RHO >= 212) & (RHO < 385), 'tower r<212': RHO < 212}
            tok = np.zeros((1080, 1920), bool)
            for u in g['units']:
                tok |= np.hypot(xx - u['token'][0], yy - u['token'][1]) <= u['tok_r'] + 6
            tot = int(near.sum())
            parts = {k: int((near & m & ~tok).sum()) for k, m in where.items()}
            parts['token discs'] = int((near & tok).sum())
            print('  corp-ink px (dE<18, board side): total %d  %s' % (tot, parts))
        # tickets
        tk = get('tickets')
        lab_, n = ndi.label(tk)
        boxes = []
        for i in range(1, n + 1):
            ys, xs = np.nonzero(lab_ == i)
            if len(xs) > 2000:
                boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
        boxes.sort()
        out = []
        for (x0, y0, x1, y1) in boxes:
            box = np.zeros((1080, 1920), bool)
            box[y0:y1 + 1, x0:x1 + 1] = True
            inner = np.zeros((1080, 1920), bool)
            inner[y0 + 4:y1 - 3, x0 + 4:x1 - 3] = True
            edge = box & ~inner
            ev = Ls[edge]
            bright = ev[ev > np.percentile(ev, 60)]
            mc = np.median(rgb[edge & (Ls > np.percentile(ev, 60))], 0)
            out.append('%s edge L* p60+ median %.1f p95 %.1f col #%02X%02X%02X' % ((x0, y0, x1, y1), float(np.median(bright)), float(np.percentile(ev, 95)), *[int(v) for v in mc]))
        print('  tickets:', ' | '.join(out))
