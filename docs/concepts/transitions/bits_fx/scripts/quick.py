import sys, importlib, time
from fxlib import *
opt = importlib.import_module('fx_' + sys.argv[1])
which = sys.argv[2]; ts = [float(x) for x in sys.argv[3].split(',')]
fr = getattr(opt, which)
tiles = []
t0 = time.time()
for t in ts: tiles.append(np.asarray(to_pil(fr(t)).resize((640, 360))))
print('s/frame', (time.time() - t0) / len(ts))
rows = [np.hstack(tiles[i:i + 2]) if len(tiles[i:i + 2]) == 2 else np.hstack([tiles[i], tiles[i] * 0]) for i in range(0, len(tiles), 2)]
Image.fromarray(np.vstack(rows).astype(np.uint8)).save('../work/q_%s_%s.png' % (sys.argv[1], which))
