"""P1 beam heads = the designer-locked H6 family (D worm / N thorn claw / E sea-mine), drawn as ONE isolated screen-space sprite layer
(swappable: replace sprite() and nothing else re-renders). Size 44 px at 1920 (E at 0.852 x), rim light + ink outline from heads6.
N claw refined here (not in H6): thicker prongs, an asymmetric hook (upper horn hooks back, lower horn is a straight blade) so it never reads as a
'3' or a Euro sign at any heading."""
import sys, math
import numpy as np
from PIL import Image
H6 = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H6_heads_final/scripts'
if H6 not in sys.path:
    sys.path.insert(0, H6)
import heads6 as H
from shapes_h3 import circ, bez, taper

import os
S = int(os.environ.get('P2_S', '1'))
SIZE = 44


def raw_N2(f, amp):
    o = H.C(f)
    op = .2 * amp * o
    ops = [('add', circ(-.45, 0, .40, 26)), ('add', H.rect(-1.05, -.22, -.7, .22)), H.dot(-.45, 0)]
    # upper horn: thick sweep with a SHARP BARB on its inner side (asymmetric hook, points back at the hub)
    p1 = bez((-.3, -.3), (.3, -(.6 + op)), (.6, -(1.3 + op)), (1.1, -(.55 + op * .5)), 16)
    ops.append(('add', taper(p1, .40, .24)))
    ops.append(('add', [(.55, -(.98 + op)), (.30, -(.55 + op * .5)), (.80, -(.80 + op * .6))]))
    # lower horn: a straighter, shorter blade (no barb)
    p2 = bez((-.3, .3), (.2, .55 + op), (.5, .85 + op), (.85, .85 + op * .6), 14)
    ops.append(('add', taper(p2, .40, .22)))
    ops.append(('add', taper([(-.2, 0), (.35, 0)], .30, .20)))
    return ops


H.RAW['N'] = raw_N2
_cache = {}


def sprite(typ, ang_deg, size=SIZE):
    """RGBA PIL sprite (premult not applied) of head `typ` heading `ang_deg` (screen angle, y down)."""
    key = (typ, round(ang_deg), size)
    if key not in _cache:
        ops = H.head(typ)
        _cache[key] = H.render_head(ops, size, ang_deg, H.HUE[typ])
    return _cache[key]


def draw(cv, items, blur_fn, k_glow=0.45):
    """items: dicts typ, x, y, ang, k. cv is a lib.Cv (sRGB float canvas)."""
    for it in items:
        im = sprite(it['typ'], it['ang'], it.get('size', SIZE) * S)
        a = np.asarray(im, np.float32) / 255
        rgb = a[..., :3]
        al = a[..., 3] * it.get('k', 1.0)
        off = (int(round(it['x'] * S - im.width / 2)), int(round(it['y'] * S - im.height / 2)))
        col = np.array(H.HUE[it['typ']], np.float32) / 255
        pad = 24 * S
        if it.get('halo'):
            # P2: an ink halo (3 px) under the sprite so the head stays legible on a hot impact / flash
            hb_ = np.zeros((al.shape[0] + 2 * pad, al.shape[1] + 2 * pad), np.float32)
            hb_[pad:-pad, pad:-pad] = al
            ink = np.clip(blur_fn(hb_, 3.0) * 4.0, 0, 1)
            cv.over(np.array([0.02, 0.015, 0.06], np.float32), ink, 0.85, (off[0] - pad, off[1] - pad))
        big = np.zeros((al.shape[0] + 2 * pad, al.shape[1] + 2 * pad), np.float32)
        big[pad:-pad, pad:-pad] = al
        cv.add(col, blur_fn(big, 8), k_glow * it.get('k', 1.0), (off[0] - pad, off[1] - pad))
        cv.over(rgb, al, 1.0, off)
