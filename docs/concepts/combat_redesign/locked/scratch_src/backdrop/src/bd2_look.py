"""bd2_look.py : compose p1 on every solved room (work/bd2_params.json) and write 1x room crops work/look_<key>.png (x 960-1920, y 380-900)
and a half-scale sheet work/look_sheet.jpg, for looking at every room at 1x before publishing"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
from PIL import Image
import bd2_lib as L

J = json.load(open(L.HERE + 'work/bd2_params.json'))
jobs = [(k, k, 'neutral') for k in L.ROOMS] + [('bio_solace', 'bio', 'solace'), ('shop_meridian', 'shop', 'meridian')]
ims = []
for name, room, corp in jobs:
    key = 'shop_meridian' if name == 'shop_meridian' else room
    if key not in J:
        continue
    pl = L.compose(L.backdrop(room, J[key]), corp).astype(np.uint8)
    im = Image.fromarray(pl)
    im.crop((960, 380, 1920, 900)).save(L.HERE + 'work/look_%s.png' % name)
    ims.append(im.resize((960, 540), Image.LANCZOS))
    print('look', name, flush=True)
cols = 3
rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGB', (960 * cols, 540 * rows))
for i, im in enumerate(ims):
    sh.paste(im, ((i % cols) * 960, (i // cols) * 540))
sh.resize((sh.width // 2, sh.height // 2), Image.LANCZOS).save(L.HERE + 'work/look_sheet.jpg', quality=90)
