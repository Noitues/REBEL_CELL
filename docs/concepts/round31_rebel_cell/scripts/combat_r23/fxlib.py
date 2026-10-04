"""Round 18 FX helpers: glyph sprites, glow/light spill, RGB split, peel, easing, GIF + storyboard output."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

import plates as P

FPS = 25
DT = 1000.0 / FPS  # ms per frame


# ------------------------------------------------------------------ easing
def clamp01(t):
    return max(0.0, min(1.0, t))


def ease_out_cubic(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in_cubic(t):
    t = clamp01(t)
    return t ** 3


def ease_in_out(t):
    t = clamp01(t)
    return 3 * t * t - 2 * t ** 3


def ease_out_back(t, s=1.70158):
    t = clamp01(t) - 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2


def seg(t, a, b):
    """0..1 progress of t (ms) inside [a, b]."""
    return clamp01((t - a) / max(1e-6, (b - a)))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp2(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def bez(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


# ------------------------------------------------------------------ glyphs
_G = {}


def glyph(ch, px, col, core=0.0, outline=True, rim=0.7):
    """A Share Tech Mono glyph, thickened with a same-colour stroke (~px/22), optional dark rim for
    legibility on bright slices, and a white-hot core blend (0..1)."""
    px = max(6, int(px))
    key = (ch, px, col, round(core, 2), outline, rim)
    if key in _G:
        return _G[key]
    f = P.mono(px)
    pad = max(3, px // 4)
    tw = int(f.getlength(ch)) + 2 * pad
    th = px + 2 * pad
    m = Image.new("L", (tw, th), 0)
    d = ImageDraw.Draw(m)
    sw = max(1, round(px / 22))
    d.text((pad, pad - px * 0.12), ch, font=f, fill=255, stroke_width=sw, stroke_fill=255)
    c = tuple(int(lerp(v, 255, core)) for v in col)
    out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    if outline:
        rim = m.filter(ImageFilter.MaxFilter(3)).point(lambda v: int(v * rim))
        dark = Image.new("RGBA", (tw, th), (10, 8, 18, 0))
        dark.putalpha(rim)
        out.alpha_composite(dark)
    body = Image.new("RGBA", (tw, th), c + (0,))
    body.putalpha(m)
    out.alpha_composite(body)
    _G[key] = out
    return out


def paste_c(dst, sprite, x, y, alpha=1.0, angle=0.0, scale=1.0):
    """Composite sprite centred at (x, y) with alpha, rotation (deg) and scale."""
    s = sprite
    if scale != 1.0:
        w, h = max(1, int(s.width * scale)), max(1, int(s.height * scale))
        s = s.resize((w, h), Image.BILINEAR)
    if angle:
        s = s.rotate(angle, resample=Image.BILINEAR, expand=True)
    if alpha < 0.999:
        a = s.split()[3].point(lambda v: int(v * max(0.0, alpha)))
        s = s.copy()
        s.putalpha(a)
    dst.alpha_composite(s, (int(round(x - s.width / 2)), int(round(y - s.height / 2))))


# ------------------------------------------------------------------ light
def glow_add(img, layer, r1=6, r2=18, k=1.0):
    """Additive glow of an emissive layer onto img (light spill), computed only around the layer's
    bounding box so the rest of the frame stays byte-identical (small GIF deltas)."""
    bb = layer.getbbox()
    if not bb:
        return img.convert("RGBA")
    m = int(r2 * 2.5 + r1 * 2)
    box = (max(0, bb[0] - m), max(0, bb[1] - m), min(img.width, bb[2] + m), min(img.height, bb[3] + m))
    sub = _glow_full(img.crop(box), layer.crop(box), r1, r2, k)
    out = img.convert("RGBA").copy()
    out.paste(sub, box[:2])
    return out


def _glow_full(img, layer, r1, r2, k):
    a = np.asarray(layer, np.float32) / 255
    rgb = a[..., :3] * a[..., 3:]
    small = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    b1 = np.asarray(small.filter(ImageFilter.GaussianBlur(r1)), np.float32) / 255
    b2 = np.asarray(small.resize((small.width // 4, small.height // 4), Image.BILINEAR)
                    .filter(ImageFilter.GaussianBlur(r2 / 4)).resize(small.size, Image.BILINEAR), np.float32) / 255
    base = np.asarray(img.convert("RGB"), np.float32) / 255
    out = base + (b1 * 0.8 + b2 * 1.2) * k
    res = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return res


def rgb_split(layer, dx, dy=0):
    """Chromatic split of an RGBA layer: red shifted -dx, blue +dx (alpha spread with them)."""
    r, g, b, a = layer.split()
    z = Image.new("L", layer.size, 0)
    rs = ImageChops.offset(Image.merge("RGBA", (r, z, z, a)), -dx, -dy)
    bs = ImageChops.offset(Image.merge("RGBA", (z, z, b, a)), dx, dy)
    gs = Image.merge("RGBA", (z, g, z, a))
    ar = np.asarray(rs, np.float32)
    ab = np.asarray(bs, np.float32)
    ag = np.asarray(gs, np.float32)
    rgb = np.zeros(ar.shape[:2] + (3,), np.float32)
    rgb[..., 0] = ar[..., 0] * ar[..., 3] / 255
    rgb[..., 1] = ag[..., 1] * ag[..., 3] / 255
    rgb[..., 2] = ab[..., 2] * ab[..., 3] / 255
    alpha = np.maximum(np.maximum(ar[..., 3], ab[..., 3]), ag[..., 3])
    safe = np.maximum(alpha, 1) / 255
    out = np.dstack([np.clip(rgb / safe[..., None], 0, 255), alpha])
    return Image.fromarray(out.astype(np.uint8), "RGBA")


# ------------------------------------------------------------------ cursor
def cursor(img, x, y, pressed=False):
    """A plain arrow pointer (the OS cursor), slightly smaller when pressed."""
    s = 0.9 if pressed else 1.0
    pts = [(0, 0), (0, 26), (7, 20), (12, 31), (17, 29), (12, 18), (21, 18)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    d = ImageDraw.Draw(img)
    d.polygon([(px + 2, py + 3) for px, py in pts], fill=(0, 0, 0, 110))
    d.polygon(pts, fill=(250, 250, 250, 255), outline=(12, 10, 18, 255))


# ------------------------------------------------------------------ peel (flat fold page curl)
def peel(card, amount, corner="tr", back=(232, 230, 224), shadow=True):
    """Fold the sticker back from `corner` by `amount` (0..1 of the diagonal). Returns a canvas the same
    size as card (+pad) with the face, the folded flap (vinyl backing) and the flap's shadow."""
    pad = 40
    w, h = card.size
    C = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    C.alpha_composite(card, (pad, pad))
    if amount <= 0.001:
        return C, pad
    a = np.asarray(C, np.float32)
    Hc, Wc = a.shape[:2]
    corners = {"tr": (pad + w, pad), "tl": (pad, pad), "br": (pad + w, pad + h), "bl": (pad, pad + h)}
    cx, cy = corners[corner]
    ox, oy = pad + w / 2, pad + h / 2
    n = np.array([cx - ox, cy - oy], np.float32)
    diag = np.linalg.norm(n)
    n /= diag
    # fold line distance from the corner, along -n
    dist_from_corner = amount * diag * 2.0
    # signed distance: positive towards the corner beyond the fold line
    yy, xx = np.mgrid[0:Hc, 0:Wc].astype(np.float32)
    proj = (xx - cx) * n[0] + (yy - cy) * n[1]  # 0 at corner, negative inward
    d = proj + dist_from_corner  # >0 beyond the fold (the flap)
    face = a.copy()
    face[..., 3] *= (d <= 0)
    # flap: pixel q with d(q) <= 0 shows source s = q + 2*(-d)*n, if source alpha and d(s) > 0
    sx = xx + 2 * (-d) * n[0]
    sy = yy + 2 * (-d) * n[1]
    valid = (d <= 0) & (sx >= 0) & (sy >= 0) & (sx < Wc - 1) & (sy < Hc - 1)
    sxi = np.clip(sx.astype(np.int32), 0, Wc - 1)
    syi = np.clip(sy.astype(np.int32), 0, Hc - 1)
    src_a = a[syi, sxi, 3] * valid
    # backing shading: brighter at the fold crease, slightly darker at the tip
    depth = np.clip(-d / max(1.0, dist_from_corner), 0, 1)
    shade = 1.0 - 0.18 * depth + 0.08 * np.exp(-(-d) / 6.0)
    flap = np.zeros_like(a)
    for i in range(3):
        flap[..., i] = np.clip(back[i] * shade, 0, 255)
    flap[..., 3] = src_a
    out = Image.fromarray(np.clip(face, 0, 255).astype(np.uint8), "RGBA")
    if shadow:
        fl = Image.fromarray(np.clip(flap[..., 3], 0, 255).astype(np.uint8))
        sh = fl.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.55))
        sh = ImageChops.offset(sh, -3, 6)
        sh = ImageChops.multiply(sh, Image.fromarray(np.clip(face[..., 3], 0, 255).astype(np.uint8)))
        shl = Image.new("RGBA", out.size, (0, 0, 0, 255))
        shl.putalpha(sh)
        out.alpha_composite(shl)
    # crease line
    crease = (np.abs(d) < 1.2) & (a[..., 3] > 0)
    flap[..., :3][crease] = 255
    out.alpha_composite(Image.fromarray(np.clip(flap, 0, 255).astype(np.uint8), "RGBA"))
    return out, pad


def drop_shadow(sprite, offset, blur, alpha):
    """Sprite plus a soft shadow below it; returns (image, (dx, dy) shift of the sprite inside it)."""
    pad = int(blur * 2 + max(abs(offset[0]), abs(offset[1])) + 4)
    out = Image.new("RGBA", (sprite.width + 2 * pad, sprite.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0)
    sh.paste(sprite.split()[3], (pad + int(offset[0]), pad + int(offset[1])))
    sh = sh.filter(ImageFilter.GaussianBlur(max(0.1, blur))).point(lambda v: int(v * alpha))
    shl = Image.new("RGBA", out.size, (0, 0, 0, 255))
    shl.putalpha(sh)
    out.alpha_composite(shl)
    out.alpha_composite(sprite, (pad, pad))
    return out, pad


def place(dst, sprite, cx, cy, sx=1.0, sy=1.0, angle=0.0, shadow=None):
    """Composite a sprite centred at (cx, cy) with non-uniform scale (squash), rotation and an optional
    shadow (offset, blur, alpha)."""
    s = sprite
    if sx != 1.0 or sy != 1.0:
        s = s.resize((max(1, int(s.width * sx)), max(1, int(s.height * sy))), Image.BICUBIC)
    if angle:
        s = s.rotate(angle, resample=Image.BICUBIC, expand=True)
    if shadow:
        s, _ = drop_shadow(s, *shadow)
    dst.alpha_composite(s, (int(round(cx - s.width / 2)), int(round(cy - s.height / 2))))


# ------------------------------------------------------------------ output
def save_gif(frames, durations, path, size=(960, 540), crop=None, colors=255):
    """frames: list of RGBA/RGB full-res images. One global palette (built from a frame mosaic) and no
    dither, so unchanged regions stay byte-identical and Pillow's delta frames stay small."""
    small = []
    for f in frames:
        f = f.convert("RGB")
        if crop:
            f = f.crop(crop)
        if f.size != size:
            f = f.resize(size, Image.LANCZOS)
        small.append(f)
    # palette from a mosaic of sample frames
    k = max(1, len(small) // 12)
    samp = small[::k][:16]
    mw, mh = size[0] // 2, size[1] // 2
    cols = 4
    rows = (len(samp) + cols - 1) // cols
    mos = Image.new("RGB", (mw * cols, mh * rows))
    for i, f in enumerate(samp):
        mos.paste(f.resize((mw, mh), Image.BILINEAR), ((i % cols) * mw, (i // cols) * mh))
    pal = mos.quantize(colors=min(colors, 255), method=Image.Quantize.MEDIANCUT)
    q = [np.asarray(f.quantize(palette=pal, dither=Image.Dither.NONE)) for f in small]
    # unchanged pixels -> transparent index 255 (frames are not disposed, so the previous frame shows)
    pl = pal.getpalette()[:255 * 3] + [0, 0, 0]
    out = []
    for i, a in enumerate(q):
        b = a.copy()
        if i > 0:
            b[a == q[i - 1]] = 255
        im = Image.fromarray(b.astype(np.uint8), "P")
        im.putpalette(pl)
        out.append(im)
    out[0].save(path, save_all=True, append_images=out[1:], duration=durations, loop=0, optimize=False,
                disposal=1, transparency=255)
    return os.path.getsize(path)


def gif_frames(path, idx):
    """Read back composed frames of a GIF (for inspection)."""
    im = Image.open(path)
    res = []
    for i in idx:
        im.seek(i)
        res.append(im.convert("RGB"))
    return res


def storyboard(cells, path, title, sub, cols=4, cell_w=None, note_lines=None, extra=None, bg=(14, 13, 20)):
    """cells: list of (image (already cropped at 1:1), label, timing text, caption lines)."""
    cw = max(c[0].width for c in cells) if cell_w is None else cell_w
    ch = max(c[0].height for c in cells)
    gap = 18
    cap_h = 96
    rows = (len(cells) + cols - 1) // cols
    W = cols * cw + (cols + 1) * gap
    head = 110
    ex_h = extra.height + gap * 2 if extra is not None else 0
    note_h = 26 * len(note_lines) + 20 if note_lines else 0
    Hh = head + rows * (ch + cap_h + gap) + gap + ex_h + note_h
    S = Image.new("RGB", (W, Hh), bg)
    d = ImageDraw.Draw(S)
    from slicelib import f_num, f_ui
    d.text((gap, 14), title, font=f_num(52), fill=(255, 255, 255))
    d.text((gap, 74), sub, font=P.mono(20), fill=(170, 170, 188))
    for i, (im, lab, tim, caps) in enumerate(cells):
        x = gap + (i % cols) * (cw + gap)
        y = head + (i // cols) * (ch + cap_h + gap)
        S.paste(im.convert("RGB"), (x, y))
        d.rectangle([x, y + ch + 6, x + 5, y + ch + 34], fill=(255, 61, 168))
        d.text((x + 14, y + ch + 4), lab, font=f_num(30), fill=(255, 255, 255))
        tw = P.mono(22).getlength(tim)
        d.text((x + cw - tw, y + ch + 10), tim, font=P.mono(22), fill=(255, 214, 64))
        for k, ln in enumerate(caps):
            d.text((x + 14, y + ch + 40 + k * 22), ln, font=f_ui(19, b"SemiBold"), fill=(200, 200, 214))
    y = head + rows * (ch + cap_h + gap) + gap
    if extra is not None:
        S.paste(extra.convert("RGB"), (gap, y))
        y += extra.height + gap * 2
    if note_lines:
        for k, ln in enumerate(note_lines):
            d.text((gap, y + k * 26), ln, font=P.mono(19), fill=(190, 190, 205))
    S.save(path, optimize=True)
    return S
