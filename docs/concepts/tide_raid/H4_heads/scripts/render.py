"""Head renderer: supersampled, ink-outlined silhouettes + detail ops."""
import math
import numpy as np
from PIL import Image, ImageDraw
from shapes import TYPES, HUE, INK, FOOT

SS = 8


def render_head(ops, size, ang_deg, fill, ink=INK, ow=None, detail=None):
    """RGBA canvas (size*1.6 square) with the head centred. ang_deg: screen heading (0 = right, +90 = down).
    ow = outline px (None -> max(1.5, size*.075); 0 -> no outline, used for the card-tab glyph).
    detail = colour for 'ink' ops (default ink)."""
    ow = max(1.5, size * .075) if ow is None else ow
    C = int(size * 1.6) + 6
    H = C * SS
    u = (size - 2 * ow) / FOOT * SS
    a = math.radians(ang_deg)
    c, s = math.cos(a), math.sin(a)

    def T(p):
        return [(H / 2 + (x * c - y * s) * u, H / 2 + (x * s + y * c) * u) for x, y in p]
    sil = Image.new('L', (H, H), 0)
    d = ImageDraw.Draw(sil)
    for k, p in ops:
        if k == 'add':
            d.polygon(T(p), fill=255)
    out = Image.new('L', (H, H), 0)
    do = ImageDraw.Draw(out)
    if ow > 0:
        r = ow * SS
        for k, p in ops:
            if k != 'add':
                continue
            q = T(p)
            do.polygon(q, fill=255)
            for i in range(len(q)):
                x0, y0 = q[i]
                x1, y1 = q[(i + 1) % len(q)]
                do.line([(x0, y0), (x1, y1)], fill=255, width=int(2 * r))
                do.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=255)
    img = Image.new('RGB', (H, H), (0, 0, 0))
    img.paste(Image.new('RGB', (H, H), ink), mask=out)
    img.paste(Image.new('RGB', (H, H), fill), mask=sil)
    dc = detail or ink
    di = ImageDraw.Draw(img)
    for k, p in ops:
        if k == 'ink' or (k == 'mot' and size >= 40):
            di.polygon(T(p), fill=dc)
        elif k == 'fill':
            di.polygon(T(p), fill=fill)
    alpha = Image.fromarray(np.maximum(np.asarray(out), np.asarray(sil)))
    img = img.resize((C, C), Image.LANCZOS)
    alpha = alpha.resize((C, C), Image.LANCZOS)
    img.putalpha(alpha)
    return img


def paste_head(base, ops, cx, cy, size, ang_deg, typ, **kw):
    """composite onto an RGBA base at (cx, cy)."""
    im = render_head(ops, size, ang_deg, kw.pop('fill', HUE[typ]), **kw)
    base.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


def mask_at(ops, size, ang_deg):
    im = render_head(ops, size, ang_deg, (255, 255, 255))
    return np.asarray(im.split()[3], np.float32) / 255.0
