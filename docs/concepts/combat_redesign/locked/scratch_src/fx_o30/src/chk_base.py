import numpy as np
from PIL import Image
F='D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
W='D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/'
a=np.asarray(Image.open(F+'p3_resolve.png').convert('RGB')).astype(int)
b=np.asarray(Image.open(W+'base_neutral_p3.png').convert('RGB')).astype(int)
k=np.asarray(Image.open(W+'base_neutral_p3kill.png').convert('RGB')).astype(int)
d=np.abs(a-b).max(2); print('final vs cdhl p3: px>6', (d>6).sum(), 'max', d.max())
d=np.abs(k-b).max(2); ys,xs=np.nonzero(d>6); print('kill diff px', len(ys), xs.min(),xs.max(),ys.min(),ys.max())
