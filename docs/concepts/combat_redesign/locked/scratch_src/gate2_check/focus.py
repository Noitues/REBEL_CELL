"""focus.py -- FOCUS bracket colour vs the FOCUS token and the Solace leaf ink.
Pixels within dE76 10 of #96FF46 (Solace leaf) and within dE76 10 of #D4FF00 (FOCUS token), split into: inside the plan mask (hover brackets /
pencil are captured as 'plan') and outside it, on the board half (x < 1060).  Per p2b plate (the hover plate is the one with FOCUS brackets)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'


def to_lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[..., 0] + 0.3576 * c[..., 1] + 0.1805 * c[..., 2]) / 0.95047
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    Z = (0.0193 * c[..., 0] + 0.1192 * c[..., 1] + 0.9505 * c[..., 2]) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.stack([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))], -1)


LEAF = to_lab(np.array([0x96, 0xFF, 0x46]))
FOC = to_lab(np.array([0xD4, 0xFF, 0x00]))
for n, s in (('p2b_hover', 'p2b'), ('p2b_hover_solace', 'p2b_solace'), ('p2b_hover_meridian', 'p2b_meridian'), ('p1_decide_solace', 'p1_solace'),
             ('p2_preview_solace', 'p2_solace')):
    rgb = np.asarray(Image.open(FINAL + n + '.png').convert('RGB')).astype(float)
    lab = to_lab(rgb)
    z = np.load(WORK + 'masks_%s.npz' % s)
    plan = np.unpackbits(z['plan'])[:1080 * 1920].reshape(1080, 1920).astype(bool) if 'plan' in z.files else np.zeros((1080, 1920), bool)
    plan = ndi.binary_dilation(plan, iterations=2)
    board = np.zeros((1080, 1920), bool)
    board[:, :1060] = True
    nl = (np.linalg.norm(lab - LEAF, axis=-1) < 10) & board
    nf = (np.linalg.norm(lab - FOC, axis=-1) < 10) & board
    print('%-20s near Solace leaf: in plan mask %5d, outside %6d | near FOCUS #D4FF00: in plan %4d, outside %4d' % (
        n, int((nl & plan).sum()), int((nl & ~plan).sum()), int((nf & plan).sum()), int((nf & ~plan).sum())))
