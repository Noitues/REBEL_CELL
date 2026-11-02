"""mk_graded_room.py: the bio room with the O-30 default room grade (corp/src bd_grade.room_grade, no board scrim).
It is what the generator draws under the board scrim, so T5 K1 / T6 end share the plate's room (one room reference).
-> fx_o30b/tr/room_bio_graded.png"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import numpy as np
from PIL import Image
import lw_render as LW
import bd_grade as BG
A = LW.R.A
A.set_room(LW.R.ROOM)
g = BG.room_grade('P')
out = 'D:/rc_scratch/combat_redesign/locked/fx_o30b/tr/room_bio_graded.png'
Image.fromarray(np.clip(np.round(g), 0, 255).astype(np.uint8)).save(out)
bare = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_bio_bare.png').convert('RGB')).astype(np.float32) / 255
gg = g / 255.0
lum = lambda a: (a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722).mean()
print('ok', out, 'mean luma bare %.3f graded %.3f' % (lum(bare), lum(gg)), 'room key', BG.room_key(getattr(__import__('o_ground'), 'BARE_PATH', None) or getattr(__import__('r2_ground'), 'BARE_PATH', None)))
