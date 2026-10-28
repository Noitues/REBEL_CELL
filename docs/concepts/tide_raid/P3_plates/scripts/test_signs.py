import numpy as np, time
from PIL import Image
import p1lib as L, p1_comp as C, p2_grade as G, p2_signs as S
geo = dict(np.load(L.WORK + 'geo.npz'))
P = np.load(L.WORK + 'recon15.npz')['P']
t = time.time()
s = S.signs(geo, P)
print(len(s['walls']), time.time() - t, s['hero'])
r = G.grade_city(C.load_plate(), geo)
img = r['img'] * (1 - s['body'][..., None] * .7) + s['emis']
refl = G.wet_reflect(r['emis'] + s['emis'] * .5, r['wet'])
out = C.haze(img + refl * .9, strength=.18)
Image.fromarray((C.tone(out) * 255 + .5).astype(np.uint8)).save(L.WORK + 'test_signs.png')
