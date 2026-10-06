"""ART-9 4A: bakes the MAINFRAME sign v4 (round 33) into per-letter light layers for the game.

Uses round 33's flicker_sign.py / board.py on tag `art-concepts-r43` (see mainframe_facade_bake.py for
how to extract them). Run as a file:

    python tools/art_bake/mainframe_sign_bake.py --gen <...>/docs/concepts/round33_mainframe_sign/scripts

Writes under assets/backdrops/shop/:
    sign_base.png     the plate with every tube dark (RGBA; alpha = the plate)
    sign_layers.png   an atlas of light layers (RGB), each the change one element makes when lit
    sign_layers.json  where each layer sits in the atlas and on the sign canvas, and whether the
                      game adds it (light) or subtracts it (snapped glass, soot)

Layers: `<pal>_frame`, `<pal>_rail` and `<pal>_<i>` (letter i of M A I N F R A M E) for the blue and
red palettes, `red_<i>o` for the two A's lit only as an "o", `soot` and `brk_<i>` (a dead letter's
snapped tube). The game draws sign = base + sum(level * layer), which is the round 33 render for
letters that do not overlap (their halos add). Data pulses are left out (static traces).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'backdrops', 'shop')
# The sign canvas is drawn at this share of round 33's 1x canvas (390x1174): the plate is about
# 1.5x its on-screen size at 1280x720, so it stays sharp in a 1920 window.
SCALE = 0.64
GLOW_K = 0.35          # round 33 composite: the glow is screened over the facade at 0.35
ATLAS_W = 1024
THRESH = 2.0 / 255.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--gen', required=True)
    a = ap.parse_args()
    sys.path.insert(0, a.gen)
    import flicker_sign as FS  # noqa: E402
    import board as BD  # noqa: E402

    mode = {'rail': 'off'}
    orig = BD.Board.light

    def light(self, levels, pulse_t=None):
        lv = dict(levels)
        if mode['rail'] == 'off':
            lv.pop('rail', None)
        elif mode['rail'] == 'only':
            lv = {'rail': (1.0, FS.PAL[FS.SIGN_PAL][0])}
        return orig(self, lv, pulse_t)

    BD.Board.light = light
    s = FS.FlickerSign('mainframe')
    keys = s.keys

    def comp(res):
        al = np.clip(res['alpha'], 0, 1)[..., None]
        return al * np.clip(res['plate'], 0, 1) + GLOW_K * np.clip(res['glow'], 0, None), al

    def r(**kw):
        return s.render(**kw)

    FS.SIGN_PAL = 'blue'
    base, alpha = comp(r(frame=0.0))
    FS.SIGN_PAL = 'red'
    base_red = comp(r(frame=0.0))[0]
    # the red sign's dark glass is tinted red: one level swaps the tint (both layers together)
    layers = {'glass_red': ('add', base_red - base), 'glass_blue': ('sub', base - base_red)}
    for pal, b0 in (('blue', base), ('red', base_red)):
        FS.SIGN_PAL = pal
        mode['rail'] = 'off'
        layers['%s_frame' % pal] = ('add', comp(r(frame=1.0))[0] - b0)
        for i, k in enumerate(keys):
            layers['%s_%d' % (pal, i)] = ('add', comp(r(frame=0.0, normal={k: 1.0}))[0] - b0)
        mode['rail'] = 'only'
        layers['%s_rail' % pal] = ('add', comp(r(frame=0.0))[0] - b0)
    FS.SIGN_PAL = 'red'
    mode['rail'] = 'off'
    for i, k in enumerate(keys):
        if (k, 'o') in s.alt and s.lets[i][1] == 'A':
            layers['red_%do' % i] = ('add', comp(r(frame=0.0, msg={k: 'o'}))[0] - base_red)
    sooted = comp(r(frame=0.0, broken={'none'}))[0]
    layers['soot'] = ('sub', base_red - sooted)
    for i, k in enumerate(keys):
        layers['brk_%d' % i] = ('sub', sooted - comp(r(frame=0.0, broken={k}))[0])

    ch, cw = base.shape[:2]
    size = (int(round(cw * SCALE)), int(round(ch * SCALE)))

    def small(img):
        chans = [np.asarray(Image.fromarray(img[..., c].astype(np.float32), 'F').resize(size, Image.LANCZOS))
                 for c in range(img.shape[-1])]
        return np.clip(np.stack(chans, -1), 0, 1)

    os.makedirs(OUT, exist_ok=True)
    base_rgba = np.concatenate([small(np.where(alpha > 0, base / np.maximum(alpha, 1e-4), 0)), small(alpha)], -1)
    Image.fromarray((base_rgba * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(OUT, 'sign_base.png'), optimize=True)
    # shelf-pack the cropped layers
    crops = []
    for name in sorted(layers):
        m, img = layers[name]
        sm = small(np.clip(img, 0, None))
        mask = sm.max(-1) > THRESH
        ys, xs = np.nonzero(mask)
        if len(ys) == 0:
            continue
        y0, y1 = max(0, ys.min() - 1), min(size[1], ys.max() + 2)
        x0, x1 = max(0, xs.min() - 1), min(size[0], xs.max() + 2)
        crops.append((name, m, sm[y0:y1, x0:x1], (x0, y0)))
    crops.sort(key=lambda c: (-c[2].shape[0], c[0]))
    x = y = shelf = 0
    place = {}
    for name, m, img, at in crops:
        h, w = img.shape[:2]
        if x + w > ATLAS_W:
            x, y, shelf = 0, y + shelf, 0
        place[name] = (x, y)
        x += w
        shelf = max(shelf, h)
    atlas_h = y + shelf
    atlas = np.zeros((atlas_h, ATLAS_W, 3), np.float32)
    meta = {}
    for name, m, img, at in crops:
        px, py = place[name]
        h, w = img.shape[:2]
        atlas[py:py + h, px:px + w] = img
        meta[name] = dict(rect=[px, py, w, h], at=[int(at[0]), int(at[1])], mode=m)
    Image.fromarray((atlas * 255 + 0.5).astype(np.uint8), 'RGB').save(os.path.join(OUT, 'sign_layers.png'), optimize=True)
    info = dict(canvas=[size[0], size[1]],
                plate=[round(FS.MARGIN * SCALE, 2), round(FS.MARGIN * SCALE, 2), round(FS.PW * SCALE, 2), round(FS.PH * SCALE, 2)],
                letters=[l[1] for l in s.lets], layers=meta)
    with open(os.path.join(OUT, 'sign_layers.json'), 'w') as fh:
        json.dump(info, fh, indent=1, sort_keys=True)
    print('sign', size, 'atlas', ATLAS_W, atlas_h, len(meta), 'layers')


if __name__ == '__main__':
    main()
