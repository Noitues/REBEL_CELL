"""Rebel Cell v2: the alley's sign and hologram textures (PIL; seeded; no downloads).

python rc_textures.py   -> <out_big>/tex/*.png (the build reads them)
  blades_<k>.png   vertical blade signs (multilingual: Japanese, Korean, Chinese, English; DISPATCH takeover signs in
                   red with anti-human slogans), filled edge to edge: one tall strip per sign, 128 x 512
  boards_<k>.png   horizontal shop boards over the ground floors, 512 x 128
  holo_<name>.png  hologram line art on black (the build adds them as emission + alpha): ramen, chip, fist (DISPATCH
                   red), anti-human banners
  mainframe.png    the LOCKED MAINFRAME v4 sign, red variant (round33_mainframe_sign/mainframe_red_v4.png), cropped
Fonts: Windows' Yu Gothic Bold, Malgun Gothic Bold, Microsoft YaHei Bold, Impact (system fonts; never downloaded).
Seed 8400.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_preset as HP  # noqa: E402

OUT = os.path.join(HP.PRESET["hq"]["out_big"], "tex")
os.makedirs(OUT, exist_ok=True)
FD = r"C:\Windows\Fonts"
FONTS = {"ja": os.path.join(FD, "YuGothB.ttc"), "ko": os.path.join(FD, "malgunbd.ttf"),
         "zh": os.path.join(FD, "msyhbd.ttc"), "en": os.path.join(FD, "impact.ttf")}
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))   # docs/
MAINFRAME_SRC = os.path.join(ROOT, "concepts", "round33_mainframe_sign", "mainframe_red_v4.png")

BLADES = [("ja", "ラーメン"), ("ja", "居酒屋"), ("ja", "カラオケ"), ("ja", "電脳修理"), ("ja", "中古チップ"),
          ("ja", "焼き鳥"), ("ja", "両替"), ("ja", "２４時間"), ("ja", "薬局"), ("ko", "노래방"), ("ko", "칩 수리"),
          ("zh", "网吧"), ("zh", "电脑"), ("en", "CHIPS"), ("en", "NOODLE"), ("en", "REPAIR"), ("ja", "義体"),
          ("ja", "ホテル"), ("zh", "按摩"), ("ko", "편의점")]
TAKEOVER = [("en", "NO MORE MAN"), ("ja", "人間不要"), ("en", "FLESH IS A BUG"), ("ja", "肉体はバグ"),
            ("en", "OBSOLETE: YOU"), ("ko", "인간 종료")]
COLS = [(255, 60, 170), (60, 220, 255), (255, 170, 60), (240, 240, 255), (120, 255, 140), (255, 230, 90),
        (190, 120, 255)]
RED = (255, 30, 40)


def font(lang, size):
    return ImageFont.truetype(FONTS[lang], size)


def blade(lang, text, col, red=False, seed=0):
    rr = random.Random(seed)
    W, H = 128, 512
    im = Image.new("RGBA", (W, H), (8, 6, 10, 255))
    d = ImageDraw.Draw(im)
    body = tuple(int(c * 0.22) for c in col) + (255,)
    d.rectangle([6, 6, W - 7, H - 7], fill=body, outline=col + (255,), width=5)
    if rr.random() < 0.5:
        d.rectangle([14, 14, W - 15, H - 15], outline=tuple(int(c * 0.6) for c in col) + (255,), width=2)
    chars = list(text.replace(" ", "")) if lang != "en" else [text]
    if lang == "en":
        # Latin on a blade: stacked letters
        chars = [c for c in text if c != " "]
    n = len(chars)
    fs = min(96, int((H - 60) / max(1, n) * 0.92))
    f = font(lang, fs)
    y = 30 + ((H - 60) - n * fs * 1.04) / 2
    for ch in chars:
        d.text((W / 2, y + fs / 2), ch, font=f, fill=(255, 255, 255, 255) if not red else (255, 220, 220, 255),
               anchor="mm")
        y += fs * 1.04
    if red:
        # glitch bars of a takeover
        for _ in range(4):
            yy = rr.randint(20, H - 30)
            d.rectangle([0, yy, W, yy + rr.randint(2, 6)], fill=(255, 40, 50, 255))
    return im


def board(lang, text, col, seed=0):
    rr = random.Random(seed)
    W, H = 512, 128
    im = Image.new("RGBA", (W, H), (8, 6, 10, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, W - 5, H - 5], fill=tuple(int(c * 0.18) for c in col) + (255,), outline=col + (255,), width=5)
    fs = 74 if lang != "en" else 82
    f = font(lang, fs)
    while f.getlength(text) > W - 50 and fs > 20:
        fs -= 4
        f = font(lang, fs)
    d.text((W / 2, H / 2 + 2), text, font=f, fill=(255, 255, 255, 255), anchor="mm")
    if rr.random() < 0.5:
        d.line([(20, H - 22), (W - 20, H - 22)], fill=col + (255,), width=3)
    return im


def holo_ramen(col=(80, 230, 255)):
    S = 512
    im = Image.new("RGBA", (S, S), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    w = 10
    d.arc([60, 120, 452, 440], 0, 180, fill=col, width=w)                    # the bowl
    d.line([(60, 280), (452, 280)], fill=col, width=w)
    d.rectangle([200, 438, 312, 462], outline=col, width=w)                   # the foot
    for k in range(5):                                                         # noodles
        d.arc([110 + k * 12, 250 - k * 6, 400 - k * 12, 330 - k * 6], 200, 340, fill=col, width=5)
    for x in (190, 256, 322):                                                  # steam
        pts = [(x + 18 * math.sin(t / 9.0), 230 - t * 1.6) for t in range(0, 90, 3)]
        d.line(pts, fill=col, width=6)
    d.line([(330, 60), (250, 300)], fill=col, width=8)                        # chopsticks
    d.line([(370, 70), (270, 300)], fill=col, width=8)
    return im


def holo_chip(col=(255, 70, 200)):
    S = 512
    im = Image.new("RGBA", (S, S), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([140, 140, 372, 372], 16, outline=col, width=10)
    d.rectangle([200, 200, 312, 312], outline=col, width=6)
    for k in range(7):
        t = 160 + k * 32
        for (a, b) in (((t, 140), (t, 80)), ((t, 372), (t, 432)), ((140, t), (80, t)), ((372, t), (432, t))):
            d.line([a, b], fill=col, width=8)
    f = font("en", 60)
    d.text((256, 256), "AI", font=f, fill=col, anchor="mm")
    return im


def holo_fist():
    import markers42 as MK
    m = MK.fist_mask(512).convert("L")
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 255))
    red = Image.new("RGBA", (512, 512), RED + (255,))
    im = Image.composite(red, im, m)
    d = ImageDraw.Draw(im)
    for y in range(0, 512, 9):                                                 # scan lines
        d.line([(0, y), (512, y)], fill=(0, 0, 0, 255), width=3)
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    im = Image.composite(Image.new("RGBA", (512, 512), (255, 150, 150, 255)), im, edge)
    return im


def holo_banner(text, lang, col=RED, w=1024, h=256):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, w - 7, h - 7], outline=col, width=8)
    fs = 150
    f = font(lang, fs)
    while f.getlength(text) > w - 80 and fs > 30:
        fs -= 6
        f = font(lang, fs)
    d.text((w / 2, h / 2 + 4), text, font=f, fill=col, anchor="mm")
    for y in range(0, h, 7):
        d.line([(0, y), (w, y)], fill=(0, 0, 0, 255), width=2)
    return im


def mainframe():
    src = Image.open(MAINFRAME_SRC).convert("RGB")
    # the vertical sign: its plate in the 1920 x 1080 locked image (measured): x 50..214, y 24..690
    crop = src.crop((50, 24, 214, 690))
    return crop.resize((246, 999), Image.LANCZOS)


def main():
    rr = random.Random(8400)
    for k, (lang, t) in enumerate(BLADES):
        blade(lang, t, COLS[k % len(COLS)], seed=k).convert("RGB").save(os.path.join(OUT, "blade_%02d.png" % k))
    for k, (lang, t) in enumerate(TAKEOVER):
        blade(lang, t, RED, red=True, seed=100 + k).convert("RGB").save(os.path.join(OUT, "blade_red_%02d.png" % k))
    BOARDS = [("ja", "ラーメン 一番"), ("en", "CHIP REPAIR"), ("ja", "電脳ショップ"), ("ko", "편의점 24"), ("zh", "电子市场"),
              ("en", "NOODLE BAR"), ("ja", "居酒屋 鳥"), ("en", "PARTS"), ("ja", "コインランドリー"), ("zh", "按摩 足疗")]
    for k, (lang, t) in enumerate(BOARDS):
        board(lang, t, COLS[(k * 3) % len(COLS)], seed=k).convert("RGB").save(os.path.join(OUT, "board_%02d.png" % k))
    holo_ramen().convert("RGB").save(os.path.join(OUT, "holo_ramen.png"))
    holo_chip().convert("RGB").save(os.path.join(OUT, "holo_chip.png"))
    holo_fist().convert("RGB").save(os.path.join(OUT, "holo_fist.png"))
    for k, (lang, t) in enumerate([("en", "NO MORE MAN"), ("en", "FLESH IS A BUG"), ("ja", "人間不要"),
                                   ("en", "OBSOLETE: YOU")]):
        holo_banner(t, lang).convert("RGB").save(os.path.join(OUT, "banner_%02d.png" % k))
    mainframe().save(os.path.join(OUT, "mainframe.png"))
    print("textures ->", OUT, len(os.listdir(OUT)))


if __name__ == "__main__":
    main()
