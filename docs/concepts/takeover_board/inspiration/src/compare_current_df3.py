"""compare_current_df3: the current plates (left) next to Deface v3 (right), rest and hover rows, one image."""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

D = 'D:/rc_art/art-pass/docs/concepts/takeover_board/'
R = D + 'inspiration/rendered/'
F = ImageFont.truetype('D:/rc_scratch/combat_redesign/locked/corp/src/fonts/Anton-Regular.ttf', 34)
ROWS = [(D + 'tk_board.png', R + 'df3_rest.png', 'AT REST'),
        (D + 'tk_forecast.png', R + 'df3_hover.png', 'HOVER: YOUR ICE')]
TW, TH, PAD, CAP = 1200, 675, 20, 56
sheet = Image.new('RGB', (2 * TW + 3 * PAD, 70 + len(ROWS) * (TH + CAP + PAD)), (14, 16, 22))
d = ImageDraw.Draw(sheet)
d.text((PAD, 14), 'TAKEOVER: CURRENT (left) vs DEFACE v3 (right)', font=F, fill=(242, 246, 255))
for k, (a, b, label) in enumerate(ROWS):
    y = 70 + k * (TH + CAP + PAD)
    for j, (path, name) in enumerate([(a, 'CURRENT'), (b, 'DEFACE v3')]):
        x = PAD + j * (TW + PAD)
        d.text((x, y + 6), '%s  ·  %s' % (name, label), font=F, fill=(255, 61, 168) if j else (92, 225, 255))
        sheet.paste(Image.open(path).convert('RGB').resize((TW, TH), Image.LANCZOS), (x, y + CAP))
sheet.save(R + 'compare_current_df3.jpg', quality=90, optimize=True)
print('ok', sheet.size)
