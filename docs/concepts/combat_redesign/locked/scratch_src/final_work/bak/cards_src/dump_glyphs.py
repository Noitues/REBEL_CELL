"""one-off: render the E10 glyph library to white-silhouette PNGs so card_render has no dependency on the old generator"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/punk/xerox_flyer/src'
sys.path.insert(0, SRC); sys.path.insert(0, 'D:/rc_art/art-pass'); sys.path.insert(0, 'D:/rc_art/art-pass/tools')
os.chdir(SRC)
import e10lib
import numpy as np
from PIL import Image
from cv_lib import glyph_rgba
OUT = 'D:/rc_scratch/combat_redesign/locked/cards/src/glyphs/'
NAMES = ['C_BRACE', 'PI_SPIN_CW', 'C_TRIG', 'C_TWIST', 'C_SHOVE', 'C_PULL', 'C_HOLD', 'C_STRIKE', 'BURN']
for n in NAMES:
    try:
        g = glyph_rgba(n, 512, 38, fill=(255, 255, 255))
        a = np.asarray(g, np.float32) / 255.0
        m = np.clip((a[..., 3] - 0.5) * 3, 0, 1) * (a[..., :3].min(-1) > 0.8)
        Image.fromarray((m * 255).astype(np.uint8), 'L').save(OUT + n + '.png')
        print(n, 'ok', m.mean())
    except Exception as e:
        print(n, 'FAIL', e)
