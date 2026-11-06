import sys, time
import scenes2 as SC
from m2 import *
name = sys.argv[1]; reduce = sys.argv[2] == 'r'
fn = getattr(SC, 'b_' + name)
fs = [int(x) for x in sys.argv[3:]]
for f in fs:
    t0 = time.time()
    a = fn(f, reduce=reduce)
    Image.fromarray(a).save('D:/rc_scratch/tide_concepts/p2m_work/t_%s_%s_%03d.png' % (name, 'r' if reduce else 'n', f))
    print(f, round(time.time() - t0, 2), a.shape, flush=True)
