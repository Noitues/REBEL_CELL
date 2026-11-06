"""o30_meter.py <full|red>: the 60 fps flash meter (the method of NOTES_MPST / fxlib.flash_check) over the whole sequenced resolve beat.
Regions, each judged against its own footprint (pixels whose relative luminance moves > 0.02 from frame 0 at any time):
  whole     the whole 1920x1080 frame
  box:<id>  each effect's own crop box, over the WHOLE sequence (so neighbours and hand-offs count against it)
  tiles     240, 120 and 60 px square windows on a half-size stride (a tile counts if 5 % of it moves), the worst reported per size
Per pixel: extremum tracker, swing >= 0.10; region event: >= 25 % of the footprint swung the same way within 100 ms (6 frames);
flash = two opposite region events; pass = no 1 s window holds more than 3 flashes.  Luminance is WCAG relative luminance,
2x2 decimated (area shares unchanged)."""
import sys, os, json, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np

WK = 'D:/rc_scratch/combat_redesign/locked/fx_o30/work/'
FPS, WIN, SWING, AREA, FOOT = 60, 6, 0.10, 0.25, 0.02


def pixel_events(L):
    """L: T x N float32.  returns ev_up, ev_dn (T x N bool) exactly as fxlib.flash_check"""
    T, N = L.shape
    ext = L[0].copy()
    mn, mx_ = L[0].copy(), L[0].copy()
    dirn = np.zeros(N, np.int8)
    ev_up = np.zeros((T, N), bool)
    ev_dn = np.zeros((T, N), bool)
    for t in range(1, T):
        v = L[t]
        z = dirn == 0
        mn = np.where(z, np.minimum(mn, v), mn)
        mx_ = np.where(z, np.maximum(mx_, v), mx_)
        u0 = z & (v - mn >= SWING)
        d0 = z & ~u0 & (mx_ - v >= SWING)
        pu = dirn == 1
        pd = dirn == -1
        ext = np.where(pu & (v > ext), v, ext)
        ext = np.where(pd & (v < ext), v, ext)
        d1 = pu & (ext - v >= SWING)
        u1 = pd & (v - ext >= SWING)
        u_ = u0 | u1
        d_ = d0 | d1
        ev_up[t], ev_dn[t] = u_, d_
        dirn = np.where(u_, 1, np.where(d_, -1, dirn)).astype(np.int8)
        ext = np.where(u_ | d_, v, ext)
    return ev_up, ev_dn


def region_flashes(eu, ed, L):
    """eu, ed, L: T x nR for the footprint pixels of one region"""
    T = eu.shape[0]
    if eu.shape[1] == 0:
        return dict(footprint_px=0, flashes=0, flash_frames=[], max_flashes_per_s=0, max_area_swing_up=0.0, max_area_swing_down=0.0, mean_curve=[])
    cu = np.concatenate([np.zeros((1, eu.shape[1]), np.int32), np.cumsum(eu, 0, dtype=np.int32)])
    cd = np.concatenate([np.zeros((1, ed.shape[1]), np.int32), np.cumsum(ed, 0, dtype=np.int32)])
    lo = np.maximum(0, np.arange(T) - WIN + 1)
    up = ((cu[1:] - cu[lo]) > 0).mean(1)
    dn = ((cd[1:] - cd[lo]) > 0).mean(1)
    events = []
    for t in range(T):
        for sgn, arr in ((1, up), (-1, dn)):
            if arr[t] >= AREA and (t == 0 or arr[t - 1] < AREA):
                events.append((t, sgn))
    events.sort()
    flashes = []
    last = None
    for t, s in events:
        if last is not None and s != last[1]:
            flashes.append(t)
            last = None
        else:
            last = (t, s)
    mx = 0
    for t in flashes:
        mx = max(mx, sum(1 for u in flashes if t <= u < t + FPS))
    mc = L.mean(1)
    return dict(footprint_px=int(eu.shape[1]) * 4, flashes=len(flashes), flash_frames=flashes, region_events=[(int(t), int(s)) for t, s in events],
                max_flashes_per_s=mx, max_area_swing_up=round(float(up.max()), 3), max_area_swing_down=round(float(dn.max()), 3),
                mean_curve=[round(float(x), 4) for x in mc], max_mean_step=round(float(np.abs(np.diff(mc)).max()), 4))


def main():
    mode = sys.argv[1]
    tl = json.load(open(WK + 'timeline.json'))
    segs, meta = tl[:-1], tl[-1]
    Lm = np.load(WK + 'lum_%s.npy' % mode, mmap_mode='r')
    T, Hh, Ww = Lm.shape
    L = np.asarray(Lm, np.float32)
    dev = np.abs(L - L[0:1]).max(0)
    foot = dev > FOOT
    print('frames', T, 'footprint share', round(float(foot.mean()), 3), flush=True)
    fy, fx = np.nonzero(foot)
    Lf = L[:, fy, fx]
    del L
    eu, ed = pixel_events(Lf)
    idx = -np.ones((Hh, Ww), np.int64)
    idx[fy, fx] = np.arange(len(fy))

    def region(mask):
        sel = idx[mask & foot]
        return region_flashes(eu[:, sel], ed[:, sel], Lf[:, sel])

    def ms(k):
        return round(-meta['pre'] + k * 1000.0 / FPS, 1)

    def seg_of(k):
        T_ = ms(k)
        nm = 'pre'
        for s in segs:
            if T_ >= s['start']:
                nm = s['name']
        return nm

    out = dict(mode=mode, frames=T, fps=FPS, total_ms=meta['total'], method=__doc__)
    w = region(np.ones((Hh, Ww), bool))
    w['flash_ms'] = [(ms(k), seg_of(k)) for k in w['flash_frames']]
    out['whole'] = {k: v for k, v in w.items() if k != 'mean_curve'}
    out['whole_mean_curve'] = w['mean_curve']
    import o30_seq as Q
    Q.init()
    boxes = {}
    for s in Q.SEGS:
        if s['name'] in ('settle',):
            continue
        fid = s['fid']
        if s['name'] == 'shield_block':
            b = Q.SH_BOX
            box = (b.x0, b.y0, b.x1, b.y1)
        elif s['name'] == 'twist':
            b = Q.RBOX
            box = (b.x0, b.y0, b.x1, b.y1)
        elif s['name'] == 'trace_add':
            b = Q.TBOX
            box = (b.x0, b.y0, b.x1, b.y1)
        elif fid in Q.E.FX:
            box = tuple(Q.E.FX[fid]['box'])
        else:
            box = tuple(Q.CD.BYID[fid]['box'])
        m = np.zeros((Hh, Ww), bool)
        m[box[1] // 2:box[3] // 2, box[0] // 2:box[2] // 2] = True
        rr = region(m)
        rr['flash_ms'] = [(ms(k), seg_of(k)) for k in rr['flash_frames']]
        rr.pop('mean_curve')
        rr['box'] = box
        boxes[s['name']] = rr
        print('box', s['name'], rr['flashes'], 'max/s', rr['max_flashes_per_s'], rr['flash_ms'], flush=True)
    out['boxes'] = boxes
    tiles_all = []
    out['tiles'] = {}
    for full_px in (240, 120, 60):
        tp, st = full_px // 2, full_px // 4
        tiles = []
        for y0 in range(0, Hh - tp + 1, st):
            for x0 in range(0, Ww - tp + 1, st):
                m = np.zeros((Hh, Ww), bool)
                m[y0:y0 + tp, x0:x0 + tp] = True
                if (m & foot).sum() < 0.05 * tp * tp:
                    continue
                rr = region(m)
                tiles.append(dict(size=full_px, x0=x0 * 2, y0=y0 * 2, flashes=rr['flashes'], max_flashes_per_s=rr['max_flashes_per_s'],
                                  flash_ms=[(ms(k), seg_of(k)) for k in rr['flash_frames']], footprint_px=rr['footprint_px']))
        tiles.sort(key=lambda d: (-d['max_flashes_per_s'], -d['flashes']))
        out['tiles'][str(full_px)] = dict(n=len(tiles), worst=tiles[:10], max_flashes_per_s=tiles[0]['max_flashes_per_s'] if tiles else 0)
        print('tiles', full_px, len(tiles), 'worst', tiles[0] if tiles else None, flush=True)
        tiles_all += tiles
    tiles = sorted(tiles_all, key=lambda d: (-d['max_flashes_per_s'], -d['flashes']))
    mx = max([out['whole']['max_flashes_per_s']] + [b['max_flashes_per_s'] for b in boxes.values()] + [t['max_flashes_per_s'] for t in tiles])
    out['max_flashes_per_s_any_region'] = mx
    out['passes'] = mx <= 3
    json.dump(out, open(WK + 'meter_%s.json' % mode, 'w'), indent=1)
    print('whole', out['whole']['flashes'], 'max/s', out['whole']['max_flashes_per_s'], out['whole']['flash_ms'])
    print('MAX any region', mx, 'pass', out['passes'])


if __name__ == '__main__':
    main()
