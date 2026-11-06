"""lc_lib: LINOCUT toolkit.  Two blocks (hot pink flat + carved black key), bone paper, scissor-cut facets, gouge lenses, ink grain.
All geometry 1x px; masks live on an f1_lib.Canvas at S x supersample."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
from f1_lib import Canvas, pol, arc_pts, smooth, warp, outline_mask, font, ANTON_F, MARKER_F, MONO_F

BONE = (240, 233, 214)          # paper
BONE_D = (205, 196, 176)
HOT = (255, 46, 160)            # block 2, the hot pink (CELL colour)
HOT_D = (196, 18, 108)
KEY = (13, 11, 17)              # block 1, carved black ink
NEAR = (28, 24, 34)
SPECK = (92, 80, 96)


def jag_path(p0, p1, r, step=(8, 16), amp=1.2, ends=False):
    """straight scissor cut: subdivided, each joint jittered sideways -> facets"""
    p0 = np.array(p0, float)
    p1 = np.array(p1, float)
    d = p1 - p0
    L = float(np.hypot(*d)) + 1e-9
    u = d / L
    n_ = np.array([-u[1], u[0]])
    pts = [p0]
    t = r.uniform(*step)
    while t < L - step[0] * 0.5:
        pts.append(p0 + u * t + n_ * r.uniform(-amp, amp))
        t += r.uniform(*step)
    pts.append(p1)
    return pts


def jag_arc(c, rad, a0, a1, r, step=(8, 16), amp=1.2):
    """arc cut: facets along the arc, radial jitter"""
    arc_len = abs(math.radians(a1 - a0)) * rad
    pts = [pol(c, rad, a0)]
    t = r.uniform(*step)
    while t < arc_len - step[0] * 0.5:
        a = a0 + (a1 - a0) * t / arc_len
        pts.append(pol(c, rad + r.uniform(-amp, amp), a))
        t += r.uniform(*step)
    pts.append(pol(c, rad, a1))
    return pts


def jag_disc(c, rad, r, step=(9, 18), amp=1.5):
    return jag_arc(c, rad, 0, 360, r, step, amp)[:-1]


def lens_mask(cv, specs, blur=0.35):
    """specs: (x0, y0, x1, y1, width, bend) in 1x px -> float mask on the canvas.  A gouge: pointed both ends, belly in the middle."""
    S = cv.S
    im = Image.new('L', (cv.W, cv.H), 0)
    d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1, w, bend) in specs:
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) + 1e-9
        nx, ny = -dy / L, dx / L
        n = 9
        left, right = [], []
        for i in range(n + 1):
            t = i / n
            bx = x0 + dx * t + nx * bend * 4 * t * (1 - t)
            by = y0 + dy * t + ny * bend * 4 * t * (1 - t)
            hw = w * 0.5 * (math.sin(math.pi * t) ** 0.62)
            left.append(((bx + nx * hw) * S, (by + ny * hw) * S))
            right.append(((bx - nx * hw) * S, (by - ny * hw) * S))
        d.polygon(left + right[::-1], fill=255)
    a = np.asarray(im, np.float32) / 255.0
    if blur:
        a = ndi.gaussian_filter(a, blur * S / 3.0)
    return a


def ink_grain(cv, m, amount=0.5):
    """printing unevenness for a solid mask: roller streak + speckle voids, returns the modulated mask"""
    S = cv.S
    h, w = m.shape
    n_lo = smooth(h, w, 14 * S, cv.r)
    n_hi = smooth(h, w, 1.1 * S, cv.r)
    voids = (n_hi > 2.05).astype(np.float32)
    voids = ndi.gaussian_filter(voids, 0.35 * S)
    return np.clip(m * (1 - amount * 0.5 * voids) * (0.97 + 0.03 * np.clip(n_lo, -2, 2)), 0, 1)


def facet(mask, S, amp=0.5):
    """slightly chiselled edge on an existing mask: warp then re-threshold"""
    r = np.random.default_rng(3)
    w = ndi.gaussian_filter(mask, 0.6 * S)
    nz = smooth(*mask.shape, 3.2 * S, r)
    return np.clip((w + nz * 0.05 * amp - 0.5) * 8 + 0.5, 0, 1)


def print_texture(im, seed=1, dens=0.012, pink_dens=0.006):
    """final pass on an RGBA 1x image: ink speckle on dark areas (paper showing through), tiny ink flecks on light areas.  Keeps alpha."""
    r = np.random.default_rng(seed)
    a = np.asarray(im, np.float32).copy()
    h, w = a.shape[:2]
    lum = a[..., :3] @ np.array([0.3, 0.59, 0.11], np.float32)
    dark = lum < 70
    n = smooth(h, w, 0.9, r)
    sp = ndi.gaussian_filter((r.random((h, w)) < dens).astype(np.float32), 0.55) * 3.0
    sp = np.clip(sp, 0, 1) * dark * (a[..., 3] > 200)
    col = np.array(SPECK, np.float32)
    a[..., :3] = a[..., :3] * (1 - sp[..., None] * 0.75) + col * sp[..., None] * 0.75
    lite = lum >= 70
    fl = np.clip(ndi.gaussian_filter((r.random((h, w)) < pink_dens).astype(np.float32), 0.5) * 3.0, 0, 1) * lite * (a[..., 3] > 200)
    a[..., :3] = a[..., :3] * (1 - fl[..., None] * 0.55) + np.array(NEAR, np.float32) * fl[..., None] * 0.55
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def jag_mask(cv, pts):
    return cv.poly_mask(pts)
