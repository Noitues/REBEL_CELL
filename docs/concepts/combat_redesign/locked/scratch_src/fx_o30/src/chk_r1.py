import numpy as np
from PIL import Image
F='D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
a=np.asarray(Image.open(F+'p1_decide.png').convert('RGB')).astype(int)
b=np.asarray(Image.open(F+'p3_resolve.png').convert('RGB')).astype(int)
yy,xx=np.mgrid[0:1080,0:1920]; r=np.hypot(xx-536,yy-540); ang=np.degrees(np.arctan2(xx-536,-(yy-540)))%360
m=(r>272)&(r<327)
d=np.abs(a-b).max(2)>20
for a0 in range(0,360,30):
    s=m&(ang>=a0)&(ang<a0+30); print(a0, round((d&s).sum()/s.sum(),3))
Image.fromarray(np.concatenate([a[150:930,140:930],b[150:930,140:930]],1).astype(np.uint8)).resize((790,390)).save('D:/rc_scratch/combat_redesign/locked/fx_o30/work/r1cmp.png')
