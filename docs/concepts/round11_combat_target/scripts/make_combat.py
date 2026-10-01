"""Round 11: combat screen mockups over the authored target-building backdrop (target_scene.py + backdrop.py).
(Round 10 composed over the round 6 city; city_base() is kept for comparison but no longer used.)

python make_combat.py render    # wheels -> ../scratch/combat
python make_combat.py compose   # combat_night_regular.png, combat_night_boss.png, combat_day_boss.png
python make_combat.py all

Base: the city crop framed on the Meridian district (art_asset C4), blurred, desaturated and dimmed,
with darker pools under each wheel and a darker band under the hand. Wheels then light the city:
their emission is blurred and multiplied back into the base (light spill).
Overlay kit: vinyl die-cut stickers (name plate, SEND IT, the cards), yellow / red grease pencil.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "combat")
CITY = os.path.join(OUT, "..", "round6_city_restyle", "views")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
from slicelib import f_num, f_ui, f_mono, glyph_rgba, PROGRAMS, R_OUT, bloom, CORPS
import roster_wheel as RW
import screens10 as S10
import combat_specs as CS
import combat_wheel as CWL

W, H = 1920, 1080
PINK = (255, 61, 168)
ORANGE = CORPS["meridian"]["col"]
YELLOW = (255, 214, 64)
GP_YELLOW = (255, 226, 0)   # grease pencil: saturated plan yellow
GP_RED = (255, 28, 44)      # grease pencil: saturated threat red
RED = (255, 64, 72)
HPG = (123, 224, 123)
INK = (14, 12, 20)
CROP = (436, 66, 2356, 1146)  # Meridian district sits behind the enemy wheel

# layout (screen px)
PLAYER = dict(c=(480, 482), r=240)
ENEMY = dict(c=(1430, 470), r=215)
BOSS = dict(c=(1450, 500), r=258)  # 120 % of the regular


# ================================================================== renders
def render_wheels():
    os.makedirs(CACHE, exist_ok=True)
    S10.select(virus="OOZE", proxy="TURN")
    jobs = [("player", CS.player(41, 8)[0]), ("player_b", CS.player(41, 14)[0]),
            ("regular", CS.regular(30, 7)[0]), ("boss", CS.boss(340, 8)[0])]
    for key, spec in jobs:
        im, c = CWL.render(spec, ss=2)
        im.save(os.path.join(CACHE, key + ".png"))
        with open(os.path.join(CACHE, key + ".txt"), "w") as f:
            f.write("%d %d" % c)
        print("wheel", key, flush=True)


def load_wheel(key, r):
    im = Image.open(os.path.join(CACHE, key + ".png")).convert("RGBA")
    cx, cy = map(int, open(os.path.join(CACHE, key + ".txt")).read().split())
    k = r / R_OUT
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    return im, (cx * k, cy * k)


# ================================================================== base
BACKDROPS = os.path.join(OUT, "scratch", "backdrops")


def target_base(variant, mode, pools):
    """Round 11: the authored close-up of the target building (backdrop.py), calmed behind the wheels:
    darker and softer inside each wheel's pool, darker hand band and top bar; the building stays crisp
    in the centre gap and along the top."""
    day = mode.startswith("day")
    src = Image.open(os.path.join(BACKDROPS, "%s_%s.png" % (variant, mode))).convert("RGB")
    a = np.asarray(src, np.float32) / 255
    soft = np.asarray(src.filter(ImageFilter.GaussianBlur(3.5)), np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    pool = np.zeros((H, W), np.float32)
    for (cx, cy), R in pools:
        q = np.hypot(xx - cx, yy - cy) / (R * 1.02)
        pool = np.maximum(pool, np.exp(-q ** 4))
    a = a * (1 - pool[..., None]) + soft * pool[..., None]  # calmer detail behind the wheels
    dim = np.full((H, W), 0.80 if day else 0.86, np.float32)
    dim *= 1 - (0.50 if day else 0.55) * pool
    dim *= 1 - 0.55 * np.clip((yy - 800) / 260, 0, 1)
    dim *= 1 - 0.40 * np.clip((96 - yy) / 96, 0, 1)
    return a * dim[..., None]


def city_base(which, pools, day=False):
    src = Image.open(os.path.join(CITY, "restyle_%s_full.png" % which)).convert("RGB").crop(CROP)
    src = src.filter(ImageFilter.GaussianBlur(2.2))
    src = ImageEnhance.Color(src).enhance(0.62 if day else 0.75)
    a = np.asarray(src, np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dim = np.full((H, W), 0.72 if day else 0.52, np.float32)
    for (cx, cy), R in pools:  # darker pool behind each wheel so slices read first
        q = np.hypot(xx - cx, yy - cy) / (R * 1.35)
        dim *= 1 - (0.6 if day else 0.5) * np.exp(-q ** 4)
    dim *= 1 - 0.55 * np.clip((yy - 800) / 260, 0, 1)  # hand band
    dim *= 1 - 0.45 * np.clip((90 - yy) / 90, 0, 1)  # top bar
    vig = np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.7))
    dim *= np.clip(1.15 - 0.45 * vig ** 2, 0.45, 1)
    a = a * dim[..., None]
    if day:  # cool the day city slightly so warm UI still pops
        a = a * np.array([0.92, 0.96, 1.04], np.float32)
    return a


def light_spill(base, emit_rgba, k=1.7, add=0.18):
    """Wheel emission lights the city: blur the bright parts and multiply them into the base."""
    e = np.asarray(emit_rgba, np.float32) / 255
    rgb = e[..., :3] * e[..., 3:]
    lum = rgb.max(axis=2, keepdims=True)
    hot = rgb * np.clip((lum - 0.25) / 0.75, 0, 1)
    small = Image.fromarray((np.clip(hot, 0, 1) * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    b1 = np.asarray(small.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR), np.float32) / 255
    b2 = np.asarray(small.filter(ImageFilter.GaussianBlur(30)).resize((W, H), Image.BILINEAR), np.float32) / 255
    spill = b1 * 0.6 + b2 * 1.4
    return base * (1 + k * spill) + spill * add


def to_rgba(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


# ================================================================== overlay kit
def vinyl(body, border=7, tilt=0.0, shadow=0.55, gloss=True):
    """Die-cut vinyl sticker: white cut margin around the body's alpha, soft drop shadow, gloss band."""
    pad = border + 18
    b = Image.new("RGBA", (body.width + 2 * pad, body.height + 2 * pad), (0, 0, 0, 0))
    b.alpha_composite(body, (pad, pad))
    a = b.split()[3].point(lambda v: 255 if v > 40 else 0)
    cut = a.filter(ImageFilter.MaxFilter(2 * border + 1)).filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 120 else 0)
    out = Image.new("RGBA", b.size, (0, 0, 0, 0))
    out.paste((246, 244, 238, 255), (0, 0), cut)
    out.alpha_composite(b)
    if gloss:
        g = Image.new("L", b.size, 0)
        dg = ImageDraw.Draw(g)
        w, h = b.size
        dg.polygon([(w * 0.18, 0), (w * 0.34, 0), (w * 0.14, h), (w * -0.02, h)], fill=60)
        dg.polygon([(w * 0.40, 0), (w * 0.45, 0), (w * 0.25, h), (w * 0.20, h)], fill=38)
        g = g.filter(ImageFilter.GaussianBlur(3))
        g = Image.fromarray(np.minimum(np.asarray(g), np.asarray(cut)).astype(np.uint8))
        out.paste((255, 255, 255, 255), (0, 0), Image.fromarray((np.asarray(g) * 1.0).astype(np.uint8)))
        # re-composite so gloss is translucent
        base = Image.new("RGBA", b.size, (0, 0, 0, 0))
        base.paste((246, 244, 238, 255), (0, 0), cut)
        base.alpha_composite(b)
        wl = Image.new("RGBA", b.size, (255, 255, 255, 0))
        wl.putalpha(g)
        base.alpha_composite(wl)
        out = base
    if tilt:
        out = out.rotate(tilt, resample=Image.BICUBIC, expand=True)
    if shadow:
        sh = out.split()[3].filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * shadow))
        s = Image.new("RGBA", (out.width + 12, out.height + 14), (0, 0, 0, 0))
        sl = Image.new("RGBA", out.size, (0, 0, 0, 255))
        sl.putalpha(sh)
        s.alpha_composite(sl, (5, 9))
        s.alpha_composite(out, (0, 0))
        out = s
    return out


def grease(layer, pts, col, width=6, seed=1, closed=False, alpha=0.96):
    """Grease pencil (round 11): near-opaque, thick, waxy. A dark under-shadow keeps it readable on day and
    night backdrops; the stroke has a rough waxy edge, a lighter sheen line and only small grain dropouts."""
    rng = np.random.default_rng(seed)
    width = int(round(width * 1.7))
    dense = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + ([pts[0]] if closed else [])):
        L = max(1, int(math.hypot(x1 - x0, y1 - y0) / 6))
        for i in range(L):
            t = i / L
            dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    dense.append(pts[-1] if not closed else pts[0])
    j = np.cumsum(rng.normal(0, 0.45, (len(dense), 2)), axis=0)
    j -= np.linspace(0, 1, len(dense))[:, None] * j[-1]
    dense = [(x + jx, y + jy) for (x, y), (jx, jy) in zip(dense, j)]
    m = Image.new("L", layer.size, 0)
    dm = ImageDraw.Draw(m)
    dm.line(dense, fill=255, width=width, joint="curve")
    for p in (dense[0], dense[-1]):
        dm.ellipse([p[0] - width / 2, p[1] - width / 2, p[0] + width / 2, p[1] + width / 2], fill=255)
    # under-shadow
    sh = np.asarray(m.filter(ImageFilter.GaussianBlur(2.2)), np.float32) / 255 * 0.75
    sh = np.roll(np.roll(sh, 3, 0), 2, 1)
    sl = Image.new("RGBA", layer.size, (14, 8, 16, 0))
    sl.putalpha(Image.fromarray((np.clip(sh, 0, 1) * 255).astype(np.uint8)))
    layer.alpha_composite(sl)
    # waxy body: rough edge (noise-eroded) + small dropouts
    h, w = layer.size[1], layer.size[0]
    grain = rng.random((h, w)).astype(np.float32)
    body = np.asarray(m.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
    edge = (body > 0.05) & (body < 0.75)
    body = np.where(edge, body * (0.55 + 0.6 * grain), body)
    body = body * np.where(grain > 0.965, 0.55, 1.0)
    st = Image.new("RGBA", layer.size, col + (0,))
    st.putalpha(Image.fromarray((np.clip(body * alpha, 0, 1) * 255).astype(np.uint8)))
    layer.alpha_composite(st)
    # sheen: a thin lighter wax line along the stroke
    hi = Image.new("L", layer.size, 0)
    ImageDraw.Draw(hi).line([(x - width * 0.18, y - width * 0.18) for x, y in dense], fill=255, width=max(1, width // 4), joint="curve")
    ha = np.asarray(hi.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255 * (0.25 + 0.3 * grain)
    light = tuple(min(255, int(v + (255 - v) * 0.55)) for v in col)
    hl = Image.new("RGBA", layer.size, light + (0,))
    hl.putalpha(Image.fromarray((np.clip(ha, 0, 1) * 255).astype(np.uint8)))
    layer.alpha_composite(hl)

def bezier(p0, p1, p2, n=30):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]


def grease_arrow(layer, p0, p1, p2, col, width=6, seed=2):
    pts = bezier(p0, p1, p2)
    grease(layer, pts, col, width, seed)
    (xa, ya), (xb, yb) = pts[-4], pts[-1]
    ang = math.atan2(yb - ya, xb - xa)
    for s in (-1, 1):
        a = ang + math.pi + s * 0.5
        grease(layer, [(xb, yb), (xb + 30 * math.cos(a), yb + 30 * math.sin(a))], col, width, seed + 3 + s)


def grease_loop(layer, c, rx, ry, col, width=6, seed=4, turns=1.18, tilt=-0.15):
    pts = []
    n = 48
    for i in range(int(n * turns) + 1):
        t = i / n * 2 * math.pi + 2.2
        k = 1 + 0.06 * math.sin(i * 0.4)
        x, y = rx * k * math.cos(t), ry * k * math.sin(t)
        pts.append((c[0] + x * math.cos(tilt) - y * math.sin(tilt), c[1] + x * math.sin(tilt) + y * math.cos(tilt)))
    grease(layer, pts, col, width, seed)


# ================================================================== HUD pieces
def plate(d, box, acc, fill=(10, 9, 15, 228)):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=8, fill=fill, outline=acc + (150,), width=2)
    d.rectangle([x0 + 2, y0 + 6, x0 + 7, y1 - 6], fill=acc + (255,))


def pips(d, x, y, n, on, col):
    for i in range(n):
        d.ellipse([x + i * 18, y, x + i * 18 + 12, y + 12], fill=col + (255,) if i < on else (60, 60, 70, 255), outline=(10, 8, 14, 255))
    return x + n * 18


def chip(d, x, y, text, col, font, fill=(16, 14, 22, 255)):
    tw = font.getlength(text)
    d.rounded_rectangle([x, y, x + tw + 16, y + 28], radius=6, fill=fill, outline=col + (255,), width=2)
    d.text((x + 8, y + 3), text, font=font, fill=col + (255,))
    return x + tw + 24


def forecast_tag(img, x, y, who, prog, value, aim, chips, acc, width=None, caption="THIS TURN"):
    d = ImageDraw.Draw(img)
    fc = f_ui(18, b"Bold Condensed")
    w = width or 440
    plate(d, [x, y, x + w, y + 116], acc)
    d.text((x + 18, y + 6), "%s  -  %s" % (who, caption), font=f_ui(15, b"Bold SemiCondensed"), fill=(190, 190, 205, 255))
    g = glyph_rgba(prog, 30, 2.5)
    img.alpha_composite(g, (x + 16, y + 30))
    col = PROGRAMS[prog]["col"]
    fn = f_num(32)
    d.text((x + 56, y + 27), "%s %s" % (prog, value), font=fn, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=INK + (255,))
    xx = x + 64 + fn.getlength("%s %s" % (prog, value))
    pips(d, xx, y + 42, 3, aim, YELLOW)
    d.text((xx + 60, y + 38), ["", "PARTIAL", "GOOD", "PERFECT"][aim], font=f_ui(15, b"Bold SemiCondensed"), fill=YELLOW + (255,))
    cx = x + 16
    for t, c in chips:  # one result chip per effect, inside the tag
        cx = chip(d, cx, y + 76, t, c, fc)


def next_plate(img, x, y, nxt, delta, acc, lethal=False):
    d = ImageDraw.Draw(img)
    f = f_num(28)
    s = "NEXT %d  (%+d)" % (nxt, delta)
    tw = f.getlength(s)
    plate(d, [x, y, x + tw + 34, y + 44], RED if lethal else acc)
    d.text((x + 20, y + 5), s, font=f, fill=(255, 255, 255, 255))
    return x + tw + 34


def hp_number(img, c, R, hp, hpmax):
    d = ImageDraw.Draw(img)
    f = f_num(62)
    s = "%d/%d" % (hp, hpmax)
    tw = f.getlength(s)
    x, y = c[0] - tw / 2, c[1] + R * (436 / 360) * 1.0 + 26
    d.text((x, y), s, font=f, fill=HPG + (255,), stroke_width=3, stroke_fill=(6, 16, 8, 255))
    return (x, y, x + tw, y + 66)


def nameplate_hud(img, x, y, name, sub, acc, anchor="l"):
    d = ImageDraw.Draw(img)
    f1, f2 = f_num(34), f_ui(16, b"Bold SemiCondensed")
    w = max(f1.getlength(name), f2.getlength(sub)) + 40
    if anchor == "r":
        x = x - w
    plate(d, [x, y, x + w, y + 66], acc)
    d.text((x + 20, y + 4), name, font=f1, fill=(255, 255, 255, 255))
    d.text((x + 20, y + 42), sub, font=f2, fill=acc + (255,))


def nudge_buttons(img, c, R):
    d = ImageDraw.Draw(img)
    for s, lab, key in ((-1, "<", "Q"), (1, ">", "E")):
        x = c[0] + s * (R * 1.32)
        y = c[1] + R * 0.86
        r = 24
        d.ellipse([x - r, y - r, x + r, y + r], fill=(16, 14, 22, 235), outline=PINK + (255,), width=3)
        a0 = -150 if s < 0 else -30
        pts = [(x + 12 * math.cos(math.radians(a)), y + 12 * math.sin(math.radians(a))) for a in np.linspace(200, 340, 8)]
        if s > 0:
            pts = pts[::-1]
        d.line(pts, fill=(255, 255, 255, 255), width=3)
        hx, hy = pts[-1]
        d.polygon([(hx, hy - 6), (hx + 7 * -s * -1, hy + 1), (hx, hy + 7)], fill=(255, 255, 255, 255))
        f = f_ui(13, b"Bold Condensed")
        d.text((x - 4, y + r + 2), key, font=f, fill=(170, 170, 185, 255))


def ram_meter(img, x, y, have, maxr, spend):
    d = ImageDraw.Draw(img)
    plate(d, [x, y, x + 400, y + 92], (92, 225, 255))
    d.text((x + 20, y + 6), "RAM", font=f_ui(16, b"Bold SemiCondensed"), fill=(190, 190, 205, 255))
    f = f_num(40)
    d.text((x + 20, y + 26), "%d/%d" % (have, maxr), font=f, fill=(92, 225, 255, 255))
    cx = x + 120
    for i in range(maxr):
        x0 = cx + i * 22
        box = [x0, y + 32, x0 + 16, y + 62]
        if i < have - spend:
            d.rounded_rectangle(box, radius=3, fill=(92, 225, 255, 255))
        elif i < have:  # about to be spent: hatched
            d.rounded_rectangle(box, radius=3, fill=(20, 40, 50, 255), outline=(220, 250, 255, 255), width=2)
            d.line([(x0 + 2, y + 58), (x0 + 14, y + 36)], fill=(220, 250, 255, 255), width=2)
        else:
            d.rounded_rectangle(box, radius=3, fill=(26, 34, 42, 255))
    d.text((cx, y + 68), "-%d on CORRUPT PACKET" % spend, font=f_mono(13, False), fill=(200, 230, 240, 255))


def piles(img, x, y):
    d = ImageDraw.Draw(img)
    f = f_ui(16, b"Bold SemiCondensed")
    for i, (lab, n) in enumerate((("DECK", 6), ("DISCARD", 3))):
        xx = x + i * 108
        for k in range(3):
            d.rounded_rectangle([xx + k * 3, y - k * 3, xx + 56 + k * 3, y + 74 - k * 3], radius=6, fill=(30, 28, 38, 255), outline=(90, 88, 104, 255), width=2)
        d.text((xx + 10, y + 16), str(n), font=f_num(34), fill=(255, 255, 255, 255))
        d.text((xx + 2, y + 80), lab, font=f, fill=(170, 170, 185, 255))


def status_bar(img, text, sub):
    d = ImageDraw.Draw(img)
    f = f_num(30)
    tw = max(f.getlength(text), f_mono(14).getlength(sub)) + 60
    x = W / 2 - tw / 2
    d.rounded_rectangle([x, 12, x + tw, 74], radius=10, fill=(10, 9, 15, 230), outline=(80, 78, 96, 255), width=2)
    d.text((W / 2 - f.getlength(text) / 2, 16), text, font=f, fill=(255, 255, 255, 255))
    d.text((W / 2 - f_mono(14).getlength(sub) / 2, 52), sub, font=f_mono(14), fill=(170, 170, 185, 255))


def small_button(img, x, y, label, sub, acc):
    d = ImageDraw.Draw(img)
    f = f_ui(19, b"Bold SemiCondensed")
    tw = max(f.getlength(label), f_mono(12).getlength(sub)) + 28
    d.rounded_rectangle([x, y, x + tw, y + 52], radius=8, fill=(16, 14, 22, 235), outline=acc + (255,), width=2)
    d.text((x + 14, y + 5), label, font=f, fill=(240, 240, 248, 255))
    d.text((x + 14, y + 31), sub, font=f_mono(12), fill=acc + (255,))
    return x + tw + 12


# ================================================================== cards (C-C vinyl sticker cards)
CARDS = [
    dict(name="FLICK", cost=0, kind="WHEEL", col=(255, 196, 40), art="SPIN", val="1", pic="SPIN", text="Spin a wheel 1 tick.", rar=1),
    dict(name="GHOST STEP", cost=1, kind="WHEEL", col=(255, 196, 40), art="EM_GHOST", val="2", pic="NUDGE", text="Two nudges on an enemy wheel, ignoring resistance.", rar=2),
    dict(name="CORRUPT PACKET", cost=1, kind="HACK", col=(255, 61, 168), art="SEG_CORRUPT", val="", pic="SEG_CORRUPT", text="CORRUPT the enemy slice under your pointer.", rar=1),
    dict(name="BULWARK", cost=2, kind="SYSTEM", col=(92, 225, 255), art="FIREWALL", val="12", pic="FIREWALL", text="Gain 12 block.", rar=2),
    dict(name="HEAVY SPIN", cost=2, kind="WHEEL", col=(255, 196, 40), art="SPIN", val="9", pic="SPIN", text="Spin a wheel 9 ticks.", rar=1),
]


def spin_glyph(px, col=(255, 255, 255)):
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(3, px // 7)
    d.arc([w, w, px - w, px - w], 40, 330, fill=INK + (255,), width=w + 4)
    d.arc([w, w, px - w, px - w], 40, 330, fill=col + (255,), width=w)
    a = math.radians(40)
    cx, cy, r = px / 2, px / 2, px / 2 - w
    hx, hy = cx + r * math.cos(a), cy + r * math.sin(a)
    d.polygon([(hx - w * 1.8, hy - w * 0.6), (hx + w * 1.4, hy - w * 1.6), (hx + w * 0.6, hy + w * 1.8)], fill=col + (255,), outline=INK + (255,))
    return im


def nudge_glyph(px):
    return glyph_rgba("SEG_ACCEL", px, max(2, px * 0.07))


def card_img(c, w=210, h=280, state="hand"):
    S = 2
    W2, H2 = w * S, h * S
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = c["col"]
    dark = tuple(int(v * 0.28) for v in col)
    d.rounded_rectangle([0, 0, W2 - 1, H2 - 1], radius=22 * S, fill=dark + (255,))
    # art box
    ax0, ay0, ax1, ay1 = 14 * S, 50 * S, W2 - 14 * S, int(H2 * 0.55)
    art = Image.new("RGBA", (ax1 - ax0, ay1 - ay0), (0, 0, 0, 0))
    da = ImageDraw.Draw(art)
    for i in range(art.height):
        k = i / art.height
        da.line([(0, i), (art.width, i)], fill=tuple(int(v * (0.55 - 0.3 * k)) for v in col) + (255,))
    rng = np.random.default_rng(len(c["name"]))
    for _ in range(14):  # faceted shards (round 4 C-C look)
        x, y = rng.random() * art.width, rng.random() * art.height
        s = 30 * S * (0.5 + rng.random())
        da.polygon([(x, y), (x + s, y + s * 0.3), (x + s * 0.2, y + s)], fill=tuple(int(v * (0.3 + 0.4 * rng.random())) for v in col) + (120,))
    gp = int(art.height * 0.78)
    g = spin_glyph(gp) if c["art"] == "SPIN" else glyph_rgba(c["art"], gp, gp * 0.06)
    art.alpha_composite(g, ((art.width - g.width) // 2, (art.height - g.height) // 2))
    im.alpha_composite(art, (ax0, ay0))
    # type band
    by = ay1
    d.rectangle([ax0, by, ax1, by + 24 * S], fill=col + (255,))
    ft = f_ui(15 * S, b"Bold SemiCondensed")
    d.text((W2 / 2 - ft.getlength(c["kind"]) / 2, by + 3 * S), c["kind"], font=ft, fill=INK + (255,))
    # title
    fti = f_num(22 * S)
    title = c["name"]
    while fti.getlength(title) > W2 - 80 * S:
        fti = f_num(int(fti.size * 0.92))
    d.text((60 * S, 13 * S), title, font=fti, fill=(255, 255, 255, 255))
    # value line
    vy = by + 30 * S
    pg = 32 * S
    pic = spin_glyph(pg) if c["pic"] == "SPIN" else (nudge_glyph(pg) if c["pic"] == "NUDGE" else glyph_rgba(c["pic"], pg, pg * 0.07))
    vx = ax0 + 6 * S
    im.alpha_composite(pic, (vx, vy))
    if c["val"]:
        fv = f_num(32 * S)
        d.text((vx + pic.width + 4 * S, vy - 2 * S), c["val"], font=fv, fill=(255, 255, 255, 255), stroke_width=2 * S, stroke_fill=INK + (255,))
    # rules text
    fr = f_ui(13 * S, b"SemiBold")
    words, lines, cur = c["text"].split(), [], ""
    for wd in words:
        if fr.getlength((cur + " " + wd).strip()) > W2 - 40 * S:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    ty = vy + 38 * S
    for ln in lines:
        d.text((W2 / 2 - fr.getlength(ln) / 2, ty), ln, font=fr, fill=(236, 236, 244, 255))
        ty += 17 * S
    for i in range(c["rar"]):
        x = W2 - 26 * S - i * 14 * S
        d.ellipse([x, H2 - 22 * S, x + 9 * S, H2 - 13 * S], fill=(92, 225, 255, 255) if c["rar"] == 1 else (255, 214, 64, 255))
    # cost coin
    r = 21 * S
    d.ellipse([10 * S, 8 * S, 10 * S + 2 * r, 8 * S + 2 * r], fill=YELLOW + (255,), outline=INK + (255,), width=3 * S)
    fc = f_num(30 * S)
    s = str(c["cost"])
    d.text((10 * S + r - fc.getlength(s) / 2, 8 * S + 3 * S), s, font=fc, fill=INK + (255,))
    im = im.resize((w, h), Image.LANCZOS)
    return vinyl(im, border=6, shadow=0.6)


# ================================================================== compose
def compose(kind, which, variant=None):
    boss = kind == "boss"
    day = which.startswith("day")
    variant = variant or ("boss" if boss else "regular")
    E = BOSS if boss else ENEMY
    pk = "player_b" if boss else "player"
    pw, pc = load_wheel(pk, PLAYER["r"])
    ew, ec = load_wheel("boss" if boss else "regular", E["r"])
    pools = [(PLAYER["c"], PLAYER["r"] * 1.12), (E["c"], E["r"] * 1.12)]
    base = target_base(variant, which, pools)
    # emission layer (wheels only) for the light spill
    emit = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ppos = (int(PLAYER["c"][0] - pc[0]), int(PLAYER["c"][1] - pc[1]))
    epos = (int(E["c"][0] - ec[0]), int(E["c"][1] - ec[1]))
    emit.alpha_composite(pw, ppos)
    emit.alpha_composite(ew, epos)
    base = light_spill(base, emit, k=0.7 if day else 1.4, add=0.05 if day else 0.14)
    img = to_rgba(base)
    # soft contact shadow under each wheel so it sits on the city
    sh = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(sh)
    for (c, R) in ((PLAYER["c"], PLAYER["r"] * 1.14), (E["c"], E["r"] * 1.14)):
        ds.ellipse([c[0] - R, c[1] - R + 14, c[0] + R, c[1] + R + 14], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    shl = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shl.putalpha(sh)
    img.alpha_composite(shl)
    img.alpha_composite(pw, ppos)
    img.alpha_composite(ew, epos)
    img = bloom(img.convert("RGB"), 1, 0.32, 0.66).convert("RGBA")

    # ------------------------------------------------ HUD
    status_bar(img, "TURN 3   |   FREE NUDGE 1", "NETRUN // MERIDIAN FREIGHT // LANE 15 DEPOT // " + ("BOSS: THE MANIFEST" if boss else "FIGHT 2 OF 4"))
    p_r = PLAYER["r"]
    pb = hp_number(img, PLAYER["c"], p_r, 41, 60)
    ploss = 14 if boss else 8
    next_plate(img, int(pb[2]) + 16, int(pb[1]) + 12, 41 - ploss, -ploss, HPG)
    if boss:
        eb = hp_number(img, E["c"], E["r"] * (448 / 436), 340, 400)
        next_plate(img, int(eb[2]) + 16, int(eb[1]) + 12, 332, -8, ORANGE)
    else:
        eb = hp_number(img, E["c"], E["r"], 30, 48)
        next_plate(img, int(eb[2]) + 16, int(eb[1]) + 12, 23, -7, ORANGE)
    nudge_buttons(img, PLAYER["c"], p_r)
    # forecast tags
    forecast_tag(img, 30, 84, "YOU", "ZERO-DAY", 12, 2,
                 [("HIT 12 - %s = %d" % (("SHIELD 4" if boss else "BLOCK 5"), 8 if boss else 7), PINK),
                  ("RING x2 ON PERFECT", (200, 200, 215))], PINK, width=400)
    if boss:
        forecast_tag(img, 1590, 84, "THE MANIFEST", "EXPLOIT", 14, 3,
                     [("HIT 14 > YOU", RED), ("+4 SHIELD", ORANGE)], ORANGE, width=322)
    else:
        forecast_tag(img, 1450, 84, "ROUTE OPTIMIZER", "EXPLOIT", 8, 3,
                     [("HIT 8 -> YOU", RED), ("READER 2: FIREWALL +5", (92, 225, 255))], ORANGE, width=440)
    ram_meter(img, 30, 958, 5, 12, 1)
    piles(img, 450, 958)
    # buttons
    bx = small_button(img, 1370, 1010, "RESPIN", "4 RAM  [R]", (92, 225, 255))
    small_button(img, bx, 1006, "UNDO", "[Z]", (190, 190, 205))

    # ------------------------------------------------ cards (hand)
    hand_cx, hand_y = 1010, 846
    hov = 2
    n = len(CARDS)
    for i in list(range(n)):
        if i == hov:
            continue
        c = card_img(CARDS[i], 144, 192)
        off = i - (n - 1) / 2
        rot = -off * 4.5
        c = c.rotate(rot, resample=Image.BICUBIC, expand=True)
        x = hand_cx + off * 128 - c.width / 2
        y = hand_y + abs(off) ** 1.6 * 10 - 6
        img.alpha_composite(c, (int(x), int(y)))
    ch = card_img(CARDS[hov], 196, 262)
    hx = hand_cx + (hov - (n - 1) / 2) * 128 - ch.width / 2
    hy = hand_y - 104
    img.alpha_composite(ch, (int(hx), int(hy)))
    d = ImageDraw.Draw(img)
    fa = f_ui(16, b"Bold SemiCondensed")
    d.rounded_rectangle([int(hx) + 30, int(hy) - 30, int(hx) + 50 + fa.getlength("AIMED: ENEMY WHEEL"), int(hy) - 4], radius=6, fill=(10, 9, 15, 235))
    d.text((int(hx) + 40, int(hy) - 27), "AIMED: ENEMY WHEEL", font=fa, fill=YELLOW + (255,))

    # ------------------------------------------------ overlay marks (max 5)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # 1 vinyl name sticker on the player wheel
    body = Image.new("RGBA", (330, 62), (0, 0, 0, 0))
    db = ImageDraw.Draw(body)
    db.rounded_rectangle([0, 0, 329, 61], radius=12, fill=PINK + (255,))
    db.text((18, 6), "CELL-9 // BREAKER", font=f_num(40), fill=INK + (255,))
    st = vinyl(body, border=7, tilt=4)
    ov.alpha_composite(st, (PLAYER["c"][0] - p_r - 200, PLAYER["c"][1] + int(p_r * 0.98)))
    # 2 SEND IT vinyl sticker (the main verb)
    body = Image.new("RGBA", (300, 112), (0, 0, 0, 0))
    db = ImageDraw.Draw(body)
    db.polygon([(16, 0), (300, 0), (284, 112), (0, 112)], fill=YELLOW + (255,))
    db.text((30, 0), "SEND IT", font=f_num(86), fill=INK + (255,))
    db.text((206, 88), "[SPACE]", font=f_mono(14), fill=INK + (255,))
    st = vinyl(body, border=8, tilt=-3)
    ov.alpha_composite(st, (1536, 912))
    # 3 yellow grease-pencil aim arrow: hovered card -> enemy slice under its pointer
    pr = E["r"] * ((404 if boss else 390) / 360)
    loop_c = (E["c"][0], E["c"][1] - pr - 2)
    grease_arrow(ov, (hx + ch.width * 0.9, hy + 14), (1120, 200 if not boss else 260), (loop_c[0] - 56, loop_c[1] + 10), GP_YELLOW, 7, seed=11)
    # 4 yellow grease loop around the enemy pointer (the target), clear of the slice values
    grease_loop(ov, loop_c, 44, 33, GP_YELLOW, 6, seed=5)
    # 5 red grease pencil: threat underline + tally under the player's NEXT plate
    nx0 = int(pb[2]) + 16
    ny = int(pb[1]) + 64
    grease(ov, [(nx0 + 4, ny), (nx0 + 90, ny + 3), (nx0 + 190, ny - 1)], GP_RED, 6, seed=21)
    grease(ov, [(nx0 + 200, ny - 34), (nx0 + 204, ny - 8)], GP_RED, 7, seed=22)
    grease(ov, [(nx0 + 204, ny + 4), (nx0 + 205, ny + 6)], GP_RED, 8, seed=23)
    img.alpha_composite(ov)
    out = img.convert("RGB")
    name = "combat_%s_%s.png" % ("boss" if boss else "regular", "day_cool" if which == "daycool" else which)
    out.save(os.path.join(OUT, name))
    print("saved", name, flush=True)
    return out


def contact():
    files = ["slices_r11.png", "target_building_night.png", "combat_boss_night.png", "combat_boss_day.png", "combat_regular_night.png", "target_building_day.png"]
    tw, th = 960, 540
    sheet = Image.new("RGB", (tw * 2 + 30, th * 3 + 130), (10, 9, 14))
    d = ImageDraw.Draw(sheet)
    d.text((14, 8), "ROUND 11  -  combat over the target building (Meridian)", font=f_num(40), fill=(255, 255, 255))
    for i, fn in enumerate(files):
        im = Image.open(os.path.join(OUT, fn)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (i % 2) * (tw + 10), 64 + (i // 2) * (th + 22)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + th + 1), fn, font=f_mono(15, False), fill=(190, 190, 200))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("render", "all"):
        render_wheels()
    if what in ("compose", "all"):
        compose("regular", "night")
        compose("boss", "night")
        compose("boss", "day")
        contact()
    print("done")












