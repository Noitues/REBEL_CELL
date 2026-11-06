"""Median colour of the most saturated pixels in a box. Usage: python pick.py <png> x0,y0,x1,y1 ..."""
import sys
import numpy as np
from PIL import Image

def main():
    im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
    for box in sys.argv[2:]:
        x0, y0, x1, y1 = (int(v) for v in box.split(','))
        r = im[y0:y1, x0:x1].reshape(-1, 3)
        sat = r.max(1) - r.min(1)
        sel = r[sat >= np.percentile(sat, 90)]
        med = np.median(sel, 0).astype(int)
        print(box, 'top-10%% saturated median #%02X%02X%02X' % tuple(med), 'n', len(sel))

if __name__ == '__main__':
    main()
