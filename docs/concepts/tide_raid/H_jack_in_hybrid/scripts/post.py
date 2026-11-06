"""Squint strips, colour-blind sims and the contact sheet.  python post.py"""
import os, glob
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

BASE = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H_jack_in_hybrid/'
FR = BASE + 'frames/'
SQ = BASE + 'squint/'
CB = BASE + 'colorblind/'
for d in (SQ, CB):
    os.makedirs(d, exist_ok=True)

# Machado, Oliveira, Fernandes 2009 (severity 1.0), applied in linear RGB
DEUT = np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]])
TRIT = np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]])


def lin(a):
    return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)


def unlin(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= .0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - .055)


def sim(im, M):
    a = lin(np.asarray(im.convert('RGB'), np.float32) / 255)
    o = a @ M.T
    return Image.fromarray((unlin(o) * 255 + .5).astype(np.uint8))


frames = sorted(glob.glob(FR + '*.png'))
# 1280 legibility check: one frame downscaled
Image.open(FR + '04_forecast.png').convert('RGB').resize((1280, 720), Image.LANCZOS).save(SQ + 'check_1280_04_forecast.png')
Image.open(FR + '07_playout_home.png').convert('RGB').resize((1280, 720), Image.LANCZOS).save(SQ + 'check_1280_07_playout_home.png')
for f in frames:
    n = os.path.basename(f)[:-4]
    im = Image.open(f).convert('RGB')
    im.resize((320, 180), Image.LANCZOS).save(SQ + n + '_320.png')
    im.filter(ImageFilter.GaussianBlur(4)).save(SQ + n + '_blur4.png')
    if n.startswith(('04_', '06_', '07_', '12_')):
        sim(im, DEUT).save(CB + n + '_deutan.png')
        sim(im, TRIT).save(CB + n + '_tritan.png')

# contact sheet
cols, tw, th = 3, 800, 450
sel = [f for f in frames]
rows = (len(sel) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw + (cols + 1) * 10, rows * (th + 30) + 10), (8, 6, 20))
d = ImageDraw.Draw(sheet)
try:
    ft = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 18)
except Exception:
    ft = None
for i, f in enumerate(sel):
    r, c = divmod(i, cols)
    x = 10 + c * (tw + 10)
    y = 10 + r * (th + 30)
    im = Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS)
    sheet.paste(im, (x, y + 24))
    d.text((x, y + 2), os.path.basename(f)[:-4], fill=(127, 239, 255), font=ft)
sheet.save(BASE + 'sheet.jpg', quality=90)
print('post done', len(frames), 'frames')
