"""dbg_ell.py : PIL ellipse widths for float bboxes vs a line of the same width (2x px)"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
for r in (3.0, 6.0, 7.0, 13.0):
    for q in (r - 0.5, r - 1.0):
        ws = []
        for cx in (20.0, 20.3, 20.5, 20.7):
            im = Image.new('L', (60, 60), 0)
            ImageDraw.Draw(im).ellipse([cx - q, 30 - q, cx + q, 30 + q], fill=255)
            a = np.asarray(im) > 0
            ws.append(int(a[30].sum()))
        im = Image.new('L', (60, 60), 0)
        ImageDraw.Draw(im).line([(30, 5), (30.2, 55)], fill=255, width=int(round(2 * r)))
        lw = int((np.asarray(im)[30] > 0).sum())
        print('r %.1f q %.1f ellipse widths %s line width %d' % (r, q, ws, lw))
