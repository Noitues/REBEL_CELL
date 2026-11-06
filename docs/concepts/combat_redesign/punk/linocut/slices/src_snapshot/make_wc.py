import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageOps
from cv_lib import C
from f1_lib import font, ANTON_F
O = 'D:/rc_scratch/combat_redesign/punk_slices/linocut/out/'
OLD = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/linocut/plate_A.png'
r = 232
box = (int(C[0] - r), int(C[1] - r), int(C[0] + r), int(C[1] + r))
def cr(p):
    return Image.open(p).convert('RGB').crop(box).resize((r * 4, r * 4), Image.LANCZOS)
ims = [('OLD: ONE COLOUR', cr(OLD)), ('A: PER-SLICE INKS', cr(O + 'plate_A_p1.png')), ('B: REVERSE PULL', cr(O + 'plate_B_p1.png'))]
w = r * 4
s = Image.new('RGB', (w * 3 + 16, (w + 44) * 2 + 8), (10, 10, 14))
d = ImageDraw.Draw(s)
for i, (n, im) in enumerate(ims):
    x = i * (w + 8)
    d.text((x + 12, 6), n, font=font(ANTON_F, 30), fill=(240, 233, 214))
    s.paste(im, (x, 44))
    y = w + 44 + 8
    d.text((x + 12, y + 6), n + ' (GREY)', font=font(ANTON_F, 30), fill=(240, 233, 214))
    s.paste(ImageOps.grayscale(im).convert('RGB'), (x, y + 44))
s.save(O + 'wheel_crop.jpg', quality=90); print(s.size)
