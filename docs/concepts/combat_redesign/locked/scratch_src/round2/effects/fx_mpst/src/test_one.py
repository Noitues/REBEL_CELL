"""test_one.py <id> <skin> <t> [reduce 0|1] [marks 0|1]: one frame of one effect -> work/look/t_<id>_<skin>_<t>.png (1x crop)"""
import sys
sys.dont_write_bytecode = True
import mp_eff as E
from mp_lib import *
fid, skin, t = sys.argv[1], sys.argv[2], float(sys.argv[3])
red = len(sys.argv) > 4 and sys.argv[4] == '1'
mk = not (len(sys.argv) > 5 and sys.argv[5] == '0')
im = to_img(E.FX[fid]['render'](t, skin, red, mk))
fp = ME + 'work/look/t_%s_%s_%d%s.png' % (fid, skin, int(t), '_r' if red else '')
im.save(fp)
print('ok', fp, im.size)
