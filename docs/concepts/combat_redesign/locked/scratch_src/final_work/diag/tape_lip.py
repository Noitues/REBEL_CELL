"""render the schedule layer alone (installed, neutral tape) and crop the tape edge, for the lip-beading check"""
import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import lw_render as LW
from PIL import Image
from cv_lib import L2
A = LW.R.A
f = A.J['f1']
out = sys.argv[1]
bg = Image.new('RGBA', (1920, 1080), (14, 16, 22, 255))
L = L2()
A.S2.SKIP_LABELS[0] = True
A.S2.schedule(L, f['schedule'], {})
bg.alpha_composite(L.done())
bg.crop((600, 130, 720, 190)).resize((840, 420), Image.LANCZOS).save(out)
