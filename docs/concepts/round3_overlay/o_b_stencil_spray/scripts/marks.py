"""High-level overlay marks placed in screen coordinates."""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from spraylib import (Layer, blur, spray, stencil_shadow, drip_mask, spray_drips, stencil_text,
                      freehand_mask, spray_freehand, IMPACT, BAHN, PINK, WHITE, YELLOW, BLACK)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))  # docs/
OUT = os.path.abspath(os.path.join(HERE, ".."))
W, H = 1920, 1080


def load_base(rel):
    return Image.open(os.path.join(ROOT, rel)).convert("RGB")


class Overlay:
    """Full-frame RGBA overlay that local marks are placed into."""

    def __init__(self):
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def place(self, local, x, y, angle=0.0):
        if angle:
            cx, cy = local.size[0] / 2, local.size[1] / 2
            local = local.rotate(angle, Image.BICUBIC, expand=True)
            x = x + cx - local.size[0] / 2
            y = y + cy - local.size[1] / 2
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tmp.paste(local, (int(round(x)), int(round(y))))
        self.img = Image.alpha_composite(self.img, tmp)

    def place_c(self, parts, cx, cy):
        """Place a (img, mask_shape, specs) stencil so the lettering (not drips/pad) centres on cx, cy."""
        img, mshape = parts[0], parts[1]
        self.place(img, cx - img.size[0] / 2, cy - mshape[0] / 2)

    def alpha(self):
        return np.asarray(self.img, np.float32)[..., 3] / 255

    def apply(self, base, darken=0.28, desat=0.35, spread=16):
        from spraylib import darken_under
        b = darken_under(base, self.alpha(), amount=darken, desat=desat, spread=spread)
        b = b.convert("RGBA")
        return Image.alpha_composite(b, self.img).convert("RGB")


def stencil_word(text, size, color, rng, angle=0.0, drips=0, drip_len=90, drip_w=(4, 8),
                 shadow=True, font=IMPACT, slice_frac=0.56, bridge=0.075, sheen=0.45,
                 halo=9.0, line_gap=-0.12, align="left", tracking=0.04, drip_lengths=None,
                 drip_specs=None, reveal=None, return_parts=False, shadow_off=(5, 6), keyline=None):
    """Sprayed stencil word. Returns (RGBA image, mask origin offset)."""
    M = stencil_text(text, size, font=font, rng=rng, angle=angle, slice_frac=slice_frac,
                     bridge=bridge, line_gap=line_gap, align=align, tracking=tracking)
    pad_b = int(drip_len * 1.25) + 10 if (drips or drip_specs) else 0
    Mp = np.pad(M, ((0, pad_b), (0, 0)))
    h, w = Mp.shape
    if reveal is not None:
        Mp = Mp * reveal(Mp.shape)
    L = Layer(w, h)
    if shadow:
        stencil_shadow(L, Mp, rng, dx=shadow_off[0], dy=shadow_off[1])
    if keyline is not None:
        # second stencil layer, slightly mis-registered: a white key under the colour
        from spraylib import shift
        spray(L, shift(Mp, -keyline[1], -keyline[2]), keyline[0], rng, halo=halo * 0.6, halo_amt=0.3, sheen=0.2)
    spray(L, Mp, color, rng, halo=halo, sheen=sheen)
    specs = None
    if drips or drip_specs:
        D, specs = drip_mask(Mp if reveal is None else np.pad(M, ((0, pad_b), (0, 0))), rng, n=drips,
                             max_len=drip_len, width=drip_w, lengths=drip_lengths, picks=drip_specs)
        if reveal is None or drip_lengths is not None:
            spray_drips(L, D, color, rng)
    img = L.to_image()
    if return_parts:
        return img, M.shape, specs
    return img


def freehand(pts, width, color, rng, upto=1.0, opacity=1.0, arrow=False, head=34, taper_out=0.22, jitter=1.2, mist=0.35):
    """Freehand spray line in screen coords. Returns (RGBA image, x0, y0)."""
    pts = [tuple(map(float, p)) for p in pts]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    m = int(width * 3 + head + 24)
    x0, y0 = int(min(xs) - m), int(min(ys) - m)
    x1, y1 = int(max(xs) + m), int(max(ys) + m)
    lp = [(x - x0, y - y0) for x, y in pts]
    M, path = freehand_mask((y1 - y0, x1 - x0), lp, width, rng, upto=upto, taper_out=taper_out, jitter=jitter)
    if arrow and upto >= 1.0:
        tip = path[-1]
        back = path[max(0, len(path) - 12)]
        ang = math.atan2(tip[1] - back[1], tip[0] - back[0])
        for da in (2.55, -2.55):
            a = ang + da
            e = (tip[0] + math.cos(a) * head, tip[1] + math.sin(a) * head)
            mid = ((tip[0] + e[0]) / 2 + math.cos(a + 1.57) * 3, (tip[1] + e[1]) / 2 + math.sin(a + 1.57) * 3)
            hm, _ = freehand_mask(M.shape, [tuple(tip), mid, e], width * 0.95, rng, taper_in=0.02, taper_out=0.4)
            M = np.maximum(M, hm)
    L = Layer(M.shape[1], M.shape[0])
    # faint black under-spray so the line separates from busy bases
    spray(L, blur(np.roll(np.roll(M, 3, 0), 3, 1), width * 0.3), BLACK, rng, halo=width, halo_amt=0.2,
          speck=0.3, opacity=0.45, edge_build=0)
    spray_freehand(L, M, color, rng, width, opacity=opacity, mist=mist)
    return L.to_image(), x0, y0


def ellipse_pts(cx, cy, rx, ry, a0, a1, n=14, wob=0.04, rng=None, tilt=0.0):
    pts = []
    for k in range(n + 1):
        t = a0 + (a1 - a0) * k / n
        r = 1 + (rng.uniform(-wob, wob) if rng is not None else 0)
        x, y = math.cos(t) * rx * r, math.sin(t) * ry * r
        ct, st = math.cos(tilt), math.sin(tilt)
        pts.append((cx + x * ct - y * st, cy + x * st + y * ct))
    return pts


def icon_layer(mask, color, rng, shadow=True, halo=7.0, sheen=0.35, pad=24):
    M = np.pad(mask, pad)
    L = Layer(M.shape[1], M.shape[0])
    if shadow:
        stencil_shadow(L, M, rng, dx=4, dy=5)
    spray(L, M, color, rng, halo=halo, sheen=sheen)
    return L.to_image()


def bahn(size, var="SemiBold"):
    f = ImageFont.truetype(BAHN, size)
    f.set_variation_by_name(var)
    return f
