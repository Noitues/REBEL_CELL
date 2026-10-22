"""REBEL_CELL graffiti MAINFRAME shop: texture builder (PIL + numpy; runs outside Blender).

python gs_tex.py [what ...]   what in: sign wall shutters stickers signs bin  (default: all)
Reuses (imports, never edits): round33 red MAINFRAME sign (flicker_sign.py) and street_graffiti/graf_atlas.py.
Writes to D:/rc_scratch/hq_styles/rebel_cell_graffiti/tex/.
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CON = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
S = r"D:/rc_scratch/hq_styles/rebel_cell_graffiti"
TEX = S + "/tex"
sys.path.insert(0, os.path.join(CON, "street_graffiti", "scripts"))
sys.path.insert(1, os.path.join(CON, "round33_mainframe_sign", "scripts"))
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import graf_atlas as GA

FW = "C:/Windows/Fonts/"
FLUO = GA.FLUO


def sign():
    import flicker_sign as FS
    FS.SIGN_PAL = "red"
    s = FS.FlickerSign("mainframe")
    res = s.state_normal()
    plate = np.clip(res["plate"], 0, 1)
    alpha = np.clip(res["alpha"], 0, 1)
    PW, PH, M = FS.PW, FS.PH, FS.MARGIN
    rgb = Image.fromarray((plate * 255 + .5).astype(np.uint8)).crop((M, M, M + PW, M + PH))
    a = Image.fromarray((alpha * 255 + .5).astype(np.uint8)).crop((M, M, M + PW, M + PH))
    rgb = rgb.resize((PW * 2, PH * 2), Image.LANCZOS)
    a = a.resize((PW * 2, PH * 2), Image.LANCZOS)
    rng = random.Random(41)
    paint = Image.new("RGBA", rgb.size, (0, 0, 0, 0))
    # tags on the frame / dead corners of the plate (outside the letter column), dimmed: paint in red light
    spots = [(20, 20, 60), (330, 14, 50), (14, 1960, 70), (330, 1980, 60), (4, 700, 60), (420, 1250, 55), (410, 640, 50), (6, 1450, 55)]
    for (x, y, sz) in spots:
        im, g = (GA.tag if rng.random() < 0.7 else GA.jp_tag)(rng, sz)
        paint.alpha_composite(im, (min(x, rgb.width - im.width - 2), min(y, rgb.height - im.height - 2)))
    pa = np.asarray(paint, np.float32)
    pa[..., :3] *= 0.62
    base = rgb.convert("RGBA")
    base.alpha_composite(Image.fromarray(pa.astype(np.uint8), "RGBA"))
    base.putalpha(a)
    base.save(TEX + "/sign_red.png")
    print("sign", base.size)


def wall():
    for name, fn, sd, W, H, dens in (("graf", GA.build, 7, 4096, 2048, 1.35), ("heaven", GA.build_heaven, 11, 4096, 2048, 1.0)):
        w = fn(sd, W, H, dens)
        w.rgba.save(f"{TEX}/{name}_albedo.png")
        w.glow.save(f"{TEX}/{name}_glow.png")
        print("wall", name)


def stickers():
    """Sticker / slap sheet 2048^2 (RGBA); used on the pole, bin and sign frame."""
    rng = random.Random(5)
    W = H = 2048
    sheet = GA.Wall(W, H)
    texts = ["NO CORP", "REBEL CELL", "FREE NET", "ZERO", "ghost", "HACK", "電脳", "反乱", "自由", "ネット", "해킹", "駭客", "RIOT", "VANDAL", "SPLICE", "JACK IN", "OBEY NOBODY", "MAINFRAME 404"]
    fonts = [GA.F_HEAVY[0], GA.F_HEAVY[1], FW + "malgunbd.ttf", FW + "msjhbd.ttc", GA.F_JP]
    for k in range(150):
        w, h = rng.randint(70, 150), rng.randint(46, 110)
        bg = rng.choice(FLUO + [(250, 250, 245), (20, 18, 24), (250, 220, 40)])
        fg = (20, 18, 24) if sum(bg) > 380 else rng.choice([(250, 250, 245), (255, 226, 0), (92, 225, 255)])
        im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if rng.random() < 0.3:
            d.ellipse([2, 2, w + 5, h + 5], fill=(250, 250, 245, 255))
            d.ellipse([6, 6, w + 1, h + 1], fill=bg + (255,))
        else:
            d.rounded_rectangle([2, 2, w + 5, h + 5], radius=rng.choice([4, 10, 18]), fill=(250, 250, 245, 255))
            d.rounded_rectangle([6, 6, w + 1, h + 1], radius=rng.choice([2, 8, 14]), fill=bg + (255,))
        t = rng.choice(texts)
        fp = rng.choice(fonts)
        f = ImageFont.truetype(fp, int(h * 0.5))
        bb = d.textbbox((0, 0), t, font=f)
        if bb[2] - bb[0] > w - 6:
            f = ImageFont.truetype(fp, max(8, int(h * 0.5 * (w - 8) / (bb[2] - bb[0]))))
            bb = d.textbbox((0, 0), t, font=f)
        d.text(((w + 8 - (bb[2] - bb[0])) / 2 - bb[0], (h + 8 - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=fg + (255,))
        if rng.random() < 0.4:
            d.ellipse([w - 24, 8, w - 8, 24], fill=fg + (255,))
        im = im.rotate(rng.uniform(-14, 14), expand=True, resample=Image.BICUBIC)
        sheet.put(im, None, rng.randrange(W - 200), rng.randrange(H - 200))
    for k in range(40):
        im, g = GA.tag(rng, rng.randint(40, 90))
        sheet.put(im, g, rng.randrange(W - 200), rng.randrange(H - 200))
    sheet.rgba.save(TEX + "/stickers.png")
    print("stickers")


def _bomb(w, h, seed, base, n_piece=1):
    """One fully bombed panel (roll shutter): base paint, buffs, paste-ups, big piece(s), throw-ups, tags."""
    rng = random.Random(seed)
    wall = GA.Wall(w, h)
    wall.rgba.alpha_composite(Image.new("RGBA", (w, h), base + (255,)))
    for _ in range(rng.randint(2, 4)):
        pw, ph = rng.randint(w // 5, w // 2), rng.randint(h // 6, h // 3)
        wall.put(Image.new("RGBA", (pw, ph), rng.choice([(60, 62, 70), (84, 78, 74), (46, 52, 66)]) + (200,)), None, rng.randrange(w), rng.randrange(h))
    for _ in range(rng.randint(1, 3)):
        im, g = GA.poster(rng, rng.randint(w // 8, w // 5), rng.randint(h // 5, h // 3))
        wall.put(im, g, rng.randrange(w), rng.randrange(h))
    for i in range(n_piece):
        im, g = GA.piece(rng, int(h * 0.20), rng.random())
        k = min(1.0, w * 0.9 / im.width, h * 0.8 / im.height)
        if k < 1.0:
            im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
            g = g.resize(im.size, Image.LANCZOS)
        y = (h - im.height) * (0.1 + 0.6 * rng.random()) if n_piece == 1 else (h - im.height) * i / max(1, n_piece - 1)
        wall.put(im, g, (w - im.width) * (0.1 + 0.5 * rng.random()), y)
    for _ in range(rng.randint(3, 6)):
        im, g = GA.throwup(rng, int(h * rng.uniform(0.07, 0.12)))
        wall.put(im, g, rng.randrange(w), rng.randrange(h))
    if rng.random() < 0.6:
        im, g = GA.skull(rng, int(h * 0.13))
        wall.put(im, g, rng.randrange(w), rng.randrange(h))
    for _ in range(rng.randint(10, 18)):
        im, g = (GA.jp_tag if rng.random() < 0.35 else GA.tag)(rng, int(h * rng.uniform(0.04, 0.08)))
        wall.put(im, g, rng.randrange(w), rng.randrange(h))
    return wall.rgba, wall.glow


def shutters():
    for k in range(8):
        w, h = 1280, 1040
        base = [(98, 104, 112), (70, 76, 86), (120, 114, 104), (60, 66, 74)][k % 4]
        rgba, glow = _bomb(w, h, 300 + k, base, 1 if k % 3 else 2)
        rgba.save(f"{TEX}/shutter{k}_albedo.png")
        glow.save(f"{TEX}/shutter{k}_glow.png")
    print("shutters")


def _vtext(d, x0, y0, cw, ch, s, f, fill):
    fs = f.size
    y = y0 + (ch - len(s) * fs * 1.08) / 2
    for c in s:
        bb = f.getbbox(c)
        d.text((x0 + (cw - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1] * 0.4), c, font=f, fill=fill)
        y += fs * 1.08


def signs():
    """Blade signs, multilingual, lit: vertical 256x1024 cells (8x3) and horizontal 1024x256 cells (2x8)."""
    styles = GA.SIGN_STYLES
    sets = [("カラオケ", GA.F_JP), ("ラーメン", GA.F_JP), ("居酒屋", GA.F_JP), ("電脳館", GA.F_JP), ("質屋", GA.F_JP), ("中古パーツ", GA.F_JP),
            ("電子零件", FW + "msjhbd.ttc"), ("維修", FW + "msjhbd.ttc"), ("麻雀", FW + "msjhbd.ttc"), ("網吧", FW + "msjhbd.ttc"),
            ("전자부품", FW + "malgunbd.ttf"), ("노래방", FW + "malgunbd.ttf"), ("술집", FW + "malgunbd.ttf"), ("PC방", FW + "malgunbd.ttf"),
            ("CHIPS", GA.F_HEAVY[0]), ("BAR", GA.F_HEAVY[0]), ("24H", GA.F_HEAVY[0]), ("RAMEN", GA.F_HEAVY[0]), ("PAWN", GA.F_HEAVY[0]),
            ("DAEMON", GA.F_HEAVY[0]), ("SIM", GA.F_HEAVY[0]), ("HOTEL", GA.F_HEAVY[0]), ("占い", GA.F_JP), ("寿司", GA.F_JP)]
    cw, ch, cols, rows = 256, 1024, 8, 3
    im = Image.new("RGB", (cols * cw, rows * ch))
    d = ImageDraw.Draw(im)
    for i, (s, fp) in enumerate(sets):
        c, r = i % cols, i // cols
        x0, y0 = c * cw, r * ch
        bg, fg = styles[(i * 3) % len(styles)]
        d.rectangle([x0, y0, x0 + cw - 1, y0 + ch - 1], fill=bg)
        d.rectangle([x0 + 10, y0 + 10, x0 + cw - 11, y0 + ch - 11], outline=fg, width=8)
        d.rectangle([x0 + 26, y0 + 26, x0 + cw - 27, y0 + 150], fill=fg)
        if all(ord(c_) < 128 for c_ in s):
            f = ImageFont.truetype(fp, 150 if len(s) <= 3 else 110)
            if len(s) > 3:   # latin word: stacked letters
                _vtext(d, x0, y0 + 150, cw, ch - 160, s, ImageFont.truetype(fp, min(140, int((ch - 260) / len(s) / 1.08))), fg)
            else:
                _vtext(d, x0, y0 + 150, cw, ch - 160, s, f, fg)
        else:
            fs = min(int(cw * 0.62), int((ch - 260) / len(s) / 1.08))
            _vtext(d, x0, y0 + 150, cw, ch - 160, s, ImageFont.truetype(fp, fs), fg)
    im.save(TEX + "/signs_v.png")
    hw, hh, hc, hr = 1024, 256, 2, 8
    im2 = Image.new("RGB", (hc * hw, hr * hh))
    d = ImageDraw.Draw(im2)
    hs = [("ラーメン 24H", GA.F_JP), ("電子零件 CHIPS", FW + "msjhbd.ttc"), ("노래방 KARAOKE", FW + "malgunbd.ttf"), ("中古 パーツ 買取", GA.F_JP),
          ("DAEMON REPAIR", GA.F_HEAVY[0]), ("居酒屋 BAR", GA.F_JP), ("維修 REPAIR 電腦", FW + "msjhbd.ttc"), ("NOODLE 麺", GA.F_JP),
          ("OPEN 営業中", GA.F_JP), ("SIM UNLOCK 解鎖", FW + "msjhbd.ttc"), ("PAWN 質", GA.F_JP), ("전자 ELECTRONICS", FW + "malgunbd.ttf"),
          ("JACK-IN CAFE", GA.F_HEAVY[0]), ("TATTOO 刺青", GA.F_JP), ("HOTEL 宿", GA.F_JP), ("NET 網", FW + "msjhbd.ttc")]
    for i, (s, fp) in enumerate(hs):
        c, r = i % hc, i // hc
        x0, y0 = c * hw, r * hh
        bg, fg = styles[(i * 5 + 1) % len(styles)]
        d.rectangle([x0, y0, x0 + hw - 1, y0 + hh - 1], fill=bg)
        d.rectangle([x0 + 8, y0 + 8, x0 + hw - 9, y0 + hh - 9], outline=fg, width=7)
        fs = 150
        f = ImageFont.truetype(fp, fs)
        while d.textlength(s, font=f) > hw - 80 and fs > 30:
            fs -= 6
            f = ImageFont.truetype(fp, fs)
        bb = d.textbbox((0, 0), s, font=f)
        d.text((x0 + (hw - (bb[2] - bb[0])) / 2 - bb[0], y0 + (hh - (bb[3] - bb[1])) / 2 - bb[1]), s, font=f, fill=fg)
    im2.save(TEX + "/signs_h.png")
    print("signs")


def bin_tex():
    """Recycle-bin wrap (1024x512): steel drum with a cyan wire grid, lime recycle emblem, tags + slaps."""
    rng = random.Random(77)
    W, H = 1024, 512
    im = Image.new("RGBA", (W, H), (30, 44, 56, 255))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 16):
        d.line([(x, 0), (x, H)], fill=(80, 150, 170, 255), width=2)
    for y in range(0, H, 16):
        d.line([(0, y), (W, y)], fill=(80, 150, 170, 255), width=2)
    cx, cy, R = 256, 270, 110
    for k in range(3):
        a0 = k * 120 - 90
        pts = [(cx + R * math.cos(math.radians(a0 + t)), cy + R * math.sin(math.radians(a0 + t))) for t in range(0, 85, 5)]
        d.line(pts, fill=(176, 255, 40, 255), width=34)
        a = math.radians(a0 + 100)
        tip = (cx + R * math.cos(a), cy + R * math.sin(a))
        n = (math.cos(a), math.sin(a))
        tg = (-math.sin(a), math.cos(a))
        d.polygon([(tip[0] + tg[0] * 40, tip[1] + tg[1] * 40), (tip[0] + n[0] * 38 - tg[0] * 5, tip[1] + n[1] * 38 - tg[1] * 5),
                   (tip[0] - n[0] * 38 - tg[0] * 5, tip[1] - n[1] * 38 - tg[1] * 5)], fill=(176, 255, 40, 255))
    wall = GA.Wall(W, H)
    wall.rgba = im
    for _ in range(14):
        s, _g = GA.tag(rng, rng.randint(50, 110))
        wall.put(s, None, rng.choice([480, 560, 640, 720, 800, 880]) + rng.randint(-40, 40), rng.randrange(H - 120))
    p, g = GA.piece(rng, 90, 0.4)
    p = p.resize((380, max(1, int(p.height * 380 / p.width))))
    wall.put(p, None, 540, 40)
    st = Image.open(TEX + "/stickers.png")
    for _ in range(40):
        x, y = rng.randrange(1800), rng.randrange(1800)
        c = st.crop((x, y, x + 120, y + 90))
        if np.asarray(c)[..., 3].mean() > 90:
            wall.put(c, None, rng.randrange(480, 980), rng.randrange(H - 90))
    wall.rgba.save(TEX + "/bin.png")
    print("bin")


def fascia():
    """MAINFRAME shop fascia board (1024x256): red neon-on-black, lit counter hours."""
    im = Image.new("RGB", (1024, 256), (14, 6, 8))
    d = ImageDraw.Draw(im)
    d.rectangle([8, 8, 1015, 247], outline=(255, 40, 60), width=8)
    f = ImageFont.truetype(GA.F_HEAVY[0], 150)
    d.text((40, 36), "MAINFRAME", font=f, fill=(255, 70, 80))
    f2 = ImageFont.truetype(GA.F_JP, 54)
    d.text((700, 40), "電脳 24H", font=f2, fill=(255, 220, 200))
    f3 = ImageFont.truetype(GA.F_HEAVY[0], 46)
    d.text((700, 150), "OPEN / 営業中", font=f3, fill=(255, 140, 150))
    im.save(TEX + "/mainframe_h.png")
    print("fascia")


if __name__ == "__main__":
    os.makedirs(TEX, exist_ok=True)
    todo = sys.argv[1:] or ["sign", "stickers", "wall", "shutters", "signs", "bin"]
    for t in todo:
        {"sign": sign, "wall": wall, "shutters": shutters, "stickers": stickers, "signs": signs, "bin": bin_tex, "fascia": fascia}[t]()
