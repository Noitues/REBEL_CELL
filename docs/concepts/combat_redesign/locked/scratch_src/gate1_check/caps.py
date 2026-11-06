# Pixel cap-height probe: light, low-chroma text components grouped into words; height = ink rows at a 50 % threshold
import sys, numpy as np
from scipy import ndimage as ndi
from lab import *
def words(p, box, thr=None, chroma_max=0.18, minh=6, gap=11):
    im = load(p); L = Ls(Y(im)); ch = im.max(2) - im.min(2)
    x0, y0, x1, y1 = box
    sub = L[y0:y1, x0:x1]; c = ch[y0:y1, x0:x1]
    bg = np.percentile(sub, 30)
    t = thr if thr else bg + 0.5 * (np.percentile(sub, 99.5) - bg)
    m = (sub > t) & (c < chroma_max)
    lab_, n = ndi.label(m)
    objs = ndi.find_objects(lab_)
    comps = []
    for i, sl in enumerate(objs):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if h >= minh and h < 60 and (lab_[sl] == i + 1).sum() > 6:
            comps.append([sl[1].start + x0, sl[0].start + y0, sl[1].stop + x0, sl[0].stop + y0])
    comps.sort(key=lambda b: (b[1] // 8, b[0]))
    # group into words: overlapping rows and small x gap
    W = []
    for b in sorted(comps, key=lambda b: b[0]):
        placed = False
        for w in W:
            cy_w = (w[1] + w[3]) / 2; cy_b = (b[1] + b[3]) / 2
            if abs(cy_w - cy_b) < 7 and b[0] - w[2] < gap and b[0] >= w[0]:
                w[2] = max(w[2], b[2]); w[1] = min(w[1], b[1]); w[3] = max(w[3], b[3]); w[4].append(b[3] - b[1]); placed = True; break
        if not placed:
            W.append([b[0], b[1], b[2], b[3], [b[3] - b[1]]])
    return sorted(W, key=lambda w: (w[1] // 10, w[0])), t
if __name__ == '__main__':
    p = sys.argv[1]; box = tuple(map(int, sys.argv[2].split(',')))
    W, t = words(p, box)
    print('threshold L* %.1f' % t)
    for w in W:
        hs = sorted(w[4])
        print('  word x %4d-%4d y %4d-%4d  letters %2d  heights median %d max %d  (all %s)' % (w[0], w[2], w[1], w[3], len(hs), int(np.median(hs)), max(hs), hs[:12]))
