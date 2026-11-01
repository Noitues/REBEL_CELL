import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E10/src')
from cv_lib import *
import cv_board
ims = []
for n in ['SHIELD', 'SHIELD@A', 'SHIELD@B', 'SHIELD@C', 'SANDBOX', 'X_SHIELD', 'U_PAYLOAD']:
    try:
        g = glyph_rgba(n, 160, 10)
        ims.append(g)
        print(n, 'ok')
    except Exception as e:
        print(n, 'ERR', e)
sheet = Image.new('RGBA', (170 * len(ims), 170), (40, 40, 60, 255))
for i, g in enumerate(ims): sheet.alpha_composite(g, (i * 170, 5))
sheet.convert('RGB').save('D:/rc_scratch/combat_polish/E7_waves/E10/gtest.png')
