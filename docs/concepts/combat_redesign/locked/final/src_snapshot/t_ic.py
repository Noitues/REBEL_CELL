import sys
sys.dont_write_bytecode=True
import f1_geo
import asm_r2 as A
A.setup()
import wc_tower as T, wc_base as WB
import slicelib as SL
from PIL import Image
import numpy as np
out=Image.new('RGBA',(1100,260),(80,60,100,255))
x=0
for nm in ('WC2_BURST_B','WC2_TURRET_A','WC2_REPAIR_P'):
    g=T.glyph_rgba(nm,200,6,fill=(255,255,255),edge=(12,10,22))
    out.alpha_composite(g,(x,10)); x+=270
    print(nm,g.size)
SL.R_IN, SL.R_OUT = T.R_IN_M, T.R_OUT_M
prog,_=T.SLC['SHIELD']
blk=SL.icon_block(prog,None,60,3,1.0,1.0,'SHIELD')
print(blk.size if hasattr(blk,'size') else type(blk), getattr(blk,'shape',None))
out.save('../out/t_ic.png')
