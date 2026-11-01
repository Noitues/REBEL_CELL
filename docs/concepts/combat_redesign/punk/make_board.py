"""Build combat_redesign/punk/board.jpg: one row per style (plate A, plate B, wheel crop) + card-title pick row."""
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = "D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/"
OUT = ROOT + "board.jpg"
STYLES = [
    ("spiderpunk_collage", "SPIDER-PUNK COLLAGE", "ref 1", "A poster / B gig flyer"),
    ("xerox_flyer", "XEROX FLYER", "ref 5", "A white sheet / B toner disc"),
    ("linocut", "TWO-TONE LINOCUT", "ref 6", "A pink on black / B pink plate"),
    ("jinx_scribble", "JINX NEON SCRIBBLE", "ref 4", "A night wall / B pink paint"),
    ("wpap_faceted", "WPAP FACETED", "ref 7", "A pink riot / B acid sunburst"),
    ("benday_stickerbomb", "BEN-DAY STICKER BOMB", "ref 8", "A teal sheet / B polka jacket"),
    ("mural_graffiti", "SPIDER-VERSE MURAL", "ref 2", "A brick / B concrete"),
]
RANKS = dict(a.split("=") for a in sys.argv[1:])  # key=label override, e.g. linocut=#1

H = 432
PW = 768
LAB = 340
GAP = 12
F = "C:/Windows/Fonts/"
fT = ImageFont.truetype(F + "impact.ttf", 34)
fH = ImageFont.truetype(F + "impact.ttf", 54)
fS = ImageFont.truetype(F + "arialbd.ttf", 20)
fC = ImageFont.truetype(F + "arialbd.ttf", 18)


def fit_h(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


rows = []
STYLES.sort(key=lambda s: int(RANKS.get(s[0], "#99")[1:]))
for key, title, ref, sub in STYLES:
    a = Image.open(ROOT + key + "/plate_A.png").convert("RGB").resize((PW, H), Image.LANCZOS)
    b = Image.open(ROOT + key + "/plate_B.png").convert("RGB").resize((PW, H), Image.LANCZOS)
    w = fit_h(Image.open(ROOT + key + "/wheel_crop.jpg").convert("RGB"), H)
    rows.append((key, title, ref, sub, a, b, w))

WW = max(r[6].width for r in rows)
W = LAB + GAP + PW + GAP + PW + GAP + WW + GAP
HEAD = 90
ROWH = H + GAP + 30
ct_pick = Image.open(ROOT + "card_titles/plate_pick.png").convert("RGB").resize((PW, H), Image.LANCZOS)
ct_hand = fit_h(Image.open(ROOT + "card_titles/hand2x_A.jpg").convert("RGB"), H)
ct_hand = ct_hand.crop((0, 0, min(ct_hand.width, W - (LAB + GAP + PW + GAP) - GAP), H))
total_h = HEAD + ROWH * (len(rows) + 1) + GAP
S = Image.new("RGB", (W, total_h), (22, 20, 24))
d = ImageDraw.Draw(S)
d.text((GAP, 14), "ART CALL 52  PUNK-ROCK WHEEL + CARD CONCEPTS  (p1_decide, needle removed)", font=fH, fill=(245, 240, 230))

y = HEAD
for key, title, ref, sub, a, b, w in rows:
    d.rectangle((0, y - 4, W, y + H + 28), fill=(32, 29, 34))
    rk = RANKS.get(key, "")
    if rk:
        d.text((GAP, y + 4), rk, font=fH, fill=(255, 60, 150))
    d.text((GAP, y + 70), title, font=fT, fill=(245, 240, 230))
    d.text((GAP, y + 112), ref, font=fS, fill=(190, 185, 180))
    d.text((GAP, y + 140), sub, font=fC, fill=(190, 185, 180))
    d.text((GAP, y + 170), key, font=fC, fill=(140, 135, 130))
    x = LAB + GAP
    for im, cap in ((a, "plate A"), (b, "plate B"), (w, "wheel crop (A | B)")):
        S.paste(im, (x, y))
        d.text((x + 4, y + H + 4), cap, font=fC, fill=(220, 215, 205))
        x += im.width + GAP
    y += ROWH

d.rectangle((0, y - 4, W, y + H + 28), fill=(32, 29, 34))
d.text((GAP, y + 4), "TITLES", font=fH, fill=(255, 60, 150))
d.text((GAP, y + 70), "CARD-TITLE PICK", font=fT, fill=(245, 240, 230))
d.text((GAP, y + 112), "A: black marker tag,", font=fC, fill=(190, 185, 180))
d.text((GAP, y + 136), "white keyline, pink offset", font=fC, fill=(190, 185, 180))
x = LAB + GAP
S.paste(ct_pick, (x, y))
d.text((x + 4, y + H + 4), "plate_pick (F1 + title A)", font=fC, fill=(220, 215, 205))
x += PW + GAP
S.paste(ct_hand, (x, y))
d.text((x + 4, y + H + 4), "hand at 2x, treatment A", font=fC, fill=(220, 215, 205))

S.save(OUT, quality=88)
print(OUT, S.size)
