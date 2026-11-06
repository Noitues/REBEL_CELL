"""mask_look.py <sfx> <plate.png> : overlay the rb_checks room region and the hud mask on a plate (writes mask_<sfx>.png, half size)"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import rb_checks as RC

sfx, png = sys.argv[1], sys.argv[2]
M = RC.load_masks(sfx)
z = np.zeros((1080, 1920), bool)
room = RC.family_regions(M, None, None, z, z)['room']
a = np.asarray(Image.open(png).convert('RGB')).astype(np.float32) * 0.5
for k, col in (('hud', (0, 200, 255)), ('you', (255, 255, 0))):
    if k in M:
        a[M[k]] = a[M[k]] * 0.4 + np.array(col) * 0.6
a[room] = a[room] * 0.4 + np.array((255, 0, 200)) * 0.6
print({k: int(v.sum()) for k, v in M.items()})
Image.fromarray(a.astype(np.uint8)).resize((960, 540), Image.LANCZOS).save('D:/rc_scratch/combat_redesign/locked/rebuild/s2/mask_%s.png' % sfx)
