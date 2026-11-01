"""Shared compositing helpers for transitions v3 (PIL + numpy only)."""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1920, 1080
LIME = (150, 255, 70); PINK = (255, 60, 180); AMB = (255, 170, 60); CYAN = (60, 220, 255)
R = 'D:/rc_art/art-pass/docs/concepts/'


def F(sz, b=False):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf', sz)
    except Exception:
        return ImageFont.load_default()


def MF(sz):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', sz)
    except Exception:
        return F(sz, True)


def L(rel, half=False):
    p = rel if ':' in rel else R + rel
    im = Image.open(p).convert('RGB')
    if half:
        im = im.crop((im.width // 2, 0, im.width, im.height))
    return im.resize((W, H), Image.LANCZOS)


def GIF(rel, i):
    im = Image.open(R + rel)
    im.seek(i)
    return im.convert('RGB').resize((W, H), Image.LANCZOS)


def zc(im, cx, cy, z):
    w, h = W / z, H / z
    x0 = min(max(cx * W - w / 2, 0), W - w)
    y0 = min(max(cy * H - h / 2, 0), H - h)
    return im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.LANCZOS)


def blend(a, b, t):
    return Image.blend(a, b, t)


def zblur(im, amt=0.06, n=7):
    acc = None
    for i in range(n):
        z = 1 + amt * i / (n - 1)
        f = zc(im, .5, .5, z) if z > 1 else im
        acc = f if acc is None else Image.blend(acc, f, 1 / (i + 1))
    return acc


def dark(im, k):
    return ImageEnhance.Brightness(im).enhance(k)


def desat(im, k):
    return ImageEnhance.Color(im).enhance(k)


def iris(a, b, r, cx=.5, cy=.5, col=LIME):
    m = Image.new('L', (W, H), 0)
    R_ = r * W
    box = (cx * W - R_, cy * H - R_, cx * W + R_, cy * H + R_)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    out = Image.composite(b, a, m)
    ImageDraw.Draw(out).ellipse(box, outline=col, width=6)
    return out


def scan(im, a=.2):
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    for y in range(0, H, 4):
        d.line((0, y, W, y), fill=int(255 * a))
    return Image.composite(dark(im, .6), im, m)


def shrink_on(base, top, s, cx=.5, cy=.5, rot=0):
    t = top.resize((int(W * s), int(H * s)), Image.LANCZOS).convert('RGBA')
    if rot:
        t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
    out = base.convert('RGBA')
    sh = Image.new('RGBA', t.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 170), (0, 0, t.width, t.height), t.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    out.alpha_composite(sh, (int(cx * W - t.width / 2 + 18), int(cy * H - t.height / 2 + 26)))
    out.alpha_composite(t, (int(cx * W - t.width / 2), int(cy * H - t.height / 2)))
    return out.convert('RGB')


def glow_line(im, pts, col=LIME, w=8):
    g = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(g)
    d.line([(x * W, y * H) for x, y in pts], fill=col, width=w * 3, joint='curve')
    g = g.filter(ImageFilter.GaussianBlur(14))
    out = Image.fromarray(np.clip(np.asarray(im).astype(int) + np.asarray(g).astype(int) * 0.8, 0, 255).astype('uint8'))
    ImageDraw.Draw(out).line([(x * W, y * H) for x, y in pts], fill=col, width=w, joint='curve')
    return out


def marker(im, cx, cy, kind):
    d = ImageDraw.Draw(im)
    x, y = cx * W, cy * H
    col = {'before': AMB, 'win': LIME, 'lose': PINK}[kind]
    for r, a in ((70, 2), (50, 4)):
        d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=a)
    d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=(10, 12, 16), outline=col, width=7)
    if kind == 'win':
        d.line((x - 15, y, x - 4, y + 13, x + 16, y - 13), fill=col, width=8)
    elif kind == 'lose':
        d.line((x - 15, y - 15, x + 15, y + 15), fill=col, width=8)
        d.line((x - 15, y + 15, x + 15, y - 15), fill=col, width=8)
    else:
        d.polygon([(x, y - 16), (x + 16, y + 12), (x - 16, y + 12)], fill=col)
    return im


def bits_to(im, src, dst, n=260, col=LIME, spread=60, size=22, seed=0):
    r = random.Random(seed)
    out = im.copy()
    d = ImageDraw.Draw(out)
    f = MF(size)
    for i in range(n):
        t = r.random()
        sx, sy = src[0] * W, src[1] * H
        dx, dy = dst[0] * W, dst[1] * H
        mx, my = (sx + dx) / 2, (sy + dy) / 2 - 140 * (1 if i % 2 else -1) * r.random()
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * dx + r.gauss(0, spread) * math.sin(t * math.pi)
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t * t * dy + r.gauss(0, spread) * math.sin(t * math.pi)
        d.text((x, y), r.choice('01'), font=f, fill=col if r.random() < .75 else PINK)
    return out


def bits_ring(im, c, rad, n=420, col=LIME, size=22, seed=1, rings=3):
    r = random.Random(seed)
    out = im.copy()
    d = ImageDraw.Draw(out)
    f = MF(size)
    for i in range(n):
        a = r.random() * math.tau
        rr = rad * (1 + .16 * r.randrange(rings)) + r.gauss(0, 6)
        d.text((c[0] * W + math.cos(a) * rr, c[1] * H + math.sin(a) * rr * .98), r.choice('01'), font=f, fill=col if r.random() < .7 else PINK)
    return out


def bits_dissolve(im, k, seed=3):
    r = random.Random(seed)
    base = dark(im, 1 - .55 * k)
    d = ImageDraw.Draw(base)
    f = MF(20)
    for gy in range(0, H, 24):
        for gx in range(0, W, 16):
            if r.random() < k * .5:
                d.text((gx, gy), r.choice('01'), font=f, fill=LIME if r.random() < .75 else PINK)
    return base


def terminal_panel(im, box, title, lines, col=LIME):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(6, 14, 20), outline=col, width=5)
    d.rectangle((x0, y0, x1, y0 + 44), fill=(10, 36, 28))
    d.text((x0 + 16, y0 + 9), title, font=MF(22), fill=col)
    y = y0 + 70
    for t, c, s in lines:
        d.text((x0 + 28, y), t, font=MF(s), fill=c or col)
        y += int(s * 1.55)
    return im


def stamp(im, text='CONCEPT'):
    """Diagonal translucent CONCEPT stamp across a frame."""
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    t = Image.new('RGBA', (1100, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.text((550, 130), text, font=F(210, True), fill=(255, 170, 60, 120), anchor='mm')
    t = t.rotate(14, expand=True, resample=Image.BICUBIC)
    ov.alpha_composite(t, ((W - t.width) // 2, (H - t.height) // 2))
    out = im.convert('RGBA')
    out.alpha_composite(ov)
    return out.convert('RGB')


def to_cyan(im, sweep=1.0, bbox=None):
    """Hue-shift lime/yellow-green to cyan. sweep 0..1 rises from the bottom of bbox (x0,y0,x1,y1) up."""
    a = np.asarray(im.convert('HSV')).astype(np.int32)
    h, s, v = a[..., 0], a[..., 1], a[..., 2]
    sel = (h >= 36) & (h <= 90) & (s > 55) & (v > 90)
    if bbox is not None:
        x0, y0, x1, y1 = bbox
        yy, xx = np.mgrid[0:H, 0:W]
        top = y1 - sweep * (y1 - y0)
        sel &= (xx >= x0) & (xx <= x1) & (yy <= y1) & (yy >= top)
    a2 = a.copy()
    a2[..., 0] = np.where(sel, 126, h)
    return Image.fromarray(a2.astype('uint8'), 'HSV').convert('RGB')
