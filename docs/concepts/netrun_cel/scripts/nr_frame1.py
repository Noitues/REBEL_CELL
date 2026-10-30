"""Frame 1: r42 plan frame with the Solace netrun district highlighted. Usage: python nr_frame1.py <out.png>"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import numpy as np

SRC = 'D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/r42/plan_r42.png'
out = sys.argv[1]
im = Image.open(SRC).convert('RGB').resize((1920, 1080), Image.LANCZOS)
POLY = [(1070, 400), (1500, 330), (1590, 700), (1150, 800)]
LIME = (150, 255, 70)
mask = Image.new('L', im.size, 0)
ImageDraw.Draw(mask).polygon(POLY, fill=255)
arr = np.asarray(im).astype(np.float32)
m = np.asarray(mask).astype(np.float32)[..., None] / 255
dim = arr * 0.38 * np.array([0.9, 0.85, 1.1])
glowm = np.asarray(mask.filter(ImageFilter.GaussianBlur(40))).astype(np.float32)[..., None] / 255
res = arr * m + dim * (1 - m)
res = res + glowm * (1 - m) * np.array([6, 24, 4])          # faint lime halo outside the edge
res = res + m * np.array([8, 14, 4])                        # lift inside slightly
img = Image.fromarray(np.clip(res, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(img, 'RGBA')
for w, a in ((9, 40), (5, 90), (2, 255)):
    d.line(POLY + [POLY[0]], fill=LIME + (a,), width=w, joint='curve')
# corner brackets
for (x, y) in POLY:
    d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=LIME + (255,), width=3)
# leader to the helix HQ and label
f = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 30)
fs = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 20)
lab = (40, 40)
d.rectangle((lab[0], lab[1], lab[0] + 560, lab[1] + 92), fill=(10, 4, 24, 215), outline=LIME + (255,), width=2)
d.text((lab[0] + 16, lab[1] + 10), 'SOLACE  /  GREENLINE AVE  /  BLK 07', font=f, fill=LIME)
d.text((lab[0] + 16, lab[1] + 52), 'NETRUN DISTRICT  -  ZOOM TO ENTER', font=fs, fill=(255, 70, 150))
d.line([(lab[0] + 560, lab[1] + 46), (1050, 420)], fill=LIME + (200,), width=2)
img.save(out)
print('wrote', out)
