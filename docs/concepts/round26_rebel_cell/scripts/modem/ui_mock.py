"""with_ui_mock.png: the recommended backdrop with ghost rectangles where the shop panels go."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else 'f1_rain.png'
img = Image.open(os.path.join(D, src)).convert('RGBA')
lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
d = ImageDraw.Draw(lay)
f = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 30)
CY = (90, 230, 255, 255)
PANELS = [((840, 60, 1500, 420), 'MICROCHIPS'), ((840, 460, 1500, 820), 'CARD BUILDER'),
          ((1560, 60, 1890, 330), 'SHOP NOTES'), ((1560, 640, 1890, 1000), 'INVENTORY')]
for (x0, y0, x1, y1), name in PANELS:
    d.rectangle([x0, y0, x1, y1], fill=(10, 12, 20, 150))
    for x in range(x0, x1, 22):                     # dashed outline
        d.line([(x, y0), (min(x + 12, x1), y0)], fill=CY, width=3)
        d.line([(x, y1), (min(x + 12, x1), y1)], fill=CY, width=3)
    for y in range(y0, y1, 22):
        d.line([(x0, y), (x0, min(y + 12, y1))], fill=CY, width=3)
        d.line([(x1, y), (x1, min(y + 12, y1))], fill=CY, width=3)
    d.text((x0 + 26, y0 + 22), name, font=f, fill=(230, 235, 240, 230))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2 + 10), '(panel)', font=f, fill=(150, 170, 190, 140), anchor='mm')
out = Image.alpha_composite(img, lay).convert('RGB')
name = sys.argv[2] if len(sys.argv) > 2 else 'with_ui_mock.png'
out.save(os.path.join(D, name), optimize=True)
print('with_ui_mock.png from', src)
