"""Spinner depth study: paint every 2D layer the Blender scenes use (Pillow only).

Run from the spinner_3d folder:  python scripts/make_textures.py
Writes work/tex/*.png. Each spinner layer is an RGBA albedo, an L height map (for the
normal-lit technique) and, where it glows, an RGBA glow map. All layers share one planar
mapping: the texture square covers [-R, R] metres around the spinner centre (R = 1.45),
so Blender maps them with object coordinates and no UV unwrapping.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "work", "tex")
FONTS = os.path.normpath(os.path.join(ROOT, "..", "..", "..", "assets", "fonts"))
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
PLEX = os.path.join(FONTS, "IBMPlexSansCondensed-Medium.ttf")
MONO = os.path.join(FONTS, "ShareTechMono-Regular.ttf")

R = 1.45          # texture half-extent in metres
N = 2048          # final texture size
SS = 2            # supersampling
NS = N * SS
S = NS / (2 * R)  # supersampled pixels per metre

INK = (17, 17, 17)
WHITE = (255, 255, 255)
PAPER = (242, 238, 228)
PAPER_ALT = (233, 228, 214)
PINK = (255, 61, 168)
CYAN = (92, 225, 255)
GREEN = (123, 224, 123)
VIOLET = (200, 90, 255)
MISS = (106, 106, 106)
FLOOR = (10, 12, 20)
MERIDIAN = (255, 140, 26)
TEXT_MID = (175, 192, 214)

KIND_COL = {"attack": PINK, "crit": PINK, "defend": CYAN, "evade": GREEN,
            "afflict": VIOLET, "miss": MISS}

# 30 ticks per wheel. (kind, ticks, number)
OP_SLICES = [("attack", 3, "6"), ("defend", 3, "5"), ("attack", 4, "6"), ("crit", 2, "12"),
             ("evade", 3, "4"), ("attack", 3, "6"), ("afflict", 3, "3"), ("defend", 3, "6"),
             ("miss", 2, ""), ("attack", 4, "8")]
EN_SLICES = [("afflict", 4, "4"), ("attack", 3, "6"), ("defend", 4, "6"), ("attack", 3, "8"),
             ("miss", 3, ""), ("crit", 2, "14"), ("defend", 3, "6"), ("attack", 4, "6"),
             ("evade", 4, "3")]


def P(x, y):
    """Metres -> supersampled pixel coordinates (y up)."""
    return ((x + R) * S, (R - y) * S)


def polar(r, phi_deg):
    """Point at radius r, angle phi clockwise from 12 o'clock."""
    a = math.radians(phi_deg)
    return (r * math.sin(a), r * math.cos(a))


def canvas(mode="RGBA", fill=None):
    if fill is None:
        fill = (0, 0, 0, 0) if mode == "RGBA" else 0
    return Image.new(mode, (NS, NS), fill)


def save(img, name):
    img = img.resize((N, N), Image.LANCZOS)
    img.save(os.path.join(OUT, name + ".png"), optimize=True)
    print("wrote", name)


def circle_box(r, cx=0.0, cy=0.0):
    x0, y0 = P(cx - r, cy + r)
    x1, y1 = P(cx + r, cy - r)
    return [x0, y0, x1, y1]


def annulus_poly(r0, r1, phi0, phi1, step=0.5):
    pts = []
    n = max(2, int(abs(phi1 - phi0) / step))
    for i in range(n + 1):
        pts.append(P(*polar(r1, phi0 + (phi1 - phi0) * i / n)))
    for i in range(n + 1):
        pts.append(P(*polar(r0, phi1 - (phi1 - phi0) * i / n)))
    return pts


def ring(draw, r0, r1, fill):
    """Filled ring as a polygon (works for L and RGBA)."""
    draw.polygon(annulus_poly(r0, r1, 0, 360, 0.25), fill=fill)


def font(path, metres):
    return ImageFont.truetype(path, int(metres * S))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- glyphs
def glyph_polys(kind):
    """Unit-space polygons (y up, roughly [-1,1]) plus circles (cx, cy, r)."""
    polys, circles = [], []
    if kind == "attack":
        polys.append([(0, 0.98), (0.17, 0.62), (0.17, -0.22), (-0.17, -0.22), (-0.17, 0.62)])
        polys.append([(-0.5, -0.2), (0.5, -0.2), (0.5, -0.4), (-0.5, -0.4)])
        polys.append([(-0.1, -0.4), (0.1, -0.4), (0.1, -0.78), (-0.1, -0.78)])
        circles.append((0, -0.84, 0.15))
    elif kind == "crit":
        pts = []
        for i in range(16):
            rr = 0.98 if i % 2 == 0 else 0.44
            a = math.radians(i * 22.5)
            pts.append((rr * math.sin(a), rr * math.cos(a)))
        polys.append(pts)
    elif kind == "defend":
        polys.append([(-0.72, 0.72), (0, 0.97), (0.72, 0.72), (0.66, -0.05), (0, -0.97), (-0.66, -0.05)])
    elif kind == "evade":
        for dx in (-0.42, 0.28):
            polys.append([(dx - 0.42, 0.72), (dx - 0.02, 0.72), (dx + 0.42, 0), (dx - 0.02, -0.72),
                          (dx - 0.42, -0.72), (dx + 0.0, 0)])
    elif kind == "afflict":
        circles.append((0, -0.32, 0.58))
        polys.append([(-0.5, -0.05), (0, 0.98), (0.5, -0.05)])
    elif kind == "miss":
        pass
    return polys, circles


def glyph_image(kind, size_px, outline_px, fill=WHITE, ink=INK):
    """RGBA glyph with a bold ink outline; also returns the dilated mask for height maps."""
    pad = outline_px * 2 + 4
    G = size_px + pad * 2
    m = Image.new("L", (G, G), 0)
    d = ImageDraw.Draw(m)

    def tp(u, v):
        return (G / 2 + u * size_px / 2, G / 2 - v * size_px / 2)

    polys, circles = glyph_polys(kind)
    for poly in polys:
        d.polygon([tp(u, v) for u, v in poly], fill=255)
    for cx, cy, rr in circles:
        x, y = tp(cx, cy)
        rp = rr * size_px / 2
        d.ellipse([x - rp, y - rp, x + rp, y + rp], fill=255)
    if kind == "miss":
        rp = 0.6 * size_px / 2
        w = int(0.2 * size_px / 2)
        d.ellipse([G / 2 - rp, G / 2 - rp, G / 2 + rp, G / 2 + rp], outline=255, width=w)
        d.line([tp(-0.62, -0.62), tp(0.62, 0.62)], fill=255, width=w)
    k = outline_px * 2 + 1
    dil = m.filter(ImageFilter.MaxFilter(k if k % 2 else k + 1))
    img = Image.new("RGBA", (G, G), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (G, G), ink + (255,)), (0, 0), dil)
    img.paste(Image.new("RGBA", (G, G), fill + (255,)), (0, 0), m)
    return img, dil, m


def text_image(txt, fnt, fill, stroke, stroke_fill=INK):
    bbox = fnt.getbbox(txt, stroke_width=stroke)
    w, h = bbox[2] - bbox[0] + 8, bbox[3] - bbox[1] + 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((4 - bbox[0], 4 - bbox[1]), txt, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return img


def paste_rot(dst, src, x, y, rot_deg, mask=None):
    """Paste src centred at metres (x, y), rotated clockwise by rot_deg."""
    s = src.rotate(-rot_deg, resample=Image.BICUBIC, expand=True)
    px, py = P(x, y)
    pos = (int(px - s.width / 2), int(py - s.height / 2))
    if mask is None:
        dst.alpha_composite(s, pos) if dst.mode == "RGBA" else dst.paste(s, pos, s)
    return s, pos


# ---------------------------------------------------------------- slices
def slices_layer(slices, prefix):
    alb = canvas()
    hgt = canvas("L")
    glw = canvas()
    da, dh, dg = ImageDraw.Draw(alb), ImageDraw.Draw(hgt), ImageDraw.Draw(glw)
    # dark well floor under everything (so parallax never opens a gap)
    da.ellipse(circle_box(0.995), fill=FLOOR + (255,))
    dh.ellipse(circle_box(0.995), fill=40)
    r0, r1 = 0.42, 0.86
    rim = int(0.011 * S)
    phi = 0.0
    centres = []
    for kind, ticks, num in slices:
        span = ticks * 12.0
        c = KIND_COL[kind]
        fillc = mix(FLOOR, c, 0.5)
        da.polygon(annulus_poly(r0, r1, phi, phi + span), fill=fillc + (255,))
        dh.polygon(annulus_poly(r0, r1, phi, phi + span), fill=150)
        # bright rim: inset outline of the sector
        inset = 0.012
        a_in = math.degrees(inset / r1)
        rim_pts = annulus_poly(r0 + inset, r1 - inset, phi + a_in, phi + span - a_in)
        if kind == "miss":
            # dashed rim
            for k in range(0, len(rim_pts) - 1, 6):
                da.line(rim_pts[k:k + 4], fill=c + (255,), width=rim)
                dg.line(rim_pts[k:k + 4], fill=c + (255,), width=rim)
        else:
            da.line(rim_pts + [rim_pts[0]], fill=c + (255,), width=rim, joint="curve")
            dg.line(rim_pts + [rim_pts[0]], fill=c + (255,), width=rim * 2, joint="curve")
        centres.append((kind, phi + span / 2, num))
        phi += span
    # dividers (grooves)
    phi = 0.0
    for kind, ticks, num in slices:
        a = P(*polar(r0, phi))
        b = P(*polar(r1, phi))
        da.line([a, b], fill=FLOOR + (255,), width=int(0.014 * S))
        dh.line([a, b], fill=20, width=int(0.03 * S))
        phi += ticks * 12.0
    dh.ellipse(circle_box(r0), fill=40)
    hgt = hgt.filter(ImageFilter.GaussianBlur(0.012 * S))
    # glyphs and numbers
    gsize = int(0.17 * S)
    fnum = font(ANTON, 0.13)
    hmask = canvas("L")
    for kind, mid, num in centres:
        g, dil, core = glyph_image(kind, gsize, int(0.012 * S))
        x, y = polar(0.69, mid)
        s, pos = paste_rot(alb, g, x, y, mid)
        dm = dil.rotate(-mid, resample=Image.BICUBIC, expand=True)
        hmask.paste(255, pos, dm)
        if num:
            t = text_image(num, fnum, WHITE, int(0.009 * S))
            x, y = polar(0.515, mid)
            s, pos = paste_rot(alb, t, x, y, mid)
            hmask.paste(235, pos, s.split()[3])
    hmask = hmask.filter(ImageFilter.GaussianBlur(0.005 * S))
    hgt = ImageChops.lighter(hgt, hmask)
    save(alb, prefix + "_slices")
    save(hgt, prefix + "_slices_h")
    save(glw.filter(ImageFilter.GaussianBlur(3)), prefix + "_slices_g")


# ---------------------------------------------------------------- bezel
def torn_poly(rng, r0, r1, phi0, phi1):
    pts = []
    n = 14
    for i in range(n + 1):
        f = phi0 + (phi1 - phi0) * i / n
        pts.append(polar(r1 - rng.uniform(0, 0.012), f + rng.uniform(-0.4, 0.4)))
    for k in range(5):
        pts.append(polar(r1 - (r1 - r0) * (k + 1) / 6, phi1 + rng.uniform(-1.5, 1.5)))
    for i in range(n + 1):
        f = phi1 - (phi1 - phi0) * i / n
        pts.append(polar(r0 + rng.uniform(0, 0.012), f + rng.uniform(-0.4, 0.4)))
    for k in range(5):
        pts.append(polar(r0 + (r1 - r0) * (k + 1) / 6, phi0 + rng.uniform(-1.5, 1.5)))
    return [P(*p) for p in pts]


def notch_r(phi, r_out=1.0, depth=0.045, every=15.0, width=5.0):
    """Outer radius of the enemy's notched hostile edge at angle phi."""
    f = (phi + every / 2) % every
    return r_out - depth if abs(f - every / 2) < width / 2 else r_out


def outline_poly(fn, r_in, step=0.25):
    pts = [P(*polar(fn(i * step), i * step)) for i in range(int(360 / step) + 1)]
    pts += [P(*polar(r_in, 360 - i * step)) for i in range(int(360 / step) + 1)]
    return pts


def bezel_layer(enemy):
    rng = random.Random(7 if not enemy else 11)
    alb, hgt, glw = canvas(), canvas("L"), canvas()
    da, dh, dg = ImageDraw.Draw(alb), ImageDraw.Draw(hgt), ImageDraw.Draw(glw)
    r_in, r_out = 0.86, 1.0
    base = (28, 31, 41) if not enemy else (40, 29, 20)
    rfn = (lambda p: notch_r(p)) if enemy else (lambda p: r_out)
    da.polygon(outline_poly(rfn, r_in), fill=base + (255,))
    dh.polygon(outline_poly(rfn, r_in), fill=120)
    # brushed concentric lines + rounded height profile
    k = 0
    r = r_in
    while r < r_out:
        t = (r - r_in) / (r_out - r_in)
        shade = mix(base, (70, 76, 92) if not enemy else (92, 66, 40), 0.25 + 0.2 * math.sin(k * 1.7) ** 2)
        da.ellipse(circle_box(r), outline=shade + (255,), width=2)
        dh.ellipse(circle_box(r), outline=int(90 + 150 * math.sin(math.pi * t) ** 0.6), width=int(0.004 * S) + 1)
        r += 0.004
        k += 1
    # re-cut the notches after the brushing
    if enemy:
        for i in range(24):
            ph = i * 15.0
            da.polygon(annulus_poly(0.95, 1.01, ph - 2.5, ph + 2.5), fill=(0, 0, 0, 0))
            dh.polygon(annulus_poly(0.95, 1.01, ph - 2.5, ph + 2.5), fill=0)
    metal = alb.copy()
    # tick marks (30)
    for i in range(30):
        a, b = P(*polar(0.868, i * 12)), P(*polar(0.895 if i % 5 else 0.91, i * 12))
        da.line([a, b], fill=(200, 210, 225, 200), width=int(0.006 * S))
        dh.line([a, b], fill=60, width=int(0.008 * S))
    if not enemy:
        # paper stickers, torn
        for i in range(7):
            ph0 = i * 51 + rng.uniform(-6, 6) + 20
            span = rng.uniform(14, 26)
            poly = torn_poly(rng, 0.9, 0.985, ph0, ph0 + span)
            c = PAPER if i % 2 else PAPER_ALT
            da.polygon(poly, fill=c + (255,))
            dh.polygon(poly, fill=215)
            # marker scrawl / grime
            for j in range(3):
                f = ph0 + rng.uniform(0.2, 0.8) * span
                p1 = P(*polar(0.915 + j * 0.02, f - 3))
                p2 = P(*polar(0.925 + j * 0.02, f + 3))
                da.line([p1, p2], fill=(INK if j else PINK) + (160,), width=int(0.006 * S))
        # Breaker ornament: pink bolts
        for ph in (45, 135, 225, 315):
            x, y = polar(0.93, ph)
            s = 0.025
            for dx, dy in ((s, 0), (0, s)):
                da.line([P(x - dx, y - dy), P(x + dx, y + dy)], fill=PINK + (255,), width=int(0.012 * S))
                dh.line([P(x - dx, y - dy), P(x + dx, y + dy)], fill=235, width=int(0.014 * S))
        # pink rims
        ring(da, 0.985, 1.0, PINK + (255,))
        ring(dg, 0.982, 1.003, PINK + (255,))
        ring(da, 0.86, 0.867, PINK + (255,))
        ring(dh, 0.985, 1.0, 190)
    else:
        # Meridian: shipping-container stripes (45 deg) on a band, orange edge
        band = canvas("L")
        ImageDraw.Draw(band).polygon(annulus_poly(0.885, 0.94, 0, 360, 0.25), fill=255)
        stripes = canvas("L")
        ds = ImageDraw.Draw(stripes)
        step = int(0.05 * S)
        for x in range(-NS, NS * 2, step):
            ds.polygon([(x, 0), (x + step // 2, 0), (x + step // 2 - NS, NS), (x - NS, NS)], fill=255)
        m = ImageChops.multiply(band, stripes)
        alb.paste(Image.new("RGBA", (NS, NS), MERIDIAN + (255,)), (0, 0), m)
        hgt.paste(200, (0, 0), m)
        edge = outline_poly(rfn, 0.975)
        da.polygon(edge, fill=MERIDIAN + (255,))
        dg.polygon(edge, fill=MERIDIAN + (255,))
        ring(da, 0.86, 0.868, MERIDIAN + (255,))
    hgt = hgt.filter(ImageFilter.GaussianBlur(0.004 * S))
    pre = "en" if enemy else "op"
    diff = ImageChops.difference(alb, metal).convert("L").point(lambda v: 255 if v > 0 else 0)
    dec = alb.copy()
    dec.putalpha(ImageChops.multiply(diff, alb.split()[3]))
    save(dec, pre + "_bezel_d")
    save(alb, pre + "_bezel")
    save(hgt, pre + "_bezel_h")
    save(glw.filter(ImageFilter.GaussianBlur(3)), pre + "_bezel_g")


# ---------------------------------------------------------------- hub
def hub_layer(enemy):
    alb, hgt, glw = canvas(), canvas("L"), canvas()
    da, dh, dg = ImageDraw.Draw(alb), ImageDraw.Draw(hgt), ImageDraw.Draw(glw)
    edge = MERIDIAN if enemy else PINK
    da.ellipse(circle_box(0.40), fill=(12, 16, 32, 255))
    dh.ellipse(circle_box(0.40), fill=200)
    ring(da, 0.385, 0.40, edge + (255,))
    ring(dg, 0.385, 0.40, edge + (255,))
    ring(dh, 0.36, 0.40, 240)
    # hub pattern: faint hatch (op) / concentric civic-ish rings (enemy)
    pat = canvas("L")
    dp = ImageDraw.Draw(pat)
    if not enemy:
        step = int(0.028 * S)
        for x in range(-NS, NS * 2, step):
            dp.line([(x, 0), (x - NS, NS)], fill=255, width=3)
    else:
        for i in range(1, 12):
            dp.ellipse(circle_box(0.03 * i), outline=255, width=3)
    clip = canvas("L")
    ImageDraw.Draw(clip).ellipse(circle_box(0.34), fill=40)
    alb.paste(Image.new("RGBA", (NS, NS), (60, 90, 140, 255)), (0, 0), ImageChops.multiply(pat, clip))
    if not enemy:
        # polaroid mini-portrait
        pol = Image.new("RGBA", (int(0.13 * S), int(0.155 * S)), PAPER + (255,))
        dpol = ImageDraw.Draw(pol)
        m = int(0.012 * S)
        dpol.rectangle([m, m, pol.width - m, pol.height - int(0.035 * S)], fill=(60, 16, 44, 255))
        cx = pol.width / 2
        dpol.ellipse([cx - 0.025 * S, 0.03 * S, cx + 0.025 * S, 0.08 * S], fill=PINK + (255,))
        dpol.pieslice([cx - 0.05 * S, 0.085 * S, cx + 0.05 * S, 0.17 * S], 180, 360, fill=PINK + (255,))
        dpol.rectangle([m, pol.height - int(0.035 * S), pol.width - m, pol.height - m], fill=PAPER + (255,))
        paste_rot(alb, pol, 0, 0.225, -6)
        name, sub = ["BREAKER"], "Breaker Core"
        fsz = 0.105
    else:
        # corp landmark: container crane, line glyph
        c = MERIDIAN
        w = int(0.012 * S)
        pts = [(-0.06, 0.16), (-0.06, 0.30), (0.08, 0.30), (-0.06, 0.26)]
        da.line([P(*p) for p in pts], fill=c + (255,), width=w)
        da.line([P(0.05, 0.30), P(0.05, 0.24)], fill=c + (255,), width=w)
        da.rectangle([*P(0.02, 0.24), *P(0.08, 0.2)], fill=c + (255,))
        name, sub = ["COLLECTIONS", "AGENT"], "Meridian Freight"
        fsz = 0.07
    f = font(ANTON, fsz)
    y = 0.02 if len(name) == 1 else 0.055
    for line in name:
        t = text_image(line, f, WHITE, int(0.004 * S))
        paste_rot(alb, t, 0, y, 0)
        y -= fsz * 1.25
    t = text_image(sub, font(PLEX, 0.045), TEXT_MID, 0)
    paste_rot(alb, t, 0, -0.16, 0)
    hgt = hgt.filter(ImageFilter.GaussianBlur(0.006 * S))
    pre = "en" if enemy else "op"
    save(alb, pre + "_hub")
    save(hgt, pre + "_hub_h")
    save(glw.filter(ImageFilter.GaussianBlur(3)), pre + "_hub_g")


# ---------------------------------------------------------------- HP arc
def hp_layer(enemy):
    alb, hgt, glw = canvas(), canvas("L"), canvas()
    da, dh, dg = ImageDraw.Draw(alb), ImageDraw.Draw(hgt), ImageDraw.Draw(glw)
    n = 22
    a0, a1 = 118.0, 242.0
    step = (a1 - a0) / n
    for i in range(n):
        p = annulus_poly(1.05, 1.13, a0 + i * step + 0.7, a0 + (i + 1) * step - 0.7, 0.3)
        da.polygon(p, fill=GREEN + (255,))
        dg.polygon(p, fill=GREEN + (255,))
        dh.polygon(p, fill=200)
    txt = "40/40" if enemy else "60/60"
    t = text_image(txt, font(ANTON, 0.2), GREEN, int(0.012 * S))
    paste_rot(alb, t, 0, -1.29, 0)
    hm = t.split()[3]
    s, pos = t, (int(P(0, -1.29)[0] - t.width / 2), int(P(0, -1.29)[1] - t.height / 2))
    hgt.paste(220, pos, hm)
    hgt = hgt.filter(ImageFilter.GaussianBlur(0.006 * S))
    pre = "en" if enemy else "op"
    save(alb, pre + "_hp")
    save(hgt, pre + "_hp_h")
    save(glw.filter(ImageFilter.GaussianBlur(3)), pre + "_hp_g")


# ---------------------------------------------------------------- neon sign
def pink_sign():
    """Vertical neon sign: illegible stroke glyphs in a frame (for the raking pink light)."""
    rng = random.Random(3)
    W, H = 360, 1400
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([12, 12, W - 12, H - 12], radius=30, outline=PINK + (255,), width=14)
    y = 80
    for k in range(5):
        cx = W / 2
        for s in range(rng.randint(3, 5)):
            x0 = cx + rng.uniform(-90, 90)
            y0 = y + rng.uniform(0, 180)
            if rng.random() < 0.5:
                d.line([(x0, y0), (x0 + rng.uniform(-80, 80), y0)], fill=PINK + (255,), width=16)
            else:
                d.line([(x0, y0), (x0, y0 + rng.uniform(40, 150))], fill=PINK + (255,), width=16)
        y += 250
    img.save(os.path.join(OUT, "sign_pink.png"))


# ---------------------------------------------------------------- backdrop
def backdrop():
    """Dimmed, desaturated night city behind the fight (feedback 3: it must recede)."""
    rng = random.Random(21)
    W, H = 2560, 1440
    sky = Image.new("RGB", (W, H))
    ds = ImageDraw.Draw(sky)
    for y in range(H):
        t = y / H
        ds.line([(0, y), (W, y)], fill=mix((8, 10, 24), (30, 22, 48), t ** 1.5))
    img = sky.convert("RGBA")
    layers = [  # (base y, height range, colour, window colour, blur, count)
        (0.55, (0.25, 0.55), (34, 40, 66), (120, 150, 190), 9, 26),
        (0.68, (0.25, 0.6), (22, 26, 46), (150, 170, 210), 5, 22),
        (0.82, (0.3, 0.7), (12, 14, 28), (200, 190, 150), 2, 16),
    ]
    for base, (h0, h1), col_, wcol, blur, count in layers:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        x = -50
        while x < W:
            bw = rng.randint(90, 260)
            bh = int(H * rng.uniform(h0, h1))
            top = int(H * base) - bh + int(H * 0.3)
            dl.rectangle([x, top, x + bw, H], fill=col_ + (255,))
            # windows
            for wy in range(top + 20, H, 26):
                for wx in range(x + 12, x + bw - 12, 22):
                    if rng.random() < 0.18:
                        a = rng.randint(60, 190)
                        dl.rectangle([wx, wy, wx + 9, wy + 12], fill=wcol + (a,))
            if rng.random() < 0.25:
                sc = rng.choice([PINK, CYAN, (176, 77, 255), (255, 176, 0)])
                sy = top + rng.randint(30, 200)
                dl.rectangle([x + 10, sy, x + bw - 10, sy + rng.randint(14, 40)], fill=sc + (200,))
            x += bw + rng.randint(-20, 30)
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))
    # haze band
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dh = ImageDraw.Draw(haze)
    for y in range(H):
        t = abs(y / H - 0.62)
        dh.line([(0, y), (W, y)], fill=(80, 70, 110, int(max(0, 70 - t * 260))))
    img.alpha_composite(haze.filter(ImageFilter.GaussianBlur(20)))
    img = img.convert("RGB")
    img = ImageEnhance.Color(img).enhance(0.35)       # desaturate
    img = ImageEnhance.Brightness(img).enhance(0.6)  # dim
    img = img.filter(ImageFilter.GaussianBlur(2))
    # vignette
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse([-W * 0.15, -H * 0.3, W * 1.15, H * 1.3], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(220))
    img = Image.composite(img, Image.new("RGB", (W, H), (2, 3, 8)), vig)
    img.save(os.path.join(OUT, "backdrop_wide.png"))
    sq = img.crop(((W - H) // 2, 0, (W + H) // 2, H))
    sq.save(os.path.join(OUT, "backdrop_square.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    slices_layer(OP_SLICES, "op")
    slices_layer(EN_SLICES, "en")
    for e in (False, True):
        bezel_layer(e)
        hub_layer(e)
        hp_layer(e)
    pink_sign()
    backdrop()
    print("done")
