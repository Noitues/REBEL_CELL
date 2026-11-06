"""o30_render.py  prep <full|red>            chain canvases (each segment's base = the previous segment's settled frame)
               frames <full|red> <i,j,..>  render every 60 fps frame of those segments -> luminance memmap + 960 px jpgs
               one <full|red> <T_ms> <out.png>   one full-res frame of the sequence at sequence time T
Sequence time starts with 100 ms of the p2 plate (SEND IT not yet pressed) and ends 300 ms after the last effect."""
import sys, os, json, math, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import o30_seq as Q

WK = Q.O30 + 'work/'
FPS = 60
PRE = 100
LH, LW = 540, 960


def canvas_path(mode, i):
    return WK + 'canvas_%s_%02d.npy' % (mode, i)


def timeline():
    segs = Q.init()
    end = Q.total_ms()
    n = int(math.floor((end + PRE) * FPS / 1000.0)) + 1
    return segs, n


def seg_at(segs, T):
    k = 0
    for i, s in enumerate(segs):
        if T >= s['start']:
            k = i
    return k


def setup_for(segs, i, mode):
    """run the segment's setup with the right canvas (a 'keep' segment reuses the last real setup's canvas)"""
    j = i
    while j >= 0 and segs[j]['setup'] == 'keep':
        j -= 1
    if j >= 0 and callable(segs[j]['setup']):
        segs[j]['setup'](np.load(canvas_path(mode, j)))


def render(segs, i, t, red, mode):
    s = segs[i]
    cv = np.load(canvas_path(mode, i)) if i > 0 else None
    return s['render'](t, red, cv)


_cv = {}


def render_c(segs, i, t, red, mode):
    if i not in _cv:
        _cv[i] = np.load(canvas_path(mode, i)) if i > 0 else None
        setup_for(segs, i, mode)
    return segs[i]['render'](t, red, _cv[i])


def main():
    cmd, mode = sys.argv[1], sys.argv[2]
    red = mode == 'red'
    segs, n = timeline()
    if cmd == 'prep':
        json.dump([dict(name=s['name'], fid=s['fid'], start=s['start'], dur=s['dur']) for s in segs] + [dict(total=Q.total_ms(), frames=n, pre=PRE, r1_units=Q.R1U)],
                  open(WK + 'timeline.json', 'w'), indent=1)
        for i, s in enumerate(segs[:-1]):
            t0 = time.time()
            if i > 0:
                setup_for(segs, i, mode)
            cv = np.load(canvas_path(mode, i)) if i > 0 else None
            end = s['render'](float(s['dur'] + Q.GAP), red, cv)
            np.save(canvas_path(mode, i + 1), end.astype(np.float32))
            _cv.clear()
            print('prep', mode, i + 1, segs[i + 1]['name'], round(time.time() - t0, 1), flush=True)
        return
    if cmd == 'frames':
        ids = [int(x) for x in sys.argv[3].split(',')]
        mm = np.lib.format.open_memmap(WK + 'lum_%s.npy' % mode, mode='r+')
        jd = Q.O30 + 'frames/%s/' % mode
        os.makedirs(jd, exist_ok=True)
        for k in range(n):
            T = -PRE + k * 1000.0 / FPS
            i = 0 if T < 0 else seg_at(segs, T)
            if i not in ids:
                continue
            t = -1.0 if T < 0 else T - segs[i]['start']
            if T < 0:
                fr = Q.P2 if i == 0 else None
                fr = Q.ring1_move(Q.pre_hud(Q.P2), -60.0)
            else:
                fr = render_c(segs, i, t, red, mode)
            fr = np.clip(fr, 0, 255)
            from fxlib import rel_lum
            mm[k] = rel_lum(fr)[::2, ::2].astype(np.float16)
            Image.fromarray(fr.astype(np.uint8)).resize((LW, LH), Image.LANCZOS).save(jd + '%04d.jpg' % k, quality=88)
            if k % 30 == 0:
                print(mode, 'frame', k, '/', n, segs[i]['name'], flush=True)
        mm.flush()
        return
    if cmd == 'one':
        T = float(sys.argv[3])
        i = seg_at(segs, T)
        fr = render_c(segs, i, T - segs[i]['start'], red, mode) if T >= 0 else Q.ring1_move(Q.pre_hud(Q.P2), -60.0)
        Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).save(sys.argv[4])
        print('one', mode, T, segs[i]['name'], T - segs[i]['start'])
        return
    if cmd == 'alloc':
        np.lib.format.open_memmap(WK + 'lum_%s.npy' % mode, mode='w+', dtype=np.float16, shape=(n, LH, LW))
        print('alloc', mode, n)


if __name__ == '__main__':
    main()
