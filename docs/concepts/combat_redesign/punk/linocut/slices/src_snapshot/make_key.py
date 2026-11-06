import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageOps
sys.path.insert(0, '.')
from f1_lib import font, ANTON_F, MONO_F
import lc_tower as LT
O = 'D:/rc_scratch/combat_redesign/punk_slices/linocut/out/'
SC = 3.2
BG = (30, 26, 52)
TXT = (240, 233, 214)
TYPES = ['BURST', 'TURRET', 'SHIELD', 'REPAIR']
TEXN = {'gouge': 'GOUGE  (slanted chisel lenses)', 'dots': 'PUNCH  (halftone dots)', 'rings': 'RIPPLE  (arc cuts along the rim)', 'plus': 'PLUS  (carved first-aid crosses)'}
NAMES = {'A': 'PALETTE A: black key plate, pink halo, bone cuts', 'B': 'PALETTE B: the reverse pull, pink plate, bone halo'}
def hexc(c): return '#%02X%02X%02X' % tuple(c)
def wedge(path, s):
    im = Image.open(path).convert('RGBA')
    bg = Image.new('RGBA', im.size, BG + (255,)); bg.alpha_composite(im)
    c = im.width / 2
    r = bg.rotate(60 * s, resample=Image.BICUBIC, center=(c, c))
    box = (int(c - 66), int(c - 183), int(c + 66), int(c - 62))
    cr = r.crop(box).convert('RGB')
    return cr.resize((int(cr.width * SC), int(cr.height * SC)), Image.LANCZOS)
def sheet():
    cw, ch = int(132 * SC), int(121 * SC)
    LAB = 210
    rows = [('COLOUR', 'clean'), ('GREY', 'clean'), ('RED HATCH', 'pend'), ('HATCH IN GREY', 'pend')]
    blockh = 118 + len(rows) * (ch + 10)
    W = LAB + 4 * (cw + 12) + 12
    sh = Image.new('RGB', (W, 82 + 2 * blockh), BG)
    d = ImageDraw.Draw(sh)
    d.text((16, 14), 'LINOCUT  /  PER-SLICE COLOUR AND TEXTURE', font=font(ANTON_F, 40), fill=TXT)
    d.text((16, 58), 'one colour and one carved texture per slice type; the grey rows prove the texture still carries the type', font=font(MONO_F, 16), fill=(180, 174, 200))
    for bi, v in enumerate('AB'):
        LT.VARIANT[0] = v
        y0 = 82 + bi * blockh
        d.text((16, y0 + 6), NAMES[v], font=font(ANTON_F, 28), fill=(255, 46, 160))
        for ti, t in enumerate(TYPES):
            T = LT.PALS[v]['T'][t]
            x = LAB + 12 + ti * (cw + 12)
            d.text((x, y0 + 40), t, font=font(ANTON_F, 36), fill=TXT)
            d.text((x + 150, y0 + 48), 'fill %s  ink %s' % (hexc(T['fill']), hexc(T['ink'])), font=font(MONO_F, 14), fill=(190, 184, 210))
            d.text((x, y0 + 86), TEXN[T['tex']], font=font(MONO_F, 14), fill=(190, 184, 210))
            for ri, (lab, kind) in enumerate(rows):
                im = wedge(O + 'key_%s_%s.png' % (v, kind), ti)
                if 'GREY' in lab:
                    im = ImageOps.grayscale(im).convert('RGB')
                y = y0 + 118 + ri * (ch + 10)
                sh.paste(im, (x, y))
                if ti == 0:
                    d.text((16, y + ch // 2 - 10), lab, font=font(ANTON_F, 24), fill=TXT)
    return sh
if __name__ == '__main__':
    s = sheet(); s.save(O + 'slice_key.jpg', quality=92); print(s.size)
