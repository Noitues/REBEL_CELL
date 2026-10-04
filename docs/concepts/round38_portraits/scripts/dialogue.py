"""Round 31 -> dialogue.png (A: low-poly cel bust on a CRT comm feed, recommended) and dialogue_B.png
(B: the same bust as a die-cut vinyl sticker portrait). Busts: bust_blender.py renders in scratch/.
Also shows the DISPATCH treatment (no face: a waveform on the same feed), since DISPATCH must look
unlike every other speaker (art_asset B3).

python dialogue.py [a|b|all]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

import r31lib as L
import sticker_lib19 as SL

BG = os.path.join(L.CONCEPTS, "round30_meridian_castle", "hq_meridian_close_night.jpg")
BUST = {k: os.path.join(L.SCRATCH, "bust_%s.png" % k) for k in ("breaker", "fixer")}
LINE = ("Meridian moved the depot's Rack to the back lot. Logistics Director sits on it now. "
        "Two elite routers on the way in. The Modem's on layer three if you need to shop.")
CHOICES = [(1, "WHO RUNS THE LOT?"), (2, "WHAT'S IN THE RACK?"), (3, "JACK IN")]


def bust(key, size):
    im = Image.open(BUST[key]).convert("RGBA")
    im = im.crop((60, 0, 860, 900))
    return im.resize(size, Image.LANCZOS)


def crt_feed(key, w, h, acc, label, live=True, dim=False):
    """The bust on the Cell's comm feed: phosphor tint, scanlines, a slight RGB split, rolling bar."""
    bg = Image.new("RGBA", (w, h), (8, 12, 18, 255))
    d = ImageDraw.Draw(bg)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=(int(10 + 20 * k), int(14 + 12 * k), int(24 + 18 * k), 255))
    for x in range(0, w, 28):
        d.line([(x, 0), (x, h)], fill=(20, 34, 44, 255))
    for y in range(0, h, 28):
        d.line([(0, y), (w, y)], fill=(20, 34, 44, 255))
    b = bust(key, (int(w * 1.0), int(w * 1.0 * 900 / 800)))
    bg.alpha_composite(b, ((w - b.width) // 2, h - b.height + int(h * 0.12)))
    img = bg
    a = np.asarray(img.convert("RGB"), np.float32)
    # phosphor: keep identity colours, lift toward the accent a little
    a = a * 0.88 + np.array(acc, np.float32) * 0.06
    # RGB split
    r = np.roll(a[..., 0], 2, axis=1)
    bl = np.roll(a[..., 2], -2, axis=1)
    a = np.stack([r, a[..., 1], bl], -1)
    # scanlines + rolling bar
    yy = np.arange(h)[:, None]
    a *= (0.80 + 0.20 * (yy % 3 != 0))[..., None]
    a += (np.exp(-((yy - h * 0.62) / 18.0) ** 2) * 18)[..., None]
    if dim:
        a *= 0.55
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    img = L.bloom(img, 0.35, 0.7, 6)
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 30 + L.f_mono(15).getlength(label), 34], fill=(6, 8, 12, 230))
    if live:
        d.ellipse([16, 16, 28, 28], fill=(255, 50, 60, 255))
    d.text((34 if live else 18, 22), label, font=L.f_mono(15), fill=acc + (255,), anchor="lm")
    # bezel
    out = Image.new("RGBA", (w + 28, h + 28), (0, 0, 0, 0))
    od = ImageDraw.Draw(out)
    od.rounded_rectangle([0, 0, w + 27, h + 27], radius=22, fill=(26, 24, 32, 255), outline=(8, 6, 12, 255), width=3)
    od.rounded_rectangle([6, 6, w + 21, h + 21], radius=18, outline=(60, 56, 72, 255), width=2)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=26, fill=255)
    img.putalpha(m)
    out.alpha_composite(img, (14, 14))
    # glass bulge highlight
    sh = SL.diag(w, h, 30).point(SL.band_lut(0.2, 0.1, 0.16))
    lay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    lay.putalpha(sh)
    out.alpha_composite(lay, (14, 14))
    od = ImageDraw.Draw(out)
    od.ellipse([w - 4, h + 4, w + 8, h + 16], fill=(80, 255, 140, 255) if live else (60, 60, 70, 255))
    return out


def dispatch_feed(w, h):
    img = Image.new("RGBA", (w, h), (6, 4, 6, 255))
    d = ImageDraw.Draw(img)
    acc = (232, 20, 30)
    for k in range(5):
        pts = []
        for x in range(0, w, 3):
            u = x / w
            env = math.sin(math.pi * u) ** 2
            y = h / 2 + env * (h * 0.32 - k * 10) * math.sin(u * 28 + k * 0.9) * math.cos(u * 7 + k)
            pts.append((x, y))
        d.line(pts, fill=acc + (255 - k * 45,), width=3 if k == 0 else 1)
    img = L.bloom(img, 0.6, 0.4, 8)
    d = ImageDraw.Draw(img)
    d.text((w / 2, h - 22), "NO FACE  //  NO FEED  //  VOICE ONLY", font=L.f_mono(14), fill=(170, 40, 50, 255), anchor="mm")
    yy = np.arange(h)[:, None]
    a = np.asarray(img, np.float32)
    a[..., :3] *= (0.78 + 0.22 * (yy % 3 != 0))[..., None]
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def text_box(w, h, acc, name, role, line, page="2/4"):
    c = L.CRT(w, h, acc, None, header=False, seed=41, alpha=240)
    c.text((28, 22), name, 40, (255, 255, 255), fnt=L.f_num(44))
    nw = L.f_num(44).getlength(name)
    c.text((40 + nw, 38), role, 17, acc)
    c.text((w - 28, 34), page, 16, tuple(int(v * 0.7) for v in acc), anchor="ra")
    c.rule(78, col=acc, a=110)
    import textwrap
    y = 96
    lines = textwrap.wrap(line, 56 if w < 1050 else 62)
    for ln in lines:
        c.text((28, y), ln, 24, (225, 240, 245))
        y += 38
    cx = 28 + L.f_mono(24).getlength(lines[-1]) + 8
    c.d.rectangle([cx, y - 36, cx + 14, y - 10], fill=acc + (255,))
    return c.finish()


def choice_sticker(n, t, hover=False, seed=1):
    import event
    return event.plate_button(n, t, w=420, h=70, plate=(30, 26, 40) if not hover else (60, 40, 70), seed=seed, hover=hover)


def base():
    img = L.backdrop(BG, blur=3, dim=0.5, sat=0.8)
    img = L.vignette(img, 0.8)
    img = L.darken_rect(img, (0, 560, 1920, 1080), a=170, blur=60)
    return img


def make_a():
    img = base()
    acc = (120, 230, 255)
    # speaker: STREET MERC (left, live) ; listener: CELL-9 BREAKER (right, dimmed)
    f1 = crt_feed("fixer", 420, 470, acc, "COMMS  //  STREET MERC")
    img = L.drop_shadow(img, f1, 70, 230, blur=20)
    f2 = crt_feed("breaker", 300, 336, (255, 120, 200), "CELL-9  //  BREAKER", live=False, dim=True)
    img = L.drop_shadow(img, f2, 1575, 330, blur=16)
    tb = text_box(1000, 300, acc, "STREET MERC", "contact  //  briefing", LINE)
    img = L.crt_glow_under(img, (540, 520, 1540, 820), acc, 0.15)
    img = L.paste(img, tb, 540, 520)
    for i, (n, t) in enumerate(CHOICES):
        hov = i == 2
        sd = choice_sticker(n, t, hover=hov, seed=80 + i)
        img = L.place_sticker(img, sd, [770, 1200, 1630][i], 900 - (10 if hov else 0), angle=[-1, 0.8, -1.5][i], scale=0.86, hover=0.8 if hov else 0)
    # DISPATCH treatment inset (another line in the queue)
    dp = dispatch_feed(300, 150)
    c = L.CRT(330, 200, (232, 20, 30), "DISPATCH", tag="QUEUED", seed=42)
    c.paste(dp, 15, 44)
    img = L.paste(img, c.finish(), 1540, 40)
    d = ImageDraw.Draw(img)
    d.text((1705, 256), "DISPATCH never gets a face", font=L.f_mono(15), fill=(200, 120, 130, 255), anchor="mm")
    # name sticker (fixed thing: who this is)
    sd = L.sticker_word(["BRIEFING"], 70, fills=["yellow"], seed=83)
    img = L.place_sticker(img, sd, 330, 110, angle=-3)
    L.caption(img, "A  //  low-poly cel bust on a CRT comm feed (speaker live, listener dimmed)", x=24, y=1066, size=16)
    img = L.bloom(img, 0.18, 0.8, 8)
    L.save(img, "dialogue.png")


def sticker_portrait(key, w):
    im = bust(key, (w, int(w * 900 / 800)))
    a = np.asarray(im, np.float32)
    # posterize the cel bands a touch more for print
    rgb = a[..., :3]
    al = a[..., 3]
    # cut off at the chest so the die-cut has a clean bottom
    hh = a.shape[0]
    al[int(hh * 0.86):, :] = 0
    im = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al]).astype(np.uint8), "RGBA")
    return L.sticker_from_art(im, border=12, seed=91 if key == "fixer" else 92)


def make_b():
    img = base()
    acc = (120, 230, 255)
    sp = sticker_portrait("fixer", 400)
    img = L.place_sticker(img, sp, 300, 470, angle=-4)
    nm = L.sticker_word(["STREET MERC"], 54, fills=[(120, 230, 255)], seed=93)
    img = L.place_sticker(img, nm, 300, 830, angle=3)
    lp = sticker_portrait("breaker", 260)
    lp = L.greyscale(lp, 0.8)
    img = L.place_sticker(img, lp, 1700, 420, angle=5, opacity=0.85)
    tb = text_box(1080, 300, acc, "STREET MERC", "contact  //  briefing", LINE)
    img = L.crt_glow_under(img, (560, 520, 1640, 820), acc, 0.15)
    img = L.paste(img, tb, 560, 520)
    for i, (n, t) in enumerate(CHOICES):
        hov = i == 2
        sd = choice_sticker(n, t, hover=hov, seed=80 + i)
        img = L.place_sticker(img, sd, [790, 1220, 1650][i], 900 - (10 if hov else 0), angle=[-1, 0.8, -1.5][i], scale=0.86, hover=0.8 if hov else 0)
    sd = L.sticker_word(["BRIEFING"], 70, fills=["yellow"], seed=83)
    img = L.place_sticker(img, sd, 960, 110, angle=-2)
    L.caption(img, "B  //  the same bust as a die-cut vinyl sticker portrait (listener: greyed sticker)", x=24, y=1066, size=16)
    img = L.bloom(img, 0.18, 0.8, 8)
    L.save(img, "dialogue_B.png")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("a", "all"):
        make_a()
    if what in ("b", "all"):
        make_b()
