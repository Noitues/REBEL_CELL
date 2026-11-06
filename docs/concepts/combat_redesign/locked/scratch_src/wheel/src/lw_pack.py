"""lw_pack: copy the five plates to the deliverable folder, make wheel_crop.jpg (2x) and the grey proof."""
import os, sys
sys.dont_write_bytecode = True
from PIL import Image
O = 'D:/rc_scratch/combat_redesign/locked/wheel/out/'
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/wheel/'
os.makedirs(D, exist_ok=True)
names = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords'}
for k, n in names.items():
    Image.open(O + 'lw_%s.png' % k).convert('RGB').save(D + n + '.png')
p1 = Image.open(O + 'lw_p1.png').convert('RGB')
box = (330, 300, 760, 760)
c = p1.crop(box).resize(((box[2] - box[0]) * 2, (box[3] - box[1]) * 2), Image.LANCZOS)
c.save(D + 'wheel_crop.jpg', quality=93)
g = p1.convert('L').convert('RGB')
g.save(D + 'grey_proof.jpg', quality=92)
gc = g.crop(box).resize(c.size, Image.LANCZOS)
w = Image.new('RGB', (c.width * 2 + 20, c.height), (21, 18, 28))
w.paste(c, (0, 0)); w.paste(gc, (c.width + 20, 0))
w.save(D + 'wheel_crop_colour_grey.jpg', quality=93)
print('packed')
