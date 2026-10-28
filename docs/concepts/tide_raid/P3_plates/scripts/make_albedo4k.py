"""P2_S=2 python make_albedo4k.py : the graded city at 3840x2160 (native Godot 4K capture) -> WORK/city_albedo4k.png (Blender spill albedo) and a base preview."""
import numpy as np
from PIL import Image
import p1lib as L, p1_comp as C, p2_grade as G, p2_signs as S

assert C.S == 2
geo = dict(np.load(L.WORK + 'geo30.npz'))
P = np.load(L.WORK + C.REC)['P']
sg = S.signs(geo, P)
r = G.grade_city(C.load_plate(), geo)
img = r['img'] * (1 - sg['body'][..., None] * .7) + sg['emis']
refl = G.wet_reflect(r['emis'] + sg['emis'] * .5, r['wet'])
out = C.haze(img + refl * .9, strength=.18)
Image.fromarray((C.tone(out) * 255 + .5).astype(np.uint8)).save(L.WORK + 'city_albedo4k.png')
print('ok', out.shape)
