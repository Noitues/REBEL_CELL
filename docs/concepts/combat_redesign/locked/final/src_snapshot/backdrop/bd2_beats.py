"""bd2_beats.py : per-beat transfer estimate from the real plates, for solving the room grade on every beat.
In the rb_checks room region the plate is the backdrop times a shadow / scrim transfer (F ~ 0 there): T_est = plate / backdrop, from the
real neutral plate of each beat and the backdrop it was rendered with (bio, the embedded rb2-1 grade).  plate2 ~ T_est * backdrop2.
Prints the real and the re-predicted room numbers per beat (sanity) and the box / street split."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
from PIL import Image
import bd2_lib as L
import bd_grade as BG
import rb_tokens as TK

BOARD = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
BEATS = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords'}
_T = {}


def transfer(beat, corp='neutral'):
    key = (beat, corp)
    if key not in _T:
        room = BG.CORP_ROOM[corp]
        bd = L.backdrop(room, BG.params_for(room, corp)).astype(np.float32)
        nm = BEATS[beat] + ('' if corp == 'neutral' else '_' + corp)
        pl = np.asarray(Image.open(BOARD + nm + '.png').convert('RGB'), np.float32)
        reg = L.room_region(beat if corp == 'neutral' else beat + '_' + corp)
        T = np.clip(pl / np.maximum(bd, 1.0), 0, 1.5)
        T[bd < 6] = 1.0                       # no estimate on near-black backdrop: assume plain backdrop
        _T[key] = (T, reg, pl)
    return _T[key]


def stats_from(bd, beat, corp='neutral'):
    T, reg, _ = transfer(beat, corp)
    pl = np.clip(T * bd, 0, 255)
    Y = TK.lum(pl[reg].astype(np.float64))
    return float(TK.lstar(Y.mean())), float(np.percentile(TK.lstar(Y), 95))


if __name__ == '__main__':
    poly = BG.ROOMS['bio']['hull_poly']
    inside = BG.poly_sdf(poly) < 0
    bd = L.backdrop('bio', BG.ROOMS['bio']).astype(np.float32)
    for b in BEATS:
        T, reg, pl = transfer(b)
        Y = TK.lum(pl.astype(np.float64))
        real = (float(TK.lstar(Y[reg].mean())), float(np.percentile(TK.lstar(Y[reg]), 95)))
        pred = stats_from(bd, b)
        box = reg & inside
        st = reg & ~inside
        print('%-8s px %6d real %.2f/%.2f pred %.2f/%.2f | box px %6d mean %.1f | street px %6d mean %.1f' % (
            b, reg.sum(), real[0], real[1], pred[0], pred[1], box.sum(), float(TK.lstar(Y[box].mean())) if box.any() else -1,
            st.sum(), float(TK.lstar(Y[st].mean()))))
