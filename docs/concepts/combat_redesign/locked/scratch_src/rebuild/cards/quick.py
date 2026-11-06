"""quick: render named cards in given states side by side.  python quick.py out.png W state[,state] Name [Name ...]"""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import card_render as C
from PIL import Image
out, w, states, names = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(','), sys.argv[4:] or C.ORDER
tiles = []
for st in states:
    row = []
    for n in names:
        s = dict(mode=st)
        if st == 'nowords':
            s = dict(mode='normal', nowords=True)
        if st == 'unaff_nw':
            s = dict(mode='unaffordable', nowords=True)
        row.append(C.draw_card(n, w, s))
    tiles.append(row)
tw, th = tiles[0][0].size
im = Image.new('RGB', (tw * len(names), th * len(states)), (38, 42, 54))
for r, row in enumerate(tiles):
    for c, t in enumerate(row):
        im.paste(t, (c * tw + (tw - t.width) // 2, r * th + (th - t.height) // 2), t)
im.save(out)
print(out, im.size)
