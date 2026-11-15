"""tk_sheet: the B-086 contact sheet (the board plate and the five fight states), 3 x 2 at half scale, with a caption per plate."""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

D = 'D:/rc_art/art-pass/docs/concepts/takeover_board/'
F = ImageFont.truetype('D:/rc_scratch/combat_redesign/locked/corp/src/fonts/Anton-Regular.ttf', 34)
F2 = ImageFont.truetype('D:/rc_scratch/combat_redesign/locked/corp/src/fonts/ShareTechMono-Regular.ttf', 24)
PLATES = [('board', 'BOARD', 'turn 3, play phase, nothing hovered'),
          ('play', '1  PLAY', 'BREACH lifted, legal targets, the take in pencil'),
          ('forecast', '2  END TURN FORECAST', 'your ICE hovered: its outcome and numbered arrows'),
          ('resolve', '3  RESOLUTION', 'replay at step 13: numbered arrows, the retake'),
          ('wallseal', '4  WALL AND SEAL', 'walls and seals of both sides as pieces'),
          ('win', '5  WIN', 'all 12 segments are yours')]
TW, TH, CAP, PAD = 960, 540, 70, 20
sheet = Image.new('RGB', (3 * TW + 4 * PAD, 2 * (TH + CAP) + 3 * PAD + 70), (14, 16, 22))
d = ImageDraw.Draw(sheet)
d.text((PAD, 18), 'B-086  TAKEOVER BOARD IN THE LOCKED FAMILY  (concept plates, Solace skin, 2026-11-15)', font=F, fill=(242, 246, 255))
for k, (name, title, sub) in enumerate(PLATES):
    x = PAD + (k % 3) * (TW + PAD); y = 70 + PAD + (k // 3) * (TH + CAP + PAD)
    im = Image.open(D + 'tk_%s.png' % name).convert('RGB').resize((TW, TH), Image.LANCZOS)
    sheet.paste(im, (x, y + CAP))
    d.text((x, y + 4), title, font=F, fill=(255, 61, 168))
    d.text((x + 6 + d.textlength(title, font=F) + 14, y + 16), sub, font=F2, fill=(175, 192, 214))
sheet.save(D + 'tk_sheet.jpg', quality=90, optimize=True)
print('ok', sheet.size)
