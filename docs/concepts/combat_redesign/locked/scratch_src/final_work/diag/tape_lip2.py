import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import lw_render as LW
from PIL import Image
from cv_lib import L2
A = LW.R.A
mode = sys.argv[2]
if mode == 'nolip':
    A.S2.LIVE_LIP = (10, 10, 10)
if mode == 'noglow':
    L2.glow = lambda self, *a, **k: None
if mode == 'noremap':
    import lw_install as LI
    LI._remap = lambda L, mk: None
f = A.J['f1']
bg = Image.new('RGBA', (1920, 1080), (14, 16, 22, 255))
L = L2()
A.S2.SKIP_LABELS[0] = True
A.S2.schedule(L, f['schedule'], {})
bg.alpha_composite(L.done())
bg.crop((600, 130, 720, 190)).resize((420, 210), Image.LANCZOS).save(sys.argv[1])
