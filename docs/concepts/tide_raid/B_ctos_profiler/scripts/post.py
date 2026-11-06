"""Squint strips, deutan/tritan sims and the contact sheet for direction B."""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FONT = 'D:/rc_art/art-pass/assets/fonts/ShareTechMono-Regular.ttf'
ORDER = [('decay', '1 DECAY'), ('draw', '2 DRAW'), ('plan', '3 PLAN'), ('forecast', '4 FORECAST'), ('response', '5 RESPONSE'),
         ('playout_impact', '6a PLAYOUT impact / shield'), ('playout_home', '6b PLAYOUT HOME hit'), ('aftermath', '7 AFTERMATH'),
         ('hq_step', '8 HQ STEP'), ('city_lost', 'CITY LOST'), ('all_panels_removed', 'ALL PANELS REMOVED (forecast)')]

# Machado, Oliveira, Fernandes 2009, severity 1.0, applied in linear RGB
M = {'deutan': np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
     'tritan': np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]])}


def to_lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def to_srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)


def sim(im, kind):
    a = to_lin(np.asarray(im.convert('RGB'), dtype=np.float32) / 255.0)
    b = a @ M[kind].T
    return Image.fromarray((to_srgb(b) * 255 + 0.5).astype(np.uint8))


def main():
    os.makedirs(f'{OUT}/strips', exist_ok=True)
    os.makedirs(f'{OUT}/cvd', exist_ok=True)
    for n, _ in ORDER:
        p = f'{OUT}/{n}.png'
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB')
        im.resize((320, 180), Image.LANCZOS).save(f'{OUT}/strips/{n}_320.png')
        im.filter(ImageFilter.GaussianBlur(4)).save(f'{OUT}/strips/{n}_blur4_1920.png')
    for n in ('forecast', 'playout_impact', 'playout_home'):
        im = Image.open(f'{OUT}/{n}.png').convert('RGB')
        for k in ('deutan', 'tritan'):
            sim(im, k).save(f'{OUT}/cvd/{n}_{k}.png')
    # contact sheet: every beat in order, each with its two squint strips
    cw, ch = 624, 351
    sw, sh = 200, 112
    cols = 4
    rows = (len(ORDER) + cols - 1) // cols
    pad = 14
    lab = 26
    cell_h = lab + ch + sh + 8
    sheet = Image.new('RGB', (cols * (cw + pad) + pad, rows * (cell_h + pad) + pad + 46), (6, 8, 18))
    d = ImageDraw.Draw(sheet)
    f1 = ImageFont.truetype(FONT, 18)
    f2 = ImageFont.truetype(FONT, 26)
    d.text((pad, 10), 'B  ctOS PROFILER   the city as a hacked surveillance feed, whole raid, no panels', font=f2, fill=(120, 225, 255))
    for i, (n, label) in enumerate(ORDER):
        p = f'{OUT}/{n}.png'
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB')
        x = pad + (i % cols) * (cw + pad)
        y = 46 + pad + (i // cols) * (cell_h + pad)
        d.text((x, y), label, font=f1, fill=(230, 235, 245))
        sheet.paste(im.resize((cw, ch), Image.LANCZOS), (x, y + lab))
        s1 = im.resize((320, 180), Image.LANCZOS).resize((sw, sh), Image.LANCZOS)
        s2 = im.filter(ImageFilter.GaussianBlur(4)).resize((sw, sh), Image.LANCZOS)
        sheet.paste(s1, (x, y + lab + ch + 4))
        sheet.paste(s2, (x + sw + 6, y + lab + ch + 4))
        d.text((x + 2 * sw + 14, y + lab + ch + 8), '320 px  |  blur 4', font=f1, fill=(120, 130, 150))
    sheet.save(f'{OUT}/sheet.jpg', quality=90)


if __name__ == '__main__':
    main()
