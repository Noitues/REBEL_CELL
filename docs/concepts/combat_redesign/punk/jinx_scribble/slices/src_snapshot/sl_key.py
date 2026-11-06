"""slice_key.jpg from the hi-res tower renders. python sl_key.py OUT.jpg"""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont
import js_slices as JS
R = 'D:/rc_scratch/combat_redesign/punk_slices/jinx_scribble/out/'
OUT = sys.argv[1]
FD = 'D:/rc_art/art-pass/assets/fonts/'
ANT = lambda s: ImageFont.truetype(FD + 'Anton-Regular.ttf', s)
PLX = lambda s: ImageFont.truetype(FD + 'IBMPlexSansCondensed-Medium.ttf', s)
MONO = lambda s: ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', s)
SECT = {'BURST': 0, 'SHIELD': 1, 'TURRET': 2, 'REPAIR': 5}
GAME = {'BURST': 'ZERO-DAY', 'SHIELD': 'SANDBOX', 'TURRET': 'EXPLOIT', 'REPAIR': 'PATCH'}
Z, CT = 3, 235
hx = lambda c: '#%02X%02X%02X' % tuple(c)


import math
from PIL import ImageChops


def wedge(im, s):
    am = math.radians(60 * s)
    cx, cy = CT + 122 * math.sin(am), CT - 122 * math.cos(am)
    hw = 70
    c = im.crop((int((cx - hw) * Z), int((cy - hw) * Z), int((cx + hw) * Z), int((cy + hw) * Z)))
    m = Image.new('L', im.size, 0)
    dm = ImageDraw.Draw(m)
    pts = []
    for a in [60 * s - 27 + i * 0.5 for i in range(109)]:
        pts.append(((CT + 181 * math.sin(math.radians(a))) * Z, (CT - 181 * math.cos(math.radians(a))) * Z))
    for a in [60 * s + 27 - i * 0.5 for i in range(109)]:
        pts.append(((CT + 68 * math.sin(math.radians(a))) * Z, (CT - 68 * math.cos(math.radians(a))) * Z))
    dm.polygon(pts, fill=255)
    m = m.crop((int((cx - hw) * Z), int((cy - hw) * Z), int((cx + hw) * Z), int((cy + hw) * Z)))
    out = Image.new('RGBA', c.size, (28, 30, 44, 255))
    out.alpha_composite(c)
    bgc = Image.new('RGBA', c.size, (28, 30, 44, 255))
    return Image.composite(out, bgc, m)


def bg(im):
    b = Image.new('RGBA', im.size, (28, 30, 44, 255)); b.alpha_composite(im); return b.convert('RGB')


grey = lambda im: im.convert('L').convert('RGB')
SC = 0.75
cw, ch = 330, 330
M, TXTW = 28, 640
W = M + 3 * (cw + 14) + TXTW + M
HEAD = 130
BLK = 70 + 4 * (ch + 16) + 20
H = HEAD + 2 * BLK + 30
sheet = Image.new('RGB', (W, H), (20, 18, 30))
d = ImageDraw.Draw(sheet)
d.text((M, 20), 'JINX SCRIBBLE  per-slice colour and texture key', font=ANT(52), fill=(246, 242, 255))
d.text((M, 82), 'Four slice types, each with its own colour AND its own scribble texture. Columns: colour | same in grey (texture carries the type) | red cross-hatch (pending loss at END TURN) on that slice.', font=PLX(21), fill=(190, 192, 215))
d.text((M, 108), 'Same type = same look on every slice of that type (SHIELD sits on sectors 1 and 3, BURST on 0 and 4).', font=PLX(21), fill=(190, 192, 215))
y0 = HEAD
for v, vn in (('A', 'VARIANT A  NIGHT WALL: dark tinted paint, neon texture and key line'), ('B', 'VARIANT B  HOT PAINT: full colour paint, ink texture and key line')):
    JS.JT.VAR[0] = v
    ci = Image.open(R + 'tw_%s_f1_calm_hi.png' % v).convert('RGBA')
    cb = Image.open(R + 'tw_%s_f1_all_hi.png' % v).convert('RGBA')
    d.text((M, y0 + 8), vn, font=ANT(32), fill=(255, 46, 154) if v == 'A' else (255, 138, 30))
    yy = y0 + 62
    for t in ('BURST', 'SHIELD', 'TURRET', 'REPAIR'):
        s = SECT[t]
        w1 = wedge(ci, s).convert('RGB').resize((cw, ch), Image.LANCZOS)
        w3 = wedge(cb, s).convert('RGB').resize((cw, ch), Image.LANCZOS)
        sheet.paste(w1, (M, yy)); sheet.paste(grey(w1), (M + cw + 14, yy)); sheet.paste(w3, (M + 2 * (cw + 14), yy))
        tx = M + 3 * (cw + 14) + 20
        p = (JS.PALA if v == 'A' else JS.PALB)[t]
        d.text((tx, yy), t, font=ANT(48), fill=(246, 242, 255))
        d.text((tx + 4, yy + 58), 'game name: %s' % GAME[t], font=PLX(22), fill=(190, 192, 215))
        d.text((tx + 4, yy + 88), 'colour: %s' % p['name'], font=PLX(22), fill=(246, 242, 255))
        if v == 'A':
            sw = [(p['viv'], 'neon key + texture ' + hx(p['viv'])), (p['c0'], 'body dark ' + hx(p['c0'])), (p['c1'], 'body rim ' + hx(p['c1']))]
        else:
            sw = [(p['fill'], 'paint ' + hx(p['fill'])), (p['lt'], 'highlight ' + hx(p['lt'])), (p['dk'], 'shade ' + hx(p['dk']))]
        for i, (c, lab) in enumerate(sw):
            d.rectangle([tx + 4, yy + 124 + i * 30, tx + 34, yy + 148 + i * 30], fill=tuple(c), outline=(240, 240, 255))
            d.text((tx + 46, yy + 124 + i * 30), lab, font=MONO(18), fill=(200, 200, 225))
        d.text((tx + 4, yy + 220), 'texture: %s' % JS.TEXNAME[t], font=PLX(24), fill=(246, 242, 255))
        yy += ch + 16
    y0 += BLK
sheet.save(OUT, quality=92)
print('ok', sheet.size)
