"""quick previews: CORP=.. python quick3.py t5|t6 t1 t2 ...  -> out/quick_<corp>_<which>.jpg (960 px tiles, 2 per row) and a 1:1 crop
sheet out/quick_<corp>_<which>_crop.png of the first time (board area); prints the frame time and the layers-vs-plate check."""
import sys, os, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
t_0 = time.time()
from fx3lib import *
import fx3 as M
print('setup', round(time.time() - t_0, 1), flush=True)
which = sys.argv[1]
ts = [float(x) for x in sys.argv[2:]]
os.makedirs(HERE + 'out', exist_ok=True)
ims = []
for t in ts:
    t1 = time.time()
    a = getattr(M, which)(t)
    ims.append(to_pil(a))
    print('%s %.2f  %.1f s' % (which, t, time.time() - t1), flush=True)
cols = 2
S = Image.new('RGB', (960 * cols, 540 * ((len(ims) + 1) // cols)), (0, 0, 0))
for i, im in enumerate(ims):
    sm = im.resize((960, 540), Image.BOX)
    d = ImageDraw.Draw(sm); d.rectangle([0, 0, 110, 22], fill=(0, 0, 0)); d.text((4, 4), '%s %.2f' % (which, ts[i]), fill=(255, 255, 255))
    S.paste(sm, ((i % cols) * 960, (i // cols) * 540))
S.save(HERE + 'out/quick_%s_%s.jpg' % (CORP, which), quality=88)
ims[0].save(HERE + 'out/quick_%s_%s_full.png' % (CORP, which))
d = np.abs(np.clip(full_plate(), 0, 255).round() - PLATE)
print('layers vs published plate: max', float(d.max()), 'mean', round(float(d.mean()), 4))
