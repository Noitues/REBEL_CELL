import sys
sys.dont_write_bytecode = True
from PIL import ImageFont
for fn in ('Anton-Regular.ttf', 'ShareTechMono-Regular.ttf'):
    for px in (30, 36, 40, 44):
        f = ImageFont.truetype('D:/rc_scratch/combat_redesign/locked/corp/src/fonts/' + fn, px)
        out = []
        for s in ('-', '+', '=', '\u2212', '\u2013'):
            bb = f.getbbox(s, anchor='mm')
            out.append('%r w%d h%d cy%.1f' % (s, bb[2] - bb[0], bb[3] - bb[1], (bb[1] + bb[3]) / 2))
        print(fn[:6], px, ' | '.join(out))
