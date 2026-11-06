"""fshow.py <fdiag json> <clip> [n]: print the worst tiles' swing series with their luma, frame by frame."""
import sys, json
d = json.load(open(sys.argv[1]))
clip = sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 4
for w in d[clip]['worst'][:n]:
    print('tile x%d y%d any1s %d' % (w['x'], w['y'], w['any_1s']))
    lum = w['luma']
    for i, s in enumerate(w['swings']):
        print('  f%02d t=%.2f %.4f -> %.4f  %s' % (i, i / 25.0, lum[i], lum[i + 1], s))
