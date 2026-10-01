"""Render all 8 S1 sheets and the contact sheet.  Usage: python render_all.py"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
from lowpoly import font
import s01_operatives, s02_enemies, s03_landmarks, s04_threats, s05_cards, s06_icons, s07_items, s08_stamps

OUT = os.path.dirname(HERE)
paths = [m.render() for m in (s01_operatives, s02_enemies, s03_landmarks, s04_threats, s05_cards, s06_icons,
                              s07_items, s08_stamps)]
tw, th, pad, lab = 640, 360, 16, 30
sheet = Image.new('RGB', (2 * tw + 3 * pad, 4 * (th + lab + pad) + pad + 40), (20, 20, 22))
d = ImageDraw.Draw(sheet)
d.text((pad, 10), 'S1  Cv2 + E cel shading  -  asset samples', font=font(11), fill=(240, 230, 210))
for k, p in enumerate(paths):
    r, c = divmod(k, 2)
    x, y = pad + c * (tw + pad), 40 + pad + r * (th + lab + pad)
    sheet.paste(Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS), (x, y))
    d.text((x, y + th + 4), os.path.basename(p)[:-4], font=font(10), fill=(220, 210, 195))
sheet.save(os.path.join(OUT, 'contact_sheet.jpg'), quality=88)
print('wrote contact_sheet.jpg')
