"""loudmap.py in.png out.png : squint luma map x8 with loud cells outlined red, tower circle"""
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
im = Image.open(sys.argv[1]).convert('RGB')
s = im.resize((120, 67), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
a = np.asarray(s, np.float32) / 255
l = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
big = s.resize((960, 536), Image.NEAREST)
d = ImageDraw.Draw(big)
for y in range(67):
    for x in range(120):
        if l[y, x] > 0.38:
            d.rectangle([x * 8, y * 8, x * 8 + 7, y * 8 + 7], outline=(255, 0, 0))
d.ellipse([268 - 106, 270 - 106, 268 + 106, 270 + 106], outline=(0, 255, 0))
big.crop((120, 130, 420, 410)).resize((600, 560), Image.NEAREST).save(sys.argv[2])
