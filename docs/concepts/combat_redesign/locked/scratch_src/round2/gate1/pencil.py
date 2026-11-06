"""C1 pencil gate (gate1, independent): on every board and hover plate, find PLAN wax pixels (dE76 < 30 of #FFE200), and measure
 - whole-stroke width, wax width, ink width per side by normal profiles from the wax skeleton (0.25 px steps, bilinear)
 - wax grain: L* std of the wax interior (wax eroded 1)
 - component sizes (to find X caps and thin marks)
Board region r < 505; HUD region x >= 1070, y < 620 reported separately.  Output: out/pencil.json + printed table."""
import sys, json, glob, os
import numpy as np
from scipy import ndimage as ndi

import glib as G

PLAN = '#FFE200'
r_, th_, xx, yy = G.polar()


def bil(A, x, y):
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    x0 = np.clip(x0, 0, A.shape[1] - 2); y0 = np.clip(y0, 0, A.shape[0] - 2)
    fx = x - x0; fy = y - y0
    return (A[y0, x0] * (1 - fx) * (1 - fy) + A[y0, x0 + 1] * fx * (1 - fy) + A[y0 + 1, x0] * (1 - fx) * fy + A[y0 + 1, x0 + 1] * fx * fy)


def measure(path, region):
    rgb = G.load(path)
    L = G.Lstar(rgb)
    lab = G.lab(rgb)
    dP = G.de(lab, PLAN)
    if region == 'board':
        reg = r_ < 505
    else:
        reg = (xx >= 1070) & (yy < 640)
    wax = (dP < 30) & reg
    lab_, n = ndi.label(wax)
    if n == 0:
        return None
    sizes = ndi.sum(wax, lab_, range(1, n + 1))
    keep = np.isin(lab_, 1 + np.nonzero(sizes >= 60)[0])
    wax = keep
    if wax.sum() < 100:
        return dict(wax_px=int(wax.sum()))
    edt0 = ndi.distance_transform_edt(wax); sk = wax & (edt0 >= ndi.maximum_filter(edt0, size=3) - 1e-6)
    edt = ndi.distance_transform_edt(wax)
    ys, xs = np.nonzero(sk & (edt >= 2))
    if len(xs) == 0:
        return dict(wax_px=int(wax.sum()))
    idx = np.arange(0, len(xs), max(1, len(xs) // 600))
    waxw, inkw_l, inkw_r, whole = [], [], [], []
    skp = np.stack([xs, ys], 1).astype(float)
    from scipy.spatial import cKDTree
    tr = cKDTree(skp)
    for i in idx:
        p = skp[i]
        nb = tr.query_ball_point(p, 5)
        if len(nb) < 5:
            continue
        q = skp[nb] - skp[nb].mean(0)
        u, s, vt = np.linalg.svd(q, full_matrices=False)
        if s[0] < 2.5 * max(s[1], 1e-6):
            continue  # junction / cap
        t = vt[0]
        nrm = np.array([-t[1], t[0]])
        ss = np.arange(-14, 14.01, 0.25)
        px = p[0] + nrm[0] * ss; py = p[1] + nrm[1] * ss
        if px.min() < 1 or py.min() < 1 or px.max() > 1917 or py.max() > 1077:
            continue
        dd = bil(dP, px, py); ll = bil(L, px, py)
        c = len(ss) // 2
        if dd[c] >= 30:
            continue
        # wax run
        a = c
        while a > 0 and dd[a - 1] < 30:
            a -= 1
        b = c
        while b < len(ss) - 1 and dd[b + 1] < 30:
            b += 1
        w = (b - a + 1) * 0.25
        # ink runs each side (L* < 20), after up to 1.25 px of wax-to-ink blend; blend samples counted half to the ink
        def run(start, step):
            i = start; blend = 0
            while 0 <= i < len(ss) and ll[i] >= 20 and blend < 5:
                blend += 1; i += step
            k = 0
            while 0 <= i < len(ss) and ll[i] < 20:
                k += 1; i += step
            return k + blend * 0.5, i
        ka, la = run(a - 1, -1)
        kb, lb = run(b + 1, 1)
        if la < 0 or lb >= len(ss) or ka == 0 or kb == 0:
            continue  # ink merged with dark ground or absent: undetermined
        waxw.append(w); inkw_l.append(ka * 0.25); inkw_r.append(kb * 0.25); whole.append(w + (ka + kb) * 0.25)
    inter = ndi.binary_erosion(wax, iterations=1)
    grain = float(L[inter].std()) if inter.sum() > 50 else float('nan')
    # grain on a high-pass (remove slow shading): std of L - 5px median
    Lm = ndi.median_filter(L, size=7)
    grain_hp = float((L - Lm)[inter].std()) if inter.sum() > 50 else float('nan')
    ink = np.array(inkw_l + inkw_r)
    return dict(wax_px=int(wax.sum()), n_profiles=len(waxw),
                wax_w_med=float(np.median(waxw)) if waxw else None,
                wax_w_p10=float(np.percentile(waxw, 10)) if waxw else None,
                wax_w_p90=float(np.percentile(waxw, 90)) if waxw else None,
                ink_side_med=float(np.median(ink)) if len(ink) else None,
                ink_side_p10=float(np.percentile(ink, 10)) if len(ink) else None,
                ink_side_p90=float(np.percentile(ink, 90)) if len(ink) else None,
                whole_med=float(np.median(whole)) if whole else None,
                grain_std=grain, grain_hp_std=grain_hp, wax_L_med=float(np.median(L[wax])),
                wax_modal=G.hexof(G.modal(rgb[wax])[0]))


res = {}
files = [G.FINAL + n + '.png' for b, c, n in G.plates() if b in ('p2', 'p2b')]
files += sorted(glob.glob(G.HOVER + 'h*.png'))
for f in files:
    nm = os.path.basename(f)[:-4]
    for region in ('board', 'hud'):
        m = measure(f, region)
        res[nm + ':' + region] = m
        if m and m.get('n_profiles'):
            print('%-28s %-5s wax_px %6d prof %4d wax %.2f [%.2f-%.2f] ink/side %.2f [%.2f-%.2f] whole %.2f grain %.2f hp %.2f L %.1f %s' % (
                nm, region, m['wax_px'], m['n_profiles'], m['wax_w_med'], m['wax_w_p10'], m['wax_w_p90'], m['ink_side_med'] or -1,
                m['ink_side_p10'] or -1, m['ink_side_p90'] or -1, m['whole_med'], m['grain_std'], m['grain_hp_std'], m['wax_L_med'], m['wax_modal']))
        else:
            print('%-28s %-5s %s' % (nm, region, m))
json.dump(res, open('out/pencil.json', 'w'), indent=1)
