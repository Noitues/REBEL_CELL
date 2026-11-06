"""Squint strips, deutan/tritan sims, contact sheet."""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from lib import OUT, font

FR = OUT + 'frames/'
SQ = OUT + 'squint/'
CB = OUT + 'colorblind/'
os.makedirs(SQ, exist_ok=True)
os.makedirs(CB, exist_ok=True)

names = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(FR + '*.png'))


def squint(name):
    im = Image.open(FR + name + '.png').convert('RGB')
    im.resize((320, 180), Image.LANCZOS).save(SQ + name + '_320.png')
    im.filter(ImageFilter.GaussianBlur(4)).save(SQ + name + '_blur4.png')


# Machado et al. 2009, severity 1.0 (applied in linear RGB)
M = {
    'deutan': np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    'tritan': np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def lin(c):
    return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def unlin(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= .0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - .055)


def cb(name, kind):
    a = np.asarray(Image.open(FR + name + '.png').convert('RGB'), np.float32) / 255
    out = unlin(lin(a) @ M[kind].T)
    Image.fromarray((out * 255 + .5).astype('uint8')).save(CB + '%s_%s.png' % (name, kind))


def sheet():
    cw, ch = 480, 270
    sw, sh = 238, 134
    pad = 10
    cols = 4
    rows = (len(names) + cols - 1) // cols
    cellh = ch + sh + 34
    S = Image.new('RGB', (cols * (cw + pad) + pad, rows * cellh + pad + 0), (20, 16, 34))
    dr = ImageDraw.Draw(S)
    f = font(20, 700, 80)
    for i, n in enumerate(names):
        c, r = i % cols, i // cols
        x, y = pad + c * (cw + pad), pad + r * cellh
        im = Image.open(FR + n + '.png').convert('RGB')
        S.paste(im.resize((cw, ch), Image.LANCZOS), (x, y))
        S.paste(Image.open(SQ + n + '_320.png').resize((sw, sh), Image.LANCZOS), (x, y + ch + 4))
        S.paste(Image.open(SQ + n + '_blur4.png').resize((sw, sh), Image.LANCZOS), (x + sw + 4, y + ch + 4))
        dr.text((x, y + ch + sh + 8), n, font=f, fill=(235, 230, 255))
    S.save(OUT + 'sheet.jpg', quality=90)


if __name__ == '__main__':
    for n in names:
        squint(n)
    for n in ('04_forecast', '06a_playout_shield', '06b_playout_home_hit'):
        for k in M:
            cb(n, k)
    sheet()
    print('ok')
