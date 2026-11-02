"""rings_crop.jpg: Solace vs Meridian enemy rings, 2x, side by side (right-upper arc of the board, with tape, tokens, tickets)"""
import sys
from PIL import Image, ImageDraw, ImageFont
O = 'D:/rc_scratch/corp_skin/colour_only/out/'
box = (60, 60, 1010, 600)       # upper half of the board
ims = []
for c in ('solace', 'meridian'):
    im = Image.open(O + 'p1_%s.png' % c).convert('RGB').crop(box)
    ims.append(im.resize((im.width * 2, im.height * 2), Image.LANCZOS))
w, h = ims[0].size
sheet = Image.new('RGB', (w, h * 2 + 70), (12, 12, 16))
f = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 34)
d = ImageDraw.Draw(sheet)
d.text((12, 12), 'SOLACE  (lime #96FF46)', fill=(150, 255, 70), font=f)
sheet.paste(ims[0], (0, 60))
d.text((12, h + 72), 'MERIDIAN  (orange #FF8C1A)', fill=(255, 140, 26), font=f)
sheet.paste(ims[1], (0, h + 130))
sheet = sheet.crop((0, 0, w, h * 2 + 130))
sheet.save('D:/rc_art/art-pass/docs/concepts/combat_redesign/corp_skins/colour_only/rings_crop.jpg', quality=92)
print(sheet.size)
