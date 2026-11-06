import sys; sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
F='D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/'
ims={n:np.asarray(Image.open(F+n+'.png').convert('RGB'),np.float32) for n in ('p1_decide','p2_preview','p2b_hover','p3_resolve','p1_nowords')}
H,W=1080,1920
yy,xx=np.mgrid[0:H,0:W]
rho=np.hypot(xx-536,yy-540)
for lo,hi in ((360,386),(500,516),(516,522),(522,535),(535,560),(560,600)):
    m=(rho>=lo)&(rho<hi)&(xx>10)&(xx<1000)
    print(lo,hi,{n[:6]:round(float(a[m].mean()),2) for n,a in ims.items()})
d=np.abs(ims['p1_decide']-ims['p2_preview']).sum(-1)
m=(rho>=516)&(rho<600)&(xx>10)&(xx<1000)
print('p1 vs p2 diff px outside bezel',int((d[m]>6).sum()))
d=np.abs(ims['p1_decide']-ims['p2b_hover']).sum(-1)
m=(rho>=520)&(rho<700)
ys,xs=np.nonzero((d>6)&m)
print('p2b vs p1 outside r520: n',len(xs),'bbox',xs.min(),ys.min(),xs.max(),ys.max())
# radial mean diff
for lo in range(520,700,20):
    mm=(rho>=lo)&(rho<lo+20)&(xx<1000)
    print(lo, round(float((ims['p2b_hover']-ims['p1_decide'])[mm].mean()),2))
