"""Boss Wheel v2: turn figure masks into lit art. Three render modes shared by every corp:

  silhouette(...)  backlit figure: dark body, rim light in the slice TYPE colour (type reads even blurred),
                   cool corp rim from the other side, gilt glints, haze on the back layer.
  mosaic(img)      re-tile any RGBA art into tesserae with grout (Roman B).
  relief(...)      carved bas-relief from a mask (height = blurred mask), lit top-left, with a type-coloured
                   under-light from the bottom edge (Roman C).
  emissive(...)    bioluminescent edge-glow figure, translucent body (Atlantis C).
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import bw_kit as K


def _fit(mask, size):
    if mask.size == size:
        return mask
    return mask.resize(size, Image.LANCZOS)


def silhouette(masks, size, key, cool, body=(16, 10, 18), haze=(60, 40, 50), gilt=(222, 182, 98), s=1.0,
               key_dir=(0.55, -0.85), rim_w=3.2, eye_col=None, detail_mode="lit", back_k=0.55, glow_k=0.7):
    """Light a figure (dict of L masks) into an RGBA layer of `size`."""
    out = K.rgba(size)
    kx, ky = key_dir
    w = max(1.0, rim_w * s)
    for name, depth in (("back", 1), ("main", 0), ("drape", 0), ("arm", 0)):
        if name not in masks:
            continue
        m = _fit(masks[name], size)
        if m.getbbox() is None:
            continue
        b = K.mix(body, haze, back_k) if depth else body
        if name == "drape":
            b = (70, 12, 46)
        lay = K.solid(m, b)
        # soft top bounce inside
        inner = K.blur(K.shifted(m, 0, 6 * s), 5 * s)
        top = ImageChops.subtract(m, inner).point(lambda v: int(v * 0.35))
        lay.alpha_composite(K.solid(top, K.mix(b, cool, 0.6)))
        rk = K.rim_light(m, kx * w, ky * w, 0.6 * s)
        rc = K.rim_light(m, -kx * w * 0.6, ky * w * 0.2, 0.5 * s)
        kk = 0.55 if depth else 1.0
        lay.alpha_composite(K.solid(rc, cool, 0.65 * kk))
        lay.alpha_composite(K.solid(rk, key, kk))
        out.alpha_composite(lay)
        if not depth:
            out = K.add(out, K.solid(K.blur(rk, 5 * s), key), glow_k * 0.6)
    if "detail" in masks:
        dm = _fit(masks["detail"], size)
        mm = _fit(masks["main"], size) if "main" in masks else K.L(size)
        inside = ImageChops.multiply(dm, mm)
        outside = ImageChops.subtract(dm, mm)
        if detail_mode == "bright":
            out.alpha_composite(K.solid(inside, K.mix(key, (255, 255, 255), 0.2)))
            out = K.add(out, K.solid(K.blur(inside, 3 * s), key), 0.6)
        elif detail_mode == "lit":
            out.alpha_composite(K.solid(inside, K.mix(body, key, 0.45)))
        else:
            out.alpha_composite(K.solid(inside, K.mul(body, 0.4)))
        out.alpha_composite(K.solid(outside, K.mix(body, key, 0.25), 0.9))
    if "glint" in masks:
        g = _fit(masks["glint"], size)
        gl = K.solid(g, gilt)
        hi = K.rim_light(g, kx * 2 * s, ky * 2 * s, 0.5 * s)
        gl.alpha_composite(K.solid(hi, (255, 240, 200)))
        out.alpha_composite(gl)
        out = K.add(out, K.solid(K.blur(g, 4 * s), gilt), 0.35)
    if "eye" in masks and eye_col:
        e = _fit(masks["eye"], size)
        out.alpha_composite(K.solid(e, eye_col))
        out = K.add(out, K.solid(K.blur(e, 6 * s), eye_col), 1.2)
    return out


def front_lit(masks, size, base, key, s=1.0, gilt=(222, 182, 98), dark=(20, 12, 18)):
    """A flat, front-lit version (used before mosaic): body in a mid tone of `base`, details dark, glints gilt."""
    out = K.rgba(size)
    for name, k in (("back", 0.55), ("main", 1.0), ("drape", 0.8), ("arm", 1.0)):
        if name in masks:
            m = _fit(masks[name], size)
            c = K.mul(base, k) if name != "drape" else (120, 30, 90)
            lay = K.solid(m, c)
            rk = K.rim_light(m, 2.5 * s, -3 * s, 0.6 * s)
            lay.alpha_composite(K.solid(rk, key))
            sh = K.rim_light(m, -2.5 * s, 3 * s, 0.6 * s)
            lay.alpha_composite(K.solid(sh, dark, 0.8))
            out.alpha_composite(lay)
    if "detail" in masks:
        out.alpha_composite(K.solid(_fit(masks["detail"], size), dark, 0.9))
    if "glint" in masks:
        out.alpha_composite(K.solid(_fit(masks["glint"], size), gilt))
    if "eye" in masks:
        out.alpha_composite(K.solid(_fit(masks["eye"], size), key))
    return out


def mosaic(img, tile, seed=3, grout=(14, 10, 12), gold=None, jitter=0.18, gap=0.16):
    """Re-tile an RGBA image as tesserae. Each tile takes the mean colour under it; grout between."""
    w, h = img.size
    a = np.asarray(img.convert("RGBA"), np.float32)
    r = K.rng(seed)
    out = Image.new("RGBA", (w, h), grout + (255,))
    d = ImageDraw.Draw(out)
    t = float(tile)
    rows = int(h / t) + 2
    cols = int(w / t) + 2
    for j in range(rows):
        off = (t / 2) if j % 2 else 0.0
        for i in range(cols):
            x0 = i * t - off + r.uniform(-jitter, jitter) * t
            y0 = j * t + r.uniform(-jitter, jitter) * t
            x1, y1 = x0 + t * (1 - gap), y0 + t * (1 - gap)
            cx, cy = int(min(w - 1, max(0, (x0 + x1) / 2))), int(min(h - 1, max(0, (y0 + y1) / 2)))
            sx0, sy0 = int(max(0, x0)), int(max(0, y0))
            sx1, sy1 = int(min(w, x1 + 1)), int(min(h, y1 + 1))
            if sx1 <= sx0 or sy1 <= sy0:
                continue
            c = a[sy0:sy1, sx0:sx1].reshape(-1, 4).mean(0)
            if c[3] < 10:
                continue
            k = 0.9 + 0.2 * r.random()
            col = tuple(int(min(255, v * k)) for v in c[:3])
            d.rounded_rectangle([x0, y0, x1, y1], radius=max(1, t * 0.18), fill=col + (int(c[3]),))
    # tile bevel: light top-left edge
    al = out.split()[3]
    return out


def relief(mask, size, stone=(214, 196, 160), shadow=(70, 52, 44), hi=(255, 246, 226), s=1.0, depth=6.0, under=None,
           under_k=0.9, light=(-0.6, -0.8)):
    """Carved relief from a mask: returns RGBA of the raised shape shaded as stone."""
    m = _fit(mask, size)
    h = np.asarray(K.blur(m, depth * s), np.float32) / 255
    gy, gx = np.gradient(h)
    lx, ly = light
    nl = -(gx * lx + gy * ly) * depth * s * 3.0
    lit = np.clip(0.55 + nl, 0, 1.3)
    base = np.array(stone, np.float32)
    hi_ = np.array(hi, np.float32)
    lo = np.array(shadow, np.float32)
    tt = lit[..., None]
    col = np.where(tt > 0.55, base + (hi_ - base) * np.clip((tt - 0.55) / 0.6, 0, 1), lo + (base - lo) * np.clip(tt / 0.55, 0, 1))
    if under is not None:   # coloured light from below (neon under-light)
        ul = np.clip(-(gy) * depth * s * 4.0, 0, 1)[..., None]
        col = col + np.array(under, np.float32) * ul * under_k
    a = np.asarray(m, np.float32)[..., None]
    out = np.concatenate([np.clip(col, 0, 255), a], axis=2)
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def cast_shadow(mask, size, dx, dy, r, k=0.6):
    m = _fit(mask, size)
    return K.solid(K.shifted(K.blur(m, r), dx, dy), (0, 0, 0), k)


def emissive(masks, size, col, s=1.0, body_k=0.18, edge_w=2.2, core=(255, 255, 255)):
    """Bioluminescent figure: faint translucent body, bright edge, inner veins (detail) glowing."""
    out = K.rgba(size)
    for name, k in (("back", 0.5), ("main", 1.0), ("arm", 1.0)):
        if name not in masks:
            continue
        m = _fit(masks[name], size)
        body = K.solid(m, col, body_k * k)
        out.alpha_composite(body)
        e = ImageChops.subtract(m, K.shrink(m, edge_w * s))
        out.alpha_composite(K.solid(e, K.mix(col, core, 0.35), 0.95 * k))
        out = K.add(out, K.solid(K.blur(e, 4 * s), col), 0.9 * k)
    if "detail" in masks:
        dm = _fit(masks["detail"], size)
        out.alpha_composite(K.solid(dm, K.mix(col, core, 0.2), 0.8))
        out = K.add(out, K.solid(K.blur(dm, 3 * s), col), 0.6)
    if "glint" in masks:
        g = _fit(masks["glint"], size)
        out.alpha_composite(K.solid(g, core))
        out = K.add(out, K.solid(K.blur(g, 5 * s), col), 1.0)
    if "eye" in masks:
        e = _fit(masks["eye"], size)
        out.alpha_composite(K.solid(e, core))
    return out


def light_rays(size, cx, cy, n, length, width, col, seed, alpha=60, spread=50, ang0=0.0):
    lay = K.rgba(size)
    d = ImageDraw.Draw(lay)
    r = K.rng(seed)
    for _ in range(n):
        a = math.radians(ang0 + r.uniform(-spread, spread))
        wv = width * r.uniform(0.5, 1.4)
        ln = length * r.uniform(0.6, 1.0)
        x1, y1 = cx + ln * math.sin(a), cy + ln * math.cos(a)
        nx, ny = math.cos(a) * wv, -math.sin(a) * wv
        d.polygon([(cx, cy), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny)], fill=tuple(col) + (int(alpha * r.uniform(0.4, 1)),))
    return K.blur(lay, width * 0.5)
