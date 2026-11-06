"""squint (320 px) + deutan sim per E8 plate, a contact sheet, and the converged-vs-E8 compare sheet."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E8/src')
from PIL import Image, ImageDraw, ImageFont
import numpy as np
P = 'D:/rc_tmp/combat_critic/plates/waves_e8/'
CV = 'D:/rc_tmp/combat_critic/plates/waves_converged/'
W = 'D:/rc_scratch/combat_polish/E7_waves/E8/'
NAMES = ['p1_decide', 'p1b_decide', 'p2_preview', 'p2b_hover', 'p3_resolve', 'p1_nowords']
FD = 'D:/rc_art/art-pass/assets/fonts/'
mo = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 18)
an = ImageFont.truetype(FD + 'Anton-Regular.ttf', 30)


def deutan(im):
    a = np.asarray(im.convert('RGB'), np.float32) / 255
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]], np.float32)
    o = np.clip(lin @ M.T, 0, 1)
    o = np.where(o <= 0.0031308, o * 12.92, 1.055 * o ** (1 / 2.4) - 0.055)
    return Image.fromarray((np.clip(o, 0, 1) * 255).astype(np.uint8))


sheet = Image.new('RGB', (1920, 60 + 6 * 560), (10, 12, 20))
d = ImageDraw.Draw(sheet)
d.text((20, 10), 'E8 plates: 320 px squint (left, shown at 3x nearest) and deutan sim (right)', font=an, fill=(255, 255, 255))
for i, n in enumerate(NAMES):
    im = Image.open(P + n + '.png').convert('RGB')
    sq = im.resize((320, 180), Image.LANCZOS)
    sq.save(W + 'squint_%s.png' % n)
    dn = deutan(im)
    dn.save(W + 'deutan_%s.png' % n)
    y = 60 + i * 560
    sheet.paste(sq.resize((960, 540), Image.NEAREST), (0, y))
    sheet.paste(dn.resize((960, 540), Image.LANCZOS), (960, y))
    d.text((12, y + 8), n + ' squint', font=mo, fill=(255, 226, 0))
    d.text((972, y + 8), n + ' deutan', font=mo, fill=(255, 226, 0))
sheet.save(W + 'checks_sheet.jpg', quality=88)
# compare sheet
rows = [('p1_decide', 'p1_decide'), ('p2_preview', 'p2_preview'), ('p3_resolve', 'p3_resolve')]
cs = Image.new('RGB', (1920, 40 + 3 * 540), (10, 12, 20))
d = ImageDraw.Draw(cs)
d.text((20, 4), 'CONVERGED (E5 numbers)', font=an, fill=(255, 226, 0))
d.text((980, 4), 'E8 (small counts, display A + H slices)', font=an, fill=(255, 226, 0))
for i, (a, b) in enumerate(rows):
    y = 40 + i * 540
    cs.paste(Image.open(CV + a + '.png').convert('RGB').resize((960, 540), Image.LANCZOS), (0, y))
    cs.paste(Image.open(P + b + '.png').convert('RGB').resize((960, 540), Image.LANCZOS), (960, y))
cs.save(W + 'compare_converged_vs_e8.jpg', quality=90)
print('ok')
