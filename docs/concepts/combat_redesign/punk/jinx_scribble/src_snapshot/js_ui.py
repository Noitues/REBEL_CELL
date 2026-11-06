"""js_ui: SEND IT / nameplate / YOU strip restyled to match the Jinx scribble wall: tape removed, paper turned into dark painted board,
neon chalk rim with a cyan plate shifted off the key.  Built on st_ui (the information and layout are st_ui's)."""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
import st_ui as UI
import st_cards as K
import st_gfx as G
import f1_hand as FH

_ZINE = G.ZINE
_orig_mt = K.marker_text


def _mt(cv, txt, x, y, px, color=None, **k):
    if color is None or (np.asarray(color) == np.asarray(_ZINE)).all():
        color = G.hx('2EEBFF')
    return _orig_mt(cv, txt, x, y, px, color, **k)


def darken_paper(im, base=(26, 14, 58)):
    a = np.asarray(im, np.float32)
    rgb, al = a[..., :3], a[..., 3:4]
    mn, mx = rgb.min(-1), rgb.max(-1)
    w = np.clip((mn - 120) / 60.0, 0, 1) * np.clip((45 - (mx - mn)) / 25.0, 0, 1)
    n = ndi.gaussian_filter(np.random.default_rng(3).standard_normal(w.shape).astype(np.float32), 1.2)
    dark = np.array(base, np.float32)[None, None, :] * (1 + 0.35 * n[..., None]) + np.array((40, 20, 90), np.float32) * ((mn / 255.0)[..., None] ** 2) * 0.5
    out = rgb * (1 - w[..., None]) + dark * w[..., None]
    return Image.fromarray(np.dstack([np.clip(out, 0, 255), al[..., 0]]).astype(np.uint8), 'RGBA')


def neon_rim(im, pad=8, cyan=(46, 235, 255), pink=(255, 46, 154), width=2.2, plate=True):
    W, H = im.width + pad * 2, im.height + pad * 2
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = np.zeros((H, W), np.float32)
    a[pad:pad + im.height, pad:pad + im.width] = np.asarray(im.split()[3], np.float32) / 255.0
    sol = a > 0.5
    ring = (ndi.binary_dilation(sol, iterations=int(width + 1)) & ~ndi.binary_dilation(sol, iterations=1)).astype(np.float32)
    ring = ndi.gaussian_filter(ring, 0.5)
    glow = ndi.gaussian_filter(ring, 3.0)
    g = Image.new('RGBA', (W, H), pink + (0,))
    g.putalpha(Image.fromarray(np.clip(glow * 255 * 1.4, 0, 255).astype(np.uint8)))
    out.alpha_composite(g)
    if plate:
        c = Image.new('RGBA', (W, H), cyan + (0,))
        sh = np.roll(np.roll(ring, -2, 1), 1, 0)
        c.putalpha(Image.fromarray(np.clip(sh * 255, 0, 255).astype(np.uint8)))
        out.alpha_composite(c)
    p = Image.new('RGBA', (W, H), pink + (0,))
    p.putalpha(Image.fromarray(np.clip(ring * 255, 0, 255).astype(np.uint8)))
    out.alpha_composite(p)
    out.alpha_composite(im, (pad, pad))
    return out, pad


_cache = {}


def ui_img(kind, nw, f=None, seed=0):
    key = (kind, nw, None if f is None else (f['hp'], f['pv']['hp_after']))
    if key in _cache:
        return _cache[key]
    if kind == 'send':
        im, (x0, y0) = UI.send_it(ss=3, scale=1, nw=nw)
        pad = 8
        # a cyan plate behind the slab, shifted off the key (the glitch print)
        a = np.asarray(im.split()[3], np.float32) / 255.0
        big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        cy = Image.new('RGBA', im.size, (46, 235, 255, 255))
        cy.putalpha(im.split()[3].filter(ImageFilter.MaxFilter(3)))
        big.alpha_composite(cy, (pad - 6, pad - 4))
        big.alpha_composite(im, (pad, pad))
        r = (big, (x0 - pad, y0 - pad))
    elif kind == 'name':
        im, (x0, y0) = UI.nameplate(ss=3, scale=1, nw=nw)
        im = darken_paper(im)
        big, pad = neon_rim(im)
        r = (big, (x0 - pad, y0 - pad))
    else:
        im, (x0, y0) = UI.you_strip(f, ss=3, nw=nw)
        im = darken_paper(im)
        big, pad = neon_rim(im, pad=6, width=1.6)
        r = (big, (x0 - pad, y0 - pad))
    _cache[key] = r
    return r


def install():
    UI.tape_piece = lambda *a, **k: None
    K.marker_text = _mt
    FH.ui_img = ui_img
