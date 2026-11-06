"""render one mural plate: python mu_run.py A|B [beat]  ->  out/plate_<V>_<beat>.png"""
import sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, '.')
import f1_render as R
import mu_art as MU
import mu_cards as MC

v = sys.argv[1] if len(sys.argv) > 1 else 'A'
beat = sys.argv[2] if len(sys.argv) > 2 else 'p1'
MU.VAR[0] = v
MC.VAR[0] = v
t = time.time()
im = R.render(beat=beat)
im.save(R.OUT + 'plate_%s_%s.png' % (v, beat))
print('ok', v, beat, round(time.time() - t), flush=True)
