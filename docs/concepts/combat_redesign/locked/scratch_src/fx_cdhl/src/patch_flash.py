p='D:/rc_scratch/combat_redesign/locked/fx_cdhl/src/fxk_lib.py'
s=open(p).read()
a=s.index('    up = np.zeros((T,)'); b=s.index('    win = max(1')
s=s[:a]+'''    up = np.zeros((T,) + Y.shape[1:], bool)
    dn = np.zeros_like(up)
    ref = Y[0].copy()
    dirn = np.zeros(Y.shape[1:], np.int8)
    for t in range(1, T):
        y = Y[t]
        dark = np.minimum(y, ref) < 0.8
        r_ev = (y - ref >= swing) & dark & (dirn != 1)
        f_ev = (ref - y >= swing) & dark & (dirn != -1)
        up[t] = r_ev
        dn[t] = f_ev
        dirn = np.where(r_ev, 1, np.where(f_ev, -1, dirn)).astype(np.int8)
        ref = np.where(r_ev | f_ev, y, ref)
        ref = np.where((dirn == 1) & (y > ref), y, ref)
        ref = np.where((dirn == -1) & (y < ref), y, ref)
'''+s[b:]
a=s.index('    def events(u, d):'); b=s.index('    fl_f, mx_f')
s=s[:a]+'''    def events(u, d):
        # waves: the moments an up-wave or a down-wave first covers more than `area` of the region (alternating);
        # one flash = an opposing pair of waves, so flashes in a 1 s window = waves in the window // 2
        waves = []
        for t in range(T):
            if u[t] > area and (not waves or waves[-1][0] != 'u'):
                waves.append(('u', t))
            elif d[t] > area and (not waves or waves[-1][0] != 'd'):
                waves.append(('d', t))
        ts = [w[1] for w in waves]
        mx = 0
        for t in ts:
            mx = max(mx, sum(1 for s in ts if t <= s < t + fps) // 2)
        return ts, mx
'''+s[b:]
s=s.replace("flashes_footprint=len(fl_f)","waves_footprint=len(fl_f), flashes_footprint=len(fl_f) // 2").replace("flashes_crop=len(fl_c)","waves_crop=len(fl_c), flashes_crop=len(fl_c) // 2")
open(p,'w').write(s)
