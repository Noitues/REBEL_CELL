"""signs_compare.jpg from the saved stills: rows = options, cols = normal + each flashed word."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_all import OPTIONS, OUT, FONT   # noqa: E402
import flicker_sign as FS                 # noqa: E402
tw, th = 250, 545
CROP = (0, 0, 330, 720)
rows = []
for key, lay, seq, title in OPTIONS:
    ext = '.png' if key.startswith('market') else '.jpg'
    cells = [('NORMAL', os.path.join(OUT, key + '_normal' + ext))]
    for w, _ in FS.SEQUENCES[seq]:
        cells.append((w, os.path.join(OUT, '%s_takeover_%s%s' % (key, w.lower(), ext))))
    rows.append((title, cells))
ncol = max(len(c) for _, c in rows)
W, LW = 0, 300
W = LW + ncol * (tw + 10) + 10
H = 20 + len(rows) * (th + 50)
sheet = Image.new('RGB', (W, H), (18, 17, 22))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype(FONT, 24)
for r, (title, cells) in enumerate(rows):
    y = 20 + r * (th + 50)
    t = title.replace('  (', '\n(').replace(' / ', '\n/ ')
    d.multiline_text((14, y + 40), t, font=f, fill=(235, 228, 220), spacing=6)
    for c, (n, p) in enumerate(cells):
        x = LW + c * (tw + 10)
        sheet.paste(Image.open(p).convert('RGB').crop(CROP).resize((tw, th), Image.LANCZOS), (x, y + 36))
        d.text((x + 4, y + 4), n if n == 'NORMAL' else '%d. %s' % (c, n), font=f,
               fill=(235, 228, 220) if n == 'NORMAL' else (170, 255, 90))
sheet.save(os.path.join(OUT, 'signs_compare.jpg'), quality=88)
print(sheet.size)
