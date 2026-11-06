import sys, time, traceback
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_build as W
from wr2_picks import R2
t = time.time()
for b in sys.argv[1:]:
    try:
        W.render(b, R2, hud=False).save('D:/rc_scratch/e10_design/wave_rings/out2/base_r2_%s.png' % b)
        print(b, time.time() - t)
    except Exception:
        traceback.print_exc()
