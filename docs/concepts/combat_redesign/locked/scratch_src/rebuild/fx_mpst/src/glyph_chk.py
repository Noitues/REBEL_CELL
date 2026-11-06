"""glyph_chk.py <skin> <kind> ...: max diff of the HUD chain TWIST glyph box (1095-1155 x 295-345) of a base against the published p3"""
import sys
import numpy as np
from PIL import Image
ME = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
skin = sys.argv[1]
b = np.asarray(Image.open(FINAL + 'p3_resolve' + ('' if skin == 'neutral' else '_' + skin) + '.png').convert('RGB'), np.int16)[295:345, 1095:1155]
for kind in sys.argv[2:]:
    a = np.asarray(Image.open(ME + 'work/bases/%s_%s_full.png' % (skin, kind)).convert('RGB'), np.int16)[295:345, 1095:1155]
    print(skin, kind, 'glyph box max diff', int(np.abs(a - b).max()))
