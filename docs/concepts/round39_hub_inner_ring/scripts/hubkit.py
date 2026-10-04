"""Round 38: the D4 hub (core emblem, name, Mk2, enemy hub, BREACHED) and the inner ring of three
10-tick segments, drawn into the round 17 slice wheel.

Geometry is in master units (slicelib: slices R_IN 130 .. R_OUT 360). The D4 hub keeps the centre;
the inner ring is the band RING_IN .. RING_OUT between the hub and the slices.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import slicelib as SL
import slicekit as K
from slicelib import R_IN, R_OUT, f_num, f_ui, f_mono

INK = (10, 8, 16)
HUB_R = 80
RING_IN, RING_OUT = 84, 124
HARM = (255, 59, 48)


def _glow_glyph(name, px, col, ss, alpha=1.0, glow=0.9):
    g = SL.glyph_rgba(name, int(px), max(1.5, px * 0.07))
    a = g.split()[3]
    blur = a.filter(ImageFilter.GaussianBlur(px * 0.12)).point(lambda v: int(min(255, v * glow)))
    halo = Image.new("RGBA", g.size, col + (0,))
    halo.putalpha(blur)
    out = Image.new("RGBA", g.size, (0, 0, 0, 0))
    out.alpha_composite(halo)
    out.alpha_composite(g)
    if alpha < 1:
        out.putalpha(out.split()[3].point(lambda v: int(v * alpha)))
    return out


def _paste_c(img, im, x, y):
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


def draw_hub(img, c, ss, acc, emblem, name, sub="", mk2=False, enemy=False, breached=False, t=0.0, lod=False, seed=1):
    """D4 hub: dark CRT disc in a machined rim; emblem centre, core name and passive under it."""
    cx, cy = c
    R = HUB_R * ss
    d = ImageDraw.Draw(img)
    # machined rim (D4-lite): dark bead, accent hairline, lip shadow
    d.ellipse([cx - R - 6 * ss, cy - R - 6 * ss, cx + R + 6 * ss, cy + R + 6 * ss], fill=(30, 28, 40, 255))
    d.ellipse([cx - R - 6 * ss, cy - R - 6 * ss, cx + R + 6 * ss, cy + R + 6 * ss], outline=acc + (255,), width=max(1, int(1.6 * ss)))
    if mk2:  # Mk2: a second, notched rim ring
        r2 = R + 3 * ss
        for k in range(24):
            a0 = k * 15
            d.arc([cx - r2, cy - r2, cx + r2, cy + r2], a0 + 2, a0 + 11, fill=acc + (255,), width=max(1, int(2.4 * ss)))
    # CRT disc
    disc = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    base = tuple(int(v * 0.10) + 10 for v in acc)
    dd.ellipse([cx - R, cy - R, cx + R, cy + R], fill=base + (255,))
    arr = np.asarray(disc, np.float32)
    yy, xx = np.mgrid[0:img.size[1], 0:img.size[0]]
    rr = np.hypot(xx - cx, yy - cy) / R
    vign = np.clip(1.15 - 0.55 * rr ** 2, 0.4, 1.2)
    scan = 0.82 + 0.18 * (np.cos(2 * np.pi * yy / (3 * ss)) * 0.5 + 0.5)
    arr[..., :3] *= (vign * scan)[..., None]
    if enemy and not breached:  # faint corp chevron watermark rotating slowly
        ang = (np.degrees(np.arctan2(yy - cy, xx - cx)) + t * 30) % 30
        arr[..., :3] += ((ang < 4) & (rr > 0.84) & (rr < 0.96))[..., None] * np.array(acc, np.float32) * 0.35
    disc = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    img.alpha_composite(disc)
    d = ImageDraw.Draw(img)
    # emblem + texts
    epx = R * (1.05 if lod else 0.86)
    ey = cy - (0 if lod else R * 0.18)
    if breached:
        g = _glow_glyph(emblem, epx, acc, ss, alpha=0.75, glow=0.3)
        r_, g_, b_, a_ = g.split()
        a2 = a_.point(lambda v: int(v * 0.6))
        red = Image.merge("RGBA", (r_, Image.new("L", g.size, 40), Image.new("L", g.size, 60), a2))
        blu = Image.merge("RGBA", (Image.new("L", g.size, 40), Image.new("L", g.size, 200), b_, a2))
        o = int(4 * ss)
        _paste_c(img, red, cx - o, ey)
        _paste_c(img, blu, cx + o, ey + ss)
        _paste_c(img, g, cx, ey)
    else:
        _paste_c(img, _glow_glyph(emblem, epx, acc, ss), cx, ey)
    if not lod:
        f1 = f_ui(int(13 * ss), b"Bold SemiCondensed")
        tw = f1.getlength(name)
        if tw > R * 1.6:
            f1 = f_ui(int(13 * ss * R * 1.6 / tw), b"Bold SemiCondensed")
            tw = f1.getlength(name)
        ny = cy + R * 0.38
        d.text((cx - tw / 2, ny), name, font=f1, fill=(240, 240, 248, 255), stroke_width=int(2 * ss), stroke_fill=INK + (255,))
        if sub:
            f2 = f_mono(int(8.5 * ss))
            sw = f2.getlength(sub)
            if sw > R * 1.5:
                f2 = f_mono(max(6, int(8.5 * ss * R * 1.5 / sw)))
                sw = f2.getlength(sub)
            sy = ny + 18 * ss
            d.text((cx - sw / 2, sy), sub, font=f2, fill=tuple(int(v * 0.6 + 90) for v in acc) + (255,))
            if breached:  # the passive is struck out while breached
                d.line([(cx - sw / 2 - 3 * ss, sy + 5 * ss), (cx + sw / 2 + 3 * ss, sy + 5 * ss)], fill=HARM + (255,), width=int(2 * ss))
        if mk2:  # MK2 tab on the bottom rim
            f3 = f_num(int(13 * ss))
            tx = "MK2"
            w3 = f3.getlength(tx) + 12 * ss
            y3 = cy + R - 2 * ss
            d.rounded_rectangle([cx - w3 / 2, y3, cx + w3 / 2, y3 + 17 * ss], radius=4 * ss, fill=acc + (255,), outline=INK + (255,), width=int(2 * ss))
            d.text((cx - f3.getlength(tx) / 2, y3 + 0.5 * ss), tx, font=f3, fill=INK + (255,))
    if breached:
        _breach(img, c, ss, R, acc, t, seed, lod)


def _breach(img, c, ss, R, acc, t, seed, lod):
    """BREACHED: the glass cracks from an impact point, the screen tears with static, sparks spit
    from the cracks, a red BREACHED plate + turn pips. Loops over t."""
    cx, cy = c
    rng = np.random.default_rng(seed)
    W, H = img.size
    # static + tear bands inside the disc
    arr = np.asarray(img, np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    inside = np.hypot(xx - cx, yy - cy) < R
    frame = int(t * 12)
    nrng = np.random.default_rng(seed * 13 + frame)
    noise = nrng.random((H // max(1, int(2 * ss)) + 1, W // max(1, int(2 * ss)) + 1))
    noise = np.kron(noise, np.ones((max(1, int(2 * ss)), max(1, int(2 * ss)))))[:H, :W]
    arr[..., :3] = np.where(inside[..., None], arr[..., :3] * 0.80 + (noise[..., None] > 0.94) * np.array([150, 150, 170]) * 0.45, arr[..., :3])
    for k in range(2):
        y0 = int(cy - R + nrng.random() * 2 * R)
        h = int((3 + nrng.random() * 7) * ss)
        dx = int((nrng.random() - 0.5) * 18 * ss)
        band = inside[y0:y0 + h]
        arr[y0:y0 + h] = np.where(band[..., None], np.roll(arr[y0:y0 + h], dx, axis=1), arr[y0:y0 + h])
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    img.paste(out)
    d = ImageDraw.Draw(img)
    # cracks: from an impact point up-right, branching to the rim
    ip = (cx + R * 0.32, cy - R * 0.30)
    cracks = []
    for k in range(7):
        a = math.radians(k * 51 + rng.random() * 20)
        pts = [ip]
        x, y = ip
        L = R * (0.5 + 0.7 * rng.random())
        steps = 6
        for s in range(steps):
            a += (rng.random() - 0.5) * 0.7
            x += math.cos(a) * L / steps
            y += math.sin(a) * L / steps
            if math.hypot(x - cx, y - cy) > R * 1.04:
                break
            pts.append((x, y))
        cracks.append(pts)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for pts in cracks:
        if len(pts) > 1:
            gd.line(pts, fill=(255, 120, 60, 255), width=int(5 * ss))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3 * ss)))
    for pts in cracks:
        if len(pts) > 1:
            d.line(pts, fill=INK + (255,), width=int(3.4 * ss))
            d.line(pts, fill=(255, 236, 210, 255), width=max(1, int(1.2 * ss)))
    d.ellipse([ip[0] - 7 * ss, ip[1] - 7 * ss, ip[0] + 7 * ss, ip[1] + 7 * ss], fill=(255, 240, 220, 255), outline=INK + (255,), width=int(2 * ss))
    # sparks from crack ends (animated)
    for i, pts in enumerate(cracks):
        ex, ey = pts[-1]
        for j in range(3):
            ph = (t * 2 + i * 0.13 + j * 0.31) % 1.0
            a = math.radians(rng.random() * 360)
            v = (8 + 18 * ph) * ss
            sx, sy = ex + math.cos(a) * v, ey + math.sin(a) * v + 10 * ss * ph * ph
            r = (2.2 - 1.6 * ph) * ss
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 220, 120, int(255 * (1 - ph))))
    if lod:  # at small sizes: a thick HARM ring around the broken hub carries the state
        d.ellipse([cx - R - 2 * ss, cy - R - 2 * ss, cx + R + 2 * ss, cy + R + 2 * ss], outline=HARM + (255,), width=int(7 * ss))
    # BREACHED plate + turn pip (Hub Breach = 1 turn; Short Circuit = 2)
    f = f_num(int((16 if not lod else 22) * ss))
    tx = "BREACHED"
    w = f.getlength(tx) + 14 * ss
    y0 = cy - R - (12 if not lod else 18) * ss
    d.rounded_rectangle([cx - w / 2, y0, cx + w / 2, y0 + 22 * ss * (1.3 if lod else 1)], radius=4 * ss, fill=HARM + (255,), outline=INK + (255,), width=int(2 * ss))
    stripe = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d.text((cx - f.getlength(tx) / 2, y0 + 1 * ss), tx, font=f, fill=(255, 255, 255, 255))
    if not lod:
        fp = f_mono(int(9 * ss))
        s = "1 TURN"
        d.text((cx - fp.getlength(s) / 2, y0 + 25 * ss), s, font=fp, fill=(255, 190, 180, 255), stroke_width=int(2 * ss), stroke_fill=INK + (255,))


def draw_ring(img, c, ss, acc, segs, active=0, lod=False):
    """Inner ring: three 120-degree segments of 10 ticks; segment glyph upright at each centre.
    Segment 0 is under the pointer (top); the active one is lit."""
    cx, cy = c
    r0, r1 = RING_IN * ss, RING_OUT * ss
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r1 - 2 * ss, cy - r1 - 2 * ss, cx + r1 + 2 * ss, cy + r1 + 2 * ss], fill=(22, 20, 30, 255))
    for i, seg in enumerate(segs):
        a0 = -90 - 60 + i * 120
        lit = i == active
        fill = tuple(int(v * (0.30 if lit else 0.12)) + (14 if lit else 10) for v in acc) + (255,)
        # the band (with a 2-degree gap each side)
        poly = []
        for k in range(41):
            a = math.radians(a0 + 2 + (116 * k / 40))
            poly.append((cx + r1 * math.cos(a), cy + r1 * math.sin(a)))
        for k in range(40, -1, -1):
            a = math.radians(a0 + 2 + (116 * k / 40))
            poly.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a)))
        d.polygon(poly, fill=fill)
        d.line(poly[:41], fill=(acc if lit else tuple(int(v * 0.55) for v in acc)) + (255,), width=max(1, int((2.2 if lit else 1.2) * ss)))
        # 10 ticks along the outer edge of the segment
        if not lod:
            for k in range(1, 10):
                a = math.radians(a0 + 2 + 116 * k / 10)
                L = (5 if k == 5 else 3) * ss
                d.line([(cx + (r1 - L) * math.cos(a), cy + (r1 - L) * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
                       fill=(150, 150, 170, 255), width=max(1, int(ss)))
        # glyph upright at the segment centre
        am = math.radians(a0 + 60)
        rm = (r0 + r1) / 2
        px = (r1 - r0) * (0.80 if not lod else 0.95)
        g = SL.glyph_rgba(seg, int(px), max(1.5, px * 0.08))
        if not lit:
            g.putalpha(g.split()[3].point(lambda v: int(v * 0.72)))
        _paste_c(img, g, cx + rm * math.cos(am), cy + rm * math.sin(am))


def pointer(img, c, ss, R):
    """Simplified D4 blade at 12 o'clock: marks the slice and the ring segment under it."""
    cx, cy = c
    d = ImageDraw.Draw(img)
    top = cy - R - 30 * ss
    tip = cy - R + 26 * ss
    d.polygon([(cx - 15 * ss, top), (cx + 15 * ss, top), (cx, tip)], fill=(240, 232, 214, 255), outline=INK + (255,))
    d.line([(cx - 15 * ss, top), (cx, tip), (cx + 15 * ss, top), (cx - 15 * ss, top)], fill=INK + (255,), width=int(3 * ss))
    # ring marker notch
    rr = RING_OUT * ss + 3 * ss
    d.polygon([(cx - 7 * ss, cy - rr - 9 * ss), (cx + 7 * ss, cy - rr - 9 * ss), (cx, cy - rr)], fill=(240, 232, 214, 255), outline=INK + (255,))


def wheel(slices, segs, hub, t=0.3, ss=2, r_px=220, ring=True, seed=5, lod=None):
    """slices: 6 x (prog, value, tier, state[, theme]); segs: 3 seg glyph ids or None (enemies);
    hub: dict(acc, emblem, name, sub, mk2, enemy, breached)."""
    K.setup()
    lod = (r_px < 100) if lod is None else lod
    M = 48
    Ro = R_OUT * ss
    S = int(2 * (Ro + M * ss))
    c = S / 2
    canvas = np.zeros((S, S, 4), np.float32)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    acc = hub["acc"]
    d.ellipse([c - Ro - 8 * ss, c - Ro - 8 * ss, c + Ro + 8 * ss, c + Ro + 8 * ss], fill=(16, 14, 22, 255), outline=acc + (255,), width=int(3 * ss))
    canvas[:] = np.asarray(im, np.float32) / 255
    span = 60
    for i, sl in enumerate(slices):
        prog, val, tier, state = sl[:4]
        theme = sl[4] if len(sl) > 4 else "player"
        K.draw_slice(canvas, c, c, prog, i * span - span / 2, span, val, t, ss, tier, state, seed + i, theme=theme)
    out = K.to_rgba(canvas)
    d = ImageDraw.Draw(out)
    d.ellipse([c - R_IN * ss + 4 * ss, c - R_IN * ss + 4 * ss, c + R_IN * ss - 4 * ss, c + R_IN * ss - 4 * ss], fill=(14, 12, 20, 255))
    if ring and segs:
        draw_ring(out, (c, c), ss, acc, segs, 0, lod)
    hr_scale = 1.0 if (ring and segs) else 1.45
    if hr_scale != 1.0:  # enemy hubs (no inner ring) fill the centre
        global HUB_R
        old = HUB_R
        HUB_R = int(old * hr_scale)
        draw_hub(out, (c, c), ss, acc, hub["emblem"], hub["name"], hub.get("sub", ""), hub.get("mk2", False),
                 hub.get("enemy", False), hub.get("breached", False), t, lod, seed)
        HUB_R = old
    else:
        draw_hub(out, (c, c), ss, acc, hub["emblem"], hub["name"], hub.get("sub", ""), hub.get("mk2", False),
                 hub.get("enemy", False), hub.get("breached", False), t, lod, seed)
    pointer(out, (c, c), ss, Ro)
    k = r_px / R_OUT / ss
    return out.resize((int(S * k), int(S * k)), Image.LANCZOS)


def hub_closeup(hub, t=0.3, ss=3, size=200, ring_segs=None):
    """A hub (optionally with its inner ring) alone, size px wide."""
    S = int((RING_OUT + 14) * 2 * ss)
    c = S / 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if ring_segs:
        draw_ring(im, (c, c), ss, hub["acc"], ring_segs, 0)
        draw_hub(im, (c, c), ss, hub["acc"], hub["emblem"], hub["name"], hub.get("sub", ""), hub.get("mk2", False),
                 hub.get("enemy", False), hub.get("breached", False), t, False, 3)
    else:
        global HUB_R
        old = HUB_R
        HUB_R = int(RING_OUT * 0.98)
        draw_hub(im, (c, c), ss, hub["acc"], hub["emblem"], hub["name"], hub.get("sub", ""), hub.get("mk2", False),
                 hub.get("enemy", False), hub.get("breached", False), t, False, 3)
        HUB_R = old
    return im.resize((size, size), Image.LANCZOS)
