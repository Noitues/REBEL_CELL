import sys
from PIL import Image
p, i, o = sys.argv[1], int(sys.argv[2]), sys.argv[3]
im = Image.open(p); print('frames', im.n_frames, 'dur', im.info.get('duration'))
im.seek(i); im.convert('RGB').save(o)
