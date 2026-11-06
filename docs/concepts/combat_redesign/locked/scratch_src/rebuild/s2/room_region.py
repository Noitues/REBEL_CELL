"""room_region.py <plate.png> <sfx> : split the rb_checks room region into hull / city parts and print L* stats; writes room_region.png"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import rb_checks as RC
import rb_tokens as T
import bd_grade as BG

png, sfx = sys.argv[1], sys.argv[2]
rgb = np.asarray(Image.open(png).convert('RGB'), np.float64)
Y = T.lum(rgb)
M = RC.load_masks(sfx)
fam = RC.family_regions(M, None, Y, np.zeros((1080, 1920), bool), np.zeros((1080, 1920), bool))
room = fam['room']
m, d = BG.hull(BG.BASE)
Ls = T.lstar(Y)
for nm, sel in (('room all', room), ('room hull m>0.5', room & (m > 0.5)), ('room city m<=0.5', room & (m <= 0.5)),
                ('review room box', None), ('review city box', None)):
    if sel is None:
        x0, y0, x1, y1 = T.REVIEW_ROOM_BOX if 'room' in nm else T.REVIEW_CITY_BOX
        sel = np.zeros((1080, 1920), bool); sel[y0:y1, x0:x1] = True
    print('%-18s px %7d  mean L* %5.1f  p50 %5.1f  p95 %5.1f' % (nm, sel.sum(), float(T.lstar(Y[sel].mean())), np.percentile(Ls[sel], 50), np.percentile(Ls[sel], 95)))
vis = (rgb * 0.35).astype(np.uint8)
vis[room & (m > 0.5)] = (rgb[room & (m > 0.5)] * 0.5 + np.array([0, 120, 0]) * 0.5).astype(np.uint8)
vis[room & (m <= 0.5)] = (rgb[room & (m <= 0.5)] * 0.5 + np.array([120, 0, 120]) * 0.5).astype(np.uint8)
Image.fromarray(vis).resize((960, 540), Image.LANCZOS).save('D:/rc_scratch/combat_redesign/locked/rebuild/s2/room_region.png')
