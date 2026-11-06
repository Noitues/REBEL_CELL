import sys, time
sys.dont_write_bytecode = True
import card_render as C
from PIL import Image
names = sys.argv[1:] or C.ORDER
t = time.time()
ims = [C.draw_card(n, 176 * 2) for n in names]
print('t', time.time() - t)
w = ims[0].width
cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGBA', (cols * w, rows * ims[0].height), (40, 34, 52, 255))
for i, im in enumerate(ims):
    sh.alpha_composite(im, ((i % cols) * w, (i // cols) * ims[0].height))
sh.convert('RGB').save('D:/rc_scratch/combat_redesign/locked/cards/work/quick.png')
