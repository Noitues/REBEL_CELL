"""v2 textures for the F1b-based exterior (PIL; reuses gs_tex.py for pieces, shutters and the clean red sign).

python gs2_tex.py        -> D:/rc_scratch/hq_styles/rebel_cell_graffiti/tex2/
  sign_clean.png      round-33 red MAINFRAME canvas (RGBA 390x1174 incl. glow), NO paint on it
  gz_wall_albedo/glow wall atlas x patch mask (about half coverage), slightly desaturated
  gz_shutter{k}_*     bombed roll-shutter panels at the F1b shutter aspect
  pole_f.png pole_r.png  sticker strips for the two visible faces of the sign-side pole: every sticker sits wholly inside its face
  bin2.png            recycle-bin wrap, seam at the back, emblem and slaps on the camera side (u 0.3-0.7)
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import gs_tex as T
GA = T.GA
OUT = T.S + "/tex2"


def clean_sign():
    import flicker_sign as FS
    FS.SIGN_PAL = "red"
    s = FS.FlickerSign("mainframe")
    FS.save_rgba(s.state_normal(), OUT + "/sign_clean.png")
    print("sign_clean")


def patch_mask(W, H, seed, cover=0.55, cells=(14, 7)):
    r = np.random.default_rng(seed)
    f = Image.fromarray((r.random((cells[1], cells[0])) * 255).astype(np.uint8), "L").resize((W, H), Image.BICUBIC)
    a = np.asarray(f.filter(ImageFilter.GaussianBlur(W // 60)), np.float32) / 255
    thr = np.quantile(a, 1 - cover)
    return np.clip((a - thr) / 0.06 + 0.5, 0, 1)


def wall():
    alb = Image.open(T.TEX + "/graf_albedo.png").convert("RGBA")
    glow = Image.open(T.TEX + "/graf_glow.png").convert("L")
    W, H = alb.size
    m = patch_mask(W, H, 5, cover=0.8)
    a = np.asarray(alb, np.float32)
    g = a[..., :3].mean(-1, keepdims=True)
    a[..., :3] = np.clip((a[..., :3] - 110) * 1.18 + 118, 0, 255)      # paint: more contrast, no desaturation (no self-glow in v4)
    a[..., 3] *= m
    Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA").save(OUT + "/gz_wall_albedo.png")
    Image.fromarray((np.asarray(glow, np.float32) * m).clip(0, 255).astype(np.uint8), "L").save(OUT + "/gz_wall_glow.png")
    print("wall")


def _bomb_clean(w, h, seed, base):
    """A roll shutter: base paint, one big piece, throw-ups, a skull, tags. No posters or buffs (they read as black holes)."""
    rng = random.Random(seed)
    wall = GA.Wall(w, h)
    wall.rgba.alpha_composite(Image.new("RGBA", (w, h), base + (255,)))
    im, g = GA.piece(rng, int(h * 0.42), rng.random())
    k = min(1.0, w * 0.92 / im.width, h * 0.85 / im.height)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    g = g.resize(im.size, Image.LANCZOS)
    wall.put(im, g, (w - im.width) / 2 + rng.randint(-40, 40), (h - im.height) / 2 + rng.randint(-20, 20))
    for _ in range(3):
        im, g = GA.throwup(rng, int(h * rng.uniform(0.16, 0.22)))
        wall.put(im, g, rng.randrange(w - 200), rng.randrange(h - 120))
    im, g = GA.skull(rng, int(h * 0.20))
    wall.put(im, g, rng.randrange(w - 250), rng.randrange(h - 250))
    for _ in range(9):
        im, g = (GA.jp_tag if rng.random() < 0.35 else GA.tag)(rng, int(h * rng.uniform(0.09, 0.14)))
        wall.put(im, g, rng.randrange(w - 200), rng.randrange(h - 120))
    return wall.rgba, wall.glow


def shutters():
    for k in range(4):
        base = [(98, 104, 112), (70, 76, 86), (120, 114, 104), (60, 66, 74)][k % 4]
        rgba, glow = _bomb_clean(1280, 806, 400 + k, base)
        from PIL import ImageEnhance
        rgbi = ImageEnhance.Contrast(ImageEnhance.Color(rgba.convert("RGB")).enhance(1.35)).enhance(1.18)
        rgbi.save(f"{OUT}/gz_shutter{k}_albedo.png")
        glow.save(f"{OUT}/gz_shutter{k}_glow.png")
    print("shutters")


def sticker_art(rng, w, h):
    bg = rng.choice(GA.FLUO + [(250, 250, 245), (20, 18, 24), (250, 220, 40)])
    fg = (20, 18, 24) if sum(bg) > 380 else rng.choice([(250, 250, 245), (255, 226, 0), (92, 225, 255)])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=rng.choice([4, 10]), fill=(250, 250, 245, 255))
    d.rounded_rectangle([4, 4, w - 5, h - 5], radius=6, fill=bg + (255,))
    t = rng.choice(["NO CORP", "ZERO", "HACK", "RIOT", "電脳", "反乱", "해킹", "ghost", "FREE NET", "REBEL"])
    fp = GA.F_JP if any(ord(c) > 127 for c in t) else GA.F_HEAVY[0]
    if any(0xAC00 <= ord(c) <= 0xD7A3 for c in t):
        fp = T.FW + "malgunbd.ttf"
    fs = int(h * 0.5)
    f = ImageFont.truetype(fp, fs)
    while d.textlength(t, font=f) > w - 14 and fs > 8:
        fs -= 2
        f = ImageFont.truetype(fp, fs)
    bb = d.textbbox((0, 0), t, font=f)
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=fg + (255,))
    return im


def pole_strips():
    """Square pole: the camera sees the -y face and the +x face. Stickers wholly inside the face (no wrap, no seam)."""
    for name, seed in (("pole_f", 1), ("pole_r", 2)):
        rng = random.Random(seed)
        W, H = 256, 2048
        im = Image.new("RGBA", (W, H), (40, 44, 52, 255))
        y = 30
        placed = 0
        while y < H - 130:
            w, h = rng.randint(100, 176), rng.randint(64, 110)
            x = rng.randint(16, W - w - 16)
            s = sticker_art(rng, w, h)
            s = s.rotate(rng.uniform(-6, 6), expand=True, resample=Image.BICUBIC)
            if s.width > W - 20:
                s = s.resize((W - 20, int(s.height * (W - 20) / s.width)))
            x = max(8, min(x, W - s.width - 8))
            im.alpha_composite(s, (x, y))
            y += s.height + rng.randint(4, 26)
            placed += 1
        im.save(f"{OUT}/{name}.png")
    print("pole strips")


def bin2():
    rng = random.Random(77)
    W, H = 1024, 512
    im = Image.new("RGBA", (W, H), (30, 44, 56, 255))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 16):
        d.line([(x, 0), (x, H)], fill=(80, 150, 170, 255), width=2)
    for y in range(0, H, 16):
        d.line([(0, y), (W, y)], fill=(80, 150, 170, 255), width=2)
    cx, cy, R = 400, 270, 90
    for k in range(3):
        a0 = k * 120 - 90
        pts = [(cx + R * math.cos(math.radians(a0 + t)), cy + R * math.sin(math.radians(a0 + t))) for t in range(0, 85, 5)]
        d.line(pts, fill=(176, 255, 40, 255), width=28)
        a = math.radians(a0 + 100)
        tip = (cx + R * math.cos(a), cy + R * math.sin(a))
        n = (math.cos(a), math.sin(a))
        tg = (-math.sin(a), math.cos(a))
        d.polygon([(tip[0] + tg[0] * 34, tip[1] + tg[1] * 34), (tip[0] + n[0] * 32 - tg[0] * 4, tip[1] + n[1] * 32 - tg[1] * 4),
                   (tip[0] - n[0] * 32 - tg[0] * 4, tip[1] - n[1] * 32 - tg[1] * 4)], fill=(176, 255, 40, 255))
    for (x, y) in ((300, 60), (520, 70), (600, 330), (330, 410), (560, 180), (650, 420), (290, 190)):
        s = sticker_art(rng, rng.randint(80, 120), rng.randint(54, 76)).rotate(rng.uniform(-10, 10), expand=True, resample=Image.BICUBIC)
        im.alpha_composite(s, (x, y))
    t, g = GA.tag(rng, 80)
    im.alpha_composite(t, (470, 120))
    im.save(OUT + "/bin2.png")
    print("bin2")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (clean_sign, wall, shutters, pole_strips, bin2):
        f()
