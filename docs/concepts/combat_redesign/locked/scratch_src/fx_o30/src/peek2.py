import numpy as np
from PIL import Image
F='D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
a=np.asarray(Image.open(F+'p3_resolve.png').convert('RGB')).astype(int)
row=a[513, 1400:1600]
# violet-ish pixels
v=(row[:,2]>180)&(row[:,0]>100)&(row[:,1]<120)
xs=np.nonzero(v)[0]+1400
print('violet x runs', xs.min(), xs.max())
runs=[];s=xs[0];p=xs[0]
for x in xs[1:]:
    if x!=p+1: runs.append((s,p)); s=x
    p=x
runs.append((s,p)); print(runs)
for y in range(495,532,3): 
    r=a[y,1400:1600]; vv=(r[:,2]>180)&(r[:,0]>100)&(r[:,1]<120); print(y, vv.sum())
Image.open(F+'p3_resolve.png').crop((1080,490,1600,540)).resize((1560,150)).save('D:/rc_scratch/combat_redesign/locked/fx_o30/work/peek_hud.png')
Image.open(F+'p3_resolve.png').crop((1130,770,1650,1080)).save('D:/rc_scratch/combat_redesign/locked/fx_o30/work/peek_slots.png')
