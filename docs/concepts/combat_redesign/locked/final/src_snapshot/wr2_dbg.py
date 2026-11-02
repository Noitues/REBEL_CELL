import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_build
import wr_state as ST
import wr_cells as WC
from wr_geo import ppx, C
from cv_lib import L2
J = wr_build.J
fr = J['f1']
ST.OPT.update({'ring_separators': 'R', 'unit_cell_screen': 'R', 'empty_cell': 'R'})
L = L2()
WC.paint_cells(L, fr, 'p1', WC.painter_mode())
im = L.done()
for ang, r in ((-20, 193), (300, 193), (320, 193)):
    p = ppx(C, r, ang)
    print(ang, [round(v) for v in p], im.getpixel((int(p[0]), int(p[1]))))
im.save('D:/rc_scratch/e10_design/wave_rings/out2/dbg_cells.png')
