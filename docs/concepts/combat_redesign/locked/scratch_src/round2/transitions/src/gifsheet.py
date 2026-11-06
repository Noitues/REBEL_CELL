"""gifsheet.py <gif> <out prefix>: every stored frame of a GIF at 1x (960 x 540), four to a 1920 x 1080 sheet, labelled with frame index
and duration, for frame-stepping the published GIFs by eye."""
import sys, os
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1])
pre = sys.argv[2]
fr = []
i = 0
while True:
    try:
        im.seek(i)
    except EOFError:
        break
    fr.append((i, im.info.get('duration', 0), im.convert('RGB').copy()))
    i += 1
for s in range(0, len(fr), 4):
    S = Image.new('RGB', (1920, 1080), (0, 0, 0))
    for k, (j, d, f) in enumerate(fr[s:s + 4]):
        x, y = (k % 2) * 960, (k // 2) * 540
        S.paste(f, (x, y))
        dr = ImageDraw.Draw(S)
        dr.rectangle([x, y, x + 150, y + 16], fill=(0, 0, 0))
        dr.text((x + 4, y + 2), 'frame %d  %d ms' % (j, d), fill=(255, 255, 255))
    S.save('%s_%d.png' % (pre, s // 4))
print(len(fr), 'frames')
