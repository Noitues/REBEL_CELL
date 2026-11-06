import sys
from PIL import Image
sys.dont_write_bytecode = True
O = 'D:/rc_scratch/combat_redesign/locked/assembled/out/'
def crop(src, box, dst, k=4):
    im = Image.open(O + src).convert('RGB').crop(box)
    im.resize((im.width * k, im.height * k), Image.LANCZOS).save(O + dst)
crop('as_p1.png', (430, 890, 650, 970), '_c1.png', 5)
crop('as_p2b.png', (840, 440, 1120, 620), '_c2.png', 4)
