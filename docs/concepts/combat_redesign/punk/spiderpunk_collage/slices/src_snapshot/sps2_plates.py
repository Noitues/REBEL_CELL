import sys, os, time
sys.dont_write_bytecode = True
import sp_render as SR
ROOT = 'D:/rc_scratch/combat_redesign/punk_slices/spiderpunk_collage/'
SR.ROOT = ROOT
import sps2_slices
os.makedirs(ROOT + 'sl_out/', exist_ok=True)
for V in sys.argv[1:]:
    t = time.time()
    im = SR.render(V, 'p1')
    im.save(ROOT + 'sl_out/s2_plate_%s.png' % V)
    print('ok', V, round(time.time() - t), flush=True)
