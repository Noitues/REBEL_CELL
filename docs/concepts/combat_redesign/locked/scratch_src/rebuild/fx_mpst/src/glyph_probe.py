"""glyph_probe.py [asm]: draw the HUD's KA_twist chain glyph after the mp_bases import order (or the asm_render order with 'asm')
-> work/look/glyph_<order>.png, to find why the chain TWIST glyph differs from the published p3"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
order = sys.argv[1] if len(sys.argv) > 1 else 'mp'
if order == 'asm':
    from PIL import ImageDraw
    import lw_render as LW
    import card_render as CR
else:
    import lw_render as LW
import cv_lib, hud2
from PIL import Image
L = cv_lib.L2()
L.glyph(hud2.GL['Twist'], 22, (60, 60), (255, 255, 255))
im = L.done().crop((30, 30, 90, 90)).resize((240, 240), Image.NEAREST)
bg = Image.new('RGBA', im.size, (0, 0, 0, 255))
bg.alpha_composite(im)
bg.save('D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/work/look/glyph_%s.png' % order)
import crests15
print(order, hud2.GL['Twist'], crests15.CUSTOM.get(hud2.GL['Twist']))
