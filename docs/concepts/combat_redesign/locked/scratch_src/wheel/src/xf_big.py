"""render the tower and the four cards at 2x for the style board and crops (variant arg)"""
import sys, os, json
sys.dont_write_bytecode = True
var = sys.argv[1]
import asm_r2 as A
A.setup()
import xf_tower as XT, xf_cards as XC
XT.VAR[0] = var
OUT = 'D:/rc_scratch/combat_redesign/locked/wheel/out/'
J = json.load(open('D:/rc_scratch/combat_redesign/locked/wheel/state_e10.json'))
what = sys.argv[2] if len(sys.argv) > 2 else 'both'
if what in ('both', 'tower'):
    cv = None
    im, cv = XT.render_tower(J['f1'], S=4)
    big = cv.to_image(scale=2)
    big.save(OUT + 'big_tower_%s.png' % var)
if what in ('both', 'cards'):
    for i, n in enumerate(['Brace', 'Spin3', 'Trigger', 'Twist']):
        XC.render_card(n, 'A', seed=[1, 4, 7, 10][i], ss=4, scale=2).save(OUT + 'big_card_%s_%s.png' % (var, n))
print('ok')
