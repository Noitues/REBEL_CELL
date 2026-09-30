"""Pillow post-pass: painterly strokes, neon glow, haze grade, then the game UI.

python post.py <shot> <raw_png> <out_png>
(Pillow only, no numpy.  Seeded randomness only.)"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L  # noqa: E402

FD = "C:/Windows/Fonts/"


def font(name, size, var=None):
    f = ImageFont.truetype(FD + name, size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


def F_HEAD(s):
    return font("AGENCYB.TTF", s)


def F_BODY(s, bold=True):
    return font("bahnschrift.ttf", s, "Bold" if bold else "SemiBold")


def F_NUM(s):
    return font("consolab.ttf", s)


def c255(c, k=1.0):
    return tuple(max(0, min(255, int(255 * min(1.0, v) * k))) for v in c[:3])


# ------------------------------------------------------------------ painterly
def kuwahara(img, half):
    """Kuwahara oil-paint filter from Pillow primitives: for each pixel take the mean of the
    quadrant window with the smallest local range (flat painted patches, crisp edges)."""
    size = 2 * half + 1
    lum = img.convert("L")
    rng_img = ImageChops.subtract(lum.filter(ImageFilter.MaxFilter(size)), lum.filter(ImageFilter.MinFilter(size)))
    mean = img.filter(ImageFilter.BoxBlur(half))
    best, bestv = None, None
    for dx, dy in ((-half, -half), (half, -half), (-half, half), (half, half)):
        m = ImageChops.offset(mean, dx, dy)
        v = ImageChops.offset(rng_img, dx, dy)
        if best is None:
            best, bestv = m, v
            continue
        mask = ImageChops.subtract(bestv, v).point(lambda p: 255 if p > 0 else 0)
        best = Image.composite(m, best, mask)
        bestv = ImageChops.darker(bestv, v)
    return best


def painterly(img, seed, strokes=60000, amount=0.5, swirl_c=None, half=5, stroke_mix=0.35):
    rng = random.Random(seed)
    W, H = img.size
    soft = kuwahara(img, half)
    src = soft.filter(ImageFilter.GaussianBlur(1.5))
    canvas = soft.copy()
    d = ImageDraw.Draw(canvas)
    px = src.load()
    for _ in range(strokes):
        x, y = rng.uniform(0, W - 1), rng.uniform(0, H - 1)
        a = 0.9 * math.sin(x / 210.0 + 1.3) + 0.8 * math.cos(y / 160.0) + 0.4 * math.sin((x + y) / 90.0)
        if swirl_c:
            dx, dy = x - swirl_c[0], y - swirl_c[1]
            r = math.hypot(dx, dy)
            w = math.exp(-r / swirl_c[2])
            a = (1 - w) * a + w * (math.atan2(dy, dx) + math.pi / 2)
        ln = rng.uniform(4, 11)
        c = px[int(x), int(y)]
        j = rng.uniform(0.95, 1.06)
        c = tuple(min(255, int(v * j)) for v in c)
        ex, ey = math.cos(a) * ln, math.sin(a) * ln
        d.line([(x - ex, y - ey), (x + ex, y + ey)], fill=c, width=rng.choice((3, 4, 5)))
    canvas = canvas.filter(ImageFilter.SMOOTH_MORE)
    painted = Image.blend(soft, canvas, stroke_mix)
    return Image.blend(img, painted, amount)


def glow(img, thr=150, gain=2.2, radii=((6, 0.8), (22, 0.7), (60, 0.5))):
    bright = img.point(lambda v: 0 if v < thr else min(255, int((v - thr) * gain)))
    out = img
    for r, k in radii:
        g = bright.filter(ImageFilter.GaussianBlur(r))
        if k != 1.0:
            g = g.point(lambda v, k=k: int(v * k))
        out = ImageChops.screen(out, g)
    return out


def grade(img, lift=(20, 6, 34), vignette=0.55, tint=None, top_haze=None):
    W, H = img.size
    out = ImageChops.screen(img, Image.new("RGB", img.size, lift))
    if top_haze:
        grad = Image.linear_gradient("L").resize((W, H)).point(lambda v: int((255 - v) * top_haze[1]))
        out = Image.composite(Image.new("RGB", (W, H), top_haze[0]), out, grad) if False else \
            ImageChops.screen(out, Image.composite(Image.new("RGB", (W, H), top_haze[0]), Image.new("RGB", (W, H), 0), grad))
    if tint:
        out = Image.blend(out, ImageChops.multiply(out, Image.new("RGB", (W, H), tint[0])), tint[1])
    # radial vignette
    m = Image.radial_gradient("L").resize((W, H))
    m = m.point(lambda v: int(255 - vignette * max(0, v - 90) * 255 / 165))
    out = ImageChops.multiply(out, Image.merge("RGB", (m, m, m)))
    return out


def grain(img, seed, amt=10):
    n = Image.effect_noise(img.size, 40).point(lambda v: 128 + int((v - 128) * amt / 40))
    n = Image.merge("RGB", (n, n, n))
    return ImageChops.add(img, n, 1.0, -128)


# ------------------------------------------------------------------ UI drawing
class UI:
    def __init__(self, img):
        self.img = img.convert("RGBA")

    def text(self, xy, s, f, fill=(255, 255, 255), glow_col=None, anchor="mm", stroke=3, glow_r=9, stroke_fill=(16, 4, 28)):
        x, y = xy
        d = ImageDraw.Draw(self.img)
        bb = d.textbbox((x, y), s, font=f, anchor=anchor, stroke_width=stroke)
        pad = glow_r * 3 + 4
        box = (int(bb[0]) - pad, int(bb[1]) - pad, int(bb[2]) + pad, int(bb[3]) + pad)
        if glow_col:
            lay = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), glow_col + (0,))
            ld = ImageDraw.Draw(lay)
            ld.text((x - box[0], y - box[1]), s, font=f, anchor=anchor, fill=glow_col + (255,), stroke_width=stroke + 2, stroke_fill=glow_col + (255,))
            lay = lay.filter(ImageFilter.GaussianBlur(glow_r))
            self.img.alpha_composite(lay, (box[0], box[1]))
            self.img.alpha_composite(lay, (box[0], box[1]))
        d.text((x, y), s, font=f, anchor=anchor, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)

    def panel(self, box, fill=(14, 4, 28, 200), outline=None, r=12, width=2, glow_col=None):
        if glow_col:
            pad = 30
            lay = Image.new("RGBA", (int(box[2] - box[0]) + 2 * pad, int(box[3] - box[1]) + 2 * pad), glow_col + (0,))
            ImageDraw.Draw(lay).rounded_rectangle((pad, pad, pad + box[2] - box[0], pad + box[3] - box[1]), r, outline=glow_col + (255,), width=width + 4)
            lay = lay.filter(ImageFilter.GaussianBlur(8))
            self.img.alpha_composite(lay, (int(box[0]) - pad, int(box[1]) - pad))
        lay = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle(box, r, fill=fill, outline=outline, width=width)
        self.img.alpha_composite(lay)

    def bar(self, box, frac, col, back=(20, 6, 34, 220), outline=(255, 255, 255, 120)):
        self.panel(box, fill=back, outline=outline, r=(box[3] - box[1]) // 2, width=2, glow_col=col)
        x0, y0, x1, y1 = box
        fx = x0 + 3 + (x1 - x0 - 6) * frac
        lay = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle((x0 + 3, y0 + 3, fx, y1 - 3), (y1 - y0 - 6) // 2, fill=col + (255,))
        self.img.alpha_composite(lay)

    def paste_rot(self, layer, center, ang):
        r = layer.rotate(ang, resample=Image.BICUBIC, expand=True)
        self.img.alpha_composite(r, (int(center[0] - r.width / 2), int(center[1] - r.height / 2)))

    def result(self):
        return self.img.convert("RGB")


KIND_NAMES = {"safe": "SAFEHOUSE", "relay": "RELAY", "vault": "VAULT", "target": "TARGET",
              "market": "MARKET", "clinic": "CLINIC", "boss": "CORP HQ"}


def city_ui(img, anchors, mood):
    ui = UI(img)
    alarm = mood == "alarm"
    for nid, a in anchors["nodes"].items():
        col = c255(L.NODE_COLORS[a["kind"]])
        tx, ty = a["top"]
        here = nid == L.YOU_ARE_HERE
        if here:
            fN, fT = F_BODY(26), F_BODY(15, False)
            w = max(200, int(fN.getlength(a["label"])) + 44)
            box = (tx - w / 2, ty - 92, tx + w / 2, ty - 26)
            ui.panel(box, fill=(10, 30, 44, 225), outline=(170, 255, 255, 255), r=14, width=3, glow_col=(90, 230, 255))
            ui.text((tx, ty - 72), "YOU ARE HERE", fT, fill=(170, 255, 255))
            ui.text((tx, ty - 45), a["label"], fN, fill=(255, 255, 255), glow_col=(60, 200, 255), glow_r=6)
        else:
            fN, fT = F_BODY(21), F_BODY(13, False)
            w = max(120, int(fN.getlength(a["label"])) + 36)
            box = (tx - w / 2, ty - 70, tx + w / 2, ty - 18)
            ui.panel(box, fill=(16, 4, 30, 215), outline=col + (255,), r=11, width=2, glow_col=col)
            ui.text((tx, ty - 55), KIND_NAMES[a["kind"]], fT, fill=col, stroke=2)
            ui.text((tx, ty - 33), a["label"], fN, fill=(255, 255, 255), stroke=3)
    # HUD: title + time
    ui.panel((28, 24, 470, 112), fill=(14, 4, 28, 205), outline=(255, 90, 180, 255), r=14, glow_col=(255, 60, 160))
    ui.text((52, 50), "SECTOR 7  //  THE SPRAWL", F_HEAD(38), anchor="lm", glow_col=(255, 60, 160), glow_r=6)
    tstr = {"day": "DAY 4  ·  14:20", "night": "NIGHT 4  ·  23:40", "alarm": "NIGHT 4  ·  23:52"}[mood]
    ui.text((54, 90), tstr, F_BODY(20, False), fill=(255, 200, 150), anchor="lm", stroke=2)
    # suspicion meter
    frac = {"day": 0.18, "night": 0.36, "alarm": 0.93}[mood]
    col = (255, 40, 50) if alarm else ((255, 170, 40) if frac > 0.3 else (90, 230, 255))
    ui.panel((1402, 24, 1892, 112), fill=(14, 4, 28, 205), outline=col + (255,), r=14, glow_col=col)
    ui.text((1426, 50), "SUSPICION", F_HEAD(34), anchor="lm", glow_col=col, glow_r=6)
    ui.text((1866, 50), f"{int(frac * 100)}%", F_NUM(30), anchor="rm", fill=col)
    ui.bar((1426, 74, 1866, 96), frac, col)
    for k in range(1, 5):
        x = 1426 + (1866 - 1426) * k / 5
        ImageDraw.Draw(ui.img).line([(x, 76), (x, 94)], fill=(14, 4, 28, 255), width=3)
    if alarm:
        ui.panel((660, 24, 1260, 96), fill=(60, 0, 8, 225), outline=(255, 60, 60, 255), r=10, width=3, glow_col=(255, 30, 30))
        ui.text((960, 50), "LOCKDOWN  ·  CORP SWEEP ACTIVE", F_HEAD(38), fill=(255, 235, 225), glow_col=(255, 30, 30), glow_r=8)
        ui.text((960, 80), "searchlights hunting your cell · moves cost +1 heat", F_BODY(17, False), fill=(255, 170, 160), stroke=2)
    # legend
    kinds = ["target", "vault", "market", "relay", "clinic", "boss"]
    ui.panel((28, 986, 900, 1052), fill=(14, 4, 28, 200), outline=(160, 120, 255, 200), r=12)
    x = 52
    for k in kinds:
        c = c255(L.NODE_COLORS[k])
        d = ImageDraw.Draw(ui.img)
        d.ellipse((x, 1010, x + 18, 1028), fill=c, outline=(255, 255, 255))
        ui.text((x + 28, 1019), KIND_NAMES[k], F_BODY(18, False), anchor="lm", stroke=2)
        x += 30 + int(F_BODY(18, False).getlength(KIND_NAMES[k])) + 34
    ui.panel((1560, 986, 1892, 1052), fill=(14, 4, 28, 200), outline=(255, 170, 60, 220), r=12, glow_col=(255, 140, 40))
    ui.text((1584, 1019), "CREDITS", F_HEAD(30), anchor="lm", fill=(255, 210, 160))
    ui.text((1866, 1019), "240", F_NUM(30), anchor="rm", fill=(255, 190, 90))
    return ui.result()


def card_layer(name, cost, kind, text, price=None):
    w, h = L.CARD_W, L.CARD_H
    pad = 40
    lay = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    u = UI.__new__(UI)
    u.img = lay
    col = c255(L.SLICE_COLORS[kind])
    ox, oy = pad, pad
    ocx = ox + (-L.CARD_W / 2 / L.PPU + 0.08) * L.PPU + w / 2
    ocy = oy + (L.CARD_H / 2 / L.PPU - 0.08) * -L.PPU + h / 2
    u.text((ocx, ocy + 1), str(cost), F_NUM(28), fill=(255, 245, 225), stroke=3, stroke_fill=(60, 20, 0))
    u.text((ox + w / 2, oy + 184), name, F_BODY(22 if len(name) < 10 else 19), fill=(255, 255, 255), glow_col=col, glow_r=5)
    u.text((ox + w / 2, oy + 216), text, F_BODY(14, False), fill=(235, 225, 255), stroke=2)
    tag = {"atk": "ATTACK", "blk": "BLOCK", "hack": "HACK"}[kind]
    u.text((ox + w / 2, oy + 248), tag, F_HEAD(20), fill=col, stroke=2)
    return lay, None


def combat_ui(img):
    ui = UI(img)
    R = L.SPINNER_R_PX
    for key, sp in L.SPINNERS.items():
        cx, cy = sp["center"]
        col = c255(sp["color"])
        for a0, a1, kind, val in L.slice_geometry(sp):
            if kind == "empty":
                continue
            am = math.radians((a0 + a1) / 2)
            x, y = cx + 0.63 * R * math.cos(am), cy - 0.63 * R * math.sin(am)
            ui.text((x, y - 6), str(val), F_NUM(40), fill=(255, 255, 255), stroke=4, stroke_fill=(30, 0, 30))
            ui.text((x, y + 22), L.SLICE_TAGS[kind], F_BODY(15), fill=(255, 245, 230), stroke=3, stroke_fill=(30, 0, 30))
        # name plate
        nm = sp["name"]
        f = F_HEAD(36)
        w = int(f.getlength(nm)) + 60
        ui.panel((cx - w / 2, 36, cx + w / 2, 92), fill=(14, 4, 28, 210), outline=col + (255,), r=12, glow_col=col)
        ui.text((cx, 64), nm, f, glow_col=col, glow_r=6)
        # hp text
        hy = cy + L.HPBAR["dy"]
        ui.text((cx, hy), f"{sp['hp'][0]} / {sp['hp'][1]}", F_NUM(24), fill=(255, 255, 255), stroke=4, stroke_fill=(10, 0, 20))
        ui.text((cx - L.HPBAR["w"] / 2 - 14, hy), "HP", F_HEAD(28), anchor="rm", fill=col, stroke=3)
    # enemy intent + block badges
    ex, ey = L.SPINNERS["enemy"]["center"]
    ui.panel((ex - 150, 100, ex + 150, 134), fill=(60, 0, 20, 200), outline=(255, 80, 120, 255), r=10)
    ui.text((ex, 117), "INTENT:  ATK 8  ·  SHIELD 6", F_BODY(17), fill=(255, 210, 220), stroke=2)
    px_, py_ = L.SPINNERS["player"]["center"]
    ui.panel((px_ - 150, 100, px_ + 150, 134), fill=(0, 30, 50, 200), outline=(90, 220, 255, 255), r=10)
    ui.text((px_, 117), "BLOCK 4  ·  NEXT SPIN 5 ticks", F_BODY(17), fill=(200, 245, 255), stroke=2)
    ui.text((960, 430), "VS", F_HEAD(64), fill=(255, 240, 230), glow_col=(255, 80, 180), glow_r=12)
    # hand
    for k, (name, cost, kind, text) in enumerate(L.HAND):
        (cx, cy), ang = L.hand_card(k)
        lay, _ = card_layer(name, cost, kind, text)
        ui.paste_rot(lay, (cx, cy), ang)
    # GO
    gx, gy = L.GO_BTN["center"]
    ui.text((gx, gy - 4), "GO", F_HEAD(96), fill=(255, 255, 255), glow_col=(255, 120, 40), glow_r=12, stroke=4, stroke_fill=(90, 10, 30))
    ui.text((gx, gy + 76), "SPIN THE WHEELS", F_BODY(17), fill=(255, 210, 170), stroke=2)
    # RAM + piles
    ui.panel((40, 830, 300, 948), fill=(14, 4, 28, 210), outline=(255, 160, 60, 255), r=14, glow_col=(255, 140, 40))
    ui.text((66, 862), "RAM", F_HEAD(36), anchor="lm", fill=(255, 220, 170), glow_col=(255, 140, 40), glow_r=5)
    ui.text((276, 862), "3/4", F_NUM(32), anchor="rm", fill=(255, 190, 90))
    d = ImageDraw.Draw(ui.img)
    for i in range(4):
        x = 78 + i * 52
        pts = [(x, 896), (x + 16, 912), (x, 928), (x - 16, 912)]
        d.polygon(pts, fill=(255, 170, 50) if i < 3 else (50, 20, 50), outline=(255, 230, 190))
    ui.panel((40, 972, 300, 1044), fill=(14, 4, 28, 210), outline=(160, 120, 255, 220), r=12)
    ui.text((66, 1008), "DECK 14", F_HEAD(30), anchor="lm")
    ui.text((276, 1008), "BIN 6", F_HEAD(30), anchor="rm", fill=(200, 180, 255))
    ui.text((960, 1060), "", F_BODY(10))
    return ui.result()


def shop_ui(img):
    ui = UI(img)
    fs = F_HEAD(150)
    ui.text((968, 132), "BLACK MARKET", fs, fill=(255, 150, 40), glow_col=(255, 110, 20), glow_r=16, stroke=0)
    ui.text((960, 124), "BLACK MARKET", fs, fill=(255, 225, 245), glow_col=(255, 40, 160), glow_r=14, stroke=4, stroke_fill=(255, 60, 170))
    ui.text((960, 222), "no names  ·  no logs  ·  no refunds", F_BODY(22, False), fill=(255, 205, 230), glow_col=(255, 60, 160), glow_r=6)
    ui.text((560, 392), "PROGRAMS", F_HEAD(40), fill=(255, 235, 250), glow_col=(255, 60, 160), glow_r=8)
    ui.text((1400, 392), "WHEEL MODS", F_HEAD(40), fill=(230, 250, 255), glow_col=(60, 200, 255), glow_r=8)
    for k, (name, kind, price, text) in enumerate(L.SHOP_CARDS):
        cx = L.SHOP_CARD_XS[k]
        lay, _ = card_layer(name, [1, 1, 1][k], kind, text)
        ui.paste_rot(lay, (cx, L.SHOP_ROW_Y), (k - 1) * -2.0)
        price_tag(ui, cx, price)
    for k, (name, kind, price, text) in enumerate(L.SHOP_PARTS):
        cx = L.SHOP_PART_XS[k]
        ui.text((cx, 700), name, F_BODY(21), glow_col=(255, 120, 60) if k == 0 else (60, 200, 255), glow_r=5)
        ui.text((cx, 726), text, F_BODY(15, False), fill=(230, 220, 255), stroke=2)
        price_tag(ui, cx, price)
    # credits + leave
    ui.panel((1560, 30, 1892, 100), fill=(14, 4, 28, 210), outline=(255, 170, 60, 230), r=12, glow_col=(255, 140, 40))
    ui.text((1584, 65), "CREDITS", F_HEAD(32), anchor="lm", fill=(255, 210, 160))
    ui.text((1866, 65), str(L.CREDITS), F_NUM(32), anchor="rm", fill=(255, 190, 90))
    lx, ly = L.LEAVE_BTN["center"]
    ui.text((lx, ly - 2), "‹ LEAVE", F_HEAD(52), glow_col=(60, 160, 255), glow_r=10, stroke=3, stroke_fill=(10, 10, 60))
    ui.panel((560, 1000, 1360, 1050), fill=(14, 4, 28, 190), outline=(160, 120, 255, 180), r=12)
    ui.text((960, 1025), "drag a program into your deck  ·  wheel mods fit your spinner  ·  reroll stock 25 cr",
            F_BODY(17, False), fill=(225, 215, 255), stroke=2)
    return ui.result()


def price_tag(ui, cx, price):
    box = (cx - 74, 800, cx + 74, 850)
    affordable = price <= L.CREDITS
    col = (255, 180, 60) if affordable else (150, 120, 160)
    ui.panel(box, fill=(30, 10, 10, 225), outline=col + (255,), r=24, width=3, glow_col=col)
    d = ImageDraw.Draw(ui.img)
    d.ellipse((cx - 58, 813, cx - 34, 837), fill=(255, 190, 60), outline=(255, 240, 200), width=2)
    ui.text((cx - 46, 825), "c", F_BODY(16), fill=(90, 40, 0), stroke=0)
    ui.text((cx + 14, 825), f"{price}", F_NUM(30), fill=(255, 240, 210), stroke=3, stroke_fill=(40, 10, 0))


def main():
    shot, raw, out = sys.argv[1], sys.argv[2], sys.argv[3]
    img = Image.open(raw).convert("RGB")
    seed = L.SEED + sum(map(ord, shot))
    if shot.startswith("city"):
        mood = {"city_day": "day", "city_night": "night", "city_suspicion": "alarm"}[shot]
        img = painterly(img, seed, strokes=30000, amount=0.75, swirl_c=(955, 150, 420), half=2, stroke_mix=0.22)
        if mood == "day":
            img = ImageEnhance.Contrast(img).enhance(1.18)
            img = ImageEnhance.Color(img).enhance(1.25)
            img = glow(img, thr=205, gain=1.6, radii=((8, 0.5), (30, 0.45), (80, 0.35)))
            img = grade(img, lift=(14, 6, 24), vignette=0.35, top_haze=((255, 170, 150), 0.18))
        elif mood == "night":
            img = glow(img, thr=140, gain=2.2)
            img = grade(img, lift=(10, 3, 20), vignette=0.55, top_haze=((150, 40, 140), 0.25))
        else:
            img = glow(img, thr=140, gain=2.2)
            img = grade(img, lift=(14, 2, 8), vignette=0.7, top_haze=((170, 20, 30), 0.3))
        img = grain(img, seed, 6)
        anchors = json.load(open(raw + ".json"))
        img = city_ui(img, anchors, mood)
    elif shot == "combat":
        img = painterly(img, seed, strokes=30000, amount=0.7, swirl_c=(960, 430, 500), half=2, stroke_mix=0.2)
        img = glow(img, thr=150, gain=2.0)
        img = grade(img, lift=(12, 4, 24), vignette=0.5, top_haze=((140, 30, 130), 0.2))
        img = grain(img, seed, 5)
        img = combat_ui(img)
    else:
        img = painterly(img, seed, strokes=30000, amount=0.7, swirl_c=(960, 150, 420), half=2, stroke_mix=0.2)
        img = glow(img, thr=150, gain=2.0)
        img = grade(img, lift=(12, 4, 24), vignette=0.5, top_haze=((140, 30, 130), 0.2))
        img = grain(img, seed, 5)
        img = shop_ui(img)
    img.save(out, optimize=True)
    print("wrote", out)


main()
