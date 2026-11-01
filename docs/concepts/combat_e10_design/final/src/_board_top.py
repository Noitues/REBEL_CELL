import sys; sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
import measure_regions as M
im=Image.open('../out/rm_bio.png').convert('RGB'); l=M.squint(im); room,board=M.regions()
v=np.where(board,l,0); idx=np.argsort(v.ravel())[::-1][:12]
for i in idx: print(round(float(v.ravel()[i]),3),(i%120*16+8,i//120*16+8))
print('board cells>0.30',int(((l>0.30)&board).sum()),'>0.38',int(((l>0.38)&board).sum()))
