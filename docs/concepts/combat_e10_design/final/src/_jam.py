import sys; sys.dont_write_bytecode=True
import asm_glyphs as AG, kglyph2 as KG
ids=list(KG.IDS)
for px in (16,20,28,37,44,70):
    best=sorted(((round(KG.iou(AG.mask('jammer'),AG.mask(h),px),3),h) for h in ids if h!='jammer'),reverse=True)[:3]
    print(px,best)
# stroke width of the jammer arc at 20 px: min width of the outer arc crop
import numpy as np
m=np.asarray(AG.mask('jammer'))>127
print('mask px fill',int(m.sum()))
