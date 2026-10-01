"""compare.jpg (3x3 grid: rows = options, cols = rain/day/night) with small labels."""
import os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TW, TH, PAD, TOP, LEFT = 960, 540, 12, 56, 240
F = 'C:/Windows/Fonts/bahnschrift.ttf'
names = {'f1': 'F1  TENEMENT', 'f2': 'F2  GARAGE', 'f3': 'F3  KIOSK STACK'}
W = LEFT + 3 * TW + 4 * PAD
H = TOP + 3 * TH + 4 * PAD
sheet = Image.new('RGB', (W, H), (18, 17, 22))
d = ImageDraw.Draw(sheet)
fb = ImageFont.truetype(F, 34)
for j, st in enumerate(('rain', 'day', 'night')):
    d.text((LEFT + PAD + j * (TW + PAD) + TW / 2, TOP / 2 + 4), st.upper(), font=fb, fill=(230, 220, 210), anchor='mm')
for i, o in enumerate(('f1', 'f2', 'f3')):
    y = TOP + PAD + i * (TH + PAD)
    d.text((PAD + 6, y + TH / 2), names[o].replace('  ', '\n'), font=fb, fill=(230, 220, 210), anchor='lm')
    for j, st in enumerate(('rain', 'day', 'night')):
        im = Image.open(os.path.join(D, '%s_%s.png' % (o, st))).resize((TW, TH), Image.LANCZOS)
        sheet.paste(im, (LEFT + PAD + j * (TW + PAD), y))
sheet.save(os.path.join(D, 'compare.jpg'), quality=86, optimize=True)
print('compare.jpg', sheet.size)
