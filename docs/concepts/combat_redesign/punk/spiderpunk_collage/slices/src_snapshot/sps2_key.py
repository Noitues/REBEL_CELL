"""build slice_key.jpg from the hi-res tower renders in work/_k_<V>_<i|h>.png.  usage: sps2_key.py OUT.jpg"""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont
sys.argv_save = sys.argv
import importlib.util
FD = 'D:/rc_art/art-pass/assets/fonts/'
R = 'D:/rc_scratch/combat_redesign/punk_slices/spiderpunk_collage/'
OUT = sys.argv[1]
ANT = lambda s: ImageFont.truetype(FD + 'Anton-Regular.ttf', s)
PLX = lambda s: ImageFont.truetype(FD + 'IBMPlexSansCondensed-Medium.ttf', s)
MONO = lambda s: ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', s)
sys.path.insert(0, R + 'src')
import json
SPEC = {}
import sps2_slices as SS
SPEC, TEXNAME = SS.SPEC, SS.TEXNAME
SECT = {'BURST': 0, 'SHIELD': 1, 'TURRET': 2, 'REPAIR': 5}
VNAME = {'A': 'VARIANT A  POSTER  (purple page, white cut edges, bone lightning)', 'B': 'VARIANT B  GIG FLYER  (newsprint page, yellow cut edges, ink lightning)'}
Z = 3
CTX = 235
HARM = (255, 68, 51)


def wedge(im, s):
    r = im.rotate(60 * s, center=(CTX * Z, CTX * Z), resample=Image.BICUBIC)
    return r.crop((CTX * Z - 300, (CTX - 188) * Z, CTX * Z + 300, (CTX - 62) * Z))


def grey(im):
    return im.convert('L').convert('RGB')


def lum(c):
    f = lambda x: x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4
    r, g, b = [f(v / 255) for v in c]
    return .2126 * r + .7152 * g + .0722 * b


def cr(a, b):
    la, lb = lum(a), lum(b)
    if la < lb:
        la, lb = lb, la
    return (la + .05) / (lb + .05)


cw, ch = 600, 378
M = 28
TXTW = 640
W = M + 3 * (cw + 14) + TXTW + M
BG = (20, 18, 26)
rows = 4
HEAD = 130
BLK = 70 + rows * (ch + 16) + 20
H = HEAD + 2 * BLK + 30
sheet = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(sheet)
d.text((M, 20), 'SPIDER-PUNK COLLAGE  per-slice colour and texture key', font=ANT(54), fill=(242, 238, 228))
d.text((M, 86), 'Columns: colour | the same in grey (texture and value carry the type) | red cross-hatch on that slice (this END TURN\'s pending loss).  Slices of one type match.', font=PLX(21), fill=(190, 192, 205))
y0 = HEAD
for v in ('A', 'B'):
    ci = Image.open(R + 'work/_k_%s_i.png' % v).convert('RGB')
    cb = Image.open(R + 'work/_k_%s_h.png' % v).convert('RGB')
    d.text((M, y0 + 8), VNAME[v], font=ANT(32), fill=(255, 61, 168) if v == 'A' else (255, 140, 40))
    yy = y0 + 62
    for t in ('BURST', 'SHIELD', 'TURRET', 'REPAIR'):
        s = SECT[t]
        w1 = wedge(ci, s)
        w3 = wedge(cb, s)
        sheet.paste(w1, (M, yy))
        sheet.paste(grey(w1), (M + cw + 14, yy))
        sheet.paste(w3, (M + 2 * (cw + 14), yy))
        sp = SPEC[v][t]
        tx = M + 3 * (cw + 14) + 18
        d.text((tx, yy + 2), t, font=ANT(46), fill=(242, 238, 228))
        d.text((tx, yy + 60), sp['name'], font=PLX(26), fill=sp['c0'])
        for i, (lab, col) in enumerate((('fill', sp['c0']), ('shade', sp['c1']), ('tex ink', sp['tc']), ('cut edge', sp['edge']))):
            x = tx + i * 150
            d.rectangle((x, yy + 98, x + 60, yy + 138), fill=col, outline=(242, 238, 228), width=2)
            d.text((x, yy + 142), '#%02X%02X%02X' % tuple(col), font=MONO(19), fill=(242, 238, 228))
            d.text((x, yy + 164), lab, font=PLX(17), fill=(150, 154, 170))
        d.text((tx, yy + 196), 'texture: %s' % TEXNAME[sp['tex']], font=PLX(23), fill=(242, 238, 228))
        gv = int(0.299 * sp['c0'][0] + 0.587 * sp['c0'][1] + 0.114 * sp['c0'][2])
        d.text((tx, yy + 228), 'grey value of the fill: %d / 255' % gv, font=PLX(20), fill=(150, 154, 170))
        d.text((tx, yy + 256), 'hatch keyline: #%02X%02X%02X   red vs fill contrast %.1f : 1' % (tuple(sp['key']) + (cr(HARM, sp['c0']),)), font=PLX(20), fill=(150, 154, 170))
        yy += ch + 16
    y0 += BLK
sheet.save(OUT, quality=92)
print(sheet.size)
