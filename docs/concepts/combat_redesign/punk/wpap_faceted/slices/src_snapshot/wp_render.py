"""wp_render: render the WPAP FACETED plates.  usage: python wp_render.py A|B beat out.png"""
import sys, os, time
sys.dont_write_bytecode = True
var = sys.argv[1] if len(sys.argv) > 1 else 'A'
beat = sys.argv[2] if len(sys.argv) > 2 else 'p1'
ROOT = 'D:/rc_scratch/combat_redesign/punk_slices/wpap_faceted/'
out = sys.argv[3] if len(sys.argv) > 3 else ROOT + 'out/plate_%s.png' % var
import wp_lib
wp_lib.VAR[0] = var
import f1_tower, f1_guns, st_cards, st_ui
import wp_tower, wp_cards, wp_ui, wp_guns
f1_tower.render_tower = wp_tower.render_tower
f1_guns.make_guns = wp_guns.make_guns
st_cards.render_card = wp_cards.render_card
st_ui.send_it = wp_ui.send_it
st_ui.nameplate = wp_ui.nameplate
st_ui.you_strip = wp_ui.you_strip
import f1_render as R
import f1_hand as FH
W = ROOT + 'w3_%s/' % var
os.makedirs(W, exist_ok=True)
R.WORK = W
FH.CACHE = W
R.A.S2.needle = lambda *a, **k: None          # ART CALL 52: no needle in the new concept
if __name__ == '__main__':
    t = time.time()
    im = R.render(beat)
    im.save(out)
    print('ok', round(time.time() - t, 1))
