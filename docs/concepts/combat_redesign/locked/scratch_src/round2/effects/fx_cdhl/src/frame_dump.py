"""frame_dump.py <id> <skin> <t> [<t> ...] : saves frame(fx, skin, t) to work/fd_<id>_<skin>_<t>.png (box crop, 1x), for diffing late frames"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_cdhl as F
from fxk_lib import frame, W
fid, skin = sys.argv[1], sys.argv[2]
for t in sys.argv[3:]:
    p = W + 'fd_%s_%s_%s.png' % (fid, skin, t)
    frame(F.BYID[fid], skin, float(t)).save(p)
    print(p)
