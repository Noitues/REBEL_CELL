import sys
from PIL import Image, ImageDraw, ImageFont
ROOT = 'D:/rc_scratch/combat_redesign/punk/jinx_scribble/'
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/jinx_scribble/'
A = Image.open(ROOT + 'out/plate_A_p1.png').convert('RGB')
B = Image.open(ROOT + 'out/plate_B_p1.png').convert('RGB')
F = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/Anton-Regular.ttf', 34)
cx, cy, r = 537, 541, 255
bw = (cx - r, cy - r, cx + r, cy + r)
wa = A.crop(bw).resize((r * 4, r * 4), Image.LANCZOS)
wb = B.crop(bw).resize((r * 4, r * 4), Image.LANCZOS)
sheet = Image.new('RGB', (r * 8 + 20, r * 4), (14, 10, 26))
sheet.paste(wa, (0, 0)); sheet.paste(wb, (r * 4 + 20, 0))
d = ImageDraw.Draw(sheet)
for t, x in (('A  NIGHT WALL', 14), ('B  HOT PAINT', r * 4 + 34)):
    d.text((x + 2, 16), t, font=F, fill=(0, 0, 0)); d.text((x, 14), t, font=F, fill=(46, 235, 255))
sheet.save(DEL + 'wheel_crop.jpg', quality=92)
hb = (840, 760, 1640, 1080)
ha, hbb = A.crop(hb), B.crop(hb)
h = Image.new('RGB', (800, 320 * 2 + 10), (14, 10, 26))
h.paste(ha, (0, 0)); h.paste(hbb, (0, 330))
d = ImageDraw.Draw(h)
F2 = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/Anton-Regular.ttf', 22)
d.text((12, 6), 'A', font=F2, fill=(46, 235, 255)); d.text((12, 336), 'B', font=F2, fill=(46, 235, 255))
h.save(DEL + 'hand_crop.jpg', quality=92)
print('ok')
