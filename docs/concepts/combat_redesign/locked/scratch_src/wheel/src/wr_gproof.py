import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import e8lib   # registers U_RING etc.
import wr_glyphs as G
from cv_lib import *
import slicelib as SL
kinds = ['Packet', 'Worm', 'Payload', 'Jammer', 'Ring']
sheet = Image.new('RGBA', (5 * 300 + 20, 4 * 330 + 20), (60, 40, 70, 255))
d = ImageDraw.Draw(sheet)
for r, o in enumerate(['E', 'A', 'B', 'C']):
    for c, k in enumerate(kinds):
        nm = G.glyph_name('', k, o)
        try:
            g = glyph_rgba(nm, 200, 15)
            sheet.alpha_composite(g, (10 + c * 300, 10 + r * 330))
            g2 = glyph_rgba(nm, 37, 3)
            sheet.alpha_composite(g2, (230 + c * 300 - 10, 10 + r * 330 + 100))
            print(nm, round(G.mask_area(nm), 3))
        except Exception as e:
            print('ERR', nm, e)
sheet.convert('RGB').save('D:/rc_scratch/e10_design/wave_rings/out/glyph_proof.png')
