"""quick previews: CORP=.. python quick2.py t5|t6 t1 t2 ...  -> out/quick_<corp>.jpg (tiles) ; also checks layers vs the published plate"""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fx2lib import *
import fx_a2 as M
which = sys.argv[1]
ts = [float(x) for x in sys.argv[2:]]
ims = [to_pil(getattr(M, which)(t)) for t in ts]
cols = 2
S = Image.new('RGB', (960 * cols, 540 * ((len(ims) + 1) // cols)), (0, 0, 0))
for i, im in enumerate(ims):
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 90, 20], fill=(0, 0, 0)); d.text((4, 3), '%s %.2f' % (which, ts[i]), fill=(255, 255, 255))
    S.paste(im, ((i % cols) * 960, (i // cols) * 540))
S.save(HERE + 'out/quick_%s.jpg' % CORP, quality=88)
pub = {'neutral': 'p1_decide.png', 'solace': 'p1_decide_solace.png'}[CORP]
P = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/' + pub).convert('RGB').resize((W, H), Image.LANCZOS)).astype(int)
print('layers vs published plate (960): max', int(np.abs(P - np.clip(PLATE, 0, 255).astype(int)).max()), 'mean', float(np.abs(P - np.clip(PLATE, 0, 255).astype(int)).mean()))
