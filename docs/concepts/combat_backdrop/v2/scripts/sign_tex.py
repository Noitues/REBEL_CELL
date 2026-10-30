"""Neon sign textures (PIL) for the street slice. usage: python sign_tex.py  -> D:/rc_scratch/cutaway_kit/signs/<name>.png"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = 'D:/rc_scratch/cutaway_kit/signs/'
R = 'D:/rc_art/art-pass/assets/fonts/'
ANTON = R + 'Anton-Regular.ttf'
MONO = R + 'ShareTechMono-Regular.ttf'
os.makedirs(OUT, exist_ok=True)

# name: (text, sub, hex colour, size (w,h) px, vertical)
SIGNS = {
    'solace_h': ('SOLACE', 'WELLNESS + GENE', '#96FF46', (1024, 256), False),
    'solace_v': ('SOLACE', 'CLINIC 24H', '#96FF46', (256, 1024), True),
    'pharma_v': ('PHARMA', 'RX', '#3FE6FF', (256, 1024), True),
    'tea_v': ('TEA', 'ALL NIGHT', '#FF4696', (256, 768), True),
    'bar_h': ('BAR', '24 H', '#FF4696', (640, 256), False),
    'data_h': ('DATA', 'OPEN', '#3FE6FF', (640, 256), False),
    'noodle_h': ('NOODLE', 'NEW', '#FFB938', (768, 256), False),
    'gene_h': ('GENE', 'TESTS', '#96FF46', (640, 256), False),
    'karaoke_h': ('KARAOKE', 'OPEN', '#FF4696', (896, 256), False),
    'rx_h': ('RX', 'PHARMA', '#96FF46', (512, 256), False),
    'sky_h': ('THE SKY IS LEASED', 'SOLACE CONTINUUM', '#B07AFF', (1280, 320), False),
    'arcade_h': ('ARCADE', '', '#FFB938', (768, 256), False),
    'vita_h': ('VITA', 'IMPLANT', '#3FE6FF', (640, 256), False),
}


def hexa(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def make(name, text, sub, col, size, vert):
    W, H = size
    im = Image.new('RGBA', (W, H), (14, 10, 28, 255))
    d = ImageDraw.Draw(im)
    c = hexa(col)
    d.rectangle([6, 6, W - 7, H - 7], outline=c, width=10)
    d.rectangle([26, 26, W - 27, H - 27], outline=hexa(col, 90), width=3)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    if not vert:
        fs = int(H * (0.52 if sub else 0.62))
        f = ImageFont.truetype(ANTON, fs)
        while d.textlength(text, font=f) > W - 80 and fs > 20:
            fs -= 4
            f = ImageFont.truetype(ANTON, fs)
        tw = d.textlength(text, font=f)
        ty = H * (0.12 if sub else 0.17)
        gd.text(((W - tw) / 2, ty), text, font=f, fill=c)
        if sub:
            f2 = ImageFont.truetype(MONO, int(H * 0.15))
            tw2 = d.textlength(sub, font=f2)
            gd.text(((W - tw2) / 2, H * 0.72), sub, font=f2, fill=hexa('#FFFFFF', 230))
    else:
        f = ImageFont.truetype(ANTON, int(W * 0.62))
        step = int(W * 0.78)
        y = 50
        for ch in text:
            tw = d.textlength(ch, font=f)
            gd.text(((W - tw) / 2, y), ch, font=f, fill=c)
            y += step
        if sub:
            f2 = ImageFont.truetype(MONO, int(W * 0.17))
            ys = H - 70
            for ch in sub[:10][::-1]:
                pass
            tw2 = d.textlength(sub, font=f2)
            gd.text(((W - tw2) / 2, H - 80), sub, font=f2, fill=hexa('#FFFFFF', 230))
    blur = glow.filter(ImageFilter.GaussianBlur(7))
    im = Image.alpha_composite(im, Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 0)), blur, 0.55))
    im = Image.alpha_composite(im, glow)
    im.convert('RGB').save(OUT + name + '.png')


if __name__ == '__main__':
    for k, v in SIGNS.items():
        make(k, *v)
    print('signs', len(SIGNS))
