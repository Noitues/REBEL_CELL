import scenes as SC
from m2 import *
D = SC.dmn()
pv = SC.nearest_s(D.R, site('t2_virus')[0])
fa = [ff for ff, ss in D.table.items() if ss >= pv]
print('pass', fa[0], 'arr', D.f_arr)
