import sys, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import asm_r2 as A
A.setup()
import wp_lib as L
import wp_tower as T
import wp_cards as K
import wp_ui as U
from st_gfx import font as sfont

R = 'D:/rc_scratch/combat_redesign/punk/wpap_faceted/'
J = json.load(open(R + 'state_e10.json'))
FD = 'D:/rc_art/art-pass/assets/fonts/'
INK = (22, 8, 38)
bg = Image.new('RGB', (1920, 1080), INK)
d = ImageDraw.Draw(bg)
ANT = lambda s: ImageFont.truetype(FD + 'Anton-Regular.ttf', s)
PLX = lambda s: ImageFont.truetype(FD + 'IBMPlexSansCondensed-Medium.ttf', s)
MON = lambda s: ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', s)

d.polygon([(0, 0), (1920, 0), (1920, 62), (1880, 84), (0, 84)], fill=(255, 61, 168))
d.text((40, 14), 'WPAP FACETED  //  THE CELL CUTS ITS OWN PLANES', font=ANT(52), fill=(255, 255, 255))
d.text((1250, 28), 'A  PINK RIOT (teal ink)     B  ACID SUNBURST (orange ink)', font=MON(20), fill=INK)

def paste_rgba(im, xy):
    bg.paste(im.convert('RGB'), xy, im.split()[3])

def crop_native(cv, box, size):
    S = cv.S
    im = cv.rgba()
    c = im.crop((box[0] * S, box[1] * S, box[2] * S, box[3] * S))
    base = Image.new('RGBA', c.size, (20, 18, 32, 255))
    base.alpha_composite(c)
    return base.convert('RGB').resize(size, Image.LANCZOS)

towers = {}
for v in 'AB':
    L.VAR[0] = v
    towers[v] = T.render_tower(J['f1'])[1]
slice_box = (150, 48, 320, 188)
for i, v in enumerate('AB'):
    im = crop_native(towers[v], slice_box, (510, 400))
    bg.paste(im, (40, 100 + i * 435))
    d.text((48, 106 + i * 435), 'SLICE ' + v, font=MON(20), fill=(255, 255, 255))
hub_box = (160, 160, 310, 300)
for i, v in enumerate('AB'):
    im = crop_native(towers[v], hub_box, (420, 400))
    bg.paste(im, (575, 100 + i * 435))
    d.text((583, 106 + i * 435), 'HUB ' + v, font=MON(20), fill=(255, 255, 255))
for i, v in enumerate('AB'):
    L.VAR[0] = v
    c = K.render_card('Spin3', 'A', seed=4, ss=4, scale=4)
    k = 560 / c.height
    c = c.resize((int(c.width * k), 560), Image.LANCZOS)
    paste_rgba(c, (1015 + i * 440, 92))
    d.text((1030 + i * 440, 96), 'CARD ' + v, font=MON(20), fill=(255, 255, 255))

# palettes
y = 990
for i, v in enumerate('AB'):
    P = L.PAL[v]
    x = 40 + i * 470
    d.text((x, y - 24), 'PALETTE ' + v, font=MON(16), fill=(200, 190, 220))
    cols = P['ramp'] + [P['accent'], P['glint']] + P['page'][:3]
    for k, c in enumerate(cols):
        d.rectangle([x + k * 36, y, x + k * 36 + 33, y + 40], fill=c, outline=(255, 255, 255))
    d.text((x, y + 46), '5 ramp, ink, glint, 3 plate', font=MON(13), fill=(170, 160, 190))
# samples: cut, hatch, ink+drop, stud
sx, sy = 1015, 700
d.text((sx, sy - 4), 'LINE / TEXTURE SAMPLES', font=MON(16), fill=(200, 190, 220))
sy += 24
d.polygon([(sx, sy + 90), (sx + 40, sy), (sx + 110, sy + 30), (sx + 100, sy + 90)], fill=(255, 61, 168))
d.polygon([(sx + 40, sy), (sx + 110, sy + 30), (sx + 60, sy + 60)], fill=(255, 170, 156))
d.polygon([(sx, sy + 90), (sx + 60, sy + 60), (sx + 100, sy + 90)], fill=(84, 16, 142))
d.polygon([(sx + 60, sy + 60), (sx + 110, sy + 30), (sx + 100, sy + 90)], fill=(22, 198, 202))
d.text((sx, sy + 96), 'flat cuts', font=PLX(16), fill=(255, 255, 255))
hx_ = sx + 140
d.rectangle([hx_, sy, hx_ + 110, sy + 90], fill=(22, 10, 36))
for k in range(-100, 200, 8):
    d.line([(hx_ + k, sy), (hx_ + k + 90, sy + 90)], fill=(255, 68, 51), width=2)
    d.line([(hx_ + k + 90, sy), (hx_ + k, sy + 90)], fill=(255, 68, 51), width=2)
d.rectangle([hx_ - 1, sy - 1, hx_ + 111, sy + 91], outline=(22, 8, 38), width=4)
d.rectangle([hx_ + 110, sy - 20, hx_ + 140, sy + 120], fill=INK)
d.text((hx_, sy + 96), 'hatch = lost', font=PLX(16), fill=(255, 255, 255))
ix = sx + 290
d.rectangle([ix + 8, sy + 10, ix + 98, sy + 80], fill=(255, 61, 168))
d.rectangle([ix, sy + 2, ix + 90, sy + 72], fill=(246, 240, 228), outline=(22, 8, 38), width=3)
d.text((ix, sy + 96), 'ink + hard drop', font=PLX(16), fill=(255, 255, 255))
st = sx + 450
x, yy, r = st + 40, sy + 40, 26
for pts, col in (([(x - r, yy - r), (x + r, yy - r), (x, yy)], (250, 252, 255)), ([(x - r, yy - r), (x, yy), (x - r, yy + r)], (190, 204, 226)), ([(x + r, yy - r), (x + r, yy + r), (x, yy)], (122, 138, 170)), ([(x - r, yy + r), (x + r, yy + r), (x, yy)], (62, 74, 104))):
    d.polygon(pts, fill=col)
d.rectangle([x - r, yy - r, x + r, yy + r], outline=(22, 8, 38), width=3)
d.text((st - 4, sy + 96), 'stud (punk)', font=PLX(16), fill=(255, 255, 255))

# manifesto
mx, my = 1015, 880
lines = ['THE CELL CUTS ITS WORLD IN HARD PLANES.', 'PINK + ONE LOUD COMPLEMENT: NOTHING THE CORP OWNS.', 'STUDS, SLANTS, SHARDS: THE WHEEL WEARS A JACKET.']
for k, t in enumerate(lines):
    d.text((mx, my + k * 40), t, font=ANT(30), fill=(255, 255, 255) if k != 1 else (255, 140, 200))
bg.save(R + 'out/style_board.jpg', quality=93)
print('ok')
