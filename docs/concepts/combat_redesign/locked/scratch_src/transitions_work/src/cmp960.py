import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fx2lib import *
P = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/p1_decide.png').convert('RGB').resize((W, H), Image.BOX)).astype(int)
d = np.abs(P - np.clip(PLATE, 0, 255).astype(int)).max(-1)
ys, xs = np.nonzero(d > 30)
print('max', d.max(), 'n>30', len(ys), 'mean', d.mean())
if len(ys):
    print(list(zip(xs[:20], ys[:20])))
Image.fromarray(np.clip(d * 3, 0, 255).astype(np.uint8)).save(HERE + 'layers/diff960.png')
