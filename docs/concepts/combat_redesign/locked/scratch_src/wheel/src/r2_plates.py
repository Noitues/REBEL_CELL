import sys
sys.dont_write_bytecode = True
from r2_render import *
OUTD = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r2/outer_rings/'
names = {'p1': 'plate_p1_decide', 'p2': 'plate_p2_preview', 'p2b': 'plate_p2b_hover', 'p3': 'plate_p3_resolve', 'nowords': 'plate_p1_nowords'}
beats = sys.argv[1:] or list(names)
for b in beats:
    im = render_r2(b, {})
    im.save(OUTD + names[b] + '.png')
    print(b, flush=True)
