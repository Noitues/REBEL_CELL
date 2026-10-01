"""Sticker designs for combined_v2 (copied from o_c_vinyl_sticker; thicker, crisper die-cut borders)."""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from sticker_lib import *  # noqa


def verb(word, size=96, seed=7, phase=0.0, curl=None, gloss_pos=0.32, lines=None):
    """Big holographic die-cut verb letters, black keyline, chunky extrude."""
    art = lettering(lines or [word], size, ["holo"], key_w=5, extrude=8, seed=seed, jitter=4.5,
                    track=1, holo_seed=seed + 40, holo_phase=phase)
    return build_sticker(art, border=20, material="gloss", gloss_pos=gloss_pos, curl=curl, seed=seed)


def yellow_word(lines, size=60, seed=3, fills=None, curl=None, gloss_pos=0.3, border=11):
    fills = fills or [("grad", (255, 236, 70), YELLOW_LO)]
    art = lettering(lines, size, fills, key_w=4, extrude=6, seed=seed, jitter=4.0, track=1)
    return build_sticker(art, border=border, material="gloss", gloss_pos=gloss_pos, curl=curl, seed=seed)


def clear_word(lines, size=58, seed=4, icon=True):
    """Clear vinyl, printed white ink with a thin black keyline."""
    art = lettering(lines, size, [(250, 250, 248)], key_w=2.2, extrude=0, seed=seed, jitter=2.0,
                    track=2, bevel=False, pad=70)
    if icon:
        S = SS
        w, h = art.size
        a = art.split()[3]
        x0, y0, x1, y1 = a.getbbox()
        canvas = Image.new("RGBA", (w + 70 * S, h), (0, 0, 0, 0))
        canvas.paste(art, (70 * S, 0))
        d = ImageDraw.Draw(canvas)
        cx, cy, r = x0 + 48 * S, (y0 + y1) / 2, 22 * S
        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.45
            an = -math.pi / 2 + i * math.pi / 5
            pts.append((cx + rr * math.cos(an), cy + rr * math.sin(an)))
        d.polygon(pts, fill=(250, 250, 248, 255), outline=INK + (255,), width=int(2 * S))
        art = canvas
    return build_sticker(art, border=14, material="clear", gloss_pos=0.4, close=26)


def price_dot(value, seed=1, d=74, angle_seed=0):
    S = SS
    P = 40 * S
    W = int(d * S) + 2 * P
    art = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    dr = ImageDraw.Draw(art)
    c = W / 2
    r = d * S / 2
    dr.ellipse([c - r, c - r, c + r, c + r], fill=INK + (255,))
    r2 = r - 3.5 * S
    tex = vgrad_tex(W, W, (255, 238, 80), YELLOW_LO)
    m = Image.new("L", (W, W), 0)
    ImageDraw.Draw(m).ellipse([c - r2, c - r2, c + r2, c + r2], fill=255)
    tex.putalpha(m)
    art = Image.alpha_composite(art, tex)
    dr = ImageDraw.Draw(art)
    # dashed inner ring, merch-style
    r3 = r2 - 5 * S
    for i in range(24):
        a0 = i * 15
        dr.arc([c - r3, c - r3, c + r3, c + r3], a0, a0 + 8, fill=INK + (255,), width=int(1.4 * S))
    text_img(dr, (c, c + 4 * S), str(value), ANTON, d * 0.46, INK + (255,))
    text_img(dr, (c, c - r2 * 0.56), "CR", MONO, d * 0.15, INK + (255,))
    return build_sticker(art, border=8, material="gloss", close=4, gloss_pos=0.3, seed=seed)


def kraft_note(lines, w=250, h=140, seed=9, curl=None, pen_size=27):
    S = SS
    P = 40 * S
    W, H = int(w * S) + 2 * P, int(h * S) + 2 * P
    body = Image.new("L", (W, H), 0)
    # slightly irregular die-cut tag: rounded rect with a notched corner + punch hole
    ImageDraw.Draw(body).rounded_rectangle([P, P, W - P, H - P], radius=18 * S, fill=255)
    hole = 9 * S
    ImageDraw.Draw(body).ellipse([P + 18 * S - hole, P + 20 * S - hole, P + 18 * S + hole, P + 20 * S + hole], fill=0)
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(MARKER, int(pen_size * S))
    rng = random.Random(seed)
    tl = Image.new("L", (W, H), 0)
    dt = ImageDraw.Draw(tl)
    lh = (h - 34) / len(lines)
    for i, line in enumerate(lines):
        y = P + 22 * S + (i + 0.5) * lh * S
        dt.text((P + 40 * S + rng.uniform(-3, 3) * S, y), line, font=font, fill=255, anchor="lm")
    tl = tl.rotate(-1.5, Image.BICUBIC)
    art = over(art, (24, 20, 26), tl)
    # rubber-stamped header strip
    dr = ImageDraw.Draw(art)
    text_img(dr, (W - P - 14 * S, P + 16 * S), "CELL//NOTE", MONO, 11, (90, 60, 34, 255), anchor="rm")
    art.putalpha(ImageChops.lighter(art.split()[3], Image.new("L", (W, H), 0)))
    return build_sticker(art, material="kraft", body=body, curl=curl, seed=seed)


def draw_portrait(w, h, seed=2):
    """Crisp vector operative portrait (hood, visor, bandana)."""
    S = SS
    W, H = int(w * S), int(h * S)
    im = Image.new("RGBA", (W, H), YELLOW + (255,))
    d = ImageDraw.Draw(im)
    # halftone falloff
    step = 8 * S
    for yy in range(0, H + step, step):
        for xx in range(0, W + step, step):
            t = (xx / W * 0.6 + yy / H * 0.8) - 0.55
            if t > 0:
                r = min(step * 0.48, t * step * 0.9)
                d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=YELLOW_LO + (255,))
    # sunburst wedges behind head
    cx, cy = 0.5 * W, 0.42 * H
    for i in range(12):
        a = i * math.pi / 6 + 0.1
        d.polygon([(cx, cy), (cx + 2 * W * math.cos(a), cy + 2 * W * math.sin(a)),
                   (cx + 2 * W * math.cos(a + 0.18), cy + 2 * W * math.sin(a + 0.18))], fill=(255, 238, 90, 255))
    def P(pts):
        return [(x * W, y * H) for x, y in pts]
    ow = int(3 * S)
    # shoulders / jacket
    d.polygon(P([(0.02, 1.02), (0.10, 0.82), (0.30, 0.72), (0.70, 0.72), (0.90, 0.82), (0.98, 1.02)]), fill=(38, 34, 44, 255), outline=INK + (255,), width=ow)
    d.line(P([(0.30, 0.74), (0.40, 1.0)]), fill=(90, 86, 100, 255), width=int(2 * S))
    d.line(P([(0.70, 0.74), (0.60, 1.0)]), fill=(90, 86, 100, 255), width=int(2 * S))
    # hood
    d.polygon(P([(0.22, 0.70), (0.20, 0.38), (0.28, 0.17), (0.50, 0.08), (0.72, 0.17), (0.80, 0.38), (0.78, 0.70), (0.64, 0.80), (0.36, 0.80)]), fill=CORAL + (255,), outline=INK + (255,), width=ow)
    d.polygon(P([(0.50, 0.08), (0.72, 0.17), (0.80, 0.38), (0.78, 0.70), (0.66, 0.66), (0.68, 0.30)]), fill=CORAL_LO + (255,))
    d.line(P([(0.50, 0.08), (0.72, 0.17), (0.80, 0.38), (0.78, 0.70), (0.64, 0.80)]), fill=INK + (255,), width=ow)
    # face
    face = P([(0.33, 0.30), (0.67, 0.30), (0.67, 0.53), (0.61, 0.66), (0.50, 0.71), (0.39, 0.66), (0.33, 0.53)])
    d.polygon(face, fill=(212, 154, 114, 255), outline=INK + (255,), width=ow)
    d.polygon(P([(0.52, 0.30), (0.67, 0.30), (0.67, 0.53), (0.61, 0.66), (0.52, 0.70)]), fill=(178, 118, 88, 255))
    # fringe
    d.polygon(P([(0.32, 0.36), (0.36, 0.25), (0.52, 0.20), (0.69, 0.27), (0.68, 0.37), (0.56, 0.30), (0.46, 0.34), (0.40, 0.31)]), fill=INK + (255,))
    # visor
    d.rounded_rectangle(P([(0.30, 0.39), (0.70, 0.48)])[0] + P([(0.30, 0.39), (0.70, 0.48)])[1], radius=int(5 * S), fill=TEAL + (255,), outline=INK + (255,), width=ow)
    d.polygon(P([(0.34, 0.405), (0.46, 0.405), (0.42, 0.425), (0.34, 0.425)]), fill=(235, 255, 252, 255))
    d.polygon(P([(0.56, 0.455), (0.67, 0.455), (0.67, 0.465), (0.55, 0.465)]), fill=(20, 120, 130, 255))
    # bandana
    band = P([(0.31, 0.53), (0.69, 0.53), (0.67, 0.64), (0.50, 0.76), (0.33, 0.64)])
    d.polygon(band, fill=(244, 240, 232, 255), outline=INK + (255,), width=ow)
    for i in range(5):
        x = 0.37 + i * 0.065
        d.polygon(P([(x, 0.56), (x + 0.03, 0.60), (x - 0.03, 0.60)]), fill=INK + (255,))
    # earpiece
    d.ellipse(P([(0.29, 0.47), (0.35, 0.53)])[0] + P([(0.29, 0.47), (0.35, 0.53)])[1], fill=INK + (255,))
    d.ellipse(P([(0.305, 0.485), (0.335, 0.515)])[0] + P([(0.305, 0.485), (0.335, 0.515)])[1], fill=CORAL + (255,))
    return im


def crew_card(seed=12, phase=0.1, curl=None):
    S = SS
    w, h = 200, 268
    P = 40 * S
    W, H = int(w * S) + 2 * P, int(h * S) + 2 * P
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    card = rrect_mask((W, H), [P, P, W - P, H - P], 16 * S)
    holo = holo_tex(W, H, seed=seed, phase=phase, sat=0.5)
    holo.putalpha(card)
    art = Image.alpha_composite(art, holo)
    d = ImageDraw.Draw(art)
    # portrait window
    px0, py0, pw = P + 14 * S, P + 34 * S, (w - 28) * S
    d.rounded_rectangle([px0 - 3 * S, py0 - 3 * S, px0 + pw + 3 * S, py0 + pw + 3 * S], radius=10 * S, fill=INK + (255,))
    por = draw_portrait(w - 28, w - 28, seed)
    pm = rrect_mask(por.size, [0, 0, por.size[0] - 1, por.size[1] - 1], 8 * S)
    por.putalpha(pm)
    art.alpha_composite(por, (int(px0), int(py0)))
    d = ImageDraw.Draw(art)
    text_img(d, (P + 16 * S, P + 17 * S), "CELL-9 // CREW", MONO, 15, INK + (255,), anchor="lm")
    text_img(d, (W - P - 16 * S, P + 17 * S), "07", ANTON, 18, INK + (255,), anchor="rm")
    # name label (printed white panel)
    ly = py0 + pw + 10 * S
    d.rounded_rectangle([px0 - 3 * S, ly, px0 + pw + 3 * S, ly + 44 * S], radius=6 * S, fill=INK + (255,))
    text_img(d, (px0 + 10 * S, ly + 22 * S), "VOSS", ANTON, 32, (250, 248, 240, 255), anchor="lm")
    text_img(d, (px0 + pw - 6 * S, ly + 14 * S), "OPERATIVE", MONO, 12, YELLOW + (255,), anchor="rm")
    text_img(d, (px0 + pw - 6 * S, ly + 31 * S), "SLICER  B+", MONO, 12, (200, 196, 206, 255), anchor="rm")
    return build_sticker(art, border=15, material="gloss", close=6, curl=curl, seed=seed, gloss_pos=0.3)


def heat_poster(heat=62, seed=31, curl=None, phase=0.3):
    S = SS
    w, h = 236, 300
    P = 40 * S
    W, H = int(w * S) + 2 * P, int(h * S) + 2 * P
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    d.rounded_rectangle([P, P, W - P, H - P], radius=14 * S, fill=INK + (255,))
    # hazard header
    hh = 44 * S
    hz = Image.new("RGBA", (W, H), YELLOW + (255,))
    hd = ImageDraw.Draw(hz)
    for x in range(-H, W + H, int(22 * S)):
        hd.polygon([(x, P), (x + 11 * S, P), (x + 11 * S - hh, P + hh), (x - hh, P + hh)], fill=INK + (255,))
    hm = rrect_mask((W, H), [P + 8 * S, P + 8 * S, W - P - 8 * S, P + 8 * S + hh], 8 * S)
    hz.putalpha(hm)
    art = Image.alpha_composite(art, hz)
    d = ImageDraw.Draw(art)
    # warning triangle badge over the stripes
    cx, cy = P + 42 * S, P + 30 * S
    tri = [(cx, cy - 26 * S), (cx + 28 * S, cy + 22 * S), (cx - 28 * S, cy + 22 * S)]
    d.polygon(tri, fill=INK + (255,))
    tri2 = [(cx, cy - 16 * S), (cx + 19 * S, cy + 16 * S), (cx - 19 * S, cy + 16 * S)]
    d.polygon(tri2, fill=CORAL + (255,))
    text_img(d, (cx, cy + 5 * S), "!", ANTON, 24, INK + (255,))
    # HEAT + number
    text_img(d, (P + 18 * S, P + 82 * S), "HEAT", ANTON, 40, YELLOW + (255,), anchor="lm")
    text_img(d, (W - P - 18 * S, P + 82 * S), "LVL", MONO, 16, (170, 164, 176, 255), anchor="rm")
    num = Image.new("L", (W, H), 0)
    text_img(ImageDraw.Draw(num), (W / 2, P + 160 * S), str(heat), ANTON, 118, 255)
    numtex = vgrad_tex(W, H, (255, 250, 236), (232, 226, 214))
    numtex.putalpha(num)
    art = Image.alpha_composite(art, numtex)
    d = ImageDraw.Draw(art)
    # meter
    segs = 10
    mx0, mx1, my = P + 18 * S, W - P - 18 * S, P + 218 * S
    sw = (mx1 - mx0) / segs
    for i in range(segs):
        fill = CORAL if i < heat // 10 else ((255, 150, 160) if i == heat // 10 else (64, 58, 70))
        d.polygon([(mx0 + i * sw + 3 * S, my), (mx0 + (i + 1) * sw, my), (mx0 + (i + 1) * sw - 3 * S, my + 14 * S), (mx0 + i * sw, my + 14 * S)], fill=fill + (255,))
    # FLAGGED band (coral) with ink type
    fy = P + 244 * S
    d.rounded_rectangle([P + 10 * S, fy, W - P - 10 * S, fy + 40 * S], radius=6 * S, fill=CORAL + (255,))
    text_img(d, (W / 2, fy + 21 * S), "FLAGGED", ANTON, 32, INK + (255,))
    # holo security seal
    sx, sy, sr = W - P - 30 * S, P + 128 * S, 20 * S
    seal = holo_tex(W, H, seed=seed + 3, phase=phase, sat=0.6)
    sm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sm).ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=255)
    seal.putalpha(sm)
    art = Image.alpha_composite(art, seal)
    d = ImageDraw.Draw(art)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], outline=INK + (255,), width=int(2 * S))
    text_img(d, (sx, sy + 1 * S), "C9", ANTON, 16, INK + (255,))
    return build_sticker(art, border=15, material="gloss", close=6, curl=curl, seed=seed, gloss_pos=0.28)


def them_warning(seed=41, curl=None):
    S = SS
    word = lettering(["THEM"], 50, [("grad", (255, 104, 116), CORAL_LO)], key_w=4, extrude=6, seed=seed,
                     jitter=3.5, track=1, pad=40)
    ww, wh = word.size
    T = 92 * S
    W, H = ww + T + 30 * S, max(wh, T + 80 * S)
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy = 40 * S + T / 2, H / 2
    d = ImageDraw.Draw(art)
    def tri(r):
        return [(cx, cy - r), (cx + r * 0.95, cy + r * 0.72), (cx - r * 0.95, cy + r * 0.72)]
    d.polygon(tri(T * 0.56), fill=INK + (255,))
    tm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(tm).polygon(tri(T * 0.42), fill=255)
    tex = vgrad_tex(W, H, (255, 236, 70), YELLOW_LO)
    tex.putalpha(tm.filter(ImageFilter.GaussianBlur(1.5 * S)).point(lambda v: 255 if v > 140 else 0))
    art = Image.alpha_composite(art, tex)
    d = ImageDraw.Draw(art)
    text_img(d, (cx, cy + 12 * S), "!", ANTON, 46, INK + (255,))
    art.alpha_composite(word, (int(T + 10 * S), int((H - wh) / 2)))
    return build_sticker(art, border=18, material="gloss", close=22, curl=curl, seed=seed, gloss_pos=0.34)
