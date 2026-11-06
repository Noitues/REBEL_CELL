import json, numpy as np
from PIL import Image
W='D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/'
g=json.load(open(W+'geo_neutral_p3.json'))
for k,v in g['pips'].items(): print('pip',k,[[round(x,1) for x in p[:4]]+[p[4]] for p in v])
for w in g['wheel_f1']: print('f1',w)
for w in g['wheel_f2']: print('f2',w)
for nm in ('yel','pink'):
    a=np.asarray(Image.open(W+'trig_%s.png'%nm))[:,:,3]; ys,xs=np.nonzero(a>20); print(nm, xs.min(),ys.min(),xs.max(),ys.max(), len(xs))
ref=np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/p3_resolve.png').convert('RGB')).astype(int)
b=np.asarray(Image.open(W+'base_neutral_p3.png').convert('RGB')).astype(int); print('p3 diff', np.abs(ref-b).mean())
