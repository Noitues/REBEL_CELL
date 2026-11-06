"""gate1 C14 (read-only proxy for the render-order bug): the card glyphs are player family and skin-independent, so the hand / played-slot
pixels of p1, p2, p3 and nowords must match across neutral, Solace and Meridian.  Diff the card boxes (inset 6 px) per beat.
Also diff p3 vs p1 hand where the same card sits in the same slot (Spin3 on p3 slot 0 is Brace on p1, so only report).
Output printed."""
import numpy as np
import glib as G
BOX = {'p1': [(940, 790, 1100, 1050), (1110, 790, 1280, 1040), (1282, 790, 1445, 1035), (1450, 790, 1640, 1040)],
       'p2': [(940, 790, 1100, 1050), (1110, 790, 1280, 1040), (1282, 600, 1460, 850), (1485, 790, 1660, 1040)],
       'p3': [(935, 790, 1135, 1050), (1120, 780, 1275, 1030), (1290, 780, 1440, 1030), (1450, 790, 1625, 1040)],
       'nowords': [(940, 790, 1100, 1050), (1110, 790, 1280, 1040), (1282, 790, 1445, 1035), (1450, 790, 1640, 1040)]}
NAME = G.NAME
for beat, boxes in BOX.items():
    imgs = {c: G.load(G.FINAL + NAME[beat] + ('' if c == 'neutral' else '_' + c) + '.png') for c in G.CORPS}
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        a = imgs['neutral'][y0:y1, x0:x1]
        for c in ('solace', 'meridian'):
            b = imgs[c][y0:y1, x0:x1]
            d = np.abs(a - b).max(-1)
            print('%-8s box %d %s vs neutral: px > 2: %6d  max %3d' % (beat, i, c, int((d > 2).sum()), int(d.max())))
