"""stage 2 scratch: render a few cards at the hand size (352 px wide 2x canvas, shown at 1.10x screen) to look at the rules text and the played slot."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
from PIL import Image
import card_render as CR
OUT = 'D:/rc_scratch/combat_redesign/locked/rebuild/s2/'
items = [('Spin3', 'normal'), ('Twist', 'normal'), ('Hold', 'normal'), ('Trigger', 'normal'), ('Twist', 'played'), ('Trigger', 'played'),
         ('Trigger', 'unaffordable'), ('Spin3', 'nowords')]
ims = []
for nm, st in items:
    im = CR.draw_card(nm, 352, st)
    k = 1.10 / 2.0
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    ims.append(im)
W = sum(i.width for i in ims) + 10 * len(ims)
sheet = Image.new('RGBA', (W, max(i.height for i in ims) + 20), (24, 26, 34, 255))
x = 5
for im in ims:
    sheet.alpha_composite(im, (x, 10))
    x += im.width + 10
sheet.convert('RGB').save(OUT + 'cards_1x.png')
for nm in CR.ORDER:
    print(nm, CR.rules_lines(CR.CARDS[nm]['txt']))
