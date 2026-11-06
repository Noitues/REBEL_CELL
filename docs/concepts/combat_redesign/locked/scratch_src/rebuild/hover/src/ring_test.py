"""LANCZOS overshoot of a wax stroke (PLAN on ink) at 2x -> 1x, with and without a pre-blur"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
for blur in (0, 0.5, 0.8, 1.0):
    for meth in ('LANCZOS', 'BOX', 'BICUBIC'):
        im = Image.new('RGBA', (400, 200), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.line([(20, 101), (380, 117)], fill=(12, 10, 22, 255), width=26)
        d.line([(20, 101), (380, 117)], fill=(255, 226, 0, 255), width=14)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        bg = Image.new('RGBA', (400, 200), (30, 30, 40, 255))
        bg.alpha_composite(im)
        sm = bg.resize((200, 100), getattr(Image, meth))
        a = np.asarray(sm).astype(int)
        print('blur', blur, meth, 'max G', a[..., 1].max(), 'max R', a[..., 0].max())
