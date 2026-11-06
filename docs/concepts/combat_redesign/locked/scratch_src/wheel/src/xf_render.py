"""xf_render: render the XEROX FLYER plates.  usage: python xf_render.py A|B beat out.png"""
import sys, os, time
sys.dont_write_bytecode = True
var = sys.argv[1] if len(sys.argv) > 1 else 'A'
beat = sys.argv[2] if len(sys.argv) > 2 else 'p1'
out = sys.argv[3] if len(sys.argv) > 3 else 'D:/rc_scratch/combat_redesign/locked/wheel/out/plate_%s.png' % var
import f1_tower, f1_guns, st_cards, st_ui
import xf_tower, xf_cards, xf_ui, xf_guns
for m in (xf_tower, xf_cards, xf_ui, xf_guns):
    pass
xf_tower.VAR[0] = var
f1_tower.render_tower = xf_tower.render_tower
f1_guns.make_guns = xf_guns.make_guns
st_cards.render_card = xf_cards.render_card
st_ui.send_it = xf_ui.send_it
st_ui.nameplate = xf_ui.nameplate
st_ui.you_strip = xf_ui.you_strip
import f1_render as R
import f1_hand as FH
W = 'D:/rc_scratch/combat_redesign/locked/wheel/work_%s_%s/' % (var, os.environ.get('XF_V', 'v2'))
os.makedirs(W, exist_ok=True)
R.WORK = W
FH.CACHE = W
R.A.S2.needle = lambda *a, **k: None          # ART CALL 52: no needle in the new concept
if __name__ == '__main__':
    t = time.time()
    im = R.render(beat)
    im.save(out)
    print('ok', round(time.time() - t, 1))
