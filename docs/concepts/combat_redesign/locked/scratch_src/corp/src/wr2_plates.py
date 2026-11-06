"""integrated cluster plates (p1, p2, p2b, p3, nowords) at 1920x1080 with the E10 HUD, R1 favourites vs R2 picks"""
import sys, time, traceback
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_build as W
from wr2_picks import R2, R1
D = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r2/wave_rings/'
beats = sys.argv[2:] or ['p1', 'p2', 'p2b', 'p3', 'nowords']
which = sys.argv[1]
t = time.time()
for b in beats:
    try:
        o = R2 if which == 'r2' else R1
        im = W.render(b, o, hud=True)
        im.save(D + 'plate_%s_%s.png' % (which, b))
        print(which, b, round(time.time() - t))
    except Exception:
        traceback.print_exc()
