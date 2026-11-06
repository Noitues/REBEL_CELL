import shutil, os
from PIL import Image
O = 'D:/rc_scratch/combat_redesign/locked/wheel/out/'
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/xerox_flyer/'
os.makedirs(D, exist_ok=True)
A = Image.open(O + 'plate_A.png').convert('RGB'); B = Image.open(O + 'plate_B.png').convert('RGB')
A.save(D + 'plate_A.png'); B.save(D + 'plate_B.png')
box = (330, 330, 750, 750)
a = A.crop(box).resize((840, 840), Image.LANCZOS); b = B.crop(box).resize((840, 840), Image.LANCZOS)
w = Image.new('RGB', (1700, 840), (21, 18, 28)); w.paste(a, (0, 0)); w.paste(b, (860, 0))
w.save(D + 'wheel_crop.jpg', quality=93)
hb = (840, 760, 1660, 1080)
a = A.crop(hb); b = B.crop(hb)
h = Image.new('RGB', (1660, 330), (21, 18, 28)); h.paste(a, (0, 5)); h.paste(b, (840, 5))
h.save(D + 'hand_crop.jpg', quality=93)
Image.open(O + 'style_board.png').convert('RGB').save(D + 'style_board.jpg', quality=92)
print('packed')
