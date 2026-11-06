"""Print image sizes for the given files."""
import sys
from PIL import Image
for p in sys.argv[1:]:
    im = Image.open(p)
    n = getattr(im, 'n_frames', 1)
    print(p.split('/')[-1], im.size, 'frames', n)
