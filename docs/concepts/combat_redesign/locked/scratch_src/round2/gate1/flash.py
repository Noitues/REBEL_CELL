"""gate1 C13: general-flash count per tile on a GIF's decoded frames (durations honoured, merged frames expanded to 80 ms steps).
Tile = 120 px at 1080p (scaled to the GIF), stride half a tile.  Per tile: mean relative luminance per step; a 'change' is a monotone swing of
>= 0.10 whose darker end is < 0.80 (WCAG 2.x general flash); a flash = two opposing changes.  Report the worst tile's flashes in any 1 s
window, and the whole frame.  usage: flash.py <gif> [tile_px_at_1080=120]"""
import sys
import numpy as np
from PIL import Image, ImageSequence
import glib as G
g = Image.open(sys.argv[1])
T = int(sys.argv[2]) if len(sys.argv) > 2 else 120
frames, durs = [], []
for fr in ImageSequence.Iterator(g):
    frames.append(np.asarray(fr.convert('RGB')).astype(np.float64))
    durs.append(fr.info.get('duration') or 80)
step = min(durs)
seq = []
for f, d in zip(frames, durs):
    seq += [f] * max(1, int(round(d / step)))
H, W = seq[0].shape[:2]
t = max(4, int(round(T * H / 1080)))
Y = np.stack([G.lum(f) for f in seq])  # n,H,W


def changes(series):
    # extract monotone swings between local extrema, keep those >= 0.1 with min < 0.8
    ex = [0]
    for i in range(1, len(series) - 1):
        a, b, c = series[i - 1], series[i], series[i + 1]
        if (b - a) * (c - b) < 0:
            ex.append(i)
    ex.append(len(series) - 1)
    out = []
    for i in range(1, len(ex)):
        a, b = series[ex[i - 1]], series[ex[i]]
        if abs(b - a) >= 0.10 and min(a, b) < 0.80:
            out.append(ex[i])
    return out


def worst_1s(ch):
    win = int(round(1000 / step))
    best = 0
    for s in range(0, max(1, len(seq) - win + 1)):
        n = sum(1 for c in ch if s <= c < s + win)
        best = max(best, n // 2)
    return best


worst = (0, None)
for y in range(0, H - t + 1, t // 2):
    for x in range(0, W - t + 1, t // 2):
        s = Y[:, y:y + t, x:x + t].mean((1, 2))
        f = worst_1s(changes(s))
        if f > worst[0]:
            worst = (f, (x, y))
whole = worst_1s(changes(Y.mean((1, 2))))
# also report the largest single-step tile luminance change
mx = 0
for y in range(0, H - t + 1, t // 2):
    for x in range(0, W - t + 1, t // 2):
        s = Y[:, y:y + t, x:x + t].mean((1, 2))
        mx = max(mx, float(np.abs(np.diff(s)).max()))
print('%s steps %d x %d ms, tile %d px (=%d at 1080p): worst tile flashes in any 1 s = %d at %s; whole frame %d; max tile step dY %.3f' % (
    sys.argv[1].split('/')[-1], len(seq), step, t, T, worst[0], worst[1], whole, mx))
