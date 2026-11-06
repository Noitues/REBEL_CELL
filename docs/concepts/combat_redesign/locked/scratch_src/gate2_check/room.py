"""room.py -- room value on the 15 plates.

A: the rb_checks room region rebuilt from the masks (x >= 1100, y >= 420, r > 505, UI / hand / name / you / tags / leader dilated 4 px cut,
   scrim cut) -> L* of mean luminance, p95 (verifies checks.json);  A2: the same with the scrim kept (as seen).
B: an independent room read that needs no masks: the 1100-1900 x 430-1080 block minus every pixel whose 9x9 neighbourhood holds a NET_CYAN
   HUD edge, a card or sticker (here: any pixel of the hand / SEND / UNDO bounding boxes measured on the plate by colour is not attempted;
   instead the block is cut to x 1660-1900 x 440-850 + 1100-1660 x 640-760 where no UI sits on any beat -- see the 1x plates).
C: the reviewer's box 1200-1800 x 450-800 as measure.py reads it."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
C = (536, 540)


def lum(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def ls(y):
    y = np.asarray(y, float)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def load_masks(sfx):
    z = np.load(WORK + 'masks_%s.npz' % sfx)
    return {k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) for k in z.files}


yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
for base, s0 in (('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p2b_hover', 'p2b'), ('p3_resolve', 'p3'), ('p1_nowords', 'nowords')):
    for sk in ('', '_solace', '_meridian'):
        name, sfx = base + sk, s0 + sk
        Y = lum(np.asarray(Image.open(FINAL + name + '.png').convert('RGB')).astype(float))
        L = ls(Y)
        M = load_masks(sfx)
        get = lambda k: M.get(k, np.zeros((1080, 1920), bool))
        ui = get('hud') | get('hand_rest') | get('hand_lift') | get('hand_played') | get('send') | get('undo') | get('name') | get('you') | get('tags') | get('leader')
        base_r = (xx >= 1100) & (yy >= 420) & ~ndi.binary_dilation(ui, iterations=4) & (RHO > 505)
        a = base_r & ~get('scrim')
        a2 = base_r
        # B: a fixed open-room window clear of UI on every beat (checked on the 1x plates): right of the hand and under the HUD
        b = np.zeros((1080, 1920), bool)
        b[660:760, 1100:1640] = True
        b[650:850, 1660:1900] = True
        b &= ~ndi.binary_dilation(ui, iterations=4)
        rb_ = L[450:800, 1200:1800]
        print('%-22s A mean %.1f p95 %.1f (px %d) | A2 as seen mean %.1f | B open window mean %.1f p95 %.1f (px %d) | C box mean %.1f p95 %.1f' % (
            name, float(ls(Y[a].mean())), float(np.percentile(L[a], 95)), a.sum(), float(ls(Y[a2].mean())),
            float(ls(Y[b].mean())), float(np.percentile(L[b], 95)), b.sum(), float(ls(Y[450:800, 1200:1800].mean())), float(np.percentile(rb_, 95))))
