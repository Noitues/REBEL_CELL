"""P3 V-gap check: plate crops side by side with the reference frames (Cyberpunk 2077, Frostpunk, WD2 / Google-style city overview).
python ref_compare.py -> P3_plates/ref_vs_p3.jpg   (each row: P3 plate crop | reference frame, labelled)"""
import os
from PIL import Image, ImageDraw, ImageFont
O = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/'
R = 'D:/rc_scratch/tide_concepts/refs/'
ROWS = [
    ('01_plan hot (wet street, facades, shafts)', '01_plan', (380, 330, 1180, 780), 'CP2077 neon alley (cp2077/s09)', R + 'cp2077/s09.jpg'),
    ('04_impact hot', '04_impact', (200, 330, 1000, 780), 'CP2077 wet street (cp2077/s11)', R + 'cp2077/s11.jpg'),
    ('02_forecast whole', '02_forecast', None, 'Frostpunk city + overlay (frostpunk/s08)', R + 'frostpunk/s08.jpg'),
    ('01_plan whole', '01_plan', None, 'WD2 city overview (wd2/s02)', R + 'wd2/s02.jpg'),
]
try:
    F = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 18)
except Exception:
    F = None
W, H = 800, 450
sh = Image.new('RGB', (2 * W + 30, len(ROWS) * (H + 32) + 10), (8, 6, 20))
d = ImageDraw.Draw(sh)
for i, (t1, key, box, t2, ref) in enumerate(ROWS):
    y = 10 + i * (H + 32)
    p = Image.open(O + 'plates/%s.png' % key).convert('RGB')
    if box:
        p = p.crop(box)
    sh.paste(p.resize((W, H), Image.LANCZOS), (10, y + 24))
    sh.paste(Image.open(ref).convert('RGB').resize((W, H), Image.LANCZOS), (20 + W, y + 24))
    d.text((10, y + 2), 'P3  ' + t1, fill=(127, 239, 255), font=F)
    d.text((20 + W, y + 2), t2, fill=(255, 200, 120), font=F)
sh.save(O + 'ref_vs_p3.jpg', quality=90)
print('ok')
