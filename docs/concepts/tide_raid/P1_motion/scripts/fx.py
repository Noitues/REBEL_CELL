"""Shared render helpers for the motion boards and tests (reuses the H2 libraries read-only)."""
import sys, math
sys.dont_write_bytecode = True
H2 = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/scripts'
if H2 not in sys.path:
    sys.path.insert(0, H2)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *
import scene as SC
import ui
import hy
import hz
import eb as EB
from hy import PX
from glyphs import *
from common import *
from tl import *

OUTDIR = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P1_motion/'
FFMPEG = 'D:/rc_scratch/tide_concepts/venv_vid/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'


def lerp(a, b, t):
    return a + (b - a) * t


def raw_city():
    """the un-hacked world: the real plate, same crop, no regrade (this is what jack-in leaves behind)."""
    a = np.asarray(Image.open(PLATES + 'city_noraid_nonet.png').convert('RGB'), np.float32) / 255
    im = Image.fromarray((a * 255).astype(np.uint8))
    x0 = CEN[0] - W / 2 / ZOOM
    y0 = CEN[1] - H / 2 / ZOOM
    im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + W / ZOOM, y0 + H / ZOOM))
    a = np.asarray(im, np.float32) / 255
    # the plate is a dim, flat-lit, un-hacked night: lift it a touch so the grade reads as a drop, not a brighten
    # pre-jack = the plain city-map look: lifted, desaturated, warm-neutral. Jack-in drops it into the night-vivid hacked grade.
    lum = (a * np.array([.3, .59, .11], np.float32)).sum(-1, keepdims=True)
    a = lum + (a - lum) * .55
    a = np.clip(a * 1.45 + np.array([.045, .04, .035], np.float32), 0, 1)
    return a


def radial_mask(c, r, feather=140.0):
    """1 inside radius r (iso-squashed) from c, soft edge."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - c[0]) ** 2 + ((yy - c[1]) / .72) ** 2)
    return np.clip((r - d) / feather + .5, 0, 1)


def to_u8(a):
    return (np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)


def crop_scale(a, box, size):
    """a: HxWx3 float; box=(x0,y0,x1,y1); size=(w,h) -> PIL RGB."""
    x0, y0, x1, y1 = [int(v) for v in box]
    im = Image.fromarray(to_u8(a)).crop((x0, y0, x1, y1))
    if im.size != tuple(size):
        im = im.resize(tuple(size), Image.LANCZOS)
    return im


def shift_img(a, dx, dy):
    """integer-pixel screen shake (edge replicate)."""
    dx, dy = int(round(dx)), int(round(dy))
    if dx == 0 and dy == 0:
        return a
    out = np.roll(a, (dy, dx), (0, 1))
    return out


def sprite(fn, box, pad=8):
    """draw with fn(cv) on a black and on a white canvas -> (rgb, alpha) of the object (box limits the work)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    res = []
    for bgc in (0.0, 1.0):
        cv = Cv(np.full((H, W, 3), bgc, np.float32))
        fn(cv)
        res.append(cv.img[y0:y1, x0:x1])
    blk, wht = res
    alpha = np.clip(1 - (wht - blk).mean(-1), 0, 1)
    rgb = np.where(alpha[..., None] > 1e-3, blk / np.maximum(alpha, 1e-3)[..., None], 0)
    return np.clip(rgb, 0, 1), alpha


def paste(cv, rgb, alpha, center, scale=1.0, angle=0.0, k=1.0, shadow=0.0, shear=None):
    """composite an RGBA sprite at `center` with scale/rotation (about its own centre)."""
    h, w = alpha.shape
    rgba = np.dstack([rgb, alpha])
    im = Image.fromarray(to_u8(rgba), 'RGBA')
    if scale != 1.0:
        im = im.resize((max(2, int(w * scale)), max(2, int(h * scale))), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    arr = np.asarray(im, np.float32) / 255
    ox, oy = int(center[0] - arr.shape[1] / 2), int(center[1] - arr.shape[0] / 2)
    if shadow:
        cv.over(INK, blur(arr[..., 3], 7), shadow * k, (ox + 5, oy + 9))
    cv.over(arr[..., :3], arr[..., 3], k, (ox, oy))


def hbar_cur(cv, p, k=1.0, sc=1.0):
    """a plain white pointer arrow (the cursor in the drag boards)."""
    pts = [(0, 0), (0, 22), (6, 17), (10, 26), (14, 24), (10, 15), (18, 15)]
    q = [(p[0] + x * sc, p[1] + y * sc) for x, y in pts]
    ly = Lyr(pbox(q, 6))
    ly.poly(q, 255)
    ol = Lyr(pbox(q, 6))
    ol.line(q + [q[0]], 2.4, 255)
    cv.over(INK, np.maximum(ol.m, ly.m), .95 * k, ly.off)
    cv.over(WHITE, ly.m, 1.0 * k, ly.off)


def pixel_blocks(cv, box, t, seed=3, cell=14, col=None, src=None):
    """pixel-block dissolve of a screen rectangle: t 0..1 = fraction of cells turned to block colour then gone."""
    x0, y0, x1, y1 = [int(v) for v in box]
    rng = np.random.RandomState(seed)
    nx, ny = (x1 - x0) // cell + 1, (y1 - y0) // cell + 1
    thr = rng.rand(ny, nx)
    m = np.kron(thr, np.ones((cell, cell), np.float32))[:y1 - y0, :x1 - x0]
    return m


def save_gif(frames, path, fps=15, size=None):
    ims = [Image.fromarray(f) if isinstance(f, np.ndarray) else f for f in frames]
    if size:
        ims = [i.resize(size, Image.LANCZOS) for i in ims]
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0, optimize=False, disposal=1)


_FIN = {}


def fast_finish(a, vig=.38, scan=.07, fringe=1.5, seed=3):
    """same look as lib.finish but with the vignette / scanline / rain layers cached (about 10x faster)."""
    key = (vig, scan, fringe, seed)
    if key not in _FIN:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        v = (1 - vig * np.clip(d - .55, 0, 1.2) ** 1.6) * (1 - scan * (np.mod(yy, 3) == 0))
        k = np.clip(np.clip(d - .75, 0, 1) * 2.2, 0, 1)
        rng = np.random.RandomState(seed)
        rl = Lyr(ss=1)
        for _ in range(170):
            x = rng.randint(0, W); y = rng.randint(0, H); L = rng.randint(14, 40)
            rl.line([(x, y), (x - L * .22, y + L)], 1, 70)
        rain = rl.m[..., None] * np.array([.35, .5, .8], np.float32) * .10
        _FIN[key] = (v[..., None].astype(np.float32), k.astype(np.float32), rain.astype(np.float32))
    v, k, rain = _FIN[key]
    a = np.clip(a, 0, 1) * v
    if fringe:
        sh = int(round(fringe))
        r = np.roll(a[..., 0], sh, 1)
        b = np.roll(a[..., 2], -sh, 1)
        a[..., 0] = a[..., 0] * (1 - k) + r * k
        a[..., 2] = a[..., 2] * (1 - k) + b * k
    return np.clip(a + rain, 0, 1)


# ------------------------------------------------------------------ premultiplied sprites (capture ANY layer incl. additive glow)
def spr(fn, box):
    """draw fn(cv) on black and on white; returns (P, a): premultiplied colour (may exceed 1 for glow) and alpha.
    composite with comp(): out = bg * (1 - a) + P."""
    x0, y0, x1, y1 = [int(v) for v in box]
    res = []
    for bgc in (0.0, 1.0):
        cv = Cv(np.full((H, W, 3), bgc, np.float32))
        fn(cv)
        res.append(cv.img[y0:y1, x0:x1].copy())
    blk, wht = res
    a = np.clip(1 - (wht - blk).mean(-1), 0, 1).astype(np.float32)
    return blk.astype(np.float32), a, (x0, y0)


def comp(cv, sp, k=1.0, off=(0, 0)):
    P, a, (x0, y0) = sp
    x0 += int(off[0]); y0 += int(off[1])
    h, w = a.shape
    cx0, cy0 = max(x0, 0), max(y0, 0)
    cx1, cy1 = min(x0 + w, W), min(y0 + h, H)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    s = (slice(cy0 - y0, cy1 - y0), slice(cx0 - x0, cx1 - x0))
    d = (slice(cy0, cy1), slice(cx0, cx1))
    cv.img[d] = cv.img[d] * (1 - a[s] * k)[..., None] + P[s] * k


def xform(sp, scale=1.0, angle=0.0):
    """scale / rotate a premultiplied sprite about its centre; returns a new sprite with its offset moved."""
    P, a, (x0, y0) = sp
    h, w = a.shape
    chans = [P[..., 0], P[..., 1], P[..., 2], a]
    out = []
    for c in chans:
        im = Image.fromarray(c.astype(np.float32), 'F')
        if scale != 1.0:
            im = im.resize((max(2, int(w * scale)), max(2, int(h * scale))), Image.BICUBIC)
        if angle:
            im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
        out.append(np.asarray(im, np.float32))
    nh, nw = out[0].shape
    cx, cy = x0 + w / 2, y0 + h / 2
    return np.stack(out[:3], -1), np.clip(out[3], 0, 1), (int(cx - nw / 2), int(cy - nh / 2))
