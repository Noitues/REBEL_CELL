import sys,json,copy
sys.dont_write_bytecode=True
import asm_r2 as A
A.setup()
import cv_board as CB, r2_arcs as A2, build10 as B10
for d in range(3): print('ring',d,CB.ring_geom(d))
f=copy.deepcopy(A.J['f1'])
for it in A2.layout_items(f): print(it['u']['id'],it['u']['kind'],'k',it['k'],'lane',it['lane'],it['a0'],it['a1'])
import wr2_lib
print(wr2_lib.LANE_COL, wr2_lib.LW)
import wr_geo; print(wr_geo.LANE if hasattr(wr_geo,'LANE') else None)
import wr2_picks; print(wr2_picks.R2)
