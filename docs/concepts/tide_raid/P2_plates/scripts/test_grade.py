import numpy as np
from PIL import Image
import p1lib as L, p1_comp as C, p2_grade as G
geo = dict(np.load(L.WORK + 'geo.npz'))
P = C.load_plate()
r = G.grade_city(P, geo)
img = r['img']
refl = G.wet_reflect(r['emis'], r['wet'])
out = C.haze(img + refl * 0.9, strength=0.18)
Image.fromarray((C.tone(out) * 255 + .5).astype(np.uint8)).save(L.WORK + 'test_grade.png')
print('ok')
