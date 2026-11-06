import sys
from stage import *
import beats_b as B
D = B.dmn()
for f in (int(sys.argv[1]),):
    a = B.b_daemon(f)
    crop_scale(a, (330, 300, 1290, 840), (960, 540)).save(WORKD + 'one_daemon_%d.png' % f)
print(D.f_arr)
