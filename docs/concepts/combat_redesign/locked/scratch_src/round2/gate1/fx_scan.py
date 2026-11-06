"""gate1: scan every published effects file (sheets, strips, beat strip, every frame of resolve_beat.gif) for round-1 board leftovers:
 leaf green #96FF46 / #4FA83A (round-1 Solace rim; also the round-1 p2b FOCUS lime) px within dE76 8, FOCUS #D4FF00 px, teal #3A827F (round-2 rim) px within 8,
 and text 'SKIP' cannot be OCR'd here: the beat frames' HUD-edge area is cropped for viewing instead.  Output printed."""
import glob, os
import numpy as np
from PIL import Image, ImageSequence
import glib as G
E = G.ROOT + 'effects/'
files = sorted(glob.glob(E + '*.png')) + sorted(glob.glob(E + '*.jpg')) + sorted(glob.glob(E + 'strips/*'))


def scan(rgb):
    lab = G.lab(rgb)
    return (int((G.de(lab, '#96FF46') < 8).sum()), int((G.de(lab, '#4FA83A') < 8).sum()), int((G.de(lab, '#D4FF00') < 8).sum()),
            int((G.de(lab, '#3A827F') < 8).sum()))


for f in files:
    try:
        im = Image.open(f).convert('RGB')
    except Exception as e:
        print(f, e); continue
    rgb = np.asarray(im).astype(np.float64)
    if rgb.shape[0] * rgb.shape[1] > 12e6:
        rgb = rgb[::2, ::2]
    a = scan(rgb)
    print('%-60s %s leaf %6d leafdeep %6d FOCUS %6d teal %6d' % (os.path.relpath(f, E), im.size, *a))
g = Image.open(E + 'resolve_beat.gif')
n = 0
for i, fr in enumerate(ImageSequence.Iterator(g)):
    n += 1
print('resolve_beat.gif frames', n, 'size', g.size, 'durations', [fr.info.get('duration') for fr in ImageSequence.Iterator(Image.open(E + 'resolve_beat.gif'))][:80])
