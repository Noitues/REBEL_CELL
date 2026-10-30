"""Shared compositing + squint helpers for the combat backdrop concepts."""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

OUT = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/'
SCR = 'D:/rc_scratch/solace_concepts/'
BOARD = np.asarray(Image.open(SCR + 'board_rgba.png')).astype(np.float32) / 255
E10 = np.asarray(Image.open('D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png').convert('RGB')).astype(np.float32) / 255
ALPHA = BOARD[..., 3]


def compose(bd):
    """bd: float RGB 0..1 (1080,1920,3). Returns plate float RGB."""
    # soft contact shadow so the board sits on the backdrop
    sh = ndi.gaussian_filter(ALPHA, 14)
    sh = np.roll(np.roll(sh, 10, axis=0), 6, axis=1)
    bd = bd * (1 - 0.38 * sh[..., None])
    return bd * (1 - ALPHA[..., None]) + BOARD[..., :3] * ALPHA[..., None]


def squint(img):
    """Heavy blur at 1/16 scale, brought back to full size."""
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    sm = im.resize((120, 68), Image.BOX).filter(ImageFilter.GaussianBlur(0.7))
    return np.asarray(sm.resize((1920, 1080), Image.BICUBIC)).astype(np.float32) / 255


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114], np.float32)


def stats(plate_or_bd, name):
    """Backdrop-visible stats on the squinted image (where the board alpha is < 0.5)."""
    sq = squint(plate_or_bd)
    vis = ALPHA < 0.5
    l = lum(sq)[vis]
    mx = sq.max(2)
    mn = sq.min(2)
    sat = ((mx - mn) / (mx + 1e-6))[vis]
    # loud mass: share of visible area brighter than 0.38 luminance in the squint
    return dict(name=name, mean=float(l.mean()), p95=float(np.percentile(l, 95)), sat=float(sat.mean()), loud=float((l > 0.38).mean()))


def save(a, path):
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(path)
