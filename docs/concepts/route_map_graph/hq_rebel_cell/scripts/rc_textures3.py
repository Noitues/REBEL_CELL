"""Rebel Cell v3: the sign families the designer asked for (round 1 review, note 7: vary the sign styles). PIL, seeded,
system fonts only (never downloaded). Writes into <out_big>/tex next to the v2 set (rc_textures.main is run first).

python rc_textures3.py
  ticker_<k>   LED tickers: a dot-matrix strip, 2048 x 64 (amber, green, cyan, white; one DISPATCH red)
  box_<k>      light-box faces (the cube signs that stick out of a facade), 256 x 256
  wrap_<k>     wrap bands (a sign wrapped round a bay's three faces), 1536 x 160
  cloth_<k>    cloth banners (nobori flags / hanging banners), 160 x 640, lit fabric (not neon)
  bill_<k>     rooftop billboards (ads), 1024 x 512
  roofneon_<k> rooftop neon letters on a frame (drawn as holo: alpha from brightness), 1024 x 256
  holo_<name>  more hologram line art: koi, maneki-neko, 24H, a can
  sewer_<k>    sewer stencils and hazard plates, 512 x 192
Seed 8430.
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
import rc_textures as T2  # noqa: E402

OUT = os.path.join(HP.PRESET["hq"]["out_big"], "tex")
os.makedirs(OUT, exist_ok=True)
font = T2.font


def fit(lang, text, w, start):
    fs = start
    f = font(lang, fs)
    while f.getlength(text) > w and fs > 12:
        fs -= 2
        f = font(lang, fs)
    return f


def ticker(text, lang, col, seed=0):
    """A dot-matrix LED strip: the text rasterised at 12 px high, every pixel drawn as a round LED (lit or dim)."""
    rr = random.Random(seed)
    cols, rows = 512, 16
    m = Image.new("L", (cols, rows), 0)
    d = ImageDraw.Draw(m)
    f = font(lang, 13)
    x = 4
    while x < cols:
        d.text((x, rows / 2), text, font=f, fill=255, anchor="lm")
        x += int(f.getlength(text)) + 30
    W, H = cols * 4, rows * 4
    im = Image.new("RGB", (W, H), (6, 5, 6))
    dd = ImageDraw.Draw(im)
    dim = tuple(int(c * 0.10) for c in col)
    px = m.load()
    for j in range(rows):
        for i in range(cols):
            on = px[i, j] > 110
            c = col if on else dim
            if on and rr.random() < 0.03:
                c = tuple(int(v * 0.6) for v in col)
            dd.ellipse([i * 4 + 0.5, j * 4 + 0.5, i * 4 + 3.3, j * 4 + 3.3], fill=c)
    return im


def lightbox(text, lang, fg, bg, seed=0):
    rr = random.Random(seed)
    S = 256
    im = Image.new("RGB", (S, S), bg)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, S - 1, S - 1], outline=tuple(int(c * 0.5) for c in bg), width=10)
    if rr.random() < 0.5:
        d.ellipse([40, 40, S - 40, S - 40], fill=fg)
        tc = bg
    else:
        tc = fg
    f = fit(lang, text, S - 70, 150)
    d.text((S / 2, S / 2 + 4), text, font=f, fill=tc, anchor="mm")
    return im


def wrap(text, lang, fg, bg, seed=0):
    W, H = 1536, 160
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    for k in range(0, W, 48):                                    # chaser bulbs top and bottom
        d.ellipse([k + 14, 8, k + 30, 24], fill=(255, 230, 160))
        d.ellipse([k + 14, H - 24, k + 30, H - 8], fill=(255, 230, 160))
    f = fit(lang, text, W / 3 - 40, 96)
    for k in range(3):                                           # one panel per face (front + two sides)
        d.text((W / 6 + k * W / 3, H / 2 + 2), text, font=f, fill=fg, anchor="mm")
        if k:
            d.line([(k * W / 3, 30), (k * W / 3, H - 30)], fill=tuple(int(c * 0.5) for c in fg), width=4)
    return im


def cloth(text, lang, fg, bg, seed=0):
    rr = random.Random(seed)
    W, H = 160, 640
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, 34], fill=tuple(int(c * 0.6) for c in bg))        # the pole hem
    for k in range(6, W, 22):
        d.ellipse([k, 10, k + 12, 22], fill=(30, 30, 30))                       # rings
    d.rectangle([10, 44, W - 11, H - 12], outline=fg, width=4)
    chars = [c for c in text if c != " "]
    fs = min(118, int((H - 90) / max(1, len(chars)) * 0.95))
    f = font(lang, fs)
    y = 60 + ((H - 90) - len(chars) * fs * 1.02) / 2
    for ch in chars:
        d.text((W / 2, y + fs / 2), ch, font=f, fill=fg, anchor="mm")
        y += fs * 1.02
    # cloth: soft folds (vertical shade bands) + grime
    sh = Image.new("L", (W, H), 255)
    sd = ImageDraw.Draw(sh)
    for x in range(W):
        v = 200 + 55 * math.sin(x / W * math.pi * rr.uniform(2.5, 3.5) + rr.random())
        sd.line([(x, 0), (x, H)], fill=int(max(150, min(255, v))))
    im = Image.composite(im, Image.new("RGB", (W, H), (0, 0, 0)), sh.point(lambda v: v))
    return Image.blend(im, Image.new("RGB", (W, H), (10, 8, 8)), 0.06)


def billboard(kind, seed=0):
    rr = random.Random(seed)
    W, H = 1024, 512
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)

    def grad(c0, c1):
        for y in range(H):
            t = y / H
            d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(c0, c1)))
    if kind == "neuro":
        grad((10, 30, 70), (120, 30, 140))
        d.ellipse([560, 70, 900, 470], fill=(20, 10, 40))                       # a head in profile
        d.polygon([(560, 260), (520, 300), (565, 320)], fill=(20, 10, 40))
        for k in range(9):                                                      # neural lines
            a = rr.uniform(0, math.pi * 2)
            d.line([(730, 250), (730 + 160 * math.cos(a), 250 + 160 * math.sin(a))], fill=(120, 240, 255), width=4)
            d.ellipse([725 + 160 * math.cos(a) - 8, 245 + 160 * math.sin(a) - 8, 735 + 160 * math.cos(a) + 8,
                       255 + 160 * math.sin(a) + 8], fill=(200, 255, 255))
        d.text((60, 170), "NEUROLINK", font=font("en", 110), fill=(240, 250, 255), anchor="lm")
        d.text((64, 300), "think faster. feel nothing.", font=font("en", 40), fill=(150, 230, 255), anchor="lm")
    elif kind == "drink":
        grad((255, 200, 40), (255, 90, 20))
        for k in range(14):
            d.line([(512, 256), (512 + 900 * math.cos(k * 0.45), 256 + 900 * math.sin(k * 0.45))], fill=(255, 225, 90),
                   width=26)
        d.rounded_rectangle([640, 60, 820, 470], 30, fill=(20, 120, 220), outline=(240, 240, 255), width=8)
        d.text((730, 265), "Z", font=font("en", 200), fill=(255, 255, 255), anchor="mm")
        d.text((60, 160), "ZERO", font=font("en", 150), fill=(30, 20, 40), anchor="lm")
        d.text((62, 330), "ゼロ・エナジー", font=font("ja", 70), fill=(30, 20, 40), anchor="lm")
    elif kind == "solace":
        grad((255, 140, 170), (40, 200, 200))
        d.ellipse([380, 160, 640, 420], fill=(255, 235, 200))
        for y in range(300, H, 16):
            d.line([(0, y), (W, y)], fill=(30, 120, 140), width=6)
        d.text((W / 2, 90), "SOLACE", font=font("en", 120), fill=(255, 255, 255), anchor="mm")
        d.text((W / 2, 460), "sleep in the clouds", font=font("en", 44), fill=(255, 255, 255), anchor="mm")
    elif kind == "ramen":
        grad((140, 20, 20), (40, 6, 6))
        d.pieslice([300, 120, 720, 520], 0, 180, fill=(250, 240, 230))
        d.rectangle([300, 300, 720, 330], fill=(250, 240, 230))
        d.ellipse([340, 270, 680, 340], fill=(230, 160, 60))
        for x in (420, 512, 604):
            d.line([(x + 12 * math.sin(t / 7.0), 250 - t * 1.6) for t in range(0, 90, 3)], fill=(255, 255, 255), width=8)
        d.text((60, 90), "一番", font=font("ja", 130), fill=(255, 230, 120), anchor="lm")
        d.text((W - 60, 90), "らーめん", font=font("ja", 80), fill=(255, 255, 255), anchor="rm")
    elif kind == "orbital":
        grad((5, 5, 20), (20, 30, 70))
        for _ in range(140):
            x, y = rr.uniform(0, W), rr.uniform(0, H)
            d.point((x, y), fill=(255, 255, 255))
        d.ellipse([620, 260, 1180, 820], fill=(30, 90, 170), outline=(140, 210, 255), width=6)
        d.polygon([(300, 380), (330, 120), (360, 380)], fill=(240, 240, 250))
        d.text((60, 120), "ORBITAL", font=font("en", 120), fill=(240, 240, 255), anchor="lm")
        d.text((64, 230), "your seat to the stars", font=font("en", 40), fill=(160, 210, 255), anchor="lm")
    elif kind == "pachinko":
        grad((40, 0, 70), (200, 0, 120))
        for k in range(60):
            x, y = rr.uniform(40, W - 40), rr.uniform(40, H - 40)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(230, 230, 240))
        d.text((W / 2, H / 2), "パチンコ", font=font("ja", 170), fill=(255, 240, 80), anchor="mm")
    elif kind == "dispatch":
        grad((12, 0, 0), (40, 0, 4))
        d.rectangle([12, 12, W - 13, H - 13], outline=(255, 40, 50), width=10)
        d.text((W / 2, 200), "OBEY DISPATCH", font=font("en", 120), fill=(255, 40, 50), anchor="mm")
        d.text((W / 2, 360), "人間不要", font=font("ja", 110), fill=(255, 120, 120), anchor="mm")
    d.rectangle([0, 0, W - 1, H - 1], outline=(20, 20, 20), width=6)
    return im


def roofneon(text, lang, col):
    W, H = 1024, 256
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    f = fit(lang, text, W - 60, 210)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).text((W / 2, H / 2), text, font=f, fill=col, anchor="mm")
    im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(10)), 0.6)
    d = ImageDraw.Draw(im)
    d.text((W / 2, H / 2), text, font=f, fill=tuple(min(255, int(c * 0.4 + 160)) for c in col), anchor="mm")
    return im


def holo_koi(col=(255, 150, 60)):
    S = 512
    im = Image.new("RGB", (S, S), (0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(120 + t * 2.8, 256 + 70 * math.sin(t / 30.0)) for t in range(0, 100, 2)]
    for k, (x, y) in enumerate(pts):
        r = 52 * math.sin(math.pi * min(1.0, (k + 4) / len(pts)))
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], outline=col, width=5)
    x, y = pts[-1]
    d.polygon([(x, y), (x + 70, y - 60), (x + 50, y), (x + 70, y + 60)], outline=col, width=6)
    d.ellipse([140, 230, 156, 246], fill=col)
    for k in range(3):
        d.arc([60 + k * 30, 120 + k * 10, 260 + k * 30, 400 - k * 10], 200, 330, fill=(120, 220, 255), width=4)
    return im


def holo_neko(col=(255, 230, 120)):
    S = 512
    im = Image.new("RGB", (S, S), (0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([136, 170, 376, 450], outline=col, width=9)                       # body
    d.ellipse([156, 70, 356, 250], outline=col, width=9)                        # head
    d.polygon([(170, 120), (180, 40), (230, 90)], outline=col, width=8)          # ears
    d.polygon([(342, 120), (332, 40), (282, 90)], outline=col, width=8)
    d.line([(376, 250), (440, 140), (450, 80)], fill=col, width=12)             # the beckoning paw
    d.ellipse([430, 50, 476, 96], outline=col, width=8)
    d.ellipse([200, 140, 222, 162], fill=col)
    d.ellipse([290, 140, 312, 162], fill=col)
    d.ellipse([196, 300, 316, 420], outline=(255, 120, 80), width=8)            # the coin
    d.text((256, 360), "福", font=font("ja", 80), fill=(255, 120, 80), anchor="mm")
    return im


def holo_24(col=(90, 255, 160)):
    S = 512
    im = Image.new("RGB", (S, S), (0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 120, 472, 392], 40, outline=col, width=10)
    d.text((256, 230), "24H", font=font("en", 190), fill=col, anchor="mm")
    d.text((256, 350), "営業中", font=font("ja", 60), fill=col, anchor="mm")
    return im


def holo_can(col=(120, 200, 255)):
    S = 512
    im = Image.new("RGB", (S, S), (0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([170, 60, 342, 110], outline=col, width=8)
    d.ellipse([170, 400, 342, 450], outline=col, width=8)
    d.line([(170, 85), (170, 425)], fill=col, width=8)
    d.line([(342, 85), (342, 425)], fill=col, width=8)
    d.text((256, 255), "Z", font=font("en", 170), fill=col, anchor="mm")
    for k in range(6):
        a = k * math.pi / 3
        d.line([(256 + 200 * math.cos(a), 255 + 200 * math.sin(a)), (256 + 240 * math.cos(a), 255 + 240 * math.sin(a))],
               fill=(255, 255, 255), width=6)
    return im


def sewer_plate(text, sub, kind):
    W, H = 512, 192
    if kind == "hazard":
        im = Image.new("RGB", (W, H), (230, 190, 20))
        d = ImageDraw.Draw(im)
        for k in range(-H, W, 48):
            d.polygon([(k, H), (k + 24, H), (k + 24 + H, 0), (k + H, 0)], fill=(20, 20, 20))
        d.rectangle([60, 30, W - 60, H - 30], fill=(230, 190, 20))
        d.text((W / 2, H / 2 - 18), text, font=font("ja", 62), fill=(20, 20, 20), anchor="mm")
        d.text((W / 2, H / 2 + 40), sub, font=font("en", 34), fill=(20, 20, 20), anchor="mm")
    else:
        im = Image.new("RGB", (W, H), (20, 60, 40))
        d = ImageDraw.Draw(im)
        d.rectangle([8, 8, W - 9, H - 9], outline=(200, 240, 210), width=6)
        d.text((W / 2, H / 2 - 20), text, font=font("ja", 66), fill=(220, 255, 230), anchor="mm")
        d.text((W / 2, H / 2 + 44), sub, font=font("en", 36), fill=(170, 230, 190), anchor="mm")
    return im


def main():
    T2.main()                                                    # the v2 set (blades, boards, holos, MAINFRAME)
    AMB, GRN, CYN, WHT, RED = (255, 170, 40), (90, 255, 120), (80, 230, 255), (240, 240, 255), (255, 40, 50)
    tick = [("en", "NIKKEI  +3.2%   CHIP INDEX  -1.4%   RAIN 90%   TRAIN 7 DELAYED", AMB),
            ("ja", "本日の天気 雨  ・  電脳修理 半額  ・  終電 23:58", GRN),
            ("en", "HALCYON  204.1   MERIDIAN  88.6   SOLACE  141.0   ORBITAL  312.9", CYN),
            ("ko", "오늘의 날씨 비  ・  칩 수리 할인  ・  24시간 영업", WHT),
            ("zh", "今日特价  ・  电脑维修  ・  网吧 通宵", AMB),
            ("en", "CURFEW 02:00  ...  DISPATCH IS WATCHING  ...  CURFEW 02:00", RED)]
    for k, (lang, t, c) in enumerate(tick):
        ticker(t, lang, c, seed=k).save(os.path.join(OUT, "ticker_%02d.png" % k))
    boxes = [("ja", "薬", (30, 120, 60), (240, 250, 240)), ("ja", "酒", (250, 245, 230), (170, 20, 20)),
             ("ja", "湯", (255, 255, 255), (30, 60, 160)), ("en", "24", (20, 20, 20), (255, 210, 40)),
             ("en", "BAR", (255, 240, 220), (120, 30, 140)), ("ja", "質", (250, 250, 250), (20, 90, 150)),
             ("ko", "칩", (20, 20, 20), (120, 255, 200)), ("zh", "电", (255, 230, 60), (200, 30, 40))]
    for k, (lang, t, fg, bg) in enumerate(boxes):
        lightbox(t, lang, fg, bg, seed=k).save(os.path.join(OUT, "box_%02d.png" % k))
    wraps = [("ja", "パチンコ", (255, 240, 120), (150, 0, 90)), ("en", "KARAOKE", (255, 255, 255), (20, 80, 200)),
             ("ja", "ゲーム", (40, 30, 10), (255, 200, 40)), ("en", "HOTEL", (255, 220, 230), (130, 20, 60))]
    for k, (lang, t, fg, bg) in enumerate(wraps):
        wrap(t, lang, fg, bg, seed=k).save(os.path.join(OUT, "wrap_%02d.png" % k))
    cl = [("ja", "営業中", (255, 255, 255), (200, 30, 30)), ("ja", "大売出し", (20, 20, 20), (240, 210, 40)),
          ("ja", "らーめん", (255, 255, 255), (30, 60, 150)), ("ja", "焼き鳥", (30, 20, 10), (240, 235, 220)),
          ("ko", "할인", (255, 255, 255), (30, 140, 90)), ("zh", "开业", (255, 230, 120), (180, 20, 30))]
    for k, (lang, t, fg, bg) in enumerate(cl):
        cloth(t, lang, fg, bg, seed=k).save(os.path.join(OUT, "cloth_%02d.png" % k))
    for k, kind in enumerate(("neuro", "drink", "solace", "ramen", "orbital", "pachinko", "dispatch")):
        billboard(kind, seed=k).save(os.path.join(OUT, "bill_%02d.png" % k))
    for k, (lang, t, c) in enumerate([("en", "HOTEL", (255, 80, 160)), ("ja", "カラオケ", (80, 220, 255)),
                                      ("en", "NOODLES", (255, 190, 60))]):
        roofneon(t, lang, c).save(os.path.join(OUT, "roofneon_%02d.png" % k))
    holo_koi().save(os.path.join(OUT, "holo_koi.png"))
    holo_neko().save(os.path.join(OUT, "holo_neko.png"))
    holo_24().save(os.path.join(OUT, "holo_24.png"))
    holo_can().save(os.path.join(OUT, "holo_can.png"))
    for k, (t, s, kind) in enumerate([("下水道 7号", "SEWER LINE 7", "plate"), ("危険", "DANGER: FLOOD CHANNEL", "hazard"),
                                      ("排水 B-4", "OUTFALL B-4", "plate")]):
        sewer_plate(t, s, kind).save(os.path.join(OUT, "sewer_%02d.png" % k))
    print("v3 textures ->", OUT, len(os.listdir(OUT)))


if __name__ == "__main__":
    main()
