"""gif_lstar.py: CIE L* of the frame mean (relative luminance) of every frame of the published GIFs, as decoded (after the palette)."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/rebuild/transitions/src')
import numpy as np
from PIL import Image, ImageSequence
from lstar import mean_L
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/transitions/'
for g in ('t5_A.gif', 't6_A.gif'):
    im = Image.open(D + g)
    v = [round(mean_L(np.asarray(f.convert('RGB')).astype(np.float64)), 1) for f in ImageSequence.Iterator(im)]
    print(g, im.size, len(v), 'frames, L*:', v)
