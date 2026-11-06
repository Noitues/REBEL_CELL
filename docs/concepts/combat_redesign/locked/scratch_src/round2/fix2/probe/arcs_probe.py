"""draw the f1 landing arcs alone on a fresh layer (lw_render installed) and report rb5's HOT chevron replays; saves the layer over black
python arcs_probe.py <out.png>"""
import sys, os, copy
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import lw_render as LW
from PIL import Image
import r2_arcs as A2
import gram as G
import rb5_patch as RB5
R = LW.R
A = R.A
print('A2.landing_arcs', A2.landing_arcs, getattr(A2.landing_arcs, '_rb5', None))
print('gram CFG colour', G.CFG.get('colour'))
print('G.arc_chevrons', G.arc_chevrons)
L = R.L2()
A.E.reg_reset()
A2.landing_arcs(L, copy.deepcopy(A.J['f1']), {})
print('INFO', {k: v for k, v in RB5.INFO.items() if k != 'lift'})
im = L.im.resize((1920, 1080), Image.LANCZOS)
bg = Image.new('RGBA', im.size, (0, 0, 0, 255))
bg.alpha_composite(im)
bg.convert('RGB').save(sys.argv[1])
