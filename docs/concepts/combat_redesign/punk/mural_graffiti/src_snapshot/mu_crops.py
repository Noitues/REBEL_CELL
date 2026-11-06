"""wheel_crop.jpg (A and B wheels at 2x side by side) and hand_crop.jpg (A and B hands at 1x); and the plate copies"""
import sys, os, shutil
sys.dont_write_bytecode = True
sys.path.insert(0, '.')
from PIL import Image, ImageDraw, ImageFont
from cv_lib import C
OUT = 'D:/rc_scratch/combat_redesign/punk/mural_graffiti/out/'
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/mural_graffiti/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
os.makedirs(DEL, exist_ok=True)
A = Image.open(OUT + 'plate_A_p1.png').convert('RGB')
B = Image.open(OUT + 'plate_B_p1.png').convert('RGB')
cx, cy = int(C[0]), int(C[1])
R = 236
wa = A.crop((cx - R, cy - R, cx + R, cy + R)).resize((R * 4, R * 4), Image.LANCZOS)
wb = B.crop((cx - R, cy - R, cx + R, cy + R)).resize((R * 4, R * 4), Image.LANCZOS)
sheet = Image.new('RGB', (R * 8 + 30, R * 4 + 60), (18, 14, 28))
sheet.paste(wa, (0, 60))
sheet.paste(wb, (R * 4 + 30, 60))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype(FD + 'Anton-Regular.ttf', 38)
d.text((14, 8), 'A  BRICK + AIRBRUSH   (2x)', font=f, fill=(255, 255, 255))
d.text((R * 4 + 44, 8), 'B  CONCRETE + CEL   (2x)', font=f, fill=(255, 255, 255))
sheet.save(DEL + 'wheel_crop.jpg', quality=92)
box = (840, 740, 1660, 1080)
ha, hb = A.crop(box), B.crop(box)
hs = Image.new('RGB', (820, 340 * 2 + 70), (18, 14, 28))
hs.paste(ha, (0, 34))
hs.paste(hb, (0, 340 + 70))
d = ImageDraw.Draw(hs)
f = ImageFont.truetype(FD + 'Anton-Regular.ttf', 26)
d.text((8, 2), 'A  BRICK + AIRBRUSH  (1x)', font=f, fill=(255, 255, 255))
d.text((8, 340 + 38), 'B  CONCRETE + CEL  (1x)', font=f, fill=(255, 255, 255))
hs.save(DEL + 'hand_crop.jpg', quality=92)
A.save(DEL + 'plate_A.png')
B.save(DEL + 'plate_B.png')
print('crops ok')
