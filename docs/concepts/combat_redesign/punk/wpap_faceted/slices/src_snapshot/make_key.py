import sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/punk_slices/wpap_faceted/src')
from PIL import Image, ImageDraw, ImageFont
import wp_lib as L
from f1_lib import ANTON_F, MONO_F
O = 'D:/rc_scratch/combat_redesign/punk_slices/wpap_faceted/out/'
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/wpap_faceted/slices/'
S = 3
C = 235.0 * S
TYPES = ['BURST', 'SHIELD', 'TURRET', 'REPAIR']
NAMES = {'BURST': 'BURST', 'SHIELD': 'SHIELD', 'TURRET': 'TURRET', 'REPAIR': 'REPAIR'}
BG = (22, 8, 38)
TW_, TH_ = 570, 360

def tile(im, s):
    am = 60 * s
    r = im.rotate(am, center=(C, C), resample=Image.BICUBIC)
    box = (int(C - 95 * S), int(C - 188 * S), int(C + 95 * S), int(C - 64 * S))
    t = r.crop(box)
    # wedge mask (upright, half angle 29 deg, r 66..183), keeps neighbours out
    m = Image.new('L', t.size, 0)
    d = ImageDraw.Draw(m)
    pts = []
    for k in range(9):
        a = math.radians(-29 + 58 * k / 8)
        pts.append((C + 183 * S * math.sin(a) - box[0], C - 183 * S * math.cos(a) - box[1]))
    for k in range(9):
        a = math.radians(29 - 58 * k / 8)
        pts.append((C + 66 * S * math.sin(a) - box[0], C - 66 * S * math.cos(a) - box[1]))
    d.polygon(pts, fill=255)
    bg = Image.new('RGB', t.size, BG)
    bg.paste(t, (0, 0), m)
    return bg.resize((TW_, TH_), Image.LANCZOS)

def hexs(c):
    return '#%02X%02X%02X' % tuple(c)

W = 40 + 4 * (TW_ + 30) + 10
rows = ['ok', 'ok_g', 'harm', 'harm_g', 'soak']
RH = TH_ + 22
BLK = 170 + len(rows) * RH + 30
img = Image.new('RGB', (W, BLK * 2 + 80), BG)
d = ImageDraw.Draw(img)
fT = ImageFont.truetype(ANTON_F, 54); fN = ImageFont.truetype(ANTON_F, 40); fM = ImageFont.truetype(MONO_F, 22); fS = ImageFont.truetype(MONO_F, 18)
rowlab = {'ok': 'COLOUR + TEXTURE', 'ok_g': 'SAME IN GREY', 'harm': 'RED CROSS-HATCH (END TURN LOSS)', 'harm_g': 'HATCH IN GREY', 'soak': 'BLUE SOAK HATCH (CHECK)'}
for vi, var in enumerate(['A', 'B']):
    y0 = 30 + vi * (BLK + 20)
    title = {'A': 'PALETTE A  RIOT SET   orange / cobalt / hot pink / acid green', 'B': 'PALETTE B  NIGHT SHIFT   acid yellow / cyan / violet / pink'}[var]
    d.text((40, y0), title, font=fT, fill=(255, 250, 240))
    imgs = {m: Image.open(O + 'tw_%s_%s_6k.png' % (var, m)).convert('RGB') for m in ('ok', 'harm', 'soak')}
    for ti, t in enumerate(TYPES):
        x = 40 + ti * (TW_ + 30)
        SP = L.SLICE[var][t]
        d.text((x, y0 + 78), NAMES[t], font=fN, fill=(255, 250, 240))
        d.text((x + 190, y0 + 92), 'texture: ' + L.PATNAME[SP['pat']], font=fM, fill=(220, 210, 235))
        # ramp swatches
        sx = x
        for c in SP['ramp'] + [SP['accent'], SP['glint']]:
            d.rectangle([sx, y0 + 134, sx + 36, y0 + 154], fill=tuple(c), outline=(10, 4, 20))
            sx += 38
        d.text((sx + 6, y0 + 134), hexs(SP['ramp'][2]), font=fS, fill=(230, 222, 240))
        for ri, rk in enumerate(rows):
            m = {'ok': 'ok', 'ok_g': 'ok', 'harm': 'harm', 'harm_g': 'harm', 'soak': 'soak'}[rk]
            tl = tile(imgs[m], ti)
            if rk.endswith('_g'):
                tl = tl.convert('L').convert('RGB')
            yy = y0 + 170 + ri * RH
            img.paste(tl, (x, yy))
            if ti == 0:
                d.text((x + 6, yy + 4), rowlab[rk], font=fS, fill=(255, 255, 255))
img.save(D + 'slice_key.jpg', quality=90)
print(img.size)
