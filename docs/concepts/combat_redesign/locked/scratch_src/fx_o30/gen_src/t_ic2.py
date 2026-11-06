import sys
sys.dont_write_bytecode=True
import f1_geo
import asm_r2 as A
A.setup()
import wc_tower as T
import slicelib as SL
from PIL import Image
import numpy as np
SL.R_IN, SL.R_OUT = T.R_IN_M, T.R_OUT_M
prog,_=T.SLC['SHIELD']
blk=SL.icon_block(prog,None,60,3,1.0,1.0,'SHIELD')
print(type(blk), getattr(blk,'size',None), getattr(blk,'shape',None))
a=np.asarray(blk); print(a.shape,a.dtype, a[...,3].max() if a.ndim==3 else '')
Image.fromarray(a if a.dtype==np.uint8 else (a*255).astype(np.uint8)).save('../out/t_sh.png')
print(T.SLC)
