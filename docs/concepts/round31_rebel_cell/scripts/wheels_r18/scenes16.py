"""Round 16 corp slice animations (drawn upright in screen space by slicelib; see skins.corp_texture).

Kept scenes come from scenes.py (round 15); the ones reworked after the round 15 review live here.
Each takes (s, t) with t in [0, 1) and loops seamlessly. Texture rows: Y(0) outer edge, Y(1) inner edge.
YC: the scene row placed at the screen point it belongs to (Meridian keeps its scenes above the barcode strip).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import f_num, f_ui, f_mono
import scenes as S0
from scenes import Sc, tri, ease, rot, rect_pts, W_, container, planet, meteor, impact

PAL = {k: dict(v) for k, v in S0.PAL.items()}
PAL["meridian"]["card"] = (236, 190, 124)
PAL["rebel_cell"] = dict(a=(255, 40, 52), dim=(110, 10, 18), hot=(255, 230, 230), paper=(255, 210, 210), ink=(20, 3, 6))
YC = {"meridian": 0.36}


def pill_capsule(d, x, y, L, r, ang, c1, c2, ink, u):
    """Simpler robust capsule: a thick line with round caps, two halves."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    p0 = (x - ux * (L / 2 - r), y - uy * (L / 2 - r))
    p1 = (x + ux * (L / 2 - r), y + uy * (L / 2 - r))
    for (pa, col) in ((p0, c1), (p1, c2)):
        d.ellipse([pa[0] - r - u, pa[1] - r - u, pa[0] + r + u, pa[1] + r + u], fill=ink + (255,))
    d.line([p0, p1], fill=ink + (255,), width=W_(2 * r + 2 * u))
    for (pa, col) in ((p0, c1), (p1, c2)):
        d.ellipse([pa[0] - r, pa[1] - r, pa[0] + r, pa[1] + r], fill=col + (255,))
        d.line([pa, (x, y)], fill=col + (255,), width=W_(2 * r))
    d.ellipse([p0[0] - r * 0.5, p0[1] - r * 0.7, p0[0] + r * 0.1, p0[1] - r * 0.1], fill=(255, 255, 255, 140))


# ================================================================== SOLACE
def sol_attack(s, t):  # syringe, needle point INSIDE the slice; liquid drips from the point
    u, d, P = s.u, s.d, s.P
    ang = 28  # pointing down-right
    cx, cy = s.cx - 55 * u, s.Y(0.60)
    L, R = 130 * u, 17 * u
    push = 22 * u * ease(tri(t))
    body = rect_pts(cx - L / 2, cy - R, cx + L / 2, cy + R)
    liquid = rect_pts(cx - L / 2 + 30 * u + push, cy - R + 4 * u, cx + L / 2 - 5 * u, cy + R - 4 * u)
    plunger = rect_pts(cx - L / 2 - 40 * u + push, cy - 4 * u, cx - L / 2 + 30 * u + push, cy + 4 * u)
    pad = rect_pts(cx - L / 2 - 46 * u + push, cy - R - 4 * u, cx - L / 2 - 38 * u + push, cy + R + 4 * u)
    head = rect_pts(cx - L / 2 + 24 * u + push, cy - R + 2 * u, cx - L / 2 + 31 * u + push, cy + R - 2 * u)
    needle = rect_pts(cx + L / 2, cy - 2.2 * u, cx + L / 2 + 46 * u, cy + 2.2 * u)
    for pts, col, a in ((plunger, (200, 230, 220), 255), (pad, (200, 230, 220), 255), (liquid, P["a"], 255),
                        (body, (200, 255, 235), 60), (head, (40, 60, 56), 255), (needle, (235, 245, 245), 255)):
        d.polygon(rot(pts, ang, cx, cy), fill=col + (a,), outline=(230, 255, 245, 255) if a == 60 else P["ink"] + (255,))
    s.g.polygon(rot(liquid, ang, cx, cy), fill=P["a"] + (200,))
    for k in range(4):
        x = cx - L / 2 + 44 * u + k * 22 * u
        d.line(rot([(x, cy - R), (x, cy - R + 8 * u)], ang, cx, cy), fill=P["ink"] + (255,), width=W_(1.5 * u))
    tip = rot([(cx + L / 2 + 46 * u, cy)], ang, cx, cy)[0]
    # a bead swells at the point, then drops fall from it (stream of 3, seamless)
    bead = 3 * u + 4 * u * ((t * 3) % 1.0)
    d.ellipse([tip[0] - bead, tip[1] - bead * 0.6, tip[0] + bead, tip[1] + bead * 1.3], fill=P["a"] + (255,))
    for k in range(3):
        ph = (t * 3 + k / 3) % 1.0 if k else (t * 3) % 1.0
        ph = ((t + k / 3) % 1.0)
        y = tip[1] + 8 * u + ph * (s.Y(0.95) - tip[1])
        r = 4.5 * u
        d.ellipse([tip[0] - r, y - r * 1.5, tip[0] + r, y + r], fill=P["a"] + (255,))
        s.g.ellipse([tip[0] - r * 1.6, y - r * 1.6, tip[0] + r * 1.6, y + r * 1.6], fill=P["a"] + (200,))
    d.ellipse([tip[0] - 22 * u, s.Y(0.95) - 5 * u, tip[0] + 22 * u, s.Y(0.95) + 5 * u], fill=P["a"] + (150,))


def sol_defend(s, t):  # a beaker with a spout, tilted ABOVE a test tube, pours straight down
    u, d, P = s.u, s.d, s.P
    vx = s.cx + 46 * u
    tube_top, tube_bot = s.Y(0.66), s.Y(0.99)
    tw = 26 * u
    # test tube: straight walls, round bottom, a lip
    d.rounded_rectangle([vx - tw / 2, tube_top, vx + tw / 2, tube_bot], radius=W_(tw / 2), fill=(200, 255, 235, 50), outline=P["glass"] + (255,), width=W_(2.5 * u))
    d.rectangle([vx - tw / 2 - 5 * u, tube_top - 4 * u, vx + tw / 2 + 5 * u, tube_top + 3 * u], fill=(225, 245, 240, 255), outline=P["ink"] + (255,))
    lvl = tube_bot - 8 * u - (tube_bot - tube_top - 20 * u) * (0.1 + 0.8 * t)
    d.rounded_rectangle([vx - tw / 2 + 4 * u, lvl, vx + tw / 2 - 4 * u, tube_bot - 4 * u], radius=W_(tw / 2 - 4 * u), fill=P["a"] + (240,))
    s.g.rectangle([vx - tw / 2, lvl, vx + tw / 2, tube_bot], fill=P["a"] + (120,))
    for k in range(3):
        ph = (t * 2 + k / 3) % 1.0
        yy = tube_bot - 10 * u - ph * (tube_bot - lvl - 6 * u)
        d.ellipse([vx - 3 * u + (k - 1) * 5 * u, yy - 3 * u, vx + 3 * u + (k - 1) * 5 * u, yy + 3 * u], outline=(225, 255, 240, 220))
    # beaker above, tilted so its spout sits right over the tube mouth
    tilt = 52 + 6 * math.sin(2 * math.pi * t)
    bw, bh = 56 * u, 64 * u
    spout = (vx, s.Y(0.56))
    # beaker drawn in its own frame with the spout at the top-right corner, then rotated about the spout
    bx0, by0 = spout[0] - bw, spout[1]
    body = [(bx0, by0), (bx0 + bw, by0), (bx0 + bw - 4 * u, by0 + bh), (bx0 + 4 * u, by0 + bh)]
    lip = [(bx0 + bw - 2 * u, by0 - 2 * u), (bx0 + bw + 12 * u, by0 - 8 * u), (bx0 + bw + 2 * u, by0 + 8 * u)]
    liq = [(bx0 + 6 * u, by0 + bh * 0.35), (bx0 + bw - 6 * u, by0 + bh * 0.35), (bx0 + bw - 7 * u, by0 + bh - 4 * u), (bx0 + 7 * u, by0 + bh - 4 * u)]
    piv = spout
    d.polygon(rot(liq, tilt, *piv), fill=P["a"] + (230,))
    d.polygon(rot(body, tilt, *piv), fill=(200, 255, 235, 70), outline=(230, 255, 245, 255), width=W_(2.5 * u))
    d.polygon(rot(lip, tilt, *piv), fill=(220, 250, 240, 255), outline=P["ink"] + (255,))
    for k in range(3):
        yk = by0 + bh * (0.3 + 0.2 * k)
        d.line(rot([(bx0 + 6 * u, yk), (bx0 + 22 * u, yk)], tilt, *piv), fill=(230, 255, 245, 200), width=W_(1.5 * u))
    sp = rot([(bx0 + bw + 10 * u, by0 - 6 * u)], tilt, *piv)[0]
    # straight vertical stream from the spout into the tube
    wob = 1 + 0.2 * math.sin(t * 2 * math.pi * 4)
    s.g.line([(sp[0], sp[1]), (sp[0], tube_top)], fill=P["a"] + (255,), width=W_(9 * u))
    d.line([(sp[0], sp[1]), (sp[0], lvl)], fill=P["a"] + (255,), width=W_(4 * u * wob))


def sol_growth(s, t):  # GROWTH (heal): a round cell splits into two round cells that drift well apart
    u, d, P = s.u, s.d, s.P
    cx, cy = s.cx, s.Y(0.62)
    k = ease(min(1.0, t / 0.8))
    sep = 130 * u * k
    r0 = 46 * u
    r = r0 * (1 - 0.22 * min(1, k * 1.5))
    if k < 0.35:  # one round cell elongating, a pinch line forms
        q = k / 0.35
        for sx in (-1, 1):
            x = cx + sx * sep / 2
            d.ellipse([x - r, cy - r, x + r, cy + r], fill=(40, 170, 110, 120), outline=P["a"] + (255,), width=W_(3 * u))
        d.line([(cx, cy - r * (1 - q * 0.8)), (cx, cy + r * (1 - q * 0.8))], fill=P["a"] + (int(255 * q),), width=W_(2 * u))
    else:  # two separate round cells
        for sx in (-1, 1):
            x = cx + sx * sep / 2
            s.g.ellipse([x - r, cy - r, x + r, cy + r], outline=P["a"] + (180,), width=W_(8 * u))
            d.ellipse([x - r, cy - r, x + r, cy + r], fill=(40, 170, 110, 120), outline=P["a"] + (255,), width=W_(3 * u))
    for sx in ((-1, 1) if k > 0.15 else (0,)):
        x = cx + sx * sep / 2 * (1 if k > 0.15 else 0)
        rn = 13 * u
        d.ellipse([x - rn, cy - rn, x + rn, cy + rn], fill=(20, 90, 60, 255), outline=P["a"] + (255,), width=W_(2 * u))
    for j in range(6):
        a = j * 60 + t * 120
        rr = r0 * 1.9
        x, y = cx + rr * 1.5 * math.cos(math.radians(a)), cy + rr * 0.8 * math.sin(math.radians(a))
        al = int(220 * tri(t * 2 + j / 6))
        d.line([(x - 5 * u, y), (x + 5 * u, y)], fill=(220, 255, 235, al), width=W_(2 * u))
        d.line([(x, y - 5 * u), (x, y + 5 * u)], fill=(220, 255, 235, al), width=W_(2 * u))


def sol_dose(s, t):  # a static tilted pill bottle; capsules keep falling out of it
    u, d, P = s.u, s.d, s.P
    bx, by = s.cx - 50 * u, s.Y(0.60)
    tilt = 118
    body = rect_pts(bx - 26 * u, by - 40 * u, bx + 26 * u, by + 40 * u)
    label = rect_pts(bx - 26 * u, by - 14 * u, bx + 26 * u, by + 20 * u)
    for pts, col in ((body, (230, 160, 60)), (label, (240, 250, 246))):
        d.polygon(rot(pts, tilt, bx, by), fill=col + (235,), outline=P["ink"] + (255,))
    lc = rot([(bx, by + 3 * u)], tilt, bx, by)[0]
    d.text((lc[0] - 10 * u, lc[1] - 8 * u), "Rx", font=f_num(int(14 * u)), fill=P["hot"] + (255,))
    mouth = rot([(bx, by - 46 * u)], tilt, bx, by)[0]
    rng = np.random.default_rng(3)
    n = 6
    for k in range(n):
        ph = (t + k / n) % 1.0
        vx = (55 + 30 * ((k * 7) % 5) / 4) * u
        x = mouth[0] + vx * ph
        y = mouth[1] + (s.Y(1.05) - mouth[1]) * ph * ph
        spin = 140 + 360 * ph + k * 47
        c1, c2 = ((P["hot"], (250, 250, 250)) if k % 2 else (P["a"], (250, 250, 250)))
        pill_capsule(d, x, y, 30 * u, 6.5 * u, spin, c1, c2, P["ink"], u)


# ================================================================== MERIDIAN (everything above the barcode strip)
def mer_attack(s, t):  # crates ride the rollers (moved above the barcode)
    u, d, P = s.u, s.d, s.P
    yb = s.Y(0.62)
    d.rectangle([0, yb, s.W, yb + 12 * u], fill=(36, 30, 26, 255))
    per = 26 * u
    for k in range(-1, int(s.W / per) + 2):
        x = k * per + 13 * u
        d.ellipse([x - 8 * u, yb + 1 * u, x + 8 * u, yb + 17 * u], fill=(90, 86, 84, 255), outline=(20, 16, 14, 255), width=W_(u))
        a = 2 * math.pi * (t * 2 + k * 0.1)
        d.line([(x, yb + 9 * u), (x + 6 * u * math.cos(a), yb + 9 * u + 6 * u * math.sin(a))], fill=(20, 16, 14, 255), width=W_(2 * u))
    gap = 110 * u
    for k in range(-1, int(s.W / gap) + 2):
        x = (k + t) * gap
        w, h = 66 * u, 52 * u
        d.rectangle([x, yb - h, x + w, yb], fill=P["card"] + (255,), outline=P["ink"] + (255,), width=W_(2 * u))
        d.rectangle([x + w * 0.42, yb - h, x + w * 0.58, yb], fill=(212, 190, 140, 255))
        d.text((x + 5 * u, yb - h + 5 * u), "MRD", font=f_num(int(14 * u)), fill=P["ink"] + (255,))
        for m in range(3):
            d.line([(x - (10 + m * 14) * u, yb - (12 + m * 13) * u), (x - (2 + m * 14) * u, yb - (12 + m * 13) * u)], fill=P["a"] + (200,), width=W_(2 * u))


def stamp_img(text, u, col, size=34, ang=-12):
    f = f_num(int(size * u))
    tw = f.getlength(text)
    st = Image.new("RGBA", (int(tw + 22 * u), int(size * 1.4 * u)), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([0, 0, st.width - 1, st.height - 1], radius=W_(5 * u), outline=col + (255,), width=W_(4 * u))
    sd.text((11 * u, 2 * u), text, font=f, fill=col + (255,))
    return st.rotate(ang, expand=True, resample=Image.BICUBIC)


def mer_crit(s, t):  # just a PRIORITY stamp slamming down (no second barcode)
    u = s.u
    cy = s.Y(0.60)
    if t < 0.30:
        k = ease(t / 0.30)
        sc, a = 2.2 - 1.2 * k, int(255 * k)
    elif t < 0.80:
        sc, a = 1.0, 255
    else:
        sc, a = 1.0, int(255 * (1 - (t - 0.8) / 0.2))
    st = stamp_img("PRIORITY", u, s.P["hot"], 38)
    st = st.resize((int(st.width * sc), int(st.height * sc)))
    if a < 255:
        st.putalpha(st.split()[3].point(lambda v: int(v * a / 255)))
    s.im.alpha_composite(st, (int(s.cx - st.width / 2), int(cy - st.height / 2)))
    if 0.28 < t < 0.45:  # ink splash ring on impact
        k = (t - 0.28) / 0.17
        r = (60 + 60 * k) * u
        s.g.ellipse([s.cx - r, cy - r * 0.45, s.cx + r, cy + r * 0.45], outline=s.P["hot"] + (int(200 * (1 - k)),), width=W_(6 * u))


def mer_defend(s, t):  # the crane brings TWO containers (from the outer edge) onto a wall on the inner side
    u, d, P = s.u, s.d, s.P
    cols = [(196, 92, 30), (60, 120, 170), (200, 150, 40), (150, 60, 50)]
    ch, cw = 26 * u, 64 * u
    wy = s.Y(0.72) - ch  # top course of the wall (bottom of the wall sits just above the barcode)
    for r in range(2):
        y = wy + r * ch
        off = (r % 2) * cw / 2
        for k in range(-2, 4):
            x = s.cx - 1.5 * cw + k * cw - off
            container(d, x, y, cw - 2 * u, ch - 2 * u, cols[(k + r) % 4], P["ink"], u)
    jy = s.Y(0.02)
    d.rectangle([0, jy, s.W, jy + 10 * u], fill=P["crane"] + (255,), outline=P["ink"] + (255,), width=W_(2 * u))
    for k in np.arange(0, s.W, 14 * u):
        d.line([(k, jy), (k + 14 * u, jy + 10 * u)], fill=P["ink"] + (255,), width=W_(2 * u))
    slots = [s.cx - cw * 0.5, s.cx + cw * 0.5]
    land = wy - ch
    for j, sx in enumerate(slots):  # container j arrives during its half of the loop and then stays
        q = (t - j * 0.5) / 0.5
        placed = [s for s in range(2) if (t >= (s + 1) * 0.5 - 0.1)]
        if 0 <= q < 1:
            k = ease(min(1, q / 0.8))
            cy = s.Y(0.10) + (land - s.Y(0.10)) * k
            tx = sx + cw / 2
            d.rectangle([tx - 14 * u, jy + 10 * u, tx + 14 * u, jy + 18 * u], fill=(70, 70, 76, 255))
            d.line([(tx - 8 * u, jy + 18 * u), (tx - cw * 0.35, cy)], fill=(30, 30, 34, 255), width=W_(1.5 * u))
            d.line([(tx + 8 * u, jy + 18 * u), (tx + cw * 0.35, cy)], fill=(30, 30, 34, 255), width=W_(1.5 * u))
            container(d, sx, cy, cw - 2 * u, ch - 2 * u, (230, 120, 30) if j == 0 else (70, 150, 200), P["ink"], u, "MRDU")
        elif q >= 1:
            container(d, sx, land, cw - 2 * u, ch - 2 * u, (230, 120, 30) if j == 0 else (70, 150, 200), P["ink"], u, "MRDU")


def box(d, P, u, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=P["card"] + (255,), outline=P["ink"] + (255,), width=W_(3.5 * u))
    d.rectangle([x0 + (x1 - x0) * 0.42, y0, x0 + (x1 - x0) * 0.58, y1], fill=(206, 160, 100, 255))
    d.text((x0 + 8 * u, y1 - 18 * u), "THIS SIDE UP ^^", font=f_mono(int(8 * u)), fill=P["ink"] + (255,))


def flaps(d, P, u, cx, y0, half, k):
    """k = 0 open (flaps up), 1 closed (flat)."""
    for side in (-1, 1):
        ang = (1 - k) * 100
        hx = cx + side * half
        tipx = hx - side * half * math.cos(math.radians(ang))
        tipy = y0 - half * math.sin(math.radians(ang))
        d.polygon([(hx, y0), (tipx, tipy), (tipx, tipy - 5 * u), (hx, y0 - 5 * u)], fill=(206, 146, 84, 255), outline=P["ink"] + (255,))


def mer_shield(s, t):  # the lid folds shut, then a THIN tape is drawn across, starting on the box
    u, d, P = s.u, s.d, s.P
    half = 64 * u
    x0, x1 = s.cx - half, s.cx + half
    y0, y1 = s.Y(0.30), s.Y(0.72)
    box(d, P, u, x0, y0, x1, y1)
    flaps(d, P, u, s.cx, y0, half, ease(min(1, t / 0.4)))
    if t > 0.45:
        k = ease(min(1, (t - 0.45) / 0.4))
        xe = x0 + 4 * u + (x1 - x0 - 8 * u) * k
        d.rectangle([x0 + 4 * u, y0 - 6 * u, xe, y0 + 0 * u], fill=(236, 210, 150, 240))
        d.line([(x0 + 4 * u, y0 - 6 * u), (x0 + 4 * u, y0 + 10 * u)], fill=(236, 210, 150, 240), width=W_(6 * u))
        if k < 1:
            d.ellipse([xe - 7 * u, y0 - 16 * u, xe + 7 * u, y0 - 2 * u], fill=(110, 90, 60, 255), outline=P["ink"] + (255,))


def mer_judgement(s, t):  # the gavel swings down from the TOP onto a block (barcode untouched)
    u, d, P = s.u, s.d, s.P
    bx, by = s.cx, s.Y(0.62)
    d.rounded_rectangle([bx - 54 * u, by, bx + 54 * u, by + 22 * u], radius=W_(5 * u), fill=(110, 64, 30, 255), outline=P["ink"] + (255,), width=W_(2 * u))
    d.rectangle([bx - 44 * u, by + 5 * u, bx + 44 * u, by + 8 * u], fill=(160, 100, 50, 255))
    piv = (bx, s.Y(-0.25))  # pivot above the screen: the gavel swings in from the top
    if t < 0.40:
        ang = 70 * (1 - ease(t / 0.40) ** 2)
    elif t < 0.62:
        ang = 0.0
    else:
        ang = 70 * ease((t - 0.62) / 0.38)
    hl = by - 4 * u - piv[1]
    handle = rect_pts(bx - 5 * u, piv[1], bx + 5 * u, by - 40 * u)
    head = rect_pts(bx - 36 * u, by - 46 * u, bx + 36 * u, by - 2 * u)
    for pts, col in ((handle, (120, 74, 36)), (head, (140, 86, 40))):
        d.polygon(rot(pts, ang, *piv), fill=col + (255,), outline=P["ink"] + (255,))
    for xb in (-24, 24):
        d.polygon(rot(rect_pts(bx + (xb - 3) * u, by - 46 * u, bx + (xb + 3) * u, by - 2 * u), ang, *piv), fill=(220, 180, 90, 255))
    if 0.40 <= t < 0.80:
        k = (t - 0.40) / 0.40
        a = int(255 * (1 - k))
        for sc in (1.0, 0.6):
            rx, ry = (30 + 150 * k * sc) * u, (8 + 26 * k * sc) * u
            s.g.ellipse([bx - rx, by - ry, bx + rx, by + ry], outline=P["a"] + (a,), width=W_(10 * u))
            d.ellipse([bx - rx, by - ry, bx + rx, by + ry], outline=(255, 230, 190, a), width=W_(3 * u))
        if k < 0.3:
            s.g.ellipse([bx - 50 * u, by - 30 * u, bx + 50 * u, by + 20 * u], fill=(255, 240, 200, 255))
        d.text((bx + 60 * u, by - 34 * u), "RAM -3", font=f_num(int(20 * u)), fill=P["hot"] + (a,))


def mer_miss(s, t):  # reverse of SHIELD (no roller): the tape peels off, the box opens, sides fall: empty
    u, d, P = s.u, s.d, s.P
    half = 64 * u
    x0, x1 = s.cx - half, s.cx + half
    y0, y1 = s.Y(0.30), s.Y(0.72)
    if t < 0.55:
        box(d, P, u, x0, y0, x1, y1)
        flaps(d, P, u, s.cx, y0, half, 1 - ease(max(0, (t - 0.30) / 0.25)))
        if t < 0.30:  # tape peels back from the right, curling up
            k = ease(t / 0.30)
            xe = x1 - 4 * u - (x1 - x0 - 8 * u) * k
            d.rectangle([x0 + 4 * u, y0 - 6 * u, xe, y0], fill=(236, 210, 150, 240))
            d.line([(xe, y0 - 3 * u), (xe + 18 * u, y0 - 26 * u * (0.4 + k))], fill=(236, 210, 150, 240), width=W_(6 * u))
    else:  # walls fall outward and flatten (seen from slightly above): an empty floor remains
        k = ease(min(1, (t - 0.55) / 0.2))
        h = y1 - y0
        fh = h * (1 - 0.72 * k)  # walls shorten as they tip away
        floor = [x0, y1 - h * 0.28, x1, y1]
        d.rectangle(floor, fill=(150, 104, 58, 255), outline=P["ink"] + (255,), width=W_(2 * u))
        for side in (-1, 1):  # side walls swing out and lie flat beside the floor
            w = h * k * 0.9
            xa = x0 - w if side < 0 else x1
            xb = x0 if side < 0 else x1 + w
            if w > 2 * u:
                d.polygon([(xa, y1 - h * 0.28), (xb, y1 - h * 0.28), (xb, y1), (xa, y1)], fill=P["card"] + (255,), outline=P["ink"] + (255,))
        if k < 1:  # back wall still tipping
            d.rectangle([x0, y1 - h * 0.28 - fh * (1 - k), x1, y1 - h * 0.28], fill=P["card"] + (255,), outline=P["ink"] + (255,))
        if k >= 1:
            f = f_num(int(20 * u))
            d.text((s.cx - f.getlength("EMPTY") / 2, y1 - h * 0.28 + 2 * u), "EMPTY", font=f, fill=(255, 236, 200, 240),
                   stroke_width=W_(2 * u), stroke_fill=(30, 20, 10))
            for j in range(6):  # dust
                dx = (t - 0.75) * 300 * u * (1 if j % 2 else -1) * (0.4 + j * 0.1)
                d.ellipse([s.cx + dx - 5 * u, y1 - h * 0.3 - j * 3 * u, s.cx + dx + 5 * u, y1 - h * 0.3 - j * 3 * u + 8 * u], fill=(220, 200, 170, 120))

# ================================================================== HALCYON
def hal_attack_a(s, t):  # A: a police baton strikes down (from the top), impact star
    u, d, P = s.u, s.d, s.P
    tx, ty = s.cx - 30 * u, s.Y(0.74)
    piv = (s.cx + 70 * u, s.Y(0.06))
    if t < 0.35:
        ang = -65 * (1 - ease(t / 0.35) ** 2)
    elif t < 0.6:
        ang = 0.0
    else:
        ang = -65 * ease((t - 0.6) / 0.4)
    L = math.hypot(tx - piv[0], ty - piv[1])
    a0 = math.degrees(math.atan2(ty - piv[1], tx - piv[0]))
    baton = rect_pts(piv[0], piv[1] - 7 * u, piv[0] + L, piv[1] + 7 * u)
    bp = rot(baton, a0 + ang, *piv)
    s.g.polygon(bp, fill=(200, 180, 255, 200))
    d.polygon(bp, fill=(26, 24, 36, 255), outline=(230, 220, 255, 255))
    hl = rot(rect_pts(piv[0] + 60 * u, piv[1] - 4 * u, piv[0] + L - 8 * u, piv[1] - 2 * u), a0 + ang, *piv)
    d.polygon(hl, fill=(200, 196, 230, 255))
    grip = rot(rect_pts(piv[0] + 10 * u, piv[1] - 9 * u, piv[0] + 60 * u, piv[1] + 9 * u), a0 + ang, *piv)
    d.polygon(grip, fill=(60, 60, 70, 255))
    side = rot(rect_pts(piv[0] + 40 * u, piv[1] + 7 * u, piv[0] + 46 * u, piv[1] + 26 * u), a0 + ang, *piv)
    d.polygon(side, fill=(30, 30, 40, 255), outline=(150, 150, 170, 255))
    if 0.35 <= t < 0.65:
        k = (t - 0.35) / 0.3
        r = (18 + 40 * k) * u
        pts = []
        for j in range(16):
            rr = r if j % 2 == 0 else r * 0.45
            pts.append((tx + rr * math.cos(math.radians(j * 22.5)), ty + rr * math.sin(math.radians(j * 22.5))))
        s.g.polygon(pts, fill=P["gold"] + (int(255 * (1 - k)),))
        d.polygon(pts, fill=(255, 230, 160, int(255 * (1 - k))))


def hal_attack_b(s, t):  # B: a patrol drone's spotlight sweeps, then LOCKS ON (reticle closes)
    u, d, P = s.u, s.d, s.P
    dx, dy = s.cx + 70 * math.sin(2 * math.pi * t) * u * (1 if t < 0.5 else 0.2), s.Y(0.14)
    tgt = (s.cx - 30 * u, s.Y(0.80))
    if t < 0.5:
        sx = s.cx + 110 * u * math.sin(2 * math.pi * t * 1.5)
    else:
        sx = tgt[0]
    cone = [(dx - 6 * u, dy + 8 * u), (dx + 6 * u, dy + 8 * u), (sx + 40 * u, tgt[1]), (sx - 40 * u, tgt[1])]
    s.g.polygon(cone, fill=(255, 240, 180, 150))
    d.polygon(cone, fill=(255, 240, 200, 70))
    d.ellipse([sx - 40 * u, tgt[1] - 10 * u, sx + 40 * u, tgt[1] + 10 * u], fill=(255, 245, 210, 140))
    d.rounded_rectangle([dx - 22 * u, dy - 8 * u, dx + 22 * u, dy + 8 * u], radius=W_(6 * u), fill=(50, 40, 80, 255), outline=P["paper"] + (255,), width=W_(2 * u))
    for sxp in (-1, 1):
        d.line([(dx + sxp * 22 * u, dy - 4 * u), (dx + sxp * 40 * u, dy - 12 * u)], fill=P["paper"] + (255,), width=W_(2 * u))
        d.ellipse([dx + sxp * 40 * u - 12 * u, dy - 16 * u, dx + sxp * 40 * u + 12 * u, dy - 8 * u], outline=P["paper"] + (200,), width=W_(1.5 * u))
    on = int(t * 10) % 2
    d.ellipse([dx - 4 * u, dy - 4 * u, dx + 4 * u, dy + 4 * u], fill=(P["hot"] if on else P["blue"]) + (255,))
    # silhouette
    hx, hy = tgt[0], tgt[1] - 30 * u
    d.ellipse([hx - 9 * u, hy - 9 * u, hx + 9 * u, hy + 9 * u], fill=(20, 12, 30, 255))
    d.rounded_rectangle([hx - 14 * u, hy + 10 * u, hx + 14 * u, tgt[1]], radius=W_(6 * u), fill=(20, 12, 30, 255))
    if t >= 0.5:
        k = ease(min(1, (t - 0.5) / 0.3))
        r = (60 - 32 * k) * u
        col = P["hot"] if k >= 1 else P["gold"]
        d.ellipse([hx - r, hy + 6 * u - r, hx + r, hy + 6 * u + r], outline=col + (255,), width=W_(3 * u))
        for a in (0, 90, 180, 270):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line([(hx + ca * r * 0.6, hy + 6 * u + sa * r * 0.6), (hx + ca * r * 1.3, hy + 6 * u + sa * r * 1.3)], fill=col + (255,), width=W_(3 * u))
        if k >= 1:
            d.text((hx + 36 * u, hy - 20 * u), "LOCKED", font=f_num(int(16 * u)), fill=P["hot"] + (255,))


def hal_attack_c(s, t):  # C: an arrest WARRANT with a mugshot gets stamped WANTED
    u, d, P = s.u, s.d, s.P
    px0, px1 = s.cx - 80 * u, s.cx + 80 * u
    py0, py1 = s.Y(0.30), s.Y(1.02)
    d.rectangle([px0, py0, px1, py1], fill=(196, 188, 170, 255), outline=P["ink"] + (255,))
    d.text((px0 + 8 * u, py0 + 4 * u), "ARREST WARRANT", font=f_num(int(13 * u)), fill=(40, 30, 30, 255))
    d.rectangle([px0 + 10 * u, py0 + 24 * u, px0 + 60 * u, py0 + 84 * u], fill=(120, 116, 110, 255), outline=(40, 30, 30, 255))
    d.ellipse([px0 + 24 * u, py0 + 32 * u, px0 + 46 * u, py0 + 56 * u], fill=(60, 56, 54, 255))
    d.rectangle([px0 + 18 * u, py0 + 58 * u, px0 + 52 * u, py0 + 84 * u], fill=(60, 56, 54, 255))
    for k in range(5):
        y = py0 + 28 * u + k * 12 * u
        d.line([(px0 + 70 * u, y), (px1 - 10 * u, y)], fill=(110, 100, 100, 255), width=W_(2 * u))
    if t >= 0.4:
        a = 255 if t < 0.85 else int(255 * (1 - (t - 0.85) / 0.15))
        st = stamp_img("WANTED", u, P["hot"], 34, ang=12)
        st.putalpha(st.split()[3].point(lambda v: int(v * a / 255)))
        s.im.alpha_composite(st, (int(s.cx - st.width / 2 + 10 * u), int(py0 + 60 * u - st.height / 2)))
    if t < 0.4:
        k = ease(t / 0.4)
        sy = s.Y(-0.2) + (py0 + 30 * u - s.Y(-0.2)) * k
        d.rectangle([s.cx - 36 * u, sy + 30 * u, s.cx + 36 * u, sy + 46 * u], fill=(120, 40, 40, 255), outline=P["ink"] + (255,))
        d.rectangle([s.cx - 9 * u, sy - 10 * u, s.cx + 9 * u, sy + 30 * u], fill=(90, 70, 50, 255))


def hal_crit(s, t):  # the jail door closes (no CLANG, no motion lines)
    u, d, P = s.u, s.d, s.P
    y0, y1 = s.Y(0.02), s.Y(0.98)
    frame_x = s.cx + 20 * u
    k = ease(min(1, t / 0.55))
    if t > 0.85:
        k = 1 - ease((t - 0.85) / 0.15) * 0.0
    dx = -170 * u * (1 - k)
    for xb in np.arange(frame_x, s.W, 22 * u):
        d.rectangle([xb, y0, xb + 7 * u, y1], fill=P["steel"] + (230,), outline=P["ink"] + (255,))
    door_x0 = frame_x - 160 * u + dx
    for xb in np.arange(door_x0, door_x0 + 160 * u, 22 * u):
        d.rectangle([xb, y0, xb + 8 * u, y1], fill=(236, 230, 248, 255), outline=P["ink"] + (255,))
    for yy in (s.Y(0.18), s.Y(0.82)):
        d.rectangle([door_x0 - 4 * u, yy, door_x0 + 164 * u, yy + 12 * u], fill=(206, 196, 226, 255), outline=P["ink"] + (255,))
    d.rectangle([door_x0 + 130 * u, s.Y(0.5) - 14 * u, door_x0 + 158 * u, s.Y(0.5) + 14 * u], fill=P["gold"] + (255,), outline=P["ink"] + (255,))


def tape_band(s, x0, y0, x1, y1, w, t, text="POLICE LINE  DO NOT CROSS  "):
    u = s.u
    L = math.hypot(x1 - x0, y1 - y0)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    band = Image.new("RGBA", (int(L), int(w)), (255, 210, 40, 255))
    bd = ImageDraw.Draw(band)
    f = f_num(int(w * 0.72))
    off = -((t * 200 * u) % (f.getlength(text)))
    x = off
    while x < L:
        bd.text((x, w * 0.08), text, font=f, fill=(20, 16, 10, 255))
        x += f.getlength(text)
    bd.line([(0, 1), (L, 1)], fill=(20, 16, 10, 255), width=W_(1.5 * u))
    bd.line([(0, w - 2), (L, w - 2)], fill=(20, 16, 10, 255), width=W_(1.5 * u))
    band = band.rotate(-ang, expand=True, resample=Image.BICUBIC)
    s.im.alpha_composite(band, (int((x0 + x1) / 2 - band.width / 2), int((y0 + y1) / 2 - band.height / 2)))


def hal_defend(s, t):  # police tape criss-crosses through the slice (strips slide in, text scrolls)
    u = s.u
    k1 = ease(min(1, t / 0.3))
    k2 = ease(min(1, max(0, (t - 0.2) / 0.3)))
    k3 = ease(min(1, max(0, (t - 0.4) / 0.3)))
    w = 20 * u
    if k1 > 0:
        tape_band(s, s.cx - 220 * u, s.Y(0.25), s.cx - 220 * u + 440 * u * k1, s.Y(0.25) + s.Y(0.6) * k1, w, t)
    if k2 > 0:
        tape_band(s, s.cx + 220 * u, s.Y(0.25), s.cx + 220 * u - 440 * u * k2, s.Y(0.25) + s.Y(0.6) * k2, w, t + 0.3)
    if k3 > 0:
        tape_band(s, s.cx - 240 * u, s.Y(0.78), s.cx - 240 * u + 480 * u * k3, s.Y(0.78), w, t + 0.6)


def hal_shield(s, t):  # a rock thrown from the TOP bounces off a riot shield held across the inner side
    u, d, P = s.u, s.d, s.P
    sy0, sy1 = s.Y(0.62), s.Y(0.80)
    d.rounded_rectangle([s.cx - 110 * u, sy0, s.cx + 110 * u, sy1], radius=W_(14 * u), fill=(200, 196, 255, 90), outline=P["steel"] + (255,), width=W_(4 * u))
    d.rectangle([s.cx - 40 * u, sy0 + 10 * u, s.cx + 40 * u, sy0 + 24 * u], fill=P["ink"] + (230,))
    d.text((s.cx - 34 * u, sy0 + 10 * u), "POLICE", font=f_num(int(13 * u)), fill=(255, 255, 255, 255))
    hit = (s.cx + 20 * u, sy0 - 6 * u)
    if t < 0.5:
        q = t / 0.5
        x = s.cx - 60 * u + (hit[0] - (s.cx - 60 * u)) * q
        y = s.Y(0.02) + (hit[1] - s.Y(0.02)) * q * q
    else:
        q = (t - 0.5) / 0.5
        x = hit[0] + 150 * u * q
        y = hit[1] - 110 * u * q + 160 * u * q * q
    rp = [(x + 12 * u * math.cos(math.radians(a)) * (1 + 0.2 * (a % 3)), y + 10 * u * math.sin(math.radians(a))) for a in range(0, 360, 50)]
    d.polygon(rot(rp, t * 600, x, y), fill=(130, 120, 110, 255), outline=P["ink"] + (255,))
    if 0.47 < t < 0.62:
        for a in range(200, 341, 28):
            d.line([hit, (hit[0] + 26 * u * math.cos(math.radians(a)), hit[1] + 26 * u * math.sin(math.radians(a)))], fill=P["gold"] + (255,), width=W_(3 * u))


# ================================================================== ORBITAL
def orb_flare(s, t):  # the flare loop erupts, flies OFF screen, and a new one forms for the next loop
    u, d, P = s.u, s.d, s.P
    cx, cy, r = s.cx, s.Y(0.86), 58 * u
    s.g.ellipse([cx - r * 2, cy - r * 2, cx + r * 2, cy + r * 2], fill=(255, 200, 80, 255))
    for k in range(18):
        a = math.radians(k * 20 + t * 40)
        L = r * (1.4 + 0.35 * ((k % 2) + tri(t * 2 + k / 18)))
        d.line([(cx + r * math.cos(a), cy + r * math.sin(a)), (cx + L * math.cos(a), cy + L * math.sin(a))], fill=P["gold"] + (255,), width=W_(4 * u))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 240, 200, 255))
    # phase 1 (0..0.45): a new loop grows on the limb; phase 2 (0.45..1): it detaches and flies off the top
    if t < 0.45:
        h = r * (0.2 + 1.6 * ease(t / 0.45))
        box = [cx - r * 0.8, cy - r - h, cx + r * 0.8, cy - r + h * 0.4]
        s.g.arc(box, 180, 360, fill=(255, 120, 40, 255), width=W_(14 * u))
        d.arc(box, 180, 360, fill=(255, 150, 60, 255), width=W_(6 * u))
    else:
        q = ease((t - 0.45) / 0.55)
        y = cy - r - r * 1.8 - q * s.Y(1.4)
        rx = r * (0.8 + 0.6 * q)
        box = [cx - rx, y - r * 0.6, cx + rx, y + r * 0.9]
        a = int(255 * (1 - q * 0.6))
        s.g.arc(box, 180, 360, fill=(255, 120, 40, a), width=W_(16 * u))
        d.arc(box, 180, 360, fill=(255, 170, 80, a), width=W_(7 * u))
        for j in range(5):
            yy = y + r * 0.9 + j * 10 * u
            d.line([(cx - rx * 0.5 + j * 9 * u, yy), (cx - rx * 0.5 + j * 9 * u, yy + 16 * u)], fill=(255, 200, 120, int(a * 0.6)), width=W_(2 * u))


# ================================================================== REBEL_CELL (custom scenes over the red player program)
def rc_shield(s, t):  # QUARANTINE: a hex barrier closes over the board (reworked: reads as a shield)
    u, d, P = s.u, s.d, s.P
    cx, cy = s.cx, s.Y(0.62)
    R = 70 * u * (0.8 + 0.2 * ease(min(1, t / 0.3)))
    for ring in range(3):
        rr = R * (1 - ring * 0.25)
        pts = [(cx + rr * math.cos(math.radians(60 * j + 30)), cy + rr * math.sin(math.radians(60 * j + 30))) for j in range(6)]
        a = int(255 * (0.55 + 0.45 * tri(t * 2 + ring / 3)))
        s.g.polygon(pts, outline=P["a"] + (a,), width=W_(14 * u))
        d.polygon(pts, outline=(255, 210, 210, a), width=W_(5 * u))
    d.polygon([(cx + R * 0.5 * math.cos(math.radians(60 * j + 30)), cy + R * 0.5 * math.sin(math.radians(60 * j + 30))) for j in range(6)], fill=P["a"] + (150,))
    ph = (t * 2) % 1.0  # a packet bounces off the barrier from the top
    if ph < 0.5:
        y = s.Y(0.02) + (cy - R - s.Y(0.02)) * (ph / 0.5)
        x = cx + 30 * u
    else:
        q = (ph - 0.5) / 0.5
        y = cy - R - 70 * u * q
        x = cx + 30 * u + 90 * u * q
    d.rectangle([x - 9 * u, y - 9 * u, x + 9 * u, y + 9 * u], fill=(92, 225, 255, 255), outline=(10, 8, 16, 255))
    d.text((cx - 38 * u, s.Y(0.94) - 12 * u), "QUARANTINE", font=f_mono(int(11 * u)), fill=P["paper"] + (int(140 + 110 * tri(t * 2)),))


def rc_defend(s, t):  # attacks fall from the OUTER arc onto a wall that sits on the INNER part
    u, d, P = s.u, s.d, s.P
    wy0, wy1 = s.Y(0.72), s.Y(0.96)
    bh, bw = (wy1 - wy0) / 3, 34 * u
    for r in range(3):
        off = (r % 2) * bw / 2
        for k in range(-6, 7):
            x = s.cx + k * bw - off
            d.rectangle([x, wy0 + r * bh, x + bw - 3 * u, wy0 + (r + 1) * bh - 3 * u], fill=(150, 24, 34, 255), outline=(255, 90, 100, 255))
    for j in range(4):  # packets fall, burst on the top course
        ph = (t + j / 4) % 1.0
        x = s.cx + (-90 + 60 * j) * u
        y = s.Y(0.02) + (wy0 - s.Y(0.02)) * min(1, ph / 0.75)
        if ph < 0.75:
            d.rectangle([x - 9 * u, y - 16 * u, x + 9 * u, y], fill=(92, 225, 255, 255), outline=(10, 8, 16, 255))
            d.line([(x, y - 30 * u), (x, y - 10 * u)], fill=(92, 225, 255, 120), width=W_(3 * u))
        else:
            k = (ph - 0.75) / 0.25
            r = (8 + 26 * k) * u
            s.g.ellipse([x - r, wy0 - r * 0.6, x + r, wy0 + r * 0.3], fill=(255, 120, 120, int(255 * (1 - k))))
            for a in range(200, 341, 35):
                d.line([(x, wy0), (x + r * math.cos(math.radians(a)), wy0 + r * math.sin(math.radians(a)))], fill=(255, 220, 220, int(255 * (1 - k))), width=W_(2 * u))


# ================================================================== registry
SCENES = {
    "meridian": {"ATTACK": mer_attack, "CRITICAL": mer_crit, "DEFEND": mer_defend, "SHIELD": mer_shield,
                 "SPECIAL": mer_judgement, "MISS": mer_miss},
    "solace": {"ATTACK": sol_attack, "CRITICAL": S0.sol_crit, "DEFEND": sol_defend, "HEAL": sol_growth,
               "SPECIAL": sol_dose, "MISS": S0.sol_miss, "SHIELD": S0.sol_shield},
    "halcyon": {"ATTACK": hal_attack_a, "ATTACK_B": hal_attack_b, "ATTACK_C": hal_attack_c, "CRITICAL": hal_crit,
                "SHIELD": hal_shield, "DEFEND": hal_defend, "HEAL": S0.hal_heal, "SPECIAL": S0.hal_citation,
                "MISS": S0.hal_miss_a},
    "orbital": {"ATTACK": S0.orb_attack, "CRITICAL": S0.orb_crit, "DEFEND": S0.orb_defend, "EVADE": S0.orb_evade,
                "SPECIAL": orb_flare, "MISS": S0.orb_miss, "SHIELD": S0.orb_shield, "HEAL": S0.orb_heal},
    "rebel_cell": {"SHIELD": rc_shield, "DEFEND": rc_defend},
}
FALLBACK = {"EVADE": "ATTACK", "HEAL": "DEFEND", "SHIELD": "DEFEND", "AFFLICT": "SPECIAL", "DEPLOY": "ATTACK"}


def scene(ctx, corp, kind, t):
    tab = SCENES[corp]
    fn = tab.get(kind) or tab.get(FALLBACK.get(kind, "ATTACK"))
    s = Sc(ctx, corp)
    s.P = PAL[corp]
    fn(s, t % 1.0)
    return s.done()
