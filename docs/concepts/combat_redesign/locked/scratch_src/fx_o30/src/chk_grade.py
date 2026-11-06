import numpy as np
from PIL import Image
F='D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/p3_resolve.png'
a=np.asarray(Image.open(F).convert('RGB')).astype(int)
b=np.asarray(Image.open('D:/rc_scratch/combat_redesign/locked/fx_o30/work/base_neutral_p3.png').convert('RGB')).astype(int)
k=np.asarray(Image.open('D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/base_neutral_p3kill.png').convert('RGB')).astype(int)
yy,xx=np.mgrid[0:1080,0:1920]; r=np.hypot(xx-536,yy-540)
d=np.abs(a-b).max(2)
for nm,m in (('board r<505',r<505),('room',r>=505)):
    print(nm,'px>6 share',round(((d>6)&m).sum()/m.sum(),4),'mean diff',round(float(np.abs(a-b)[m].mean()),2))
