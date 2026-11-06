from m2 import *
import scenes as SC
D = SC.dmn()
print(D.table[60], D.table[72], D.s_stop)
R = route('K1')
print(R.pos(D.table[60]), R.pos(D.s_stop))
rb = R.ribbon_map()
print(len(rb['s']), rb['s'].min(), rb['s'].max())
sel=(rb['s']>1400)&(rb['s']<1500); print(sel.sum())
