"""lw_render: render the locked wheel plates.   python lw_render.py <beat> [out.png]      beats: p1 p2 p2b p3 nowords
Stack: F1 generator (f1_render) + F1 cards (placeholders, st_cards untouched) + xerox guns (pink marker) + lw_tower (spinner) + lw_ui (player pieces)
+ lw_install with lw_skin.NeutralSkin (neutral corp base) and the corp-independent tape.   env LW_SKIN=0 renders the unskinned F1 board."""
import sys, os, time
sys.dont_write_bytecode = True
beat = sys.argv[1] if len(sys.argv) > 1 else 'p1'
HERE = 'D:/rc_scratch/combat_redesign/locked/corp/'
out = sys.argv[2] if len(sys.argv) > 2 else HERE + 'out/lw_%s.png' % beat
import f1_tower, f1_guns, st_cards, st_ui
import xf_tower, xf_guns
import lw_tower, lw_ui
f1_tower.render_tower = lw_tower.render_tower
f1_guns.make_guns = xf_guns.make_guns
st_ui.send_it = lw_ui.send_it
st_ui.nameplate = lw_ui.nameplate
st_ui.you_strip = lw_ui.you_strip
import f1_render as R
import f1_hand as FH
import a2_stick as AS
from PIL import Image
import numpy as np
R.A.S2.needle = lambda *a, **k: None          # ART CALL 52: no needle
import lw_install as LI
from lw_skin import NeutralSkin
import cs_skin as _CS
_CORP = os.environ.get('CORP', 'neutral')
SKIN = NeutralSkin() if _CORP == 'neutral' else _CS.SKINS[_CORP]
if os.environ.get('LW_SKIN', '1') == '1':
    LI.install(SKIN)
# O-30 fix 2: the room grade (bd_grade, per-room parameters from locked/backdrop/grade.json) is the default room grade.
# 2026-11-03 stage 2: rb2-1 grade (review 2.8).  env BD_GRADE=step6 renders with the step6-1 table; BD_GRADE=0 restores r2_ground.grade('P').
import bd_grade as _BG
OLD_GRADE = R.A.G2.grade
if os.environ.get('BD_GRADE', '1') != '0':
    R.A.G2.grade = _BG.room_grade
W = HERE + 'work/'
os.makedirs(W, exist_ok=True)
R.WORK = W
FH.CACHE = W

# UNDO is player-owned: replace the stack layer's slate UNDO box with the paper tab
_orig_stack = AS.stack_layer


def stack_layer(words, sel):
    lay, info = _orig_stack(words, sel)
    a = np.asarray(lay).copy()
    a[846:906, 1650:1915] = 0
    lay = Image.fromarray(a, 'RGBA')
    u, (x0, y0) = lw_ui.undo(nw=not words)
    lay.alpha_composite(u, (x0, y0))
    return lay, info


AS.stack_layer = stack_layer

# 2026-11-03 rebuild (AD review IMPL items, locked/REVIEW_RESPONSE.md): installed last, over every layer above.  env RB=0 = the O-30 board.
if os.environ.get('RB', '1') == '1':
    import rb_patch as _RB
    _RB.install(R, R.A, SKIN)
    # stage 2 of the rebuild (bill digits, tickets, Heat glyph, REFUND tab, YOU hatch, hand margin, played slots).  env RB2=0 skips it.
    if os.environ.get('RB2', '1') == '1':
        import rb2_patch as _RB2
        _RB2.install(R, R.A, SKIN)
        # 2026-11-04: the gate-1 fixes (value order of the E / K marks, TURRET, BEST chip, cell ratio vs the brightest empty, the dying cell,
        # the Adjuster track, the resolve log).  env RB3=0 skips it.
        if os.environ.get('RB3', '1') == '1':
            import rb3_patch as _RB3
            _RB3.install(R, R.A, SKIN)

if __name__ == '__main__':
    t = time.time()
    im = R.render(beat)
    im.save(out)
    print('ok', out, round(time.time() - t, 1))
