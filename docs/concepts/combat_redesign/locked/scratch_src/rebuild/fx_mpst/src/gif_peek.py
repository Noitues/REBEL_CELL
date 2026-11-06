"""gif_peek.py <gif> <out> <frame...>: stack the given GIF frames (1x) for looking"""
import sys
from PIL import Image, ImageSequence
g = Image.open(sys.argv[1])
want = [int(v) for v in sys.argv[3:]]
fr = {}
for i, f in enumerate(ImageSequence.Iterator(g)):
    if i in want:
        fr[i] = f.convert('RGB')
print('frames', g.n_frames, 'size', g.size, 'durations ms', g.info.get('duration'))
ims = [fr[i] for i in want if i in fr]
c = Image.new('RGB', (ims[0].width * 2, ims[0].height * ((len(ims) + 1) // 2)), (40, 40, 50))
for k, im in enumerate(ims):
    c.paste(im, ((k % 2) * im.width, (k // 2) * im.height))
c.save(sys.argv[2])
