import sys, time
import boardscenes as BS
from m2 import *
R = BS.board_renderers()
name = sys.argv[1]
for f in [int(x) for x in sys.argv[2:]]:
    t0 = time.time()
    a = R[name](f)
    Image.fromarray(a).save('D:/rc_scratch/tide_concepts/p2m_work/bs_%s_%03d.png' % (name, f))
    print(name, f, round(time.time() - t0, 1), flush=True)
