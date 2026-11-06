import sys
sys.dont_write_bytecode = True
from a_render import *
OUTD = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/actions/'
FAV = dict(send='A', undo='A', name='A', mat='A', snw='A', hint='A', rtoken='A', rburst='A', tpath='A', tbadge='A', fire='A', htag='B', hpath='A', hslice='A', hfdim='A', hodim='A', hcell='A', ctar='A')
names = {'p1': 'fav_p1_decide', 'p2': 'fav_p2_preview', 'p2b': 'fav_p2b_hover', 'p3': 'fav_p3_resolve', 'nowords': 'fav_p1_nowords'}
for b in sys.argv[1:] or list(names):
    sel = dict(FAV)
    if b == 'nowords':
        sel.pop('name')
    render(b, sel).save(OUTD + names[b] + '.png')
    print(b, flush=True)
