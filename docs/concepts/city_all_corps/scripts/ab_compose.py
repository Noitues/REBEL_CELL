"""Round 3c: the realism A/B contact sheet: ab_compose.py <out.jpg> <a.png> <b.png> <c.png> -- three frames side by side with
their values (median, under 0.10, over 0.85, spread) and the settings under each."""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

out, paths = sys.argv[1], sys.argv[2:5]
LAB = ["(a) current: 32 spp, vignette + full bloom, 28 mm", "(b) 80 spp, albedo+normal OIDN, bloom x0.5, no vignette, fog tint -40 %",
       "(c) (b) + 50 mm lens from 1.8x further back"]
ims = [Image.open(p).convert("RGB") for p in paths]
w = 1280
h = int(ims[0].size[1] * w / ims[0].size[0])
sheet = Image.new("RGB", (w * 3 + 40, h + 130), (12, 12, 16))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 22)
for i, (im, p) in enumerate(zip(ims, paths)):
    a = np.asarray(im, np.float32) / 255
    l = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    lin = l
    s = "median %.3f   <0.10 %.1f %%   >0.85 %.2f %%   spread %.3f" % (np.median(lin), 100 * (lin < 0.1).mean(), 100 * (lin > 0.85).mean(),
                                                                       np.percentile(lin, 90) - np.percentile(lin, 10))
    x = 10 + i * (w + 10)
    sheet.paste(im.resize((w, h), Image.LANCZOS), (x, 10))
    d.text((x, h + 22), LAB[i], font=f, fill=(235, 235, 240))
    d.text((x, h + 56), s, font=f, fill=(255, 190, 120))
    print(LAB[i], s)
sheet.save(out, quality=90)
