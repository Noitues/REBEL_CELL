"""wheel_crop.jpg: old single-colour wheel vs A vs B at 2x.  python sl_wheel.py OUT.jpg"""
import sys
from PIL import Image, ImageDraw, ImageFont
R = 'D:/rc_scratch/combat_redesign/punk_slices/jinx_scribble/out/'
OLD = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/jinx_scribble/plate_B.png'
FD = 'D:/rc_art/art-pass/assets/fonts/'
ANT = ImageFont.truetype(FD + 'Anton-Regular.ttf', 34)
box = (330, 330, 745, 770)
ims = [(Image.open(OLD), 'OLD  one colour (hot pink)'), (Image.open(R + 'plate_A_p1.png'), 'A  NIGHT WALL  per-type colour + texture'), (Image.open(R + 'plate_B_p1.png'), 'B  HOT PAINT  per-type colour + texture')]
tiles = [im.convert('RGB').crop(box).resize(((box[2] - box[0]) * 2, (box[3] - box[1]) * 2), Image.LANCZOS) for im, _ in ims]
w, h = tiles[0].size
o = Image.new('RGB', (w * 3 + 20, h + 56), (14, 12, 24))
d = ImageDraw.Draw(o)
for i, (t, (_, n)) in enumerate(zip(tiles, ims)):
    o.paste(t, (i * (w + 10), 56))
    d.text((i * (w + 10) + 12, 10), n, font=ANT, fill=(255, 70, 170) if i == 0 else (46, 235, 255))
o.save(sys.argv[1], quality=92)
print(o.size)
