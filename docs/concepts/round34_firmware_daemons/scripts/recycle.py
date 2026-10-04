"""Round 33 -> recycle_bin.png + recycle_bin.gif: removal = the RECYCLE BIN. A cel-shaded wire-mesh bin
with a hinged flap lid (simple 3D projection so the lid swings right); the card / slice sticker drops in,
crumples into a faceted low-poly ball (Cv2 triangles), and dissolves to bits inside the mesh.

python recycle.py [still|gif|all]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import r31lib as L
import sticker_lib19 as SL

E = math.radians(16)        # view elevation
RT, RB, HT = 130, 104, 250  # top radius, bottom radius, height
LID_R = 138
BODY = (46, 60, 70)
WIRE = (150, 196, 210)
LIME = (166, 255, 72)
CARD = dict(name="Feather Touch", cost=0, kind="WHEEL", art="picto_nudge", pic="picto_nudge", val="1", text="One +-1 nudge.", rar="Common")


def set_scale(k):
    """Bin size multiplier (the still uses a bigger bin than the GIF)."""
    global RT, RB, HT, LID_R
    RT, RB, HT, LID_R = int(130 * k), int(104 * k), int(250 * k), int(138 * k)


def proj(o, X, Y, Z):
    return (o[0] + X, o[1] - Y * math.cos(E) + Z * math.sin(E))


def ring(o, r, y, a0=0, a1=360, n=72):
    return [proj(o, r * math.cos(math.radians(a)), y, r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


def lid_poly(o, theta, dy=0.0):
    """Lid disc hinged at the back of the rim; theta = 0 closed, 90 standing up."""
    pts = []
    th = math.radians(theta)
    for ph in np.linspace(0, 2 * math.pi, 64):
        x = LID_R * math.cos(ph)
        d = LID_R + LID_R * math.sin(ph)
        Y = HT + 8 + dy + d * math.sin(th)
        Z = -LID_R + d * math.cos(th)
        pts.append(proj(o, x, Y, Z))
    return pts


def bin_back(o, size):
    """Interior: the dark mouth and the inside of the back wall."""
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # back wall (visible through the mesh and the mouth)
    back = ring(o, RT, HT, 180, 360) + ring(o, RB, 0, 360, 180)
    d.polygon(back, fill=(18, 22, 28, 255))
    d.polygon(ring(o, RT, HT), fill=(10, 12, 16, 255))
    for a in range(190, 360, 15):
        p0 = proj(o, RT * math.cos(math.radians(a)), HT, RT * math.sin(math.radians(a)))
        p1 = proj(o, RB * math.cos(math.radians(a)), 0, RB * math.sin(math.radians(a)))
        d.line([p0, p1], fill=(50, 66, 76, 255), width=2)
    return im


def bin_front(o, size, fill_k=0.0):
    """Front half: wire mesh (see-through), toon bands, rim, the recycle sticker."""
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    front = ring(o, RT, HT, 180, 0) + ring(o, RB, 0, 0, 180)
    # translucent mesh body with toon bands (light from the left)
    body = Image.new("RGBA", size, (0, 0, 0, 0))
    db = ImageDraw.Draw(body)
    db.polygon(front, fill=BODY + (150,))
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(front, fill=255)
    band = Image.new("L", size, 0)
    bd = ImageDraw.Draw(band)
    bd.polygon(ring(o, RT, HT, 180, 130) + ring(o, RB, 0, 130, 180), fill=70)
    bd.polygon(ring(o, RT, HT, 50, 0) + ring(o, RB, 0, 0, 50), fill=0)
    body = SL.over(body, (255, 255, 255), ImageChops.multiply(band, m))
    dark = Image.new("L", size, 0)
    ImageDraw.Draw(dark).polygon(ring(o, RT, HT, 45, 0) + ring(o, RB, 0, 0, 45), fill=90)
    body = SL.over(body, (0, 0, 0), ImageChops.multiply(dark, m))
    im.alpha_composite(body)
    d = ImageDraw.Draw(im)
    # wires: verticals + diagonal weave + rings
    for a in range(180, -1, -12):
        p0 = proj(o, RT * math.cos(math.radians(a)), HT, RT * math.sin(math.radians(a)))
        p1 = proj(o, RB * math.cos(math.radians(a)), 0, RB * math.sin(math.radians(a)))
        lit = 0.6 + 0.4 * (a / 180)
        d.line([p0, p1], fill=tuple(int(c * lit) for c in WIRE) + (255,), width=3)
    for y in range(30, HT, 44):
        r = RB + (RT - RB) * y / HT
        d.line(ring(o, r, y, 180, 0, 40), fill=WIRE + (255,), width=3)
    # rims
    d.line(ring(o, RB, 0, 180, 0, 40), fill=(20, 24, 30, 255), width=8)
    d.line(ring(o, RT, HT, 0, 360, 90), fill=(20, 24, 30, 255), width=12)
    d.line(ring(o, RT, HT, 180, 0, 50), fill=(190, 225, 235, 255), width=5)
    d.line(ring(o, RT, HT, 180, 360, 50), fill=(110, 140, 150, 255), width=4)
    # outline
    d.line(ring(o, RT, HT, 180, 0, 50)[:1] + [proj(o, -RB, 0, 0)], fill=(10, 10, 14, 255), width=4)
    d.line([proj(o, RT, HT, 0), proj(o, RB, 0, 0)], fill=(10, 10, 14, 255), width=4)
    # fill level: crumpled stuff visible through the mesh is drawn by the caller between back and front
    return im


def lid(o, size, theta, dy=0.0):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top = lid_poly(o, theta, dy + 10)
    bot = lid_poly(o, theta, dy)
    # thickness: draw the lower disc, then the upper, with the rim band between
    d.polygon(bot, fill=(26, 32, 40, 255), outline=(10, 10, 14, 255))
    d.polygon(top, fill=(70, 96, 110, 255), outline=(10, 10, 14, 255))
    cx_ = sum(p[0] for p in top) / len(top)
    cy_ = sum(p[1] for p in top) / len(top)
    for k_, col_, wd in ((0.82, (54, 76, 90), 0), (0.62, LIME, 4), (0.3, (40, 56, 66), 0)):
        inner = [(cx_ + (p[0] - cx_) * k_, cy_ + (p[1] - cy_) * k_) for p in top]
        if wd:
            d.line(inner + [inner[0]], fill=col_ + (255,), width=wd)
        else:
            d.polygon(inner, fill=col_ + (255,), outline=(20, 26, 32, 255))
    for j in range(8):
        q = top[j * 8]
        rv = (cx_ + (q[0] - cx_) * 0.9, cy_ + (q[1] - cy_) * 0.9)
        d.ellipse([rv[0] - 4, rv[1] - 3, rv[0] + 4, rv[1] + 3], fill=(150, 180, 190, 255))
    # toon highlight on the lid face
    th = math.radians(theta)
    if theta < 80:
        hl = [(x, y) for (x, y) in lid_poly((o[0] - 12, o[1]), theta, dy + 10)]
        dd = Image.new("L", size, 0)
        ImageDraw.Draw(dd).polygon(hl, fill=60)
        mm = Image.new("L", size, 0)
        ImageDraw.Draw(mm).polygon(top, fill=255)
        im = SL.over(im, (255, 255, 255), ImageChops.multiply(dd, mm))
        d = ImageDraw.Draw(im)
    # handle: a little tab at the front edge of the lid
    ph = math.pi / 2
    d_front = 2 * LID_R
    Y = HT + 18 + dy + d_front * math.sin(th)
    Z = -LID_R + d_front * math.cos(th)
    hx, hy = proj(o, 0, Y, Z)
    d.rounded_rectangle([hx - 26, hy - 6, hx + 26, hy + 8], radius=4, fill=LIME + (255,), outline=(10, 10, 14, 255), width=2)
    return im


def recycle_sticker(px=120):
    S = 2
    P = px * S
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r = P / 2, P * 0.32
    for k in range(3):
        a0 = k * 120 + 20
        a1 = a0 + 80
        d.arc([c - r, c - r, c + r, c + r], a0, a1, fill=LIME + (255,), width=int(P * 0.11))
        a = math.radians(a1)
        hx, hy = c + r * math.cos(a), c + r * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        nx, ny = math.cos(a), math.sin(a)
        s = P * 0.13
        d.polygon([(hx + tx * s * 1.3, hy + ty * s * 1.3), (hx + nx * s, hy + ny * s), (hx - nx * s, hy - ny * s)], fill=LIME + (255,))
    a = im.split()[3]
    edge = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(7)), a)
    im = SL.over(im, (14, 12, 20), edge)
    im = im.resize((px, px), Image.LANCZOS)
    return L.sticker_from_art(im, border=6, seed=7)


def crumple(img, c, seed=3):
    """Crumple a sticker image into a faceted ball: a triangle mesh pulled to the centre with random
    folds, each facet shaded (the Cv2 triangulated look)."""
    if c <= 0:
        return img
    w, h = img.size
    rng = np.random.default_rng(seed)
    nx, ny = 6, 8
    xs = np.linspace(0, w - 1, nx + 1)
    ys = np.linspace(0, h - 1, ny + 1)
    cx, cy = w / 2, h / 2
    src = {}
    dst = {}
    k = 1 - 0.72 * c
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            src[(i, j)] = (x, y)
            dx, dy = x - cx, y - cy
            rr = math.hypot(dx / w, dy / h) + 1e-6
            # pull everything toward a ball (radius ~ 0.32 of the card) + fold noise
            ball = 0.32 * min(w, h) / max(1.0, math.hypot(dx, dy))
            f = (1 - c) * 1 + c * min(1.0, ball * 1.6)
            nxj = rng.normal(0, 0.07 * min(w, h)) * c
            nyj = rng.normal(0, 0.07 * min(w, h)) * c
            dst[(i, j)] = (cx + dx * f * (0.6 + 0.4 * k) + nxj, cy + dy * f * (0.6 + 0.4 * k) + nyj)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tris = []
    for j in range(ny):
        for i in range(nx):
            a, b, cc, d = (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)
            tris += [(a, b, cc), (a, cc, d)] if (i + j) % 2 == 0 else [(a, b, d), (b, cc, d)]
    order = rng.permutation(len(tris))
    for t in order:
        tri = tris[t]
        S_ = [src[v] for v in tri]
        D = [dst[v] for v in tri]
        # affine dst -> src
        A = np.array([[D[0][0], D[0][1], 1], [D[1][0], D[1][1], 1], [D[2][0], D[2][1], 1]], np.float64)
        try:
            cx_ = np.linalg.solve(A, np.array([S_[0][0], S_[1][0], S_[2][0]]))
            cy_ = np.linalg.solve(A, np.array([S_[0][1], S_[1][1], S_[2][1]]))
        except np.linalg.LinAlgError:
            continue
        warped = img.transform((w, h), Image.AFFINE, (cx_[0], cx_[1], cx_[2], cy_[0], cy_[1], cy_[2]), resample=Image.BILINEAR)
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon(D, fill=255)
        m = ImageChops.multiply(m, warped.split()[3])
        shade = 1 + rng.uniform(-0.38, 0.22) * c
        arr = np.asarray(warped, np.float32)
        arr[..., :3] = np.clip(arr[..., :3] * shade, 0, 255)
        warped = Image.fromarray(arr.astype(np.uint8), "RGBA")
        out.paste(warped, (0, 0), m)
        if c > 0.3:
            ImageDraw.Draw(out).line(D + [D[0]], fill=(30, 26, 34, int(120 * c)), width=1)
    return out


def card_img(scale=1.0):
    sd = L.card_sticker(CARD, 200, 266, seed=21)
    im = sd["img"]
    im = im.resize((int(im.width / SL.SS * scale), int(im.height / SL.SS * scale)), Image.LANCZOS)
    return im


def bits(img, cx, cy, t, n=140, seed=5):
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    f = L.f_mono(16)
    for _ in range(n):
        ang = rng.uniform(-math.pi * 0.85, -math.pi * 0.15)
        sp = rng.uniform(60, 220)
        x = cx + math.cos(ang) * sp * t + rng.normal(0, 12)
        y = cy + math.sin(ang) * sp * t * 0.9 - 40 * t
        col = LIME if rng.random() < 0.5 else (255, 61, 168)
        d.text((x, y), "01"[int(rng.random() * 2)], font=f, fill=col + (int(255 * max(0, 1 - t) ** 0.7),), anchor="mm")
    return img


def scene(size, o, theta, item=None, item_pos=None, item_rot=0.0, crumple_k=0.0, inside=(), bits_t=None, badge=0, sticker=True):
    """Compose one bin state. inside = list of (x, y, scale, seed) crumpled balls lying in the bin."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    # floor shadow
    sh = Image.new("L", size, 0)
    ImageDraw.Draw(sh).polygon(ring((o[0] + 16, o[1] + 6), RB + 30, 0), fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    lay = Image.new("RGBA", size, (4, 3, 8, 0))
    lay.putalpha(sh)
    img.alpha_composite(lay)
    lid_behind = theta > 60
    if lid_behind:
        img.alpha_composite(lid(o, size, theta))
    img.alpha_composite(bin_back(o, size))
    for (x, y, s, sd) in inside:
        b = crumple(card_img(0.6 * s), 1.0, seed=sd)
        img.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
    if item is not None:
        it = crumple(item, crumple_k, seed=13)
        if item_rot:
            it = L.rotate_rgba(it, item_rot)
        img.alpha_composite(it, (int(item_pos[0] - it.width / 2), int(item_pos[1] - it.height / 2)))
    img.alpha_composite(bin_front(o, size))
    if sticker:
        st = recycle_sticker(110)
        img = L.place_sticker(img, st, o[0] - 4, o[1] - int(HT * 0.48), angle=-4, scale=RT / 130)
    if not lid_behind:
        img.alpha_composite(lid(o, size, theta))
    if bits_t is not None:
        img = bits(img, o[0], o[1] - HT * math.cos(E) - 10, bits_t)
    if badge:
        d = ImageDraw.Draw(img)
        bx, by = o[0] + RT - 10, o[1] - HT * math.cos(E) - 40
        d.ellipse([bx - 22, by - 22, bx + 22, by + 22], fill=(255, 61, 168, 255), outline=(10, 10, 14, 255), width=3)
        d.text((bx, by), str(badge), font=L.f_num(30), fill=(255, 255, 255, 255), anchor="mm")
    return img


def backdrop(size):
    import shop as S1
    return S1.pegboard(*size)


def make_still():
    W_, H_ = 1920, 1080
    img = Image.new("RGBA", (W_, H_), (11, 10, 16, 255))
    pb = backdrop((W_, H_))
    img.alpha_composite(pb)
    img = L.vignette(img, 0.6)
    set_scale(1.4)
    o = (760, 1010)
    st = scene((W_, H_), o, 96, item=card_img(1.15), item_pos=(780, 560), item_rot=-14, crumple_k=0.45,
               inside=[(690, 830, 0.9, 21), (840, 860, 0.8, 22)], badge=0)
    set_scale(1.0)
    img.alpha_composite(st)
    # a slice tile parked, also droppable
    tile = L.tile("big_tile_SANDBOX_8_1.png")
    tl = L.sticker_from_art(tile.resize((int(tile.width * 0.8), int(tile.height * 0.8)), Image.LANCZOS), border=7, seed=40)
    img = L.place_sticker(img, tl, 1230, 300, angle=6, hover=0.6)
    p = L.pen(L.GP_YELLOW, seed=31)
    p.arrow([(1130, 360), (1020, 420), (930, 520)], width=8, head=20)
    p.text("slices too", 1160, 430, 32, angle=-8)
    p.text("drop it in", 520, 330, 38, angle=-6)
    p.arrow([(560, 360), (620, 420), (650, 470)], width=8, head=20)
    img = L.ink(img, p)
    c = L.CRT(520, 300, L.CYAN, "RECYCLE BIN", tag="50 CYCLES", seed=8)
    c.text((20, 56), "in the bin:", 18, (150, 200, 220))
    c.text((20, 86), "  FEATHER TOUCH      card", 20, L.CYAN)
    c.text((20, 116), "  SANDBOX 8          slice slot", 20, (120, 160, 175))
    c.rule(150, dash=True)
    c.text((20, 166), "deck 18 -> 17   next removal 75", 17, (150, 200, 220))
    c.text((20, 196), "fish it back out until you", 17, (150, 200, 220))
    c.text((20, 222), "LEAVE THE MAINFRAME", 17, (255, 214, 64))
    c.text((20, 256), "sfx: lid clank / crunch / fizz", 15, (110, 140, 150))
    img = L.paste(img, c.finish(), 1260, 560)
    sd = L.sticker_word(["RECYCLE BIN"], 64, fills=[LIME], seed=12)
    img = L.place_sticker(img, sd, 330, 90, angle=-3)
    d = ImageDraw.Draw(img)
    d.text((600, 96), "removal: drop a card sticker or a slice in; it crumples and dissolves into bits", font=L.f_mono(18), fill=(200, 200, 215, 255), anchor="lm")
    img = L.bloom(img, 0.15, 0.82, 8)
    L.save(img, "recycle_bin.png")


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lid_angle(f):
    """0 closed; flaps open with an overshoot, holds, slams shut with a rebound."""
    if f < 6:
        return 0.0
    if f < 12:
        t = (f - 6) / 6
        return 118 * ease(t) + 12 * math.sin(t * math.pi)
    if f < 26:
        return 110.0
    if f < 31:
        return 110 * (1 - ease((f - 26) / 5))
    if f < 36:
        t = (f - 31) / 5
        return 18 * math.sin(t * math.pi) * (1 - t)
    return 0.0


def make_gif():
    size = (760, 640)
    o = (380, 600)
    pb = backdrop(size)
    pb = L.vignette(pb, 0.5)
    frames, durs = [], []
    card = card_img(0.85)
    N = 44
    for f in range(N):
        th = lid_angle(f)
        item, pos, rot, ck, bt, badge = None, None, 0.0, 0.0, None, 0
        if f < 12:
            item, pos, rot = card, (380, 150 + 4 * math.sin(f * 0.8)), -6
        elif f < 20:
            t = (f - 12) / 8
            item = card
            pos = (380 + 10 * t, 150 + 330 * t * t)
            rot = -6 - 70 * t
            ck = ease(t * 1.2)
        if 19 <= f < 30:
            bt = (f - 19) / 11
        if f >= 31:
            badge = 1
        inside = [(330, 500, 0.6, 21)] + ([(410, 520, 0.6, 13)] if f >= 20 else [])
        img = pb.copy()
        img.alpha_composite(scene(size, o, th, item=item, item_pos=pos, item_rot=rot, crumple_k=ck, inside=inside, bits_t=bt, badge=badge))
        if f >= 34:
            c = L.CRT(330, 74, L.CYAN, None, header=False, seed=9)
            c.text((14, 12), "RECYCLED: FEATHER TOUCH", 17, L.CYAN)
            c.text((14, 42), "deck 18 -> 17", 15, (150, 200, 220))
            img = L.paste(img, c.finish(), 20, 20)
        frames.append(img.convert("RGB"))
        durs.append(60)
        print("bin", f, flush=True)
    durs[11] = 200
    durs[-1] = 1500
    mont = Image.new("RGB", (size[0], size[1] * 4))
    for k_, fi in enumerate((2, 15, 24, 40)):
        mont.paste(frames[fi], (0, size[1] * k_))
    pal = mont.quantize(colors=220, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [fr.quantize(palette=pal, dither=Image.NONE) for fr in frames]
    path = os.path.join(L.OUT, "recycle_bin.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("wrote", path, os.path.getsize(path) / 1e6, "MB")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("still", "all"):
        make_still()
    if what in ("gif", "all"):
        make_gif()
