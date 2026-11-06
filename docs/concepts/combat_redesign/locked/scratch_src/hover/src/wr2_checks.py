import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
from PIL import Image, ImageDraw
import wr2_lib as W2
from wr2_sheets import F_T, F_C, F_S, BG
D = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r2/wave_rings/'
ld = lambda w, b: Image.open(D + 'plate_%s_%s.png' % (w, b)).convert('RGB')
W = 1980
sh = Image.new('RGB', (W, 2400), BG)
d = ImageDraw.Draw(sh)
d.text((12, 8), 'CHECKS: 320 px squint, deutan, tritan, nowords (cluster plates, E10 HUD)', font=F_T, fill=(255, 255, 255))
y = 54
def row(title, a, b, w):
    global y
    d.text((12, y), title, font=F_C, fill=(230, 235, 245)); y += 24
    h = int(w * 1080 / 1920)
    for i, im in enumerate((a, b)):
        sh.paste(im.resize((w, h), Image.LANCZOS if w > 400 else Image.BOX), (10 + i * (w + 10), y))
        d.text((16 + i * (w + 10), y + 4), ('R1 favourites', 'R2 picks')[i], font=F_S, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    y += h + 12
def squint(im):
    s = im.resize((320, 180), Image.BOX)
    return s.resize((960, 540), Image.NEAREST)
r1, r2 = ld('r1', 'p1'), ld('r2', 'p1')
row('320 px squint (the plate downscaled to 320 x 180, shown 3x): read order L1 red chevrons / hero, L2 board, L3 HUD', squint(r1), squint(r2), 960)
row('deutan (Machado, full severity), plate at 960', W2.sim_cb(r1, 'deutan'), W2.sim_cb(r2, 'deutan'), 960)
row('tritan', W2.sim_cb(r1, 'tritan'), W2.sim_cb(r2, 'tritan'), 960)
row('nowords (p1_nowords): every element reads by shape', ld('r1', 'nowords'), ld('r2', 'nowords'), 960)
sh = sh.crop((0, 0, W, y))
sh.save(D + 'sheet_checks_squint_deutan_nowords.jpg', quality=88)
print(sh.size)
