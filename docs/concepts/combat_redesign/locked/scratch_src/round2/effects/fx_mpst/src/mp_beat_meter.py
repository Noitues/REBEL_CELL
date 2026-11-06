"""mp_beat_meter.py <full|red>: the 60 fps flash meter (NOTES_MPST method, unchanged) over the whole resolve beat and over every skip path.
Regions, each judged against its own footprint (px whose relative luminance moves > 0.02 from frame 0 of the run):
  whole       the whole 1920 x 1080 frame
  box:<track> each track's own box, over the WHOLE beat (neighbours and hand-offs count against it)
  tiles       240, 120 and 60 px windows on a half-size stride (a tile counts if 5 % of it moves); the worst per size is reported
Skip paths: the player skips at Ts (every 250 ms): beat frames up to Ts, the 200 ms dissolve to the settled frame, 300 ms settled;
measured from Ts - 1000 ms (the whole 1 s window before the skip counts), whole frame and the same tiles.
Per pixel: extremum tracker, swing >= 0.10; region event: >= 25 % of the footprint swung the same way within 100 ms (6 frames);
flash = two opposite region events; pass = no 1 s window holds more than 3 flashes.  -> work/beat/meter_<mode>.json"""
import sys, os, json, glob
sys.dont_write_bytecode = True
import numpy as np
import mp_beat as B
import mp_beat_render as BR
from mp_lib import ME

FPS, WIN, SWING, AREA, FOOT = 60, 6, 0.10, 0.25, 0.02


def pixel_events(L):
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


def region_flashes(eu, ed):
    T = eu.shape[0]
    if eu.shape[1] == 0:
        return dict(footprint_px=0, flashes=0, flash_frames=[], max_flashes_per_s=0, max_area_swing_up=0.0, max_area_swing_down=0.0)
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
    return dict(footprint_px=int(eu.shape[1]) * 4, flashes=len(flashes), flash_frames=flashes, max_flashes_per_s=mx,
                max_area_swing_up=round(float(up.max()), 3), max_area_swing_down=round(float(dn.max()), 3))


def meter(L, t_of, boxes=None, tiles=True):
    """L: T x h x w float32 lum.  returns whole / boxes / tiles results"""
    T, Hh, Ww = L.shape
    foot = np.abs(L - L[0:1]).max(0) > FOOT
    fy, fx = np.nonzero(foot)
    Lf = L[:, fy, fx]
    eu, ed = pixel_events(Lf)
    idx = -np.ones((Hh, Ww), np.int64)
    idx[fy, fx] = np.arange(len(fy))

    def region(mask):
        sel = idx[mask & foot]
        r = region_flashes(eu[:, sel], ed[:, sel])
        r['flash_ms'] = [t_of(k) for k in r['flash_frames']]
        return r
    out = dict(frames=T, footprint_share=round(float(foot.mean()), 3))
    out['whole'] = region(np.ones((Hh, Ww), bool))
    if boxes:
        out['boxes'] = {}
        for nm, (x0, y0, x1, y1) in boxes.items():
            m = np.zeros((Hh, Ww), bool)
            m[y0 // 2:y1 // 2, x0 // 2:x1 // 2] = True
            r = region(m)
            r['box'] = (x0, y0, x1, y1)
            out['boxes'][nm] = r
    if tiles:
        out['tiles'] = {}
        for full_px in (240, 120, 60):
            tp, st = full_px // 2, full_px // 4
            res = []
            for y0 in range(0, Hh - tp + 1, st):
                for x0 in range(0, Ww - tp + 1, st):
                    m = np.zeros((Hh, Ww), bool)
                    m[y0:y0 + tp, x0:x0 + tp] = True
                    if (m & foot).sum() < 0.05 * tp * tp:
                        continue
                    r = region(m)
                    res.append(dict(x0=x0 * 2, y0=y0 * 2, flashes=r['flashes'], max_flashes_per_s=r['max_flashes_per_s'], flash_ms=r['flash_ms']))
            res.sort(key=lambda d: (-d['max_flashes_per_s'], -d['flashes']))
            out['tiles'][str(full_px)] = dict(n=len(res), worst=res[:6], max_flashes_per_s=res[0]['max_flashes_per_s'] if res else 0)
    vals = [out['whole']['max_flashes_per_s']] + [b['max_flashes_per_s'] for b in out.get('boxes', {}).values()] + [t['max_flashes_per_s'] for t in out.get('tiles', {}).values()]
    out['max_flashes_per_s_any_region'] = max(vals)
    out['passes'] = out['max_flashes_per_s_any_region'] <= 3
    return out


def track_boxes():
    bx = {}
    for nm, s, d, f, c in B.TRACKS:
        if nm in B.CDX:
            bx[nm] = tuple(B.CDX[nm]['box'])
        elif nm == 'twist':
            bx[nm] = B.RBOX.t()
        elif nm == 'trace_add':
            bx[nm] = B.TRBOX.t()
        elif nm == 'rings_step':
            bx[nm] = B.RSBOX.t()
        elif nm == 'settle':
            bx[nm] = B.RSBOX.t()
        elif nm == 'commit':
            bx[nm] = (0, 0, 1920, 1080)
        else:
            bx[nm] = tuple(B.E.FX['fx_' + nm]['box'])
    bx['skip_hint'] = B.SKIP_BOX.t()          # round 2 (C12): the SKIP key hint's own box, over the whole beat
    return bx


def main():
    mode = sys.argv[1]
    fs = sorted(glob.glob(ME + 'work/beat/%s_[0-9]*.npz' % mode))
    lum, idx = [], []
    for f in fs:
        z = np.load(f)
        lum.append(z['lum'].astype(np.float32))
        idx.append(z['idx'])
    L = np.concatenate(lum)
    idx = np.concatenate(idx)
    assert (np.diff(idx) == 1).all() and idx[0] == 0 and len(idx) == BR.N, (idx[:3], len(idx), BR.N)
    sk = {}
    for f in sorted(glob.glob(ME + 'work/beat/skip_%s_*.npz' % mode)):
        z = np.load(f)
        for k in z.files:
            sk[k] = z[k].astype(np.float32)
    ms = lambda k: round(k * 1000.0 / FPS, 1)

    def seg_of(T_):
        nm = []
        for n, s, d, f, c in B.TRACKS:
            if s <= T_ < s + d:
                nm.append(n)
        return '+'.join(nm) or 'settled'
    out = dict(mode=mode, total_ms=B.TOTAL_MS, frames=int(len(idx)), skip_ms=B.SKIP_MS, method=__doc__, tracks=[dict(name=n, start_ms=s, dur_ms=d, family=f, what=c) for n, s, d, f, c in B.TRACKS])
    r = meter(L, lambda k: (ms(k), seg_of(ms(k))), track_boxes(), True)
    out['beat'] = r
    print('beat whole', r['whole']['flashes'], 'max/s', r['whole']['max_flashes_per_s'], r['whole']['flash_ms'], flush=True)
    for nm, b in r['boxes'].items():
        print('  box', nm, b['flashes'], 'max/s', b['max_flashes_per_s'], b['flash_ms'], flush=True)
    for k, t in r['tiles'].items():
        print('  tiles', k, t['n'], 'max/s', t['max_flashes_per_s'], t['worst'][:2], flush=True)
    settled = L[-1]
    out['skips'] = {}
    for Ts in BR.SKIPS:
        i_s = int(np.ceil(Ts * FPS / 1000.0 - 1e-9))
        i_from = max(0, int(round((Ts - 1000) * FPS / 1000.0)))
        frames = [L[i] for i in range(i_from, i_s)]
        k = i_s
        while ('%d_%d' % (Ts, k)) in sk:
            frames.append(sk['%d_%d' % (Ts, k)])
            k += 1
        frames += [settled] * int(300 * FPS / 1000)
        P = np.stack(frames)
        rr = meter(P, lambda j, i_from=i_from: ms(i_from + j), None, True)
        out['skips'][str(Ts)] = dict(whole=rr['whole'], tiles={kk: dict(max_flashes_per_s=v['max_flashes_per_s'], worst=v['worst'][:2]) for kk, v in rr['tiles'].items()},
                                     max_flashes_per_s_any_region=rr['max_flashes_per_s_any_region'], passes=rr['passes'], dissolve_frames=k - i_s)
        print('skip', Ts, 'whole', rr['whole']['flashes'], 'max any region', rr['max_flashes_per_s_any_region'], flush=True)
    out['max_flashes_per_s_beat'] = r['max_flashes_per_s_any_region']
    out['max_flashes_per_s_skips'] = max(v['max_flashes_per_s_any_region'] for v in out['skips'].values())
    out['passes'] = out['max_flashes_per_s_beat'] <= 3 and out['max_flashes_per_s_skips'] <= 3
    json.dump(out, open(ME + 'work/beat/meter_%s.json' % mode, 'w'), indent=1)
    print('MAX beat', out['max_flashes_per_s_beat'], 'skips', out['max_flashes_per_s_skips'], 'pass', out['passes'], flush=True)


if __name__ == '__main__':
    main()
