"""Round 44 A (map screens): the shared kit.

Reuses the locked kits, never redraws them:
  ui31 / sticker_lib31  round 31-33 chrome (terminal panels, terminal buttons, stickers, wax pencil, paper, stamps)
  post40                 the unified city finish (round 40 v3, SOLID40 for the translucent views)
  markers42              Site markers v4 (City Grid)
  r32ui / r35ui          netrun node stickers, token, dossier
  round39_portraits      the operative busts (cropped from the locked sheet portraits_classes_v2.png)
New here (composition only): the per-page resource bar, the world dimming map, light spill, the holo file shell built
to bible 1.2 (corp tint 78 %, 4 px scanlines, slow bands, RGB edge split, 0.88 scrim, cracked seal + DECRYPTED),
the crew polaroid and the one-at-a-time rainbow gloss sweep. All randomness is seeded.
"""
import math
import os
import random
import sys

os.environ.setdefault("NET36", "net_scope.json")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageEnhance  # noqa: E402

import ui31 as K  # noqa: E402
import sticker_lib31 as SL  # noqa: E402

OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")
CONC = K.CONC
W, H = 1920, 1080

PEN_Y = (255, 226, 0)        # bible PENCIL_PLAN #FFE200
PEN_R = (255, 28, 44)        # bible PENCIL_THREAT #FF1C2C
HEATC = (255, 122, 26)       # FLAGGED band colour
MER = (255, 140, 26)
LIME = K.LIME
CYAN = K.CYAN
PINK = K.PINK
GOLD = K.GOLD
HARM = K.HARM
GREEN = K.GREEN
AMBER = K.AMBER
WHITE = K.WHITE
DIM = K.DIM
NAVY = K.NAVY
COUR, COUR_B = K.COUR, K.COUR_B
F = K.F


# ------------------------------------------------------------------ conversions
def f2p(img_f):
    return Image.fromarray((np.clip(img_f, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


def p2f(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def save(img, name, jpg_q=None):
    path = os.path.join(OUT, name)
    im = img.convert("RGB")
    if name.endswith(".jpg"):
        im.save(path, quality=jpg_q or 88, optimize=True)
    else:
        im.save(path, optimize=True)
    print("saved", name, flush=True)
    return path


# ------------------------------------------------------------------ world treatment
def soft_rect(box, blur=70, size=(W, H)):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, 40, fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255.0


def soft_ellipse(cx, cy, rx, ry, blur=60, size=(W, H)):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255.0


def grade_map(img, net_mask, lit_mask=None, band=0.68, inside=0.86, desat_out=0.25):
    """The map band: x0.68 outside the network fit rect (a touch desaturated, hue kept), x0.86 inside it, and full
    strength only inside the lit vignette round the selected Site."""
    a = p2f(img)
    f = band + (inside - band) * net_mask
    if lit_mask is not None:
        f = f + (1.0 - f) * lit_mask
    lum = a.mean(axis=2, keepdims=True)
    ds = (desat_out * (1 - net_mask))[..., None]
    a = a * (1 - ds) + lum * ds
    a = a * f[..., None]
    return f2p(a)


def spill(img, mask_l, col, k=0.25, radius=40):
    """Additive light spill of an emissive element onto the world under it (bible 1.2 / D19)."""
    return K.add_glow(img, mask_l, col, radius, k)


def sticker_mask(sd, cx, cy, angle=0.0, scale=1.0):
    im = sd["img"]
    a = im.split()[3]
    w, h = a.size
    a = a.resize((max(2, int(w * scale / SL.SS)), max(2, int(h * scale / SL.SS))), Image.LANCZOS).rotate(angle, expand=True)
    m = Image.new("L", (W, H), 0)
    m.paste(a, (int(cx - a.width / 2), int(cy - a.height / 2)))
    return m


def place_sticker(img, sd, cx, cy, angle=0.0, scale=1.0, hover=0.0, spill_col=None, spill_k=0.28):
    """Place a vinyl sticker; a glowing sticker spills its colour on the city (radius 1.5x the element)."""
    if spill_col:
        m = sticker_mask(sd, cx, cy, angle, scale)
        bb = m.getbbox()
        r = max(20, int(((bb[2] - bb[0]) + (bb[3] - bb[1])) / 4 * 0.75)) if bb else 40
        img = spill(img, m, spill_col, spill_k, r)
    return SL.place(img, sd, cx, cy, angle=angle, scale=scale, hover=hover)


def panel_shadow(img, box, chamfer=16, blur=18, k=0.45, off=(0, 10)):
    """Panels sit ON the world: a soft 18 px black drop shadow at 45 %."""
    m = K.rect_mask(img.size, box, chamfer=chamfer)
    return K.over(img, (2, 2, 6), SL.shift(m, *off).filter(ImageFilter.GaussianBlur(blur)), k)


def term(img, box, title=None, accent=CYAN, tag=None, tag_col=None, seed=1, header=True, chamfer=16):
    img = panel_shadow(img, box, chamfer)
    return K.term_panel(img, box, title, accent=accent, tag=tag, tag_col=tag_col, seed=seed, header=header, chamfer=chamfer,
                        hexbg=True, scan=0.10)


# ------------------------------------------------------------------ stickers
def sticker(word, size, fill="pink", seed=7, curl=None, gloss_k=0.22):
    fl = {"pink": K.FILL_PINK, "yellow": K.FILL_YELLOW}[fill]
    return K.sticker([word], size=size, fill=fl, seed=seed, curl=curl, gloss_k=gloss_k)


def rainbow_sweep(sd, pos=0.5, width=0.07, k=0.75, seed=3):
    """The one sticker mid-sweep on this screen (designer: the rainbow gloss sweep runs on a scheduler, one at a time)."""
    img = sd["img"].copy()
    body = sd["body"]
    w, h = img.size
    band = SL.diag(w, h, 28).point(SL.band_lut(pos, width, 1.0))
    holo = SL.holo_tex(w, h, seed=seed, phase=pos * 3.0, sat=0.75)
    m = SL.mul(SL.scale_mask(band, k), body)
    lay = holo.copy()
    lay.putalpha(m)
    img = Image.alpha_composite(img, lay)
    sharp = SL.diag(w, h, 28).point(SL.band_lut(pos + 0.02, 0.012, 0.8))
    img = SL.over(img, (255, 255, 255), SL.mul(sharp, body))
    out = dict(sd)
    out["img"] = img
    return out


# ------------------------------------------------------------------ grease pencil
def pencil(col, seed):
    return K.Pencil((W, H), col, seed=seed)


def ink(img, pen):
    return pen.ink(img, shadow=0.85)


# ------------------------------------------------------------------ the resource bar (terminal; bible 4.13 / 2.8)
def _res_icon(kind, px, col):
    import r31lib as RL
    if kind == "schem":
        return RL.schem_mark(px, col)
    if kind == "cycles":
        return RL.cycles_mark(px, col)
    if kind == "crew":
        return RL.crew_mark(px, col)
    g = {"hp": "picto_hp", "home": "placeholder_shield", "exploit": "placeholder_key", "raid": "picto_target",
         "ice": "state_frozen", "heat": "placeholder_burn", "ram": "picto_ram", "deck": "picto_draw"}[kind]
    return K.glyph(g, px, col)


RES_COL = {"schem": (255, 200, 80), "home": PINK, "exploit": GOLD, "raid": HARM, "ice": (150, 225, 255), "crew": CYAN,
           "hp": (255, 90, 110), "cycles": (120, 255, 200), "heat": HEATC, "ram": CYAN, "deck": DIM}
HEAT_BANDS = (("COOL", 0, (92, 225, 255)), ("NOTICED", 25, AMBER), ("FLAGGED", 50, HEATC), ("HUNTED", 75, HARM))


def heat_band(v):
    b = HEAT_BANDS[0]
    for t in HEAT_BANDS:
        if v >= t[1]:
            b = t
    return b


def cell_width(it, scale=1.0):
    if it["kind"] == "heat":
        return int((it.get("w", 330)) * scale)
    f = F(K.ANTON, int(30 * scale))
    v = f.getlength(it["value"]) + (F(K.MONO, int(14 * scale)).getlength(it.get("max", "")) + 4 if it.get("max") else 0)
    lab = F(K.MONO, int(13 * scale)).getlength(it["label"]) * 1.1
    return int(max(v, lab) + 54 * scale + 22 * scale)


def topbar(img, x0, y0, items, scale=1.0, accent=CYAN, h=None, seed=11, right_button=None):
    """One terminal strip: icon + mono label + bare Anton value per resource; Heat = number, band word and strip
    with the 25/50/75 ticks (no stamp: the change is the gauge's roll). Returns (img, box)."""
    h = h or int(72 * scale)
    ws = [cell_width(it, scale) for it in items]
    x1 = x0 + sum(ws) + int(16 * scale)
    box = (x0, y0, x1, y0 + h)
    img = term(img, box, None, accent=accent, header=False, seed=seed, chamfer=int(14 * scale))
    x = x0 + int(10 * scale)
    d = K.BD(img)
    for it, w in zip(items, ws):
        cy = y0 + h / 2
        if it["kind"] == "heat":
            v = it["value"]
            name, _, bc = heat_band(v)
            K.text(img, (x + 6 * scale, y0 + 14 * scale), "HEAT", F(K.MONO, int(13 * scale)), bc, "la", 1.4)
            img = K.live_number(img, (x + 8 * scale, cy + 12 * scale), str(v), int(40 * scale), bc, "lm", 1.0, 0.45)
            bx = x + 80 * scale
            bw = w - 96 * scale
            K.text(img, (bx, y0 + 14 * scale), name, F(K.MONO, int(16 * scale)), bc, "la", 1.6)
            K.text(img, (bx + bw, y0 + 14 * scale), "/100", F(K.MONO, int(13 * scale)), DIM, "ra", 0.8)
            by = y0 + 40 * scale
            bh = 10 * scale
            d = K.BD(img)
            for (nm, t0, c), t1 in zip(HEAT_BANDS, (25, 50, 75, 100)):
                xa, xb = bx + bw * t0 / 100, bx + bw * t1 / 100
                fill = min(1.0, max(0.0, (v - t0) / (t1 - t0)))
                d.rectangle([xa + 1, by, xb - 1, by + bh], fill=tuple(int(cc * 0.22) for cc in c) + (255,))
                if fill > 0:
                    d.rectangle([xa + 1, by, xa + 1 + (xb - xa - 2) * fill, by + bh], fill=c + (255,))
            for t in (25, 50, 75):
                tx = bx + bw * t / 100
                d.line([(tx, by - 4 * scale), (tx, by + bh + 4 * scale)], fill=(235, 240, 250, 255), width=max(1, int(2 * scale)))
            mx = bx + bw * v / 100
            d.polygon([(mx - 6 * scale, by - 9 * scale), (mx + 6 * scale, by - 9 * scale), (mx, by - 1)], fill=(245, 245, 250, 255))
            if it.get("rule"):
                K.text(img, (bx, by + bh + 7 * scale), it["rule"], F(K.MONO, int(12 * scale)), DIM, "la", 0.6)
        else:
            col = RES_COL[it["kind"]]
            ic = _res_icon(it["kind"], int(26 * scale), col)
            img.alpha_composite(ic, (int(x + 6 * scale), int(cy - 13 * scale + 6 * scale)))
            K.text(img, (x + 6 * scale, y0 + 10 * scale), it["label"], F(K.MONO, int(13 * scale)), DIM, "la", 1.3)
            vx = x + 40 * scale
            img = K.live_number(img, (vx, cy + 8 * scale), it["value"], int(30 * scale), it.get("col", (240, 244, 252)), "lm", 1.0, 0.3)
            if it.get("max"):
                fx = vx + F(K.ANTON, int(30 * scale)).getlength(it["value"]) + 4 * scale
                K.text(img, (fx, cy + 14 * scale), it["max"], F(K.MONO, int(14 * scale)), DIM, "lm", 0.6)
        x += w
        if it is not items[-1]:
            d = K.BD(img)
            d.line([(x - 4 * scale, y0 + 10 * scale), (x - 4 * scale, y0 + h - 10 * scale)], fill=accent + (70,), width=1)
    return img, box


# ------------------------------------------------------------------ the decrypted holo file (bible 1.2, D17)
def corp_emblem(px, col, corp="meridian"):
    g = Image.open(os.path.join(SCR, "emblems", corp + ".png")).convert("RGBA").split()[3].resize((px, px), Image.LANCZOS)
    im = Image.new("RGBA", (px, px), col + (0,))
    im.putalpha(g)
    return im


def cracked_seal(px, col, corp="meridian"):
    """The corp mark cracked: halves offset, a red fracture through it."""
    em = corp_emblem(px, col, corp)
    w, h = em.size
    out = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.ellipse([2, 2, w + 5, h + 5], outline=col + (220,), width=2)
    left, right = em.crop((0, 0, w // 2 + 2, h)), em.crop((w // 2 - 2, 0, w, h))
    out.alpha_composite(left, (1, 6))
    out.alpha_composite(right, (w // 2 + 5, 2))
    pts = [(w * 0.53 + 4, 0), (w * 0.46 + 4, h * 0.3), (w * 0.57 + 4, h * 0.56), (w * 0.47 + 4, h * 0.82), (w * 0.54 + 4, h + 8)]
    d.line(pts, fill=(255, 68, 51, 255), width=max(2, w // 26))
    return out


def holo_file(img, box, title, rows, corp="meridian", seed=4, stamp=True, sub=None, scale=1.0, key_w=None, extra=None):
    """Hacked corp intel. rows: (key, value[, col]). The 0.88 scrim dims the world behind, the corp tint sits at 78 %,
    4 px scanlines and three slow bands, a +-2 px RGB split on the edge only, the cracked seal + DECRYPTED at the foot."""
    x0, y0, x1, y1 = [int(v) for v in box]
    col = K.CORP[corp]
    m = K.rect_mask(img.size, box)
    img = panel_shadow(img, box, 0)
    img = K.over(img, (2, 2, 8), m.filter(ImageFilter.GaussianBlur(3)), 0.88)
    img = K.holo_panel(img, box, corp=corp, title=None, seed=seed, alpha=0.78)
    rng = random.Random(seed)
    band = Image.new("L", img.size, 0)
    dd = ImageDraw.Draw(band)
    for _ in range(3):                                  # three slow bands (6 s period in game)
        by = rng.randint(y0 + 20, y1 - 30)
        dd.rectangle([x0, by, x1, by + rng.randint(14, 26)], fill=26)
    img = K.over(img, col, ImageChops.multiply(band.filter(ImageFilter.GaussianBlur(4)), m))
    hi = tuple(min(255, int(c * 0.35 + 255 * 0.65)) for c in col)
    K.text(img, (x0 + 18 * scale, y0 + 26 * scale), title, F(K.PLEX_M, int(25 * scale)), hi, "lm", 1.4)
    if sub:
        K.text(img, (x0 + 18 * scale, y0 + 50 * scale), sub, F(K.MONO, int(13 * scale)), tuple(int(c * 0.85) for c in hi), "lm", 1.0)
    y = y0 + (78 if sub else 60) * scale
    kw = key_w or 108 * scale
    for r in rows:
        if r[0] == "sep":
            d = K.BD(img)
            d.line([(x0 + 16, y - 6 * scale), (x1 - 16, y - 6 * scale)], fill=col + (110,), width=1)
            y += 8 * scale
            continue
        K.text(img, (x0 + 18 * scale, y), r[0], F(K.MONO, int(14 * scale)), tuple(int(c * 0.9) for c in hi), "lm", 1.2)
        K.text(img, (x0 + 18 * scale + kw, y), r[1], F(K.PLEX_M, int(19 * scale)), r[2] if len(r) > 2 else (255, 240, 222), "lm", 0.3)
        y += 30 * scale
    if extra:
        img = extra(img, y)
    if stamp:
        sz = int(64 * scale)
        se = cracked_seal(sz, col, corp)
        sx, sy = x1 - sz - 26 * scale, y1 - sz - 18 * scale
        img = K.paste_rgba(img, se, (sx, sy), anchor="la")
        st = K.rubber_stamp("DECRYPTED", int(19 * scale), (140, 255, 170), angle=-10, seed=seed + 3, pad=7)
        img = K.paste_rgba(img, st, (min(sx + sz / 2, x1 - st.width / 2 - 6), sy + sz * 0.52))
    return img


# ------------------------------------------------------------------ corp paper: the intercepted work order
def work_order(rows, w=330, seed=5, scale=1.0, title="ROUTE AUDIT", head="MERIDIAN FREIGHT", sub="YARD SECURITY  //  WO 52-MF"):
    """RAID INCOMING = the intercepted corp work order (Courier Prime fields, Plex letterhead, INTERCEPTED stamp, clip)."""
    s = scale
    lh = int(28 * s)
    h = int((150 + len(rows) * 28 + 70) * s)
    W_ = int(w * s)
    p = K.paper_tex(W_, h, seed=seed, col=K.PAPER)
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, W_, int(6 * s)], fill=MER + (255,))
    hs = int(19 * s)
    while hs > 8 and F(K.PLEX_M, hs).getlength(head) > W_ - int(64 * s):
        hs -= 1
    d.text((int(16 * s), int(16 * s)), head, font=F(K.PLEX_M, hs), fill=(200, 96, 10, 255))
    d.text((int(16 * s), int(40 * s)), sub, font=F(COUR, int(13 * s)), fill=(90, 82, 72, 255))
    ts = int(40 * s)
    while ts > 12 and F(K.ANTON, ts).getlength(title) > W_ - int(32 * s):
        ts -= 1
    d.text((int(16 * s), int(62 * s)), title, font=F(K.ANTON, ts), fill=(22, 20, 24, 255))
    y = int(122 * s)
    for k, v, *c in rows:
        d.text((int(16 * s), y), k, font=F(COUR, int(15 * s)), fill=(90, 82, 72, 255))
        col = c[0] if c else (24, 20, 26)
        vs = int(18 * s)
        while vs > 8 and F(COUR_B, vs).getlength(v) + F(COUR, int(15 * s)).getlength(k) + int(44 * s) > W_:
            vs -= 1
        d.text((W_ - int(16 * s), y - int(2 * s)), v, font=F(COUR_B, vs), fill=col + (255,), anchor="ra")
        y += lh
    rng = np.random.default_rng(seed)
    for k in range(2):
        yy = y + int((12 + k * 16) * s)
        x = int(16 * s)
        while x < W_ * 0.62:
            ln = rng.uniform(30, 70) * s
            d.rectangle([x, yy, x + ln, yy + int(9 * s)], fill=(16, 14, 18, 255))
            x += ln + rng.uniform(6, 14) * s
    st = K.rubber_stamp("INTERCEPTED", int(26 * s), (196, 30, 40), angle=-9, seed=seed + 1, pad=int(10 * s))
    p.alpha_composite(st, (W_ - st.width - int(4 * s), h - st.height - int(4 * s)))
    # the paper clip
    clip = Image.new("RGBA", (int(26 * s), int(64 * s)), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clip)
    cd.rounded_rectangle([2, 2, clip.width - 3, clip.height - 3], int(11 * s), outline=(150, 156, 168, 255), width=max(2, int(3 * s)))
    cd.rounded_rectangle([int(7 * s), int(8 * s), clip.width - int(8 * s), clip.height - int(16 * s)], int(7 * s),
                         outline=(120, 126, 138, 255), width=max(2, int(2 * s)))
    p.alpha_composite(clip, (W_ - clip.width - int(10 * s), 0))
    return p


# ------------------------------------------------------------------ crew polaroids (portraits v2 busts)
PORTRAITS = os.path.join(CONC, "round39_portraits", "portraits_classes_v2.png")
BUST_BOX = {"breaker": (44, 186, 308, 446), "ghost": (994, 186, 1258, 446), "rigger": (44, 666, 308, 926),
            "phantom": (1470, 186, 1734, 446), "botnet": (994, 666, 1258, 926)}
CLASS_COL = {"breaker": (255, 61, 168), "ghost": (92, 225, 255), "rigger": (123, 224, 123), "phantom": (200, 160, 255),
             "botnet": (120, 130, 255)}


def bust(cls, size):
    im = Image.open(PORTRAITS).convert("RGB").crop(BUST_BOX[cls])
    return im.resize(size, Image.LANCZOS)


def polaroid(name, cls, rank, status, status_col, dead=False, w=150, seed=1, selected=False):
    """A crew polaroid: the operative's CRT bust printed on instant film, name and rank printed, status on a terminal
    chip clipped to the foot (the status changes, so it is the Cell's terminal, not the print)."""
    ph = int(w * 0.86)
    h = ph + 66
    p = K.paper_tex(w, h, seed=seed, col=(244, 242, 236), fold=False)
    photo = bust(cls, (w - 16, ph - 8))
    if dead:
        photo = ImageEnhance.Brightness(photo.convert("L").convert("RGB")).enhance(0.7)
    p.paste(photo, (8, 8))
    d = ImageDraw.Draw(p)
    d.rectangle([8, 8, w - 9, ph - 1], outline=(30, 28, 34, 255), width=1)
    d.text((10, ph + 4), name, font=F(K.ANTON, 26), fill=(22, 20, 24, 255))
    d.text((w - 10, ph + 14), rank, font=F(K.ANTON, 16), fill=CLASS_COL[cls] if not dead else (110, 110, 118), anchor="ra")
    if dead:
        st = K.rubber_stamp("FLATLINED", 22, (200, 30, 36), angle=-12, seed=seed + 4, pad=8)
        p.alpha_composite(st, ((w - st.width) // 2, ph // 2 - st.height // 2))
    # status chip (terminal)
    chip = Image.new("RGBA", (w - 16, 22), (0, 0, 0, 0))
    cd = ImageDraw.Draw(chip)
    cd.rectangle([0, 0, chip.width - 1, 21], fill=(5, 13, 28, 240), outline=status_col + (230,), width=1)
    fs = 13
    while fs > 9 and F(K.MONO, fs).getlength(status) > chip.width - 10:
        fs -= 1
    cd.text((chip.width / 2, 11), status, font=F(K.MONO, fs), fill=status_col + (255,), anchor="mm")
    p.alpha_composite(chip, (8, h - 28))
    if selected:
        d.rectangle([0, 0, w - 1, 5], fill=CYAN + (255,))
    return p


def paste_polaroid(img, p, x, y, angle=0.0, lift=0.0):
    pr = p.rotate(angle, Image.BICUBIC, expand=True)
    full = Image.new("L", img.size, 0)
    full.paste(pr.split()[3], (int(x), int(y)))
    img = K.over(img, (3, 2, 8), SL.shift(full, 6 + int(10 * lift), 10 + int(14 * lift)).filter(ImageFilter.GaussianBlur(10 + 8 * lift)),
                 0.6)
    img.alpha_composite(pr, (int(x), int(y)))
    return img


# ------------------------------------------------------------------ small terminal chips and tags
def chip(img, xy, s, col=CYAN, size=15, anchor="mm", bright=False, pad=10):
    f = F(K.MONO, size)
    tw_ = f.getlength(s)
    hh = size + 12
    x, y = xy
    if anchor == "mm":
        x0, y0 = x - tw_ / 2 - pad, y - hh / 2
    elif anchor == "lm":
        x0, y0 = x, y - hh / 2
    else:
        x0, y0 = x, y
    box = (x0, y0, x0 + tw_ + 2 * pad, y0 + hh)
    img = panel_shadow(img, box, 0, blur=8, k=0.5, off=(0, 4))
    d = K.BD(img)
    d.rectangle(box, fill=(5, 13, 28, 236), outline=col + (230,), width=1)
    if bright:
        img = K.add_glow(img, K.rect_mask(img.size, box), col, 6, 0.12)
    K.text(img, (box[0] + pad, (box[1] + box[3]) / 2), s, f, col, "lm", 0.8)
    return img, box


def key_strip(img, x, y, items, hint="HOVER: SHOW ALL", accent=CYAN, scale=1.0, hot=False):
    """The collapsed map legend: a single terminal key strip (expands on hover / [K])."""
    f = F(K.MONO, int(15 * scale))
    widths = [int(30 * scale + f.getlength(lab) + 18 * scale) for _, lab in items]
    tail = f.getlength("|  " + hint) + 20 * scale
    w = sum(widths) + tail + 20 * scale
    h = int(40 * scale)
    box = (x, y, x + w, y + h)
    img = term(img, box, None, accent=LIME if hot else accent, header=False, seed=33, chamfer=int(10 * scale))
    xx = x + 12 * scale
    for (ic, lab), ww in zip(items, widths):
        icon = ic(int(24 * scale))
        img.alpha_composite(icon, (int(xx), int(y + h / 2 - icon.height / 2)))
        K.text(img, (xx + 28 * scale, y + h / 2), lab, f, (215, 225, 232), "lm", 0.6)
        xx += ww
    K.text(img, (xx, y + h / 2), "|  " + hint, f, LIME if hot else accent, "lm", 0.8)
    return img, box


def cursor(img, x, y, scale=1.0):
    pts = [(0, 0), (0, 26), (7, 20), (12, 31), (17, 29), (12, 18), (21, 18)]
    pts = [(x + px * scale, y + py * scale) for px, py in pts]
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    img = K.over(img, (0, 0, 0), SL.shift(m, 2, 3).filter(ImageFilter.GaussianBlur(2)), 0.6)
    d = K.BD(img)
    d.polygon(pts, fill=(250, 250, 250, 255), outline=(10, 10, 14, 255))
    return img


def label(img, xy, s, size=15, col=(150, 150, 166)):
    return K.text(img, xy, s, F(K.MONO, size), col, "la", 0.6)


def soft_l(box, blur=30, size=(W, H)):
    """Soft rectangle as an L mask (for K.over darkening bands)."""
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rectangle(box, fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur))
