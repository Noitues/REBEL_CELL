"""mp_beat_render.py <full|red> <i0> <i1>: render beat frames i0 .. i1-1 (60 fps, T = i * 1000 / 60) of mp_beat ->
  work/beat/<mode>_<i0>.npz : lum (n x 540 x 960 float16: WCAG relative luminance of every 2nd px, = flash_check's 2x2 decimation),
                              rgb (n x 540 x 960 uint8, the same px: the GIF), idx (frame numbers)
  work/beat/skip_<mode>_<i0>.npz : for every skip time Ts in SKIPS with Ts <= T < Ts + SKIP_MS: the lum of the skip dissolve frame
  work/beat/key_<mode>_<T>.png : the full-size keyframes (KEYS) for the strip"""
import sys, os, time
sys.dont_write_bytecode = True
import numpy as np
import mp_beat as B
from mp_lib import rel_lum, to_img, ME

FPS = 60
N = int(round((B.TOTAL_MS + B.TAIL_MS) * FPS / 1000.0)) + 1
SKIPS = list(range(250, int(B.TOTAL_MS), 250))
KEYS = [0, 250, 520, 700, 900, 1020, 1160, 1400, 1640, 2080, 2250, 2480, 2740, 3000, 3400, 3650, 3800]
KEYI = {int(round(k * FPS / 1000.0)): k for k in KEYS}

if __name__ == '__main__':
    mode, i0, i1 = sys.argv[1], int(sys.argv[2]), min(int(sys.argv[3]), N)
    red = mode == 'red'
    os.makedirs(ME + 'work/beat', exist_ok=True)
    lum, rgb, idx, sk = [], [], [], {}
    t0 = time.time()
    for i in range(i0, i1):
        T = i * 1000.0 / FPS
        f = np.clip(B.frame(T, red), 0, 255)
        if i in KEYI:
            to_img(f).save(ME + 'work/beat/key_%s_%d.png' % (mode, KEYI[i]))
        d = f[::2, ::2]
        lum.append(rel_lum(d).astype(np.float16))
        rgb.append(d.astype(np.uint8))
        idx.append(i)
        for Ts in SKIPS:
            if Ts <= T < Ts + B.SKIP_MS + 1000.0 / FPS:
                g = B.skip_frame(T, Ts, f, red)[::2, ::2]
                sk['%d_%d' % (Ts, i)] = rel_lum(g).astype(np.float16)
        print(mode, i, round(T, 1), round(time.time() - t0, 1), flush=True)
    np.savez(ME + 'work/beat/%s_%04d.npz' % (mode, i0), lum=np.stack(lum), rgb=np.stack(rgb), idx=np.array(idx))
    np.savez(ME + 'work/beat/skip_%s_%04d.npz' % (mode, i0), **sk)
    print('done', mode, i0, i1, round(time.time() - t0, 1), flush=True)
