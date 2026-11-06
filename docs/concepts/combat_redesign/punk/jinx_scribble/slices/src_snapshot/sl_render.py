"""sl_render: the per-slice-colour plate. python sl_render.py <A|B> [beat]"""
import sys, time
sys.dont_write_bytecode = True
import js_render as JR
import js_slices as JS
import f1_render as R
var = sys.argv[1]
beat = sys.argv[2] if len(sys.argv) > 2 else 'p1'
JR.setup(var)
JS.install()
t = time.time()
im = R.render(beat=beat, check=False)
im.save(JR.ROOT + 'out/plate_%s_%s.png' % (var, beat))
print(var, beat, round(time.time() - t), flush=True)
