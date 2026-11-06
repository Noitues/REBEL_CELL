"""gate1 C16 on the effects set: green-hue px (LCh h 115-150, C* > 20, L* 40-90) in the Solace vs neutral strips, and the modal green colour.
usage: fx_green.py <file> ..."""
import sys
import numpy as np
from PIL import Image
import glib as G
for f in sys.argv[1:]:
    rgb = np.asarray(Image.open(f).convert('RGB')).astype(np.float64)
    lab = G.lab(rgb)
    C = np.hypot(lab[..., 1], lab[..., 2]); H = np.degrees(np.arctan2(lab[..., 2], lab[..., 1])) % 360
    m = (C > 20) & (H >= 115) & (H <= 150) & (lab[..., 0] > 40) & (lab[..., 0] < 90)
    col, cnt = G.modal(rgb[m], 8) if m.any() else (None, 0)
    med = np.median(rgb[m], 0) if m.any() else None
    print('%-40s green-hue px %7d  median %s  dE(median, GAIN) %s  dE(median, HP green) %s' % (
        f.split('/')[-1], int(m.sum()), G.hexof(med) if med is not None else '-',
        round(G.de_cols(med, '#7BE07B'), 1) if med is not None else '-', round(G.de_cols(med, '#7BD37B'), 1) if med is not None else '-'))
