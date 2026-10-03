"""f1b_compare.jpg: rows f1 / f1b, columns rain / day / night."""
import os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TW, TH, PAD, TOP, LEFT = 960, 540, 12, 56, 200
f = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 34)
sheet = Image.new('RGB', (LEFT + 3 * TW + 4 * PAD, TOP + 2 * TH + 3 * PAD), (18, 17, 22))
d = ImageDraw.Draw(sheet)
for j, st in enumerate(('rain', 'day', 'night')):
    d.text((LEFT + PAD + j * (TW + PAD) + TW / 2, TOP / 2 + 4), st.upper(), font=f, fill=(230, 220, 210), anchor='mm')
for i, (o, lab) in enumerate((('f1', 'F1'), ('f1b', 'F1B'))):
    y = TOP + PAD + i * (TH + PAD)
    d.text((PAD + 10, y + TH / 2), lab, font=f, fill=(230, 220, 210), anchor='lm')
    for j, st in enumerate(('rain', 'day', 'night')):
        sheet.paste(Image.open(os.path.join(D, '%s_%s.png' % (o, st))).resize((TW, TH), Image.LANCZOS),
                    (LEFT + PAD + j * (TW + PAD), y))
sheet.save(os.path.join(D, 'f1b_compare.jpg'), quality=86, optimize=True)
print('f1b_compare.jpg')
