"""beat_guard.py: review 1.8 in the resolve beat, measured on the rendered 60 fps beat frames (work/beat/full_*.npz, every 2nd px).
Round each kill token (Packet 1 at kill_p1, Worm 2 at kill: CD.TOK3['1'], CD.TOK3['2']), within 90 px, during its kill track:
px within dE76 15 of GAIN, FOCUS, lime (fxk_lib.TOKEN_GUARD) and of CELL_PINK, minus the same count on the settled beat frame
(the board's own marks), as the peak over the track's frames, in full-size px (x 4).  -> work/beat/guard.json"""
import sys, glob, json
sys.dont_write_bytecode = True
import numpy as np
from mp_lib import ME
import mp_beat as B
CD, K = B.CD, B.K

fs = sorted(glob.glob(ME + 'work/beat/full_[0-9]*.npz'))
rgb = np.concatenate([np.load(f)['rgb'] for f in fs])
cols = dict(K.TOKEN_GUARD)
cols['CELL_PINK'] = tuple(K.RT.TOKENS['CELL_PINK'])
out = {}
for trk, tok in (('kill_p1', CD.TOK3['1']), ('kill', CD.TOK3['2'])):
    s, du = B.TL[trk], B.DUR[trk]
    cx, cy = tok[0] / 2.0, tok[1] / 2.0
    yy, xx = np.mgrid[0:rgb.shape[1], 0:rgb.shape[2]]
    m = np.hypot(xx - cx, yy - cy) <= 45
    def count(img):
        lab = K.RT.lab(img[m].astype(np.float64))
        return {k: int((np.linalg.norm(lab - K.RT.lab(np.array(c, np.float64)), axis=1) < 15.0).sum()) * 4 for k, c in cols.items()}
    base = count(rgb[-1])
    peak = {k: 0 for k in cols}
    for i in range(int(s * 60 / 1000), min(len(rgb), int((s + du) * 60 / 1000) + 1)):
        c = count(rgb[i])
        for k in cols:
            peak[k] = max(peak[k], c[k] - base[k])
    out[trk] = dict(token=tok, radius_px=90, settled_frame_px=base, peak_added_px=peak)
    print(trk, tok, 'settled', base, 'peak added', peak, flush=True)
json.dump(dict(method=__doc__, **out), open(ME + 'work/beat/guard.json', 'w'), indent=1)
