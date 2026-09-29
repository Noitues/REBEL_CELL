"""Lay the three marker frames out as one 1920x1080 strip with beat captions (pure Pillow).
Usage: python strip_layout.py STAGE1.png STAGE2.png STAGE3.png OUT.png"""
import os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "assets", "fonts"))
mono = lambda s: ImageFont.truetype(os.path.join(FONTS, "ShareTechMono-Regular.ttf"), s)
anton = lambda s: ImageFont.truetype(os.path.join(FONTS, "Anton-Regular.ttf"), s)

stages, out = sys.argv[1:4], sys.argv[4]
W, H = 1920, 1080
PW, PH, G, TOP = 600, 840, 30, 96
sheet = Image.new("RGB", (W, H), (5, 7, 11))
d = ImageDraw.Draw(sheet)
d.text((G, 26), "THE MARKER IS LIVE INK", font=anton(40), fill=(242, 246, 255))
d.text((G + 470, 44), "feedback 6  //  pink marker = someone writing on the screen glass; the page underneath is what moves",
       font=mono(18), fill=(122, 136, 156))
caps = [("1  WRITE-ON", "stroke by stroke in stroke order, 0.45 s; the nib rides the last point"),
        ("2  DRIPS FORM, THEN HOLD", "4 drips swell for 0.8 s at the letters' low points, then pause while the game waits"),
        ("3  PRESS: PAGE LEAVES, INK RUNS", "the page slides out under the glass; the drips keep running down the screen")]
for i, p in enumerate(stages):
    im = Image.open(p).convert("RGB")
    sw = im.width / 1920
    crop = im.crop((int(660 * sw), int(110 * sw), int((660 + PW) * sw), int((110 + PH) * sw))).resize((PW, PH), Image.LANCZOS)
    x = G + i * (PW + G)
    sheet.paste(crop, (x, TOP))
    d.rectangle((x, TOP, x + PW - 1, TOP + PH - 1), outline=(58, 90, 112), width=1)
    d.line((x, TOP + PH + 14, x + PW, TOP + PH + 14), fill=(255, 61, 168), width=2)
    d.text((x, TOP + PH + 24), caps[i][0], font=anton(26), fill=(255, 61, 168))
    for j, line in enumerate(textwrap.wrap(caps[i][1], 66)):
        d.text((x, TOP + PH + 58 + j * 20), line, font=mono(15), fill=(175, 192, 214))
    if i < 2:
        d.text((x + PW + 4, TOP + PH // 2 - 14), ">", font=mono(26), fill=(122, 136, 156))
sheet.save(out, optimize=True)
print("STRIP", out)
