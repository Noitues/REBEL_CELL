"""fx_one.py <id> <skin> <t> [reduce] -> work/one.png"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_cdhl as F
from fxk_lib import frame
fx = F.BYID.get(sys.argv[1]) or F.SHIELD_BLOCK
im = frame(fx, sys.argv[2], float(sys.argv[3]), reduce=len(sys.argv) > 4)
sc = 1.0 if im.width > 600 else 2.0
im.resize((int(im.width * sc), int(im.height * sc))).save('D:/rc_scratch/combat_redesign/locked/fx_o30b/cdhl/work/one.png')
