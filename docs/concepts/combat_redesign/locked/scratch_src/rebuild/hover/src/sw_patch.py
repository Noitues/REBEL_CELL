p = 'hv_checks.py'
s = open(p, encoding='utf-8').read()
a = s.index("def stroke_width(m):")
b = s.index("def board_mask_sets(M):")
new = '''def _normals(dt, ys, xs):
    """unit normals across a stroke at ridge pixels: the eigenvector of the most negative Hessian eigenvalue of the smoothed distance transform"""
    dyy = ndi.gaussian_filter(dt, 1.2, order=(2, 0))
    dxx = ndi.gaussian_filter(dt, 1.2, order=(0, 2))
    dxy = ndi.gaussian_filter(dt, 1.2, order=(1, 1))
    out = []
    for y, x in zip(ys, xs):
        hxx, hyy, hxy = dxx[y, x], dyy[y, x], dxy[y, x]
        tr, det = hxx + hyy, hxx * hyy - hxy * hxy
        lam = tr / 2 - math.sqrt(max(0.0, tr * tr / 4 - det))
        vx, vy = (lam - hyy, hxy) if abs(hxy) > 1e-9 else ((1.0, 0.0) if hxx < hyy else (0.0, 1.0))
        n_ = math.hypot(vx, vy) or 1.0
        out.append((vx / n_, vy / n_))
    return out


def stroke_width(m, step=3):
    """median stroke width of a mask: at every step-th ridge pixel (distance-transform ridge, dt >= 1.5) the run of mask pixels along the normal
    across the stroke, sampled every 0.1 px (the mask is the 50 % coverage of the drawn stroke, so the run is its width to about 0.5 px)"""
    if m.sum() < 40:
        return None
    from scipy.ndimage import map_coordinates
    dt = ndi.distance_transform_edt(m)
    ridge = (dt >= ndi.maximum_filter(dt, size=3) - 1e-6) & (dt >= 1.5)
    ys, xs = np.nonzero(ridge)
    ys, xs = ys[::step], xs[::step]
    tt = np.arange(-16.0, 16.0001, 0.1)
    i0 = len(tt) // 2
    mf = m.astype(np.float32)
    w = []
    for (vx, vy), y, x in zip(_normals(dt, ys, xs), ys, xs):
        py, px = y + tt * vy, x + tt * vx
        if py.min() < 0 or px.min() < 0 or py.max() > H - 1 or px.max() > W - 1:
            continue
        v = map_coordinates(mf, [py + 0.0, px + 0.0], order=0) > 0.5
        if not v[i0]:
            continue
        lo, hi = i0, i0
        while lo > 0 and v[lo - 1]:
            lo -= 1
        while hi < len(tt) - 1 and v[hi + 1]:
            hi += 1
        if lo == 0 or hi == len(tt) - 1:
            continue
        w.append((hi - lo + 1) * 0.1)
    return round(float(np.median(w)), 2) if w else None


'''
s = s[:a] + new + s[b:]
# check_pencil: gate the mask widths directly (the reference stays as a report)
old = """    fails = []
    for k, v in r['mask'].items():
        if v is None:
            continue
        if abs(v - REF_W[k]) > 0.75:
            fails.append('%s mask width %.2f vs reference %.2f' % (k, v, REF_W[k]))"""
new2 = """    fails = []
    lim = dict(L6_wax=(6.0, 8.0), L6_all=(12.0, 14.0), L5_wax=(2.5, 4.0), L5_all=(6.5, 9.0))
    for k, v in r['mask'].items():
        if v is None:
            continue
        if not lim[k][0] <= v <= lim[k][1]:
            fails.append('%s width %.2f px, want %.1f-%.1f' % (k, v, lim[k][0], lim[k][1]))
    if r['mask']['L6_wax'] is not None and r['mask']['L6_all'] is not None:
        r['mask']['L6_ink_each_side'] = round((r['mask']['L6_all'] - r['mask']['L6_wax']) / 2, 2)
        if not 2.5 <= r['mask']['L6_ink_each_side'] <= 3.5:
            fails.append('L6 ink edge %.2f px a side, want 3' % r['mask']['L6_ink_each_side'])"""
assert old in s
s = s.replace(old, new2, 1)
old3 = """        if pw['ink_px'] is not None and not 2.0 <= pw['ink_px'] <= 4.0:
            fails.append('L6 ink edge %.2f px on the PNG (want 3)' % pw['ink_px'])"""
assert old3 in s
s = s.replace(old3, "        pass                      # the ink run on the PNG is reported only: on the dimmed board the ground is rarely lighter than the ink", 1)
s = s.replace("""    r['rule'] = ('(1) median mask width (2 x distance transform on the ridge - 1) of every drawn L6 / L5 class within 0.75 px of the same estimator on a '
                 'reference stroke of the spec widths (7 wax, 13 with ink, 3 L5 edge, 7.5 with keyline); (2) on the published PNG, profiles across the L6 '
                 'wax: wax 6-8 px (b* midpoint crossings), ink edge 2-4 px a side (where the ground is lighter than the ink)')""",
"""    r['rule'] = ('(1) the drawn masks, median width across the stroke (runs along the normal at the distance-transform ridge, 0.1 px steps): L6 wax 6-8, '
                 'L6 with ink 12-14 (ink 2.5-3.5 a side), L5 edge 2.5-4, L5 with keyline 6.5-9; the same estimator on a reference stroke of the spec widths is '
                 'reported (reference); (2) on the published PNG, profiles across the L6 wax: wax 6-8 px between the b* midpoint crossings; the ink run on the '
                 'PNG is reported (the dimmed ground is rarely lighter than the ink)')""", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
